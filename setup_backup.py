#!/usr/bin/env python3
"""
Setup script for the backup system.
Run this to configure your backup settings interactively.
"""

import os
import sys
import shutil
from backup_config import BACKUP_DESTINATION

def setup_backup():
    """Interactive setup for backup configuration"""
    print("=" * 60)
    print("BACKUP SYSTEM SETUP")
    print("=" * 60)
    
    # Check if backup directory exists
    if not os.path.exists(BACKUP_DESTINATION):
        print(f"Creating backup directory: {BACKUP_DESTINATION}")
        os.makedirs(BACKUP_DESTINATION)
        print("✓ Backup directory created")
    else:
        print(f"✓ Backup directory exists: {BACKUP_DESTINATION}")
    
    # Create a sample backup
    print("\nCreating a sample backup structure...")
    sample_config = os.path.join(BACKUP_DESTINATION, "backup_config_sample.txt")
    with open(sample_config, 'w') as f:
        f.write("Sample backup configuration file\n")
        f.write("=" * 40 + "\n\n")
        f.write("To customize your backup:\n")
        f.write("1. Edit backup_config.py\n")
        f.write("2. Set SOURCE_FOLDER to your desired source directory\n")
        f.write("3. Set BACKUP_DESTINATION to your backup location\n")
        f.write("4. Configure EXCLUDE_EXTENSIONS and EXCLUDE_FOLDERS as needed\n")
        f.write("5. Set MAX_BACKUPS_TO_KEEP to limit the number of backups\n\n")
        f.write("To run the backup:\n")
        f.write("  python backup_main.py\n\n")
        f.write("For help:\n")
        f.write("  python backup_main.py --help\n")
    
    print(f"✓ Sample configuration created: {sample_config}")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit backup_config.py to set your source folder")
    print("2. Run: python backup_main.py")
    print("\nAdditional options:")
    print("  python backup_main.py --verify          # Verify backup integrity")
    print("  python backup_main.py --cleanup         # Clean up old backups")
    print("  python backup_main.py --source /path    # Override source folder")
    print("  python backup_main.py --help            # Show all options")
    print("=" * 60)

def check_requirements():
    """Check if Python and required packages are installed"""
    print("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("✗ Python 3.6 or higher is required")
        print(f"  Current version: {sys.version}")
        return False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check for required packages (none needed for standard library)
    print("✓ All required packages are available (using standard library only)")
    
    return True

if __name__ == "__main__":
    if not check_requirements():
        sys.exit(1)
    
    try:
        setup_backup()
    except Exception as e:
        print(f"\nERROR during setup: {str(e)}")
        sys.exit(1)
