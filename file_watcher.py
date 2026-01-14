"""
File System Watcher
Monitors a drop folder and creates tasks for new files
"""
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from base_watcher import BaseWatcher
import time
import logging


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('DropFolderHandler')

    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return

        # Wait a moment for file to be fully written
        time.sleep(0.5)

        source = Path(event.src_path)

        # Skip hidden files and temp files
        if source.name.startswith('.') or source.name.startswith('~'):
            return

        self.logger.info(f'New file detected: {source.name}')

        # Create task file in Needs_Action
        self.create_task_file(source)

    def create_task_file(self, source: Path):
        """Create a markdown task file for the dropped file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_file = self.needs_action / f'FILE_{timestamp}_{source.name}.md'

        # Get file info
        file_size = source.stat().st_size
        file_type = source.suffix or 'unknown'

        # Create task content
        content = f"""---
type: file_drop
original_name: {source.name}
file_path: {source.absolute()}
size: {file_size} bytes
file_type: {file_type}
detected: {datetime.now().isoformat()}
status: pending
priority: medium
---

# New File Detected: {source.name}

## File Information
- **Name**: {source.name}
- **Size**: {file_size:,} bytes
- **Type**: {file_type}
- **Location**: `{source.absolute()}`

## Suggested Actions
- [ ] Review file contents
- [ ] Organize into appropriate folder
- [ ] Extract any important information
- [ ] Update Dashboard with file summary

## Notes
This file was automatically detected by the File Watcher.
Claude Code should process this task and determine the best action.

---
*Created by File Watcher: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        task_file.write_text(content)
        self.logger.info(f'Created task file: {task_file.name}')


class FileWatcher:
    """Main file watcher class using watchdog"""

    def __init__(self, vault_path: str, drop_folder: str):
        """
        Initialize file watcher

        Args:
            vault_path: Path to Obsidian vault
            drop_folder: Folder to monitor for new files
        """
        self.vault_path = Path(vault_path)
        self.drop_folder = Path(drop_folder)
        self.drop_folder.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('FileWatcher')

        # Setup observer
        self.observer = Observer()
        self.handler = DropFolderHandler(vault_path)

    def start(self):
        """Start monitoring the drop folder"""
        self.logger.info(f'Starting File Watcher')
        self.logger.info(f'Monitoring: {self.drop_folder}')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info('Waiting for files... (Press Ctrl+C to stop)')

        self.observer.schedule(self.handler, str(self.drop_folder), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping File Watcher...')
            self.observer.stop()

        self.observer.join()


if __name__ == '__main__':
    # Configuration
    VAULT_PATH = '../AI_Employee_Vault'
    DROP_FOLDER = '../AI_Employee_Vault/Drop_Folder'

    # Create and start watcher
    watcher = FileWatcher(VAULT_PATH, DROP_FOLDER)
    watcher.start()
