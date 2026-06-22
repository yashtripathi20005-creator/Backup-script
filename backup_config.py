"""
Configuration file for the backup script.
Edit these settings according to your needs.
"""

import os
from datetime import datetime

# Source folder to backup (change this to your folder path)
SOURCE_FOLDER = os.path.expanduser("~/Documents")  # Default: Documents folder

# Destination backup folder (change this to your backup location)
BACKUP_DESTINATION = os.path.expanduser("~/Backups")

# Backup naming format: uses timestamp
BACKUP_NAME_FORMAT = "backup_%Y%m%d_%H%M%S"

# Log file location
LOG_FILE = os.path.join(BACKUP_DESTINATION, "backup_log.txt")

# File extensions to exclude (optional)
EXCLUDE_EXTENSIONS = ['.tmp', '.log', '.cache']

# Folders to exclude (optional)
EXCLUDE_FOLDERS = ['__pycache__', '.git', 'node_modules', '.venv']

# Maximum number of backups to keep (0 = unlimited)
MAX_BACKUPS_TO_KEEP = 10

# Whether to compress the backup (True/False)
COMPRESS_BACKUP = False

# Whether to verify backup integrity (True/False)
VERIFY_BACKUP = True

# Create a backup folder with current timestamp
def get_backup_folder_name():
    """Generate a backup folder name with current timestamp"""
    timestamp = datetime.now().strftime(BACKUP_NAME_FORMAT)
    return os.path.join(BACKUP_DESTINATION, timestamp)

# Ensure destination directory exists
def ensure_destination():
    """Create destination directory if it doesn't exist"""
    if not os.path.exists(BACKUP_DESTINATION):
        os.makedirs(BACKUP_DESTINATION)
