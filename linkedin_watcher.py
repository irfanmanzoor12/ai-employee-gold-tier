"""
LinkedIn Watcher - Silver Tier (READ-ONLY)
Monitors LinkedIn for messages, connection requests, and keyword signals
COMPLIANCE: No posting, no commenting, human-in-the-loop only
"""
import os
import re
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ============================================================================
# CONFIGURATION (Modify as needed)
# ============================================================================

# Keywords to monitor in messages and profiles
KEYWORDS = ["hire", "project", "consulting", "ai", "automation", "freelance", "opportunity"]

# Polling interval in minutes
POLL_INTERVAL_MINUTES = 15

# LinkedIn URLs
LINKEDIN_BASE = "https://www.linkedin.com"
LINKEDIN_MESSAGES = f"{LINKEDIN_BASE}/messaging/"
LINKEDIN_NETWORK = f"{LINKEDIN_BASE}/mynetwork/invitation-manager/"

# Session storage
SESSION_DIR = Path(__file__).parent / ".linkedin_session"
COOKIES_FILE = SESSION_DIR / "cookies.json"
PROCESSED_IDS_FILE = SESSION_DIR / "processed_ids.json"

# ============================================================================


class LinkedInWatcher(BaseWatcher):
    """
    READ-ONLY LinkedIn Watcher
    Monitors for messages, connection requests, and keyword signals
    Creates task files in Needs_Action/ for human review

    CRITICAL: This watcher performs NO actions on LinkedIn
    All detected items require human approval before any response
    """

    def __init__(self, vault_path: str, check_interval: int = None):
        """
        Initialize LinkedIn Watcher

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: POLL_INTERVAL_MINUTES * 60)
        """
        if check_interval is None:
            check_interval = POLL_INTERVAL_MINUTES * 60

        super().__init__(vault_path, check_interval)

        # Create session directory
        SESSION_DIR.mkdir(parents=True, exist_ok=True)

        # Track processed items to avoid duplicates
        self.processed_ids = self._load_processed_ids()

        # Playwright browser and context
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def _load_processed_ids(self) -> set:
        """Load previously processed LinkedIn item IDs"""
        if PROCESSED_IDS_FILE.exists():
            try:
                data = json.loads(PROCESSED_IDS_FILE.read_text())
                return set(data.get('processed_ids', []))
            except Exception as e:
                self.logger.error(f'Error loading processed IDs: {e}')
        return set()

    def _save_processed_ids(self):
        """Save processed LinkedIn item IDs to avoid duplicates"""
        try:
            data = {'processed_ids': list(self.processed_ids)}
            PROCESSED_IDS_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')

    def _load_cookies(self):
        """Load saved LinkedIn session cookies"""
        if COOKIES_FILE.exists():
            try:
                cookies = json.loads(COOKIES_FILE.read_text())
                self.context.add_cookies(cookies)
                self.logger.info('✅ Loaded LinkedIn session cookies')
                return True
            except Exception as e:
                self.logger.error(f'Error loading cookies: {e}')
        return False

    def _save_cookies(self):
        """Save LinkedIn session cookies for reuse"""
        try:
            cookies = self.context.cookies()
            COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
            self.logger.info('✅ Saved LinkedIn session cookies')
        except Exception as e:
            self.logger.error(f'Error saving cookies: {e}')

    def _init_browser(self):
        """Initialize Playwright browser with persistent session"""
        if self.playwright is None:
            self.logger.info('Initializing Playwright browser...')

            self.playwright = sync_playwright().start()

            # Launch browser (headless after first login)
            headless = COOKIES_FILE.exists()  # Headless if we have cookies

            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )

            # Create persistent context
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # Load cookies if available
            self._load_cookies()

            self.page = self.context.new_page()
            self.logger.info('✅ Browser initialized')

    def _ensure_logged_in(self) -> bool:
        """
        Ensure user is logged into LinkedIn
        Returns True if logged in, False otherwise
        """
        try:
            self.page.goto(LINKEDIN_BASE, timeout=30000)
            time.sleep(2)

            # Check if we're on the feed (logged in)
            if '/feed' in self.page.url or '/mynetwork' in self.page.url:
                self.logger.info('✅ Already logged into LinkedIn')
                self._save_cookies()
                return True

            # Check if we're on login page
            if '/login' in self.page.url or 'authwall' in self.page.url:
                self.logger.warning('❌ Not logged into LinkedIn')
                self.logger.warning('Please log in manually in the browser window')
                self.logger.warning('Waiting 60 seconds for manual login...')

                # Wait for user to log in manually
                for i in range(60):
                    time.sleep(1)
                    if '/feed' in self.page.url:
                        self.logger.info('✅ Login detected!')
                        self._save_cookies()
                        return True

                self.logger.error('Login timeout - please run again and log in')
                return False

            return True

        except Exception as e:
            self.logger.error(f'Error checking login status: {e}')
            return False

    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new messages, connection requests, and keyword signals

        Returns:
            List of detected items (messages, requests, signals)
        """
        items = []

        try:
            # Initialize browser if needed
            if self.page is None:
                self._init_browser()

            # Ensure logged in
            if not self._ensure_logged_in():
                self.logger.error('Not logged into LinkedIn - skipping check')
                return []

            # Check for new messages
            messages = self._check_messages()
            items.extend(messages)

            # Check for connection requests
            requests = self._check_connection_requests()
            items.extend(requests)

            self.logger.info(f'Found {len(items)} new LinkedIn items')

        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}', exc_info=True)

        return items

    def _check_messages(self) -> list:
        """Check for new unread LinkedIn messages"""
        messages = []

        try:
            self.logger.info('Checking LinkedIn messages...')
            self.page.goto(LINKEDIN_MESSAGES, timeout=30000)
            time.sleep(3)

            # Look for unread message conversations
            # LinkedIn DOM selectors (may need updating)
            try:
                # Find unread conversation elements
                unread_selectors = [
                    'li.msg-conversations-container__pillar--unread',
                    '[aria-label*="unread"]',
                    '.msg-conversation-card__unread-count'
                ]

                for selector in unread_selectors:
                    unread_elements = self.page.query_selector_all(selector)

                    for element in unread_elements[:5]:  # Limit to 5 most recent
                        try:
                            # Extract message details
                            name = element.query_selector('[data-anonymize="person-name"]')
                            name_text = name.inner_text() if name else "Unknown"

                            # Generate unique ID based on name and timestamp
                            item_id = f"msg_{name_text}_{datetime.now().strftime('%Y%m%d')}"

                            # Skip if already processed
                            if item_id in self.processed_ids:
                                continue

                            # Check for keywords in preview
                            preview = element.query_selector('.msg-conversation-card__message-snippet')
                            preview_text = preview.inner_text() if preview else ""

                            has_keyword = any(kw.lower() in preview_text.lower() for kw in KEYWORDS)
                            priority = 'high' if has_keyword else 'medium'

                            messages.append({
                                'id': item_id,
                                'type': 'message',
                                'name': name_text,
                                'preview': preview_text[:200],
                                'priority': priority,
                                'has_keyword': has_keyword,
                                'url': LINKEDIN_MESSAGES
                            })

                        except Exception as e:
                            self.logger.debug(f'Error parsing message element: {e}')
                            continue

                    if messages:
                        break  # Found messages, no need to try other selectors

            except Exception as e:
                self.logger.debug(f'No unread messages found or selector changed: {e}')

        except Exception as e:
            self.logger.error(f'Error checking messages: {e}')

        return messages

    def _check_connection_requests(self) -> list:
        """Check for new LinkedIn connection requests"""
        requests = []

        try:
            self.logger.info('Checking connection requests...')
            self.page.goto(LINKEDIN_NETWORK, timeout=30000)
            time.sleep(3)

            # Look for pending invitation elements
            try:
                invitation_cards = self.page.query_selector_all('[data-test-invitation-card]')

                for card in invitation_cards[:5]:  # Limit to 5 most recent
                    try:
                        # Extract requester details
                        name_elem = card.query_selector('.invitation-card__name')
                        name = name_elem.inner_text() if name_elem else "Unknown"

                        headline_elem = card.query_selector('.invitation-card__subtitle')
                        headline = headline_elem.inner_text() if headline_elem else "No headline"

                        # Generate unique ID
                        item_id = f"req_{name}_{datetime.now().strftime('%Y%m%d')}"

                        # Skip if already processed
                        if item_id in self.processed_ids:
                            continue

                        # Check for keywords in headline
                        has_keyword = any(kw.lower() in headline.lower() for kw in KEYWORDS)
                        priority = 'high' if has_keyword else 'low'

                        requests.append({
                            'id': item_id,
                            'type': 'connection_request',
                            'name': name,
                            'headline': headline,
                            'priority': priority,
                            'has_keyword': has_keyword,
                            'url': LINKEDIN_NETWORK
                        })

                    except Exception as e:
                        self.logger.debug(f'Error parsing invitation card: {e}')
                        continue

            except Exception as e:
                self.logger.debug(f'No connection requests found: {e}')

        except Exception as e:
            self.logger.error(f'Error checking connection requests: {e}')

        return requests

    def create_action_file(self, item: dict) -> Path:
        """
        Create a task file in Needs_Action/ for detected LinkedIn item

        Args:
            item: Dictionary with LinkedIn item details

        Returns:
            Path to created task file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', item['name'])[:30]
            filename = f"LINKEDIN_{item['type'].upper()}_{timestamp}_{safe_name}.md"
            filepath = self.needs_action / filename

            # Determine priority
            priority = item.get('priority', 'medium')

            # Build content based on type
            if item['type'] == 'message':
                content = self._create_message_task(item, timestamp)
            elif item['type'] == 'connection_request':
                content = self._create_connection_request_task(item, timestamp)
            else:
                content = self._create_keyword_signal_task(item, timestamp)

            # Write file
            filepath.write_text(content)

            # Mark as processed
            self.processed_ids.add(item['id'])
            self._save_processed_ids()

            self.logger.info(f'Created LinkedIn task: {filename}')

            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def _create_message_task(self, item: dict, timestamp: str) -> str:
        """Create task content for LinkedIn message"""
        keyword_note = "\n⚠️ **Contains monitored keywords**" if item.get('has_keyword') else ""

        return f"""---
source: linkedin
type: message
detected_at: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
---

# LinkedIn Message

## Summary
New unread message from **{item['name']}** on LinkedIn{keyword_note}

## Details
- **From:** {item['name']}
- **Preview:** {item['preview']}
- **LinkedIn URL:** {item['url']}

## Message Preview
```
{item['preview']}
```

## Suggested Next Action
1. Open LinkedIn and read the full message
2. Assess if this is a business opportunity, spam, or personal connection
3. If relevant, draft a response for approval
4. If spam/irrelevant, archive or ignore

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic replies have been sent
- Human review and approval required before any response
- LinkedIn messages require manual action

## Keywords Detected
{', '.join([kw for kw in KEYWORDS if kw.lower() in item['preview'].lower()]) if item.get('has_keyword') else 'None'}

---
*Detected by LinkedIn Watcher: {timestamp}*
*Human review required before any action*
"""

    def _create_connection_request_task(self, item: dict, timestamp: str) -> str:
        """Create task content for LinkedIn connection request"""
        keyword_note = "\n⚠️ **Profile contains monitored keywords**" if item.get('has_keyword') else ""

        return f"""---
source: linkedin
type: connection_request
detected_at: {datetime.now().isoformat()}
priority: {item['priority']}
status: pending
---

# LinkedIn Connection Request

## Summary
New connection request from **{item['name']}**{keyword_note}

## Details
- **Name:** {item['name']}
- **Headline/Role:** {item['headline']}
- **LinkedIn URL:** {item['url']}

## Profile Information
**Headline:** {item['headline']}

## Suggested Next Action
1. Open LinkedIn and view the requester's full profile
2. Check mutual connections and background
3. Assess if this connection aligns with business goals
4. Decide: Accept, Ignore, or Reply with message

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic acceptance or rejection
- Human review required for all connections
- Manual decision required

## Keywords Detected
{', '.join([kw for kw in KEYWORDS if kw.lower() in item['headline'].lower()]) if item.get('has_keyword') else 'None'}

---
*Detected by LinkedIn Watcher: {timestamp}*
*Manual review and action required*
"""

    def _create_keyword_signal_task(self, item: dict, timestamp: str) -> str:
        """Create task content for keyword signal"""
        return f"""---
source: linkedin
type: keyword_signal
detected_at: {datetime.now().isoformat()}
priority: high
status: pending
---

# LinkedIn Keyword Signal

## Summary
Detected monitored keywords in LinkedIn activity

## Details
- **Source:** {item.get('name', 'Unknown')}
- **Context:** {item.get('context', 'N/A')}
- **Keywords Found:** {item.get('keywords', [])}
- **LinkedIn URL:** {item.get('url', LINKEDIN_BASE)}

## Suggested Next Action
1. Review the content that triggered this signal
2. Assess business relevance
3. Take appropriate manual action if needed

## Notes
⚠️ **Keyword monitoring active**
- This signal indicates potential business opportunity
- Manual review and judgment required

---
*Detected by LinkedIn Watcher: {timestamp}*
"""

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info('Browser cleaned up')
        except Exception as e:
            self.logger.error(f'Error during cleanup: {e}')

    def run(self):
        """Main loop - runs continuously with cleanup"""
        try:
            super().run()
        finally:
            self.cleanup()


if __name__ == '__main__':
    import sys

    # Configuration
    VAULT_PATH = '../AI_Employee_Vault'

    print("=" * 70)
    print("🔵 LinkedIn Watcher - Silver Tier (READ-ONLY)")
    print("=" * 70)
    print()
    print("⚠️  COMPLIANCE MODE:")
    print("   - No automatic posting")
    print("   - No automatic replies")
    print("   - No automatic connections")
    print("   - Human-in-the-loop required")
    print()
    print("📊 Monitoring:")
    print("   - New LinkedIn messages")
    print("   - Connection requests")
    print(f"   - Keywords: {', '.join(KEYWORDS)}")
    print()
    print(f"⏰ Check interval: {POLL_INTERVAL_MINUTES} minutes")
    print(f"📁 Output: {VAULT_PATH}/Needs_Action/")
    print()
    print("🔐 First-time setup:")
    print("   1. Browser will open (non-headless)")
    print("   2. Log into LinkedIn manually")
    print("   3. Session will be saved for future runs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    try:
        watcher = LinkedInWatcher(VAULT_PATH)
        watcher.run()
    except KeyboardInterrupt:
        print()
        print("LinkedIn Watcher stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'watcher' in locals():
            watcher.cleanup()
