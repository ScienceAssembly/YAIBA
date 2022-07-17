def check_running_in_colab():
    try:
        import google.colab
    except:
        assert False, "This library must be run in Google Colab"


check_running_in_colab()
from yaiba_colab.storage import GoogleDriveFolder, GoogleDriveLogFile
