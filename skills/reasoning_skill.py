#!/usr/bin/env python3
"""
Reasoning Skill - AI task analysis and strategic planning
Converts the ReasoningLoop into an Agent Skill
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_skill import Skill
from openai import OpenAI


class ReasoningSkill(Skill):
    """
    Skill that analyzes tasks and creates strategic plans

    Takes a task file as input, uses AI to analyze it, and generates
    a strategic Plan.md file with actionable steps.
    """

    def __init__(self):
        super().__init__(
            name="reasoning",
            description="Analyzes tasks using AI and creates strategic plans",
            version="1.0.0"
        )

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.ai_client = OpenAI(api_key=api_key)

    def get_required_params(self) -> List[str]:
        return ['vault_path', 'task_file']

    def get_optional_params(self) -> List[str]:
        return ['model', 'max_tokens', 'company_context']

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reasoning on a task file

        Args:
            context: Must contain:
                - vault_path: Path to AI Employee Vault
                - task_file: Path to task file to analyze
                - model: (optional) OpenAI model to use
                - max_tokens: (optional) Max tokens for response
                - company_context: (optional) Company handbook content

        Returns:
            dict: Result with plan_file path in output
        """
        vault_path = Path(context['vault_path'])
        task_file = Path(context['task_file'])

        model = context.get('model', 'gpt-4o')
        max_tokens = context.get('max_tokens', 2000)

        # Read task
        task_content = task_file.read_text()

        # Read company context if available
        company_context = context.get('company_context')
        if not company_context:
            handbook_path = vault_path / 'Company_Handbook.md'
            if handbook_path.exists():
                company_context = handbook_path.read_text()
            else:
                company_context = "No company context available."

        # Create prompt
        prompt = self._create_analysis_prompt(task_content, company_context)

        # Call OpenAI
        try:
            response = self.ai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=max_tokens
            )

            plan_content = response.choices[0].message.content

            # Save plan file
            plans_folder = vault_path / 'Plans'
            plans_folder.mkdir(exist_ok=True)

            # Generate plan filename
            plan_filename = f"PLAN_{task_file.stem}.md"
            plan_path = plans_folder / plan_filename

            # Write plan with frontmatter
            full_plan = self._create_plan_file(task_file, plan_content)
            plan_path.write_text(full_plan)

            self.logger.info(f"Created plan: {plan_path.name}")

            return {
                'success': True,
                'output': {
                    'plan_file': str(plan_path),
                    'task_file': str(task_file),
                    'tokens_used': response.usage.total_tokens
                }
            }

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': f"Failed to generate plan: {str(e)}"
            }

    def _create_analysis_prompt(self, task_content: str, company_context: str) -> str:
        """Create the AI prompt for task analysis"""
        return f"""You are an AI reasoning assistant for an autonomous employee system.

Analyze the following task and create a strategic plan.

COMPANY CONTEXT:
{company_context}

TASK TO ANALYZE:
{task_content}

Create a strategic plan that includes:
1. **Summary**: Brief overview of the task
2. **Priority**: High/Medium/Low
3. **Recommended Action**: What should be done
4. **Steps**: Concrete, actionable steps to complete the task
5. **Reasoning**: Why this approach is recommended
6. **Expected Outcome**: What success looks like

Format the plan in clear Markdown with sections.
Be specific and actionable. Focus on business value.
"""

    def _create_plan_file(self, task_file: Path, plan_content: str) -> str:
        """Create plan file with frontmatter"""
        from datetime import datetime

        frontmatter = f"""---
type: strategic_plan
source_task: {task_file.name}
generated_at: {datetime.now().isoformat()}
status: pending_review
skill: reasoning
---

"""
        return frontmatter + plan_content


# Export for skill registry
__all__ = ['ReasoningSkill']
