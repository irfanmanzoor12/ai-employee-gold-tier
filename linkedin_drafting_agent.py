"""
LinkedIn Content Drafting Agent - Silver Tier
Generates draft LinkedIn posts for human approval
🚨 DRAFT-ONLY: NO AUTOMATIC POSTING 🚨
"""
import os
import re
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============================================================================
# CONFIGURATION
# ============================================================================

# Drafting preferences
DEFAULT_TONE = "professional, helpful, non-spammy"
DEFAULT_AUDIENCE = "founders, business owners, tech leaders"
MAX_DRAFT_LENGTH = 1500  # characters

# Check interval (minutes)
POLL_INTERVAL_MINUTES = 30

# Paths
PROCESSED_SIGNALS_FILE = Path(__file__).parent / ".linkedin_drafts" / "processed_signals.json"

# ============================================================================


class LinkedInDraftingAgent:
    """
    LinkedIn Content Drafting Agent

    🚨 CRITICAL SAFETY NOTICE 🚨
    This agent ONLY generates draft content.
    It does NOT post, comment, or interact with LinkedIn.
    All drafts require explicit human approval before posting.
    """

    def __init__(self, vault_path: str, check_interval: int = None):
        """
        Initialize LinkedIn Drafting Agent

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: POLL_INTERVAL_MINUTES * 60)
        """
        if check_interval is None:
            check_interval = POLL_INTERVAL_MINUTES * 60

        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.check_interval = check_interval

        # Ensure folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        PROCESSED_SIGNALS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('LinkedInDraftingAgent')

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OPENAI_API_KEY environment variable not set')

        self.client = OpenAI(api_key=api_key)

        # Track processed signals
        self.processed_signals = self._load_processed_signals()

        # Load business context
        self.business_context = self._load_business_context()

    def _load_processed_signals(self) -> set:
        """Load list of signals that already have drafts"""
        if PROCESSED_SIGNALS_FILE.exists():
            try:
                data = json.loads(PROCESSED_SIGNALS_FILE.read_text())
                return set(data.get('processed', []))
            except Exception as e:
                self.logger.error(f'Error loading processed signals: {e}')
        return set()

    def _save_processed_signals(self):
        """Save processed signals list"""
        try:
            data = {'processed': list(self.processed_signals)}
            PROCESSED_SIGNALS_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Error saving processed signals: {e}')

    def _load_business_context(self) -> str:
        """Load business context from vault"""
        context_parts = []

        # Try to load Company_Handbook.md
        handbook = self.vault_path / 'Company_Handbook.md'
        if handbook.exists():
            try:
                context_parts.append("=== Company Handbook ===")
                context_parts.append(handbook.read_text()[:2000])  # First 2000 chars
            except Exception as e:
                self.logger.warning(f'Could not load handbook: {e}')

        # Try to load Business_Goals.md
        goals = self.vault_path / 'Business_Goals.md'
        if goals.exists():
            try:
                context_parts.append("\n=== Business Goals ===")
                context_parts.append(goals.read_text()[:1000])  # First 1000 chars
            except Exception as e:
                self.logger.warning(f'Could not load business goals: {e}')

        if context_parts:
            return "\n".join(context_parts)
        else:
            # Default context
            return """=== Default Business Context ===
Professional services business offering AI and automation solutions.
Target audience: Founders, business owners, tech leaders.
Tone: Professional, helpful, credible.
Goal: Build trust, demonstrate expertise, attract qualified leads."""

    def find_linkedin_signals(self) -> list:
        """
        Find unprocessed LinkedIn signal files in Needs_Action/

        Returns:
            List of LinkedIn signal file paths that need drafts
        """
        signals = []

        for file in self.needs_action.glob('LINKEDIN_*.md'):
            # Skip if already processed
            if file.name in self.processed_signals:
                continue

            # Check if it's a LinkedIn signal (has source: linkedin in frontmatter)
            try:
                content = file.read_text()
                if 'source: linkedin' in content:
                    signals.append(file)
            except Exception as e:
                self.logger.error(f'Error reading {file.name}: {e}')

        return signals

    def generate_draft(self, signal_file: Path) -> str:
        """
        Generate LinkedIn post draft using OpenAI

        Args:
            signal_file: Path to LinkedIn signal file

        Returns:
            Generated draft content
        """
        # Read signal content
        signal_content = signal_file.read_text()

        # Extract metadata
        signal_type = self._extract_metadata(signal_content, 'type')
        priority = self._extract_metadata(signal_content, 'priority')

        # Build prompt for OpenAI
        prompt = f"""You are a LinkedIn Content Drafting Agent for a professional services business.

🚨 CRITICAL: You are ONLY generating a DRAFT. NO posting capabilities. Human approval required.

=== BUSINESS CONTEXT ===
{self.business_context}

=== LINKEDIN SIGNAL ===
Signal Type: {signal_type}
Priority: {priority}
File: {signal_file.name}

Signal Content:
{signal_content}

=== YOUR TASK ===
Generate a professional LinkedIn post draft that:
1. Provides value or insight (no hard selling)
2. Is 3-8 short paragraphs with natural line breaks
3. Uses a professional, helpful tone
4. Demonstrates expertise without clickbait
5. Includes subtle positioning (not aggressive sales)
6. Is ready for human review and approval

=== CONSTRAINTS ===
- Target Audience: {DEFAULT_AUDIENCE}
- Tone: {DEFAULT_TONE}
- Max Length: {MAX_DRAFT_LENGTH} characters
- No emojis unless natural
- Max 3 hashtags if any
- NO "DM me" or hard CTAs
- Experience-based framing preferred

=== OUTPUT FORMAT ===
Provide:
1. Main draft text (LinkedIn-ready)
2. Brief explanation of why this works
3. Two optional variations (shorter and more conversational)

Generate the draft now:"""

        try:
            self.logger.info(f'Generating draft for: {signal_file.name}')

            response = self.client.chat.completions.create(
                model="gpt-4o",
                max_tokens=1500,
                temperature=0.7,
                messages=[{
                    "role": "system",
                    "content": "You are a professional LinkedIn content strategist. You ONLY create drafts for human approval. You NEVER automate posting."
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )

            draft_content = response.choices[0].message.content
            self.logger.info(f'Draft generated for: {signal_file.name}')

            return draft_content

        except Exception as e:
            self.logger.error(f'Error generating draft: {e}')
            raise

    def save_draft_file(self, signal_file: Path, draft_content: str) -> Path:
        """
        Save draft as Markdown file in Pending_Approval/

        Args:
            signal_file: Original signal file
            draft_content: Generated draft content

        Returns:
            Path to saved draft file
        """
        timestamp = datetime.now()

        # Create filename
        base_name = signal_file.stem.replace('LINKEDIN_', 'DRAFT_LINKEDIN_')
        filename = f"{base_name}.md"
        filepath = self.pending_approval / filename

        # Extract sections from draft_content
        # Parse the AI response to separate main draft, explanation, and variations
        sections = self._parse_draft_content(draft_content)

        # Build final draft file
        content = f"""---
type: linkedin_draft
status: draft_only
approval_required: true
generated_at: {timestamp.isoformat()}
source_signal: {signal_file.name}
audience: {DEFAULT_AUDIENCE}
tone: {DEFAULT_TONE}
risk_level: low
---

# LinkedIn Draft (NOT POSTED)

⚠️ **THIS IS A DRAFT ONLY - NOT POSTED TO LINKEDIN**
⚠️ **HUMAN APPROVAL REQUIRED BEFORE POSTING**

---

## Draft Text

{sections['main_draft']}

---

## Why This Works

{sections['explanation']}

---

## Optional Variations

{sections['variations']}

---

## Compliance Check

- [x] Draft only - NOT posted
- [x] No auto-posting capability
- [x] Human approval required
- [x] Manual posting only

---

## Next Steps for Human

1. **Review** this draft carefully
2. **Edit** as needed for your voice
3. **Decide**: Approve, Reject, or Request Revision
4. **Post Manually** on LinkedIn if approved
5. **Move to Done/** after posting (or Rejected/ if declined)

---

## Source Signal

Original signal: [[{signal_file.stem}]]
Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---

*Generated by LinkedIn Drafting Agent - Silver Tier*
*Draft-only mode - Human-in-the-loop governance*
"""

        # Write file
        filepath.write_text(content)

        # Mark signal as processed
        self.processed_signals.add(signal_file.name)
        self._save_processed_signals()

        self.logger.info(f'Draft saved: {filename}')

        return filepath

    def _parse_draft_content(self, content: str) -> dict:
        """Parse AI-generated draft into sections"""
        sections = {
            'main_draft': '',
            'explanation': '',
            'variations': ''
        }

        # Try to intelligently parse the response
        # Look for common section markers
        lines = content.split('\n')

        current_section = 'main_draft'
        buffer = []

        for line in lines:
            line_lower = line.lower().strip()

            # Detect section transitions
            if 'why this works' in line_lower or 'explanation' in line_lower:
                sections[current_section] = '\n'.join(buffer).strip()
                current_section = 'explanation'
                buffer = []
                continue
            elif 'variation' in line_lower or 'optional' in line_lower or 'alternative' in line_lower:
                sections[current_section] = '\n'.join(buffer).strip()
                current_section = 'variations'
                buffer = []
                continue

            buffer.append(line)

        # Save final section
        sections[current_section] = '\n'.join(buffer).strip()

        # Cleanup: remove empty sections
        for key in sections:
            if not sections[key]:
                sections[key] = 'N/A'

        return sections

    def _extract_metadata(self, content: str, key: str) -> str:
        """Extract metadata value from frontmatter"""
        pattern = rf'^{key}:\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE)
        return match.group(1).strip() if match else 'unknown'

    def process_signals(self):
        """Find LinkedIn signals and generate drafts"""
        signals = self.find_linkedin_signals()

        if not signals:
            self.logger.debug('No new LinkedIn signals found')
            return

        self.logger.info(f'Found {len(signals)} LinkedIn signals that need drafts')

        for signal_file in signals:
            try:
                self.logger.info(f'Processing: {signal_file.name}')

                # Generate draft
                draft_content = self.generate_draft(signal_file)

                # Save draft file
                draft_path = self.save_draft_file(signal_file, draft_content)

                self.logger.info(f'✅ Draft created: {draft_path.name}')

            except Exception as e:
                self.logger.error(f'Error processing {signal_file.name}: {e}')
                continue

    def run(self):
        """Main loop - runs continuously"""
        self.logger.info('=' * 70)
        self.logger.info('LinkedIn Drafting Agent Started - Silver Tier')
        self.logger.info('🚨 DRAFT-ONLY MODE: NO AUTOMATIC POSTING 🚨')
        self.logger.info('=' * 70)
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        self.logger.info(f'Monitoring: {self.needs_action}')
        self.logger.info(f'Output: {self.pending_approval}')
        self.logger.info('=' * 70)

        while True:
            try:
                self.process_signals()

            except KeyboardInterrupt:
                self.logger.info('Stopping LinkedIn Drafting Agent...')
                break
            except Exception as e:
                self.logger.error(f'Error in drafting loop: {e}', exc_info=True)

            time.sleep(self.check_interval)


if __name__ == '__main__':
    import sys

    # Configuration
    VAULT_PATH = '../AI_Employee_Vault'

    print("=" * 70)
    print("✍️  LinkedIn Content Drafting Agent - Silver Tier")
    print("=" * 70)
    print()
    print("🚨 CRITICAL SAFETY NOTICE:")
    print("   - This agent ONLY generates DRAFTS")
    print("   - NO automatic posting to LinkedIn")
    print("   - ALL drafts require human approval")
    print("   - Manual posting only")
    print()
    print("📊 What this agent does:")
    print("   1. Monitors Needs_Action/ for LinkedIn signals")
    print("   2. Generates professional draft posts")
    print("   3. Saves drafts to Pending_Approval/")
    print("   4. Waits for human review and approval")
    print()
    print(f"⏰ Check interval: {POLL_INTERVAL_MINUTES} minutes")
    print(f"📁 Input: {VAULT_PATH}/Needs_Action/")
    print(f"📁 Output: {VAULT_PATH}/Pending_Approval/")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print()
        print("Set it with:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
        sys.exit(1)

    try:
        agent = LinkedInDraftingAgent(VAULT_PATH)
        agent.run()
    except KeyboardInterrupt:
        print()
        print("LinkedIn Drafting Agent stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
