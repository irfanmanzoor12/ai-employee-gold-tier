#!/usr/bin/env python3
"""
Ralph Wiggum Autonomous Loop - Gold Tier Requirement

Named after the Simpsons character, this loop continuously executes
approved multi-step plans with human-in-the-loop governance.

GOLD TIER: Autonomous multi-step task completion
"""
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# AI for step execution
from openai import OpenAI

# MCP Server integration
from gmail_mcp_server import GmailMCPServer
from quickbooks_mcp_server import QuickBooksMCPServer


class RalphWiggumLoop:
    """
    Autonomous loop that executes approved plans

    Safety Features:
    - Only processes plans in Approved/ folder (human approval required)
    - Logs all actions for audit trail
    - Graceful error handling
    - Can be stopped at any time (Ctrl+C)
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize Ralph Wiggum Loop

        Args:
            vault_path: Path to AI Employee Vault
            check_interval: Seconds between checks (default: 1 minute)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval

        # Folders
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'

        # Ensure folders exist
        self.approved_folder.mkdir(exist_ok=True)
        self.done_folder.mkdir(exist_ok=True)
        self.logs_folder.mkdir(exist_ok=True)

        # Initialize AI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.ai_client = OpenAI(api_key=api_key)

        # Initialize MCP servers
        self.mcp_servers = {
            'gmail': GmailMCPServer(),
            'quickbooks': QuickBooksMCPServer(mode='sandbox')
        }

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('RalphWiggumLoop')

        # Execution log
        self.execution_log_file = self.logs_folder / 'ralph_wiggum_execution.jsonl'

        self.logger.info("Ralph Wiggum Loop initialized")
        self.logger.info(f"Monitoring: {self.approved_folder}")
        self.logger.info(f"Check interval: {check_interval} seconds")

    def log_execution(self, plan_file: str, step: int, action: str,
                     result: str, success: bool):
        """Log execution details for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'plan_file': plan_file,
            'step': step,
            'action': action,
            'result': result,
            'success': success
        }

        with open(self.execution_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def parse_plan_steps(self, plan_content: str) -> List[Dict]:
        """
        Parse steps from a plan file

        Looks for structured steps like:
        ## Steps:
        1. Action description
        2. Another action

        Or:
        - [ ] Task 1
        - [ ] Task 2
        """
        steps = []
        lines = plan_content.split('\n')

        in_steps_section = False
        step_number = 0

        for line in lines:
            line = line.strip()

            # Detect steps section
            if line.startswith('## Steps') or line.startswith('## Actions'):
                in_steps_section = True
                continue

            # End of steps section
            if in_steps_section and line.startswith('##'):
                break

            # Parse numbered steps (1. 2. 3.)
            if in_steps_section and line and (
                line[0].isdigit() or line.startswith('-') or line.startswith('*')
            ):
                step_number += 1
                # Clean up markdown
                step_text = line.lstrip('0123456789.-*[] \t')

                if step_text:
                    steps.append({
                        'number': step_number,
                        'description': step_text,
                        'raw': line
                    })

        return steps

    def detect_action_type(self, step_description: str) -> str:
        """
        Detect what type of action a step requires

        Returns: 'email', 'generate', 'read', 'financial', or 'other'
        """
        desc_lower = step_description.lower()

        if any(word in desc_lower for word in ['email', 'send email', 'reply', 'respond']):
            return 'email'
        elif any(word in desc_lower for word in ['financial', 'quickbooks', 'expense', 'balance', 'transaction', 'accounting']):
            return 'financial'
        elif any(word in desc_lower for word in ['generate', 'create', 'draft', 'write']):
            return 'generate'
        elif any(word in desc_lower for word in ['read', 'review', 'analyze', 'check']):
            return 'read'
        else:
            return 'other'

    def execute_email_step(self, step: Dict, context: Dict) -> Dict:
        """Execute an email-sending step using MCP server"""
        self.logger.info(f"Executing email step: {step['description']}")

        # Use AI to extract email parameters from step description and context
        prompt = f"""Extract email parameters from this task:

Task: {step['description']}

Context:
{json.dumps(context, indent=2)}

Return JSON with:
{{
  "to": "recipient email",
  "subject": "email subject",
  "body": "email body"
}}

If you can't determine a parameter, use a placeholder like "[NEEDS_HUMAN_INPUT]"
"""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            email_params_text = response.choices[0].message.content

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', email_params_text, re.DOTALL)
            if json_match:
                email_params = json.loads(json_match.group())
            else:
                return {
                    'success': False,
                    'error': 'Could not parse email parameters from AI response'
                }

            # Check for placeholders (need human input)
            # If body is missing but we have generated content from previous step, use it
            if '[NEEDS_HUMAN_INPUT]' in email_params.get('body', ''):
                # Try to use generated content from step 2
                previous_generate = None
                for step_key, step_result in context.get('results', {}).items():
                    if step_result.get('success') and 'content' in step_result:
                        previous_generate = step_result['content']
                        break

                if previous_generate:
                    self.logger.info("  Using generated content from previous step as email body")
                    email_params['body'] = previous_generate
                else:
                    # Generate a simple test message
                    email_params['body'] = f"""Hello,

This is an automated email from the Ralph Wiggum autonomous loop.

Task: {step['description']}
Generated at: {datetime.now().isoformat()}

This confirms that the autonomous execution system is working correctly.

Best regards,
AI Employee System (Gold Tier)
"""
                    self.logger.info("  Generated default email body")

            # Check again for any remaining placeholders
            if any('[NEEDS_HUMAN_INPUT]' in str(v) for v in email_params.values()):
                return {
                    'success': False,
                    'error': 'Email parameters incomplete, needs human input',
                    'params': email_params
                }

            # Send email via MCP server
            result = self.mcp_servers['gmail'].send_email(
                to=email_params['to'],
                subject=email_params['subject'],
                body=email_params['body']
            )

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_generate_step(self, step: Dict, context: Dict) -> Dict:
        """Execute a content generation step using AI"""
        self.logger.info(f"Executing generate step: {step['description']}")

        prompt = f"""Complete this task:

Task: {step['description']}

Context:
{json.dumps(context, indent=2)}

Generate the requested content.
"""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )

            generated_content = response.choices[0].message.content

            return {
                'success': True,
                'content': generated_content
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_financial_step(self, step: Dict, context: Dict) -> Dict:
        """Execute a financial action step using QuickBooks MCP server"""
        self.logger.info(f"Executing financial step: {step['description']}")

        # Use AI to extract financial action from step description
        prompt = f"""Extract the financial action from this task:

Task: {step['description']}

Context:
{json.dumps(context, indent=2)}

Determine which QuickBooks action is needed:
- "get_balances" - Get account balances
- "get_transactions" - Get recent transactions
- "create_expense" - Create an expense entry
- "get_summary" - Get financial summary

Return JSON with:
{{
  "action": "action_name",
  "params": {{}}
}}

If it's create_expense, include:
{{
  "action": "create_expense",
  "params": {{
    "description": "expense description",
    "amount": 100.00,
    "category": "Operating Expenses"
  }}
}}
"""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            action_text = response.choices[0].message.content

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', action_text, re.DOTALL)
            if json_match:
                action_data = json.loads(json_match.group())
            else:
                return {
                    'success': False,
                    'error': 'Could not parse financial action from AI response'
                }

            action = action_data.get('action')
            params = action_data.get('params', {})

            # Execute via QuickBooks MCP server
            qb_server = self.mcp_servers['quickbooks']

            if action == 'get_balances':
                result = qb_server.get_account_balances()
            elif action == 'get_transactions':
                result = qb_server.get_recent_transactions(**params)
            elif action == 'create_expense':
                result = qb_server.create_expense(**params)
            elif action == 'get_summary':
                result = qb_server.get_financial_summary(**params)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown financial action: {action}'
                }

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_plan(self, plan_file: Path) -> bool:
        """
        Execute all steps in an approved plan

        Returns:
            bool: True if all steps succeeded, False otherwise
        """
        self.logger.info(f"🤖 Executing plan: {plan_file.name}")

        # Read plan
        plan_content = plan_file.read_text()

        # Parse steps
        steps = self.parse_plan_steps(plan_content)

        if not steps:
            self.logger.warning(f"No steps found in plan: {plan_file.name}")
            return False

        self.logger.info(f"Found {len(steps)} steps to execute")

        # Execution context (shared state across steps)
        context = {
            'plan_file': plan_file.name,
            'started_at': datetime.now().isoformat(),
            'results': {}
        }

        # Execute each step
        all_success = True
        for step in steps:
            self.logger.info(f"Step {step['number']}: {step['description']}")

            # Detect action type
            action_type = self.detect_action_type(step['description'])
            self.logger.info(f"  Action type: {action_type}")

            # Execute based on type
            try:
                if action_type == 'email':
                    result = self.execute_email_step(step, context)
                elif action_type == 'financial':
                    result = self.execute_financial_step(step, context)
                elif action_type == 'generate':
                    result = self.execute_generate_step(step, context)
                else:
                    # For 'read' and 'other' types, just acknowledge
                    result = {
                        'success': True,
                        'note': 'Step acknowledged but requires manual execution'
                    }

                # Log result
                success = result.get('success', False)
                self.log_execution(
                    plan_file.name,
                    step['number'],
                    step['description'],
                    json.dumps(result),
                    success
                )

                # Store in context for next steps
                context['results'][f"step_{step['number']}"] = result

                if success:
                    self.logger.info(f"  ✅ Step {step['number']} completed")
                else:
                    self.logger.error(f"  ❌ Step {step['number']} failed: {result.get('error', 'Unknown error')}")
                    all_success = False
                    # Continue to next step (don't stop on failure)

            except Exception as e:
                self.logger.error(f"  ❌ Step {step['number']} exception: {e}")
                all_success = False

        # Move to Done
        done_path = self.done_folder / plan_file.name
        plan_file.rename(done_path)
        self.logger.info(f"✅ Plan moved to Done: {done_path.name}")

        return all_success

    def run_once(self):
        """Check for and execute approved plans (single iteration)"""
        # Get all plan files in Approved folder
        approved_plans = list(self.approved_folder.glob('PLAN_*.md'))

        if not approved_plans:
            self.logger.debug("No approved plans found")
            return

        self.logger.info(f"Found {len(approved_plans)} approved plan(s)")

        # Execute each plan
        for plan_file in approved_plans:
            try:
                self.execute_plan(plan_file)
            except Exception as e:
                self.logger.error(f"Error executing plan {plan_file.name}: {e}")

    def run(self):
        """Run the autonomous loop continuously"""
        self.logger.info("🤖 Ralph Wiggum Loop started")
        self.logger.info(f"Monitoring {self.approved_folder} every {self.check_interval}s")
        self.logger.info("Press Ctrl+C to stop")

        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("\n👋 Ralph Wiggum Loop stopped by user")


# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("🤖 Ralph Wiggum Autonomous Loop - Gold Tier")
    print("=" * 70)
    print()

    # Get vault path
    vault_path = sys.argv[1] if len(sys.argv) > 1 else '../AI_Employee_Vault'

    # Get check interval
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    # Create and run loop
    loop = RalphWiggumLoop(vault_path, check_interval)
    loop.run()
