"""
Gmail Watcher
Monitors Gmail inbox for new important emails and creates tasks
"""
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes (read + send for MCP server)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'  # For MCP server
]


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new important emails"""

    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 300):
        """
        Initialize Gmail Watcher

        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json from Google Cloud
            check_interval: Seconds between checks (default: 5 minutes)
        """
        super().__init__(vault_path, check_interval)

        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / 'token.json'
        self.service = None
        self.processed_ids = set()

        # Load processed IDs from file if exists
        self.processed_ids_file = self.vault_path / 'Logs' / 'gmail_processed.txt'
        self._load_processed_ids()

        # Authenticate
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Token file stores user's access and refresh tokens
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # If no valid credentials, login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info('Refreshing expired token...')
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'credentials.json not found at {self.credentials_path}\n'
                        f'Follow GMAIL_SETUP_GUIDE.md to get credentials'
                    )

                self.logger.info('Starting OAuth flow...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            self.token_path.write_text(creds.to_json())
            self.logger.info('Credentials saved')

        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('✅ Gmail API connected successfully')
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            raise

    def check_for_updates(self) -> list:
        """
        Check Gmail for new important emails

        Returns:
            List of new email messages
        """
        if not self.service:
            self.logger.error('Gmail service not initialized')
            return []

        try:
            # Query for unread important emails
            query = 'is:unread (is:important OR is:starred)'

            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed
            new_messages = [
                msg for msg in messages
                if msg['id'] not in self.processed_ids
            ]

            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new important emails')

            return new_messages

        except HttpError as error:
            self.logger.error(f'Error checking Gmail: {error}')
            return []

    def create_action_file(self, message) -> Path:
        """
        Create a task file for an email

        Args:
            message: Gmail message object (just ID initially)

        Returns:
            Path to created task file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {
                h['name']: h['value']
                for h in msg['payload']['headers']
            }

            sender = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date_str = headers.get('Date', '')
            to = headers.get('To', 'Unknown')

            # Get snippet (preview)
            snippet = msg.get('snippet', '')

            # Check for labels
            labels = msg.get('labelIds', [])
            is_important = 'IMPORTANT' in labels
            is_starred = 'STARRED' in labels

            # Determine priority
            priority = 'high' if (is_important or is_starred) else 'medium'

            # Create task file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_subject = ''.join(c for c in subject[:50] if c.isalnum() or c in (' ', '-', '_'))
            safe_subject = safe_subject.replace(' ', '_')

            filename = f'EMAIL_{timestamp}_{safe_subject}.md'
            filepath = self.needs_action / filename

            # Build task content
            content = f"""---
type: email
message_id: {message['id']}
from: {sender}
to: {to}
subject: {subject}
date: {date_str}
priority: {priority}
important: {is_important}
starred: {is_starred}
detected: {datetime.now().isoformat()}
status: pending
---

# New Email: {subject}

## 📧 Email Information
- **From:** {sender}
- **To:** {to}
- **Date:** {date_str}
- **Priority:** {priority.upper()}
- **Important:** {'Yes' if is_important else 'No'}
- **Starred:** {'Yes' if is_starred else 'No'}

## 📝 Preview
{snippet}

## 🎯 Suggested Actions
- [ ] Read full email content
- [ ] Determine if response needed
- [ ] Check for attachments
- [ ] Categorize (client, personal, spam, etc.)
- [ ] Draft response if needed (requires approval)

## 📎 Links
- Gmail Message ID: `{message['id']}`
- View in Gmail: https://mail.google.com/mail/#inbox/{message['id']}

## 🤖 AI Notes
This email was automatically detected by Gmail Watcher.
Priority level determined by Gmail importance markers.

---
*Created by Gmail Watcher: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            # Write file
            filepath.write_text(content)

            # Mark as processed
            self.processed_ids.add(message['id'])
            self._save_processed_ids()

            self.logger.info(f'Created task for email: {subject[:50]}')

            return filepath

        except HttpError as error:
            self.logger.error(f'Error creating task for message {message["id"]}: {error}')
            return None

    def _load_processed_ids(self):
        """Load previously processed email IDs"""
        if self.processed_ids_file.exists():
            content = self.processed_ids_file.read_text()
            self.processed_ids = set(line.strip() for line in content.split('\n') if line.strip())
            self.logger.info(f'Loaded {len(self.processed_ids)} processed email IDs')

    def _save_processed_ids(self):
        """Save processed email IDs to file"""
        self.processed_ids_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_ids_file.write_text('\n'.join(self.processed_ids))


if __name__ == '__main__':
    # Configuration
    VAULT_PATH = '../AI_Employee_Vault'
    CREDENTIALS_PATH = 'credentials.json'

    print("📧 Gmail Watcher for AI Employee")
    print("=" * 60)
    print()

    # Check if credentials exist
    if not Path(CREDENTIALS_PATH).exists():
        print("❌ credentials.json not found!")
        print()
        print("Please follow these steps:")
        print("1. Read GMAIL_SETUP_GUIDE.md")
        print("2. Set up Google Cloud Project")
        print("3. Download credentials.json")
        print("4. Place it in watchers/ directory")
        print()
        exit(1)

    print("Starting Gmail Watcher...")
    print(f"Vault: {VAULT_PATH}")
    print(f"Check interval: 5 minutes")
    print()

    try:
        # Create watcher
        watcher = GmailWatcher(VAULT_PATH, CREDENTIALS_PATH, check_interval=300)

        print("✅ Gmail Watcher started successfully!")
        print()
        print("Monitoring your inbox for important emails...")
        print("Press Ctrl+C to stop")
        print()

        # Run watcher
        watcher.run()

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print()
        print("Gmail Watcher stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
