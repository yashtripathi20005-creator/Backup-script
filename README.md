# Backup Script

A simple, configurable backup script that copies folders to a backup location with verification, logging, and automatic cleanup.

## Features

- 📁 Copy entire folder structures to backup location
- ⏱️ Timestamp-based backup folders (prevents overwriting)
- 📝 Comprehensive logging
- ✅ Backup verification (checksum validation)
- 🧹 Automatic cleanup of old backups
- 🔧 Configurable exclusions (file extensions and folders)
- 📊 Backup metadata JSON export
- 🎯 Command-line argument support
- 🔒 Preserves file metadata (timestamps, permissions)

## Requirements

- Python 3.6 or higher
- No additional packages required (uses standard library only)

## Installation

1. Download all files to your backup directory
2. Run the setup script:
   ```bash
   python setup_backup.py
