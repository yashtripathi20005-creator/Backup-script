"""
Utility functions for the backup script.
"""

import os
import shutil
import logging
from datetime import datetime
import hashlib
import json
from typing import List, Tuple

class BackupUtils:
    """Utility class for backup operations"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration"""
        if self.log_file:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file),
                    logging.StreamHandler()  # Also print to console
                ]
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
    
    def copy_folder(self, source: str, destination: str, 
                   exclude_extensions: List[str] = None, 
                   exclude_folders: List[str] = None) -> Tuple[int, int]:
        """
        Copy folder from source to destination with exclusion options.
        
        Returns:
            Tuple[int, int]: (files_copied, folders_created)
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source folder '{source}' does not exist.")
        
        if not os.path.exists(destination):
            os.makedirs(destination)
            logging.info(f"Created destination folder: {destination}")
        
        files_copied = 0
        folders_created = 0
        
        try:
            for root, dirs, files in os.walk(source):
                # Skip excluded folders
                if exclude_folders:
                    dirs[:] = [d for d in dirs if d not in exclude_folders]
                
                # Calculate relative path
                rel_path = os.path.relpath(root, source)
                target_dir = os.path.join(destination, rel_path)
                
                # Create target directory if it doesn't exist
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    folders_created += 1
                    logging.debug(f"Created directory: {target_dir}")
                
                # Copy files
                for file in files:
                    # Skip excluded extensions
                    if exclude_extensions:
                        if any(file.endswith(ext) for ext in exclude_extensions):
                            logging.debug(f"Skipped excluded file: {file}")
                            continue
                    
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    
                    # Copy file, but only if it's newer or doesn't exist
                    if not os.path.exists(dst_file) or \
                       os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                        try:
                            shutil.copy2(src_file, dst_file)  # copy2 preserves metadata
                            files_copied += 1
                            logging.debug(f"Copied: {src_file} -> {dst_file}")
                        except Exception as e:
                            logging.error(f"Error copying {src_file}: {str(e)}")
                    else:
                        logging.debug(f"Skipped (already exists and up-to-date): {src_file}")
        
        except Exception as e:
            logging.error(f"Error during backup: {str(e)}")
            raise
        
        return files_copied, folders_created
    
    def calculate_checksum(self, filepath: str) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating checksum for {filepath}: {str(e)}")
            return None
    
    def verify_backup(self, source: str, destination: str) -> bool:
        """
        Verify backup integrity by comparing checksums of files.
        Returns True if all files match, False otherwise.
        """
        logging.info("Verifying backup integrity...")
        all_matched = True
        verified_count = 0
        error_count = 0
        
        try:
            for root, dirs, files in os.walk(source):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(root, source)
                    dst_file = os.path.join(destination, rel_path, file)
                    
                    if not os.path.exists(dst_file):
                        logging.error(f"Missing file in backup: {dst_file}")
                        all_matched = False
                        error_count += 1
                        continue
                    
                    src_checksum = self.calculate_checksum(src_file)
                    dst_checksum = self.calculate_checksum(dst_file)
                    
                    if src_checksum and dst_checksum and src_checksum == dst_checksum:
                        verified_count += 1
                    else:
                        logging.error(f"Checksum mismatch for: {file}")
                        all_matched = False
                        error_count += 1
            
            logging.info(f"Verification complete: {verified_count} files verified, {error_count} errors found.")
            return all_matched
            
        except Exception as e:
            logging.error(f"Error during verification: {str(e)}")
            return False
    
    def get_folder_size(self, folder_path: str) -> int:
        """Calculate total size of a folder in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
        except Exception as e:
            logging.error(f"Error calculating folder size: {str(e)}")
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def cleanup_old_backups(self, backup_dir: str, max_keep: int):
        """Delete old backups, keeping only the most recent ones"""
        if max_keep <= 0:
            return
        
        try:
            # Get all backup folders
            items = os.listdir(backup_dir)
            backup_folders = []
            
            for item in items:
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path) and item.startswith('backup_'):
                    backup_folders.append((item_path, os.path.getmtime(item_path)))
            
            # Sort by modification time (oldest first)
            backup_folders.sort(key=lambda x: x[1])
            
            # Delete old backups
            to_delete = len(backup_folders) - max_keep
            for i in range(to_delete):
                folder_path = backup_folders[i][0]
                try:
                    shutil.rmtree(folder_path)
                    logging.info(f"Deleted old backup: {folder_path}")
                except Exception as e:
                    logging.error(f"Error deleting old backup {folder_path}: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
