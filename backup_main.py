#!/usr/bin/env python3
"""
Main backup script - Copy folder to backup location.
Usage: python backup_main.py [--verify] [--cleanup] [--source SOURCE] [--dest DEST]
"""

import os
import sys
import argparse
import time
from datetime import datetime
import json

from backup_config import (
    SOURCE_FOLDER,
    BACKUP_DESTINATION,
    EXCLUDE_EXTENSIONS,
    EXCLUDE_FOLDERS,
    MAX_BACKUPS_TO_KEEP,
    VERIFY_BACKUP,
    get_backup_folder_name,
    ensure_destination,
    LOG_FILE
)
from backup_utils import BackupUtils

def main():
    """Main backup execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Backup script for copying folders')
    parser.add_argument('--source', help='Source folder to backup (overrides config)')
    parser.add_argument('--dest', help='Destination backup folder (overrides config)')
    parser.add_argument('--verify', action='store_true', help='Verify backup integrity')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup old backups after backup')
    parser.add_argument('--max-keep', type=int, help='Maximum backups to keep (overrides config)')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')
    args = parser.parse_args()
    
    # Set up paths
    source_folder = args.source if args.source else SOURCE_FOLDER
    backup_destination = args.dest if args.dest else BACKUP_DESTINATION
    
    # Create backup destination if it doesn't exist
    ensure_destination()
    
    # Create backup folder with timestamp
    backup_folder = get_backup_folder_name()
    
    # Set up logging
    log_file = os.path.join(backup_destination, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    if args.quiet:
        # Suppress console output by setting logging to only file
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file)]
        )
        logger = logging.getLogger()
    else:
        utils = BackupUtils(log_file)
        logger = utils.setup_logging()
    
    # Initialize backup utilities
    backup_utils = BackupUtils(log_file)
    
    print("=" * 60)
    print("BACKUP SCRIPT")
    print("=" * 60)
    print(f"Source: {source_folder}")
    print(f"Destination: {backup_folder}")
    print(f"Log file: {log_file}")
    print("-" * 60)
    
    # Check if source exists
    if not os.path.exists(source_folder):
        print(f"ERROR: Source folder '{source_folder}' does not exist!")
        sys.exit(1)
    
    # Start backup process
    start_time = time.time()
    
    try:
        # Get source folder size before backup
        source_size = backup_utils.get_folder_size(source_folder)
        print(f"Source folder size: {backup_utils.format_size(source_size)}")
        print("-" * 60)
        
        # Perform the backup
        print("Starting backup...")
        files_copied, folders_created = backup_utils.copy_folder(
            source_folder,
            backup_folder,
            EXCLUDE_EXTENSIONS,
            EXCLUDE_FOLDERS
        )
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Get backup folder size
        backup_size = backup_utils.get_folder_size(backup_folder)
        
        # Print summary
        print("-" * 60)
        print("BACKUP SUMMARY")
        print("-" * 60)
        print(f"Files copied: {files_copied}")
        print(f"Folders created: {folders_created}")
        print(f"Backup size: {backup_utils.format_size(backup_size)}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Backup location: {backup_folder}")
        print("-" * 60)
        
        # Verify backup if requested
        perform_verify = args.verify if args.verify else (VERIFY_BACKUP and not args.no_verify)
        
        if perform_verify:
            print("Verifying backup integrity...")
            verify_result = backup_utils.verify_backup(source_folder, backup_folder)
            if verify_result:
                print("✓ Backup verification PASSED")
            else:
                print("✗ Backup verification FAILED - Please check the logs")
        else:
            print("Verification skipped.")
        
        # Cleanup old backups if requested
        max_keep = args.max_keep if args.max_keep is not None else MAX_BACKUPS_TO_KEEP
        
        if args.cleanup and max_keep > 0:
            print("-" * 60)
            print("Cleaning up old backups...")
            backup_utils.cleanup_old_backups(backup_destination, max_keep)
        
        # Save backup metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source": source_folder,
            "destination": backup_folder,
            "files_copied": files_copied,
            "folders_created": folders_created,
            "size_bytes": backup_size,
            "size_formatted": backup_utils.format_size(backup_size),
            "time_seconds": elapsed_time,
            "verified": perform_verify
        }
        
        metadata_file = os.path.join(backup_folder, "backup_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("-" * 60)
        print("✓ Backup completed successfully!")
        print(f"Metadata saved to: {metadata_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: Backup failed: {str(e)}")
        # Log error to file
        import logging
        logging.error(f"Backup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
