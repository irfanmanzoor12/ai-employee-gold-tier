"""
Claude Reasoning Loop - Plan.md Generation System
Creates structured plans before executing complex tasks
"""
from pathlib import Path
from datetime import datetime
import json


class PlanningSystem:
    """Creates and manages execution plans for complex tasks"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

    def should_create_plan(self, task_content: str, task_type: str) -> bool:
        """
        Determine if a task needs a plan

        Args:
            task_content: Content of the task file
            task_type: Type of task (email, file_drop, manual, etc.)

        Returns:
            bool: True if task needs planning
        """
        # Keywords that indicate complexity
        complex_keywords = [
            'multiple', 'several', 'complex', 'integrate', 'build',
            'create system', 'implement', 'develop', 'design',
            'refactor', 'migrate', 'setup', 'configure',
            'approval required', 'sensitive', 'important'
        ]

        content_lower = task_content.lower()

        # Check for complexity indicators
        has_complex_keywords = any(kw in content_lower for kw in complex_keywords)

        # Check for multiple steps/actions
        has_multiple_steps = (
            content_lower.count('- [ ]') > 3 or
            content_lower.count('\n## ') > 3
        )

        # Email replies might need planning
        needs_careful_response = (
            task_type == 'email' and
            any(word in content_lower for word in ['complaint', 'refund', 'legal', 'contract'])
        )

        return has_complex_keywords or has_multiple_steps or needs_careful_response

    def create_plan(
        self,
        task_file: Path,
        task_summary: str,
        complexity: str = 'medium'
    ) -> Path:
        """
        Create a Plan.md file for a task

        Args:
            task_file: Path to the task file
            task_summary: Brief summary of what needs to be done
            complexity: low, medium, high, critical

        Returns:
            Path to created plan file
        """
        timestamp = datetime.now()
        plan_id = f"PLAN_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Create plan filename
        task_name = task_file.stem.replace('FILE_', '').replace('EMAIL_', '')[:50]
        plan_filename = f"{plan_id}_{task_name}.md"
        plan_path = self.plans_dir / plan_filename

        # Build plan template
        content = f"""---
type: execution_plan
plan_id: {plan_id}
task_file: {task_file.name}
created: {timestamp.isoformat()}
complexity: {complexity}
status: pending
---

# Execution Plan: {task_summary}

## 📋 Task Overview

**Task File:** [[{task_file.name}]]
**Complexity:** {complexity.upper()}
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Summary:**
{task_summary}

---

## 🎯 Objectives

List the main goals of this task:

1. [ ] Objective 1: _[Define primary objective]_
2. [ ] Objective 2: _[Define secondary objective]_
3. [ ] Objective 3: _[Define tertiary objective]_

---

## 📝 Step-by-Step Plan

### Phase 1: Analysis
- [ ] **Step 1.1:** Review task requirements thoroughly
- [ ] **Step 1.2:** Identify dependencies and prerequisites
- [ ] **Step 1.3:** Assess risks and potential issues
- [ ] **Step 1.4:** Determine if approval needed

### Phase 2: Preparation
- [ ] **Step 2.1:** Gather necessary information/resources
- [ ] **Step 2.2:** Verify permissions and access
- [ ] **Step 2.3:** Create backups if modifying existing data
- [ ] **Step 2.4:** Prepare rollback strategy

### Phase 3: Execution
- [ ] **Step 3.1:** Execute primary action
- [ ] **Step 3.2:** Verify action succeeded
- [ ] **Step 3.3:** Handle any errors or edge cases
- [ ] **Step 3.4:** Complete secondary actions

### Phase 4: Validation
- [ ] **Step 4.1:** Test/verify results
- [ ] **Step 4.2:** Check for side effects
- [ ] **Step 4.3:** Confirm objectives met
- [ ] **Step 4.4:** Get user confirmation if needed

### Phase 5: Completion
- [ ] **Step 5.1:** Update Dashboard with results
- [ ] **Step 5.2:** Archive task to Done/
- [ ] **Step 5.3:** Log actions taken
- [ ] **Step 5.4:** Mark plan as completed

---

## ⚠️ Risk Assessment

### Potential Risks
1. **Risk:** _[Describe potential issue]_
   - **Mitigation:** _[How to prevent/handle it]_

2. **Risk:** _[Describe potential issue]_
   - **Mitigation:** _[How to prevent/handle it]_

### Rollback Plan
If something goes wrong:
1. _[Step to undo changes]_
2. _[Step to restore state]_
3. _[Step to notify user]_

---

