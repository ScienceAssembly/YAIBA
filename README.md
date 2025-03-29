# YAIBA: Yet Another Interactive Behavior Analysis for VRSNS

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1fqfbRb6w7VzDEXGho6KWOLFVfQFU0WlS?usp=sharing)

## Installation

### Prerequisites

- Python (>=3.8, <3.12)
- Poetry (for package management)

### Setting up YAIBA

```bash
# Create and activate a new virtual environment
poetry env use python3.8

# Install dependencies with visualization support
poetry install --extras "visualize"

# Start Jupyter Lab
poetry run jupyter lab
```

Want to analyze user logs in VRSNS like player location, head angle, questionnaire answers?
This library is for the purpose!

![](https://raw.githubusercontent.com/ScienceAssembly/YAIBA/main/ipynb_examples/PlayerPositionPlot.gif)

## Features

* Collecting following informations in VRChat
    * Player join / leave event
    * PlayerPosition / head angle (install
      [unitypackage in this reposlitory](https://github.com/ScienceAssembly/yaiba-vrc))
    * [Yodokoro Tag Marker](https://booth.pm/ja/items/3109716) history
    * Questionnaire answers (install [unitypackage in this reposlitory](https://github.com/ScienceAssembly/yaiba-vrc))
* Pseudonymize user name / user id
* Output as CSV / JSON / Google Drive

## Example

```python
import yaiba

# Parse VRChat log to get SessionLog
with open(r"C:\Users\USER_NAME\AppData\Local\VRChat\log_XXXXX.log", "r") as fp:
    session_log = yaiba.parse_vrchat_log(fp)

# You can attach any metadata
session_log.metadata = {
    "date": "2028-07-06",
    "title": "理系集会 Cyberia",
    "instance": "第一インスタンス",
}

# Save SessionLog to file
with open("XXXX.json", "w") as fp:
    # Only stores pseudonymized username
    options = yaiba.JsonEncoder.Options.default()
    options.output_pseudo_user_name = True
    options.output_user_name = False

    # save to file
    yaiba.save_session_log(session_log, fp, options)

# Load SessionLog from file
with open("XXXX.json", "r") as fp:
    session_log = yaiba.load_session_log(fp)

# Do analysis
joined_user_names = set([
    e.pseudo_user_name
    for e in session_log.log_entries
    if isinstance(e, yaiba.log.vrc.VRCPlayerJoinEntry)
])
print(f"The number of unique user joined: {len(joined_user_names)}")
```

### Yodokoro tag marker customization

```python
import yaiba

# Parse VRChat log to get SessionLog
with open(r"C:\Users\USER_NAME\AppData\Local\VRChat\log_XXXXX.log", "r") as fp:
    config = yaiba.VRCLogParser.Config()
    config.yodokoro_tag_marker_names = [
        "tag name 1",
        "tag name 2",
        "tag name 3",
    ]
    session_log = yaiba.parse_vrchat_log(fp, config=config)
```

### Integration with Google Colab

This is useful for collaboration.

Note: Those examples only work in Google Colab.

```python
import yaiba
import yaiba_colab

with open(r"C:\Users\USER_NAME\AppData\Local\VRChat\log_XXXXX.log", "r") as fp:
    session_log = yaiba.parse_vrchat_log(fp)

# drive_id: Find share link in Google Drive, and drive_id contains in the URL 
# as follows: https://drive.google.com/drive/folders/${drive_id}?${not_related_parameters}
GOOGLE_DRIVE_ID = "xxxxxxxxx"

folder = yaiba_colab.GoogleDriveFolder(GOOGLE_DRIVE_ID)

# Upload log to Google Drive
folder.upload_log(session_log, title="20220722-理系集会-some_title")

# Get a list of logs stored in Google Drive
folder.get_log_list()

# Download a session log from Google Drive
#
# Note: `get_log_by_title` returns a list of session logs, because Google Drives allows having same title.
session_logs = folder.get_log_by_title("20220722-理系集会-some_title")

one_session_log = session_logs[0]
```
