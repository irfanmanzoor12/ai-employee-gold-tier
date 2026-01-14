#!/usr/bin/env python3
"""
Drafting Skill - LinkedIn content generation
Converts the LinkedInDraftingAgent into an Agent Skill
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_skill import Skill
from openai import OpenAI


class DraftingSkill(Skill):
    """
    Skill that generates professional LinkedIn content drafts

    Takes a LinkedIn signal as input, uses AI to generate professional
    post drafts, and saves them to Pending_Approval folder.
    """

    def __init__(self):
        super().__init__(
            name="drafting",
            description="Generates professional LinkedIn content drafts using AI",
            version="1.0.0"
        )

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.ai_client = OpenAI(api_key=api_key)

    def get_required_params(self) -> List[str]:
        return ['vault_path', 'signal_file']

    def get_optional_params(self) -> List[str]:
        return ['model', 'max_tokens', 'tone', 'audience', 'company_context']

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute LinkedIn content drafting

        Args:
            context: Must contain:
                - vault_path: Path to AI Employee Vault
                - signal_file: Path to LinkedIn signal file
                - model: (optional) OpenAI model to use
                - max_tokens: (optional) Max tokens for response
                - tone: (optional) Tone (professional, casual, etc.)
                - audience: (optional) Target audience
                - company_context: (optional) Company info

        Returns:
            dict: Result with draft_file path in output
        """
        vault_path = Path(context['vault_path'])
        signal_file = Path(context['signal_file'])

        model = context.get('model', 'gpt-4o')
        max_tokens = context.get('max_tokens', 1500)
        tone = context.get('tone', 'professional, helpful, non-spammy')
        audience = context.get('audience', 'founders, business owners, tech leaders')

        # Read signal
        signal_content = signal_file.read_text()

        # Read company context if available
        company_context = context.get('company_context')
        if not company_context:
            handbook_path = vault_path / 'Company_Handbook.md'
            if handbook_path.exists():
                company_context = handbook_path.read_text()
            else:
                company_context = "AI consulting and automation services company."

        # Create prompt
        prompt = self._create_drafting_prompt(
            signal_content,
            company_context,
            tone,
            audience
        )

        # Call OpenAI
        try:
            response = self.ai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens
            )

            draft_content = response.choices[0].message.content

            # Save draft file
            pending_folder = vault_path / 'Pending_Approval'
            pending_folder.mkdir(exist_ok=True)

            # Generate draft filename
            draft_filename = f"DRAFT_LINKEDIN_{signal_file.stem.replace('LINKEDIN_', '')}.md"
            draft_path = pending_folder / draft_filename

            # Write draft with frontmatter
            full_draft = self._create_draft_file(
                signal_file,
                draft_content,
                tone,
                audience
            )
            draft_path.write_text(full_draft)

            self.logger.info(f"Created draft: {draft_path.name}")

            return {
                'success': True,
                'output': {
                    'draft_file': str(draft_path),
                    'signal_file': str(signal_file),
                    'tokens_used': response.usage.total_tokens
                }
            }

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': f"Failed to generate draft: {str(e)}"
            }

    def _create_drafting_prompt(self, signal_content: str, company_context: str,
                                tone: str, audience: str) -> str:
        """Create the AI prompt for content drafting"""
        return f"""You are a LinkedIn Content Drafting Agent for a professional business.

COMPANY CONTEXT:
{company_context}

SIGNAL/OPPORTUNITY:
{signal_content}

TASK:
Draft a professional LinkedIn post that responds to this signal or opportunity.

TARGET AUDIENCE: {audience}
TONE: {tone}

REQUIREMENTS:
1. Provide value - don't be salesy or spammy
2. Be authentic and conversational
3. Keep it concise (200-300 words ideal)
4. Include relevant hashtags (2-3 max)
5. Optional: Include a subtle call-to-action
6. DO NOT post automatically - this is a DRAFT only

Generate:
1. **Main Draft**: The primary post text
2. **Why This Works**: Brief explanation
3. **Optional Variations**: 1-2 alternative versions (shorter/longer)

Format in clear Markdown.
"""

    def _create_draft_file(self, signal_file: Path, draft_content: str,
                          tone: str, audience: str) -> str:
        """Create draft file with frontmatter and safety warnings"""
        from datetime import datetime

        frontmatter = f"""---
type: linkedin_draft
status: draft_only
approval_required: true
generated_at: {datetime.now().isoformat()}
source_signal: {signal_file.name}
audience: {audience}
tone: {tone}
risk_level: low
skill: drafting
---

# LinkedIn Draft (NOT POSTED)

⚠️ **THIS IS A DRAFT ONLY - NOT POSTED TO LINKEDIN**
⚠️ **HUMAN APPROVAL REQUIRED BEFORE POSTING**

---

"""
        footer = """
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
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*Generated by LinkedIn Drafting Skill*
*Draft-only mode - Human-in-the-loop governance*
"""
        return frontmatter + draft_content + footer


# Export for skill registry
__all__ = ['DraftingSkill']
