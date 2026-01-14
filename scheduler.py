"""
Scheduler for AI Employee - Orchestrates scheduled tasks
This script is called by cron to run automated tasks
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
import subprocess

# Setup logging
log_dir = Path(__file__).parent.parent / 'AI_Employee_Vault' / 'Logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'scheduler.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled task execution"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.dashboard = self.vault_path / 'Dashboard.md'

    def check_pending_tasks(self) -> int:
        """Check for pending tasks and log count"""
        tasks = list(self.needs_action.glob('*.md'))
        # Exclude SAMPLE_TASK
        tasks = [t for t in tasks if 'SAMPLE' not in t.name]

        count = len(tasks)
        logger.info(f"Found {count} pending tasks")

        return count

    def check_approvals(self) -> dict:
        """Check approval folders"""
        pending = len(list((self.vault_path / 'Pending_Approval').glob('*.md')))
        approved = len(list((self.vault_path / 'Approved').glob('*.md')))

        logger.info(f"Approvals: {pending} pending, {approved} approved")

        return {'pending': pending, 'approved': approved}

    def check_gmail(self) -> bool:
        """Check if Gmail watcher should run"""
        # Check if credentials exist
        creds = Path(__file__).parent / 'credentials.json'
        if creds.exists():
            logger.info("Gmail credentials found - ready to check email")
            return True
        else:
            logger.info("Gmail credentials not found - skipping email check")
            return False

    def daily_briefing(self):
        """Generate daily briefing"""
        logger.info("=== DAILY BRIEFING ===")

        # Task counts
        pending_tasks = self.check_pending_tasks()
        approvals = self.check_approvals()

        # Count completed tasks
        done_folder = self.vault_path / 'Done'
        completed_today = len([
            f for f in done_folder.glob('*.md')
            if f.stat().st_mtime > (datetime.now().timestamp() - 86400)
        ])

        logger.info(f"Completed in last 24h: {completed_today}")

        # Summary
        briefing = f"""
Daily Briefing - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'=' * 50}
Pending Tasks: {pending_tasks}
Pending Approvals: {approvals['pending']}
Approved Actions: {approvals['approved']}
Completed (24h): {completed_today}
{'=' * 50}
"""
        logger.info(briefing)

        # Write briefing to file
        briefing_file = self.vault_path / 'Logs' / f"briefing_{datetime.now().strftime('%Y%m%d')}.txt"
        briefing_file.write_text(briefing)

        return briefing

    def hourly_check(self):
        """Hourly task check"""
        logger.info("=== HOURLY CHECK ===")

        pending = self.check_pending_tasks()
        approvals = self.check_approvals()

        if pending > 0:
            logger.info(f"⚠️  {pending} tasks need attention")

        if approvals['pending'] > 0:
            logger.info(f"⏳ {approvals['pending']} approvals waiting")

        if approvals['approved'] > 0:
            logger.info(f"✅ {approvals['approved']} actions ready to execute")


def main():
    """Main entry point for scheduled tasks"""

    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <task_type>")
        print("Tasks: hourly_check, daily_briefing, check_gmail, process_approvals")
        sys.exit(1)

    task_type = sys.argv[1]
    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    scheduler = TaskScheduler(str(vault_path))

    logger.info(f"Starting scheduled task: {task_type}")

    try:
        if task_type == 'hourly_check':
            scheduler.hourly_check()

        elif task_type == 'daily_briefing':
            scheduler.daily_briefing()

        elif task_type == 'check_gmail':
            if scheduler.check_gmail():
                logger.info("Gmail check would run here")
                # In production: subprocess.run(['python', 'gmail_watcher.py', '--once'])

        elif task_type == 'process_approvals':
            approvals = scheduler.check_approvals()
            if approvals['approved'] > 0:
                logger.info(f"Processing {approvals['approved']} approved actions")
                # In production: Call approval processing logic

        else:
            logger.error(f"Unknown task type: {task_type}")
            sys.exit(1)

        logger.info(f"Completed scheduled task: {task_type}")

    except Exception as e:
        logger.error(f"Error in scheduled task: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