## 🔐 Approval Requirements

**Actions requiring approval:**
- [ ] Sending emails to external recipients
- [ ] Modifying/deleting important files
- [ ] Financial transactions
- [ ] Posting to social media
- [ ] Other sensitive actions

**Approval status:** ⏳ Pending (if applicable)

---

## 📊 Progress Tracking

**Started:** _Not yet started_
**Current Phase:** Phase 1 - Analysis
**Completed Steps:** 0 / 20
**Estimated Completion:** _To be determined_

---

## 📝 Execution Notes

_Add notes here as you execute the plan..._

### Decisions Made
- _[Date/Time]_ Decision: _[What was decided and why]_

### Issues Encountered
- _[Date/Time]_ Issue: _[Problem description]_
  - Resolution: _[How it was resolved]_

### Modifications to Plan
- _[Date/Time]_ Change: _[What was changed and why]_

---

## ✅ Completion Checklist

Before marking this plan complete:

- [ ] All objectives achieved
- [ ] All steps completed
- [ ] No errors or issues remaining
- [ ] User notified of completion
- [ ] Dashboard updated
- [ ] Task archived
- [ ] This plan archived

---

## 🔗 Related Files

- **Task File:** `Needs_Action/{task_file.name}`
- **Plan File:** `Plans/{plan_filename}`
- **Log File:** `Logs/plans.log`

---

*Plan created by Claude Reasoning Loop*
*This plan guides step-by-step execution with safety checks*
"""

        # Write plan file
        plan_path.write_text(content)

        # Log plan creation
        self._log_plan_created(plan_id, task_file.name, complexity)

        return plan_path

    def update_plan_progress(
        self,
        plan_file: Path,
        current_phase: str,
        completed_steps: int,
        total_steps: int,
        notes: str = None
    ):
        """
        Update a plan's progress

        Args:
            plan_file: Path to plan file
            current_phase: Current phase name
            completed_steps: Number of completed steps
            total_steps: Total number of steps
            notes: Optional notes to add
        """
        content = plan_file.read_text()

        # Update progress tracking section
        progress_section = f"""**Current Phase:** {current_phase}
**Completed Steps:** {completed_steps} / {total_steps}
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        # Find and replace progress section
        # (In production, use proper markdown parsing)
        # For now, simple replacement

        # Add notes if provided
        if notes:
            notes_section = f"\n\n### Latest Update\n- **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:** {notes}\n"
            content = content.replace(
                "_Add notes here as you execute the plan..._",
                f"_Add notes here as you execute the plan..._\n{notes_section}"
            )

        plan_file.write_text(content)

    def mark_plan_complete(self, plan_file: Path, success: bool = True):
        """
        Mark a plan as completed

        Args:
            plan_file: Path to plan file
            success: Whether plan completed successfully
        """
        content = plan_file.read_text()

        # Update status in frontmatter
        content = content.replace('status: pending', f'status: {"completed" if success else "failed"}')

        # Add completion note
        completion_note = f"\n\n---\n\n## ✅ Plan Completed\n\n**Status:** {'Success' if success else 'Failed'}\n**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        content += completion_note

        plan_file.write_text(content)

        # Log completion
        self._log_plan_completed(plan_file.stem, success)

    def _log_plan_created(self, plan_id: str, task_file: str, complexity: str):
        """Log plan creation"""
        log_file = self.logs / 'plans.log'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'plan_created',
            'plan_id': plan_id,
            'task_file': task_file,
            'complexity': complexity
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_plan_completed(self, plan_id: str, success: bool):
        """Log plan completion"""
        log_file = self.logs / 'plans.log'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'plan_completed',
            'plan_id': plan_id,
            'success': success
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# Example usage
if __name__ == '__main__':
    # Initialize
    planner = PlanningSystem('../AI_Employee_Vault')

    # Simulate a complex task
    from pathlib import Path
    task_file = Path('../AI_Employee_Vault/Needs_Action/SAMPLE_TASK.md')

    # Create a plan
    plan = planner.create_plan(
        task_file=task_file,
        task_summary="Review and organize quarterly business reports",
        complexity='medium'
    )

    print("✅ Plan created successfully!")
    print(f"📄 Plan file: {plan.name}")
    print(f"📁 Location: {plan}")
    print()
    print("📋 Plan structure includes:")
    print("   - Objectives checklist")
    print("   - 5-phase execution plan")
    print("   - Risk assessment")
    print("   - Approval tracking")
    print("   - Progress updates")
    print()
    print("Next: Open the plan file in Obsidian to review!")
