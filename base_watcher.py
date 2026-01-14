"""
Base Watcher Template
All watchers inherit from this base class
"""
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Base class for all watcher types"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process
        Returns: List of items that need action
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md file in Needs_Action folder
        Returns: Path to created file
        """
        pass

    def run(self):
        """Main loop - runs continuously"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Monitoring interval: {self.check_interval} seconds')
        self.logger.info(f'Vault path: {self.vault_path}')

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    self.logger.info(f'Found {len(items)} new items to process')
                    for item in items:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created action file: {filepath.name}')
                else:
                    self.logger.debug('No new items found')

            except KeyboardInterrupt:
                self.logger.info('Stopping watcher...')
                break
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}', exc_info=True)

            time.sleep(self.check_interval)
