import io
from dataclasses import dataclass
from typing import List

import yaiba
from yaiba import JsonEncoder
from yaiba.log import JsonDecoder, SessionLog


def _get_drive_in_colab():
    """
    Only work in colab.
    """
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)
    return drive


def load_session_log(file):
    decider = JsonDecoder()
    return decider.decode(file.GetContentString())


def get_log_by_gdrive_id(gdrive_id: str) -> SessionLog:
    drive = _get_drive_in_colab()
    file = drive.CreateFile({"id": gdrive_id})
    return load_session_log(file)


@dataclass
class GoogleDriveFolder:
    """
    drive_id: Find share link in Google Drive, and drive_id contains in the URL 
    as follows: https://drive.google.com/drive/folders/${drive_id}?${not_related_parameters}
    """

    def __init__(self, drive_id: str):
        self.drive_id = drive_id

    def get_log_list(self) -> List['GoogleDriveLogFile']:
        files = self._get_log_files()
        return [
            GoogleDriveLogFile.from_gfile(file)
            for file in files
        ]

    def _get_log_files(self):
        drive = _get_drive_in_colab()
        return sum(list(drive.ListFile({
            "q": f"'{self.drive_id}' in parents and trashed = false",
            "includeItemsFromAllDrives": True,
            "supportsAllDrives": True,
        })), [])

    def get_log_by_title(self, title: str) -> List[SessionLog]:
        drive = _get_drive_in_colab()
        files = sum(list(drive.ListFile({
            "q": f"title = '{title}' and '{self.drive_id}' in parents and trashed = false",
            "includeItemsFromAllDrives": True,
            "supportsAllDrives": True
        })), [])
        if len(files) == 0:
            assert False, f'not found: {files}'
        session_logs = []
        for file in files:
            session_logs.append(
                load_session_log(drive.CreateFile({"id": file['id']}))
            )
        return session_logs

    def upload_log(self, log: SessionLog, title: str, options: JsonEncoder.Options = None):
        drive = _get_drive_in_colab()
        preprocessed_log_file = drive.CreateFile({"parents": [{"id": self.drive_id}]})
        fp = io.StringIO()
        yaiba.save_session_log(log, fp, options)
        preprocessed_log_file.SetContentString(fp.getvalue())
        preprocessed_log_file['title'] = title
        preprocessed_log_file.Upload()
        return preprocessed_log_file


@dataclass
class GoogleDriveLogFile():
    title: str
    id: str
    created_time: str
    modified_time: str
    owner_display_name: str

    @classmethod
    def from_gfile(cls, gfile):
        # See: https://developers.google.com/drive/api/v3/reference/files
        get_owner_display_name = lambda owners: owners[0].get('displayName', 'no name') if len(owners) > 0 else ''
        return cls(
            title=gfile['title'],
            id=gfile['id'],
            created_time=gfile['createdDate'],
            modified_time=gfile['modifiedDate'],
            owner_display_name=get_owner_display_name(gfile['owners']),
        )

    def get_session_log(self) -> SessionLog:
        return get_log_by_gdrive_id(self.id)
