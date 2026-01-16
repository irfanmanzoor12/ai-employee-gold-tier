#!/usr/bin/env python3
"""
AI Employee Scheduler - Cron-like Task Scheduling

Silver Tier Requirement: Basic scheduling via cron or Task Scheduler

This module provides:
- Scheduled task execution for watchers
- Periodic CEO briefings
- Background monitoring with configurable intervals

Usage:
    python scheduler.py              # Run all scheduled tasks
    python scheduler.py --status     # Check scheduler status
    python scheduler.py --install    # Generate crontab entries
"""

import os
import sys
import time
import signal
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import threading
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIEmployeeScheduler')


class ScheduledTask:
    """Represents a scheduled task"""

    def __init__(self, name: str, command: str, interval_minutes: int,
                 enabled: bool = True, run_on_start: bool = False):
        self.name = name
        self.command = command
        self.interval_minutes = interval_minutes
        self.enabled = enabled
        self.run_on_start = run_on_start
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.running = False
        self.run_count = 0
        self.error_count = 0

    def should_run(self) -> bool:
        if not self.enabled or self.running:
            return False
        if self.next_run is None:
            return True
        return datetime.now() >= self.next_run

    def update_next_run(self):
        self.last_run = datetime.now()
        self.next_run = self.last_run + timedelta(minutes=self.interval_minutes)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'command': self.command,
            'interval_minutes': self.interval_minutes,
            'enabled': self.enabled,
            'running': self.running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'error_count': self.error_count
        }


class AIEmployeeScheduler:
    """Main scheduler for AI Employee watchers and tasks"""

    def __init__(self, vault_path: str = '../AI_Employee_Vault'):
        self.vault_path = Path(vault_path)
        self.running = False
        self.tasks: List[ScheduledTask] = []
        self.status_file = Path(__file__).parent / '.scheduler_status.json'
        self._init_default_tasks()
        logger.info("AI Employee Scheduler initialized")

    def _init_default_tasks(self):
        """Initialize default scheduled tasks"""
        
        # Gmail Watcher - Check every 2 minutes
        self.tasks.append(ScheduledTask(
            name="Gmail Watcher",
            command="gmail_watcher.py",
            interval_minutes=2,
            enabled=True,
            run_on_start=True
        ))

        # LinkedIn Watcher - Check every 5 minutes
        self.tasks.append(ScheduledTask(
            name="LinkedIn Watcher",
            command="linkedin_watcher.py",
            interval_minutes=5,
            enabled=True,
            run_on_start=False
        ))

        # Reasoning Loop - Check every 3 minutes
        self.tasks.append(ScheduledTask(
            name="Reasoning Loop",
            command="reasoning_loop.py",
            interval_minutes=3,
            enabled=True,
            run_on_start=True
        ))

        # Ralph Wiggum - Check every minute
        self.tasks.append(ScheduledTask(
            name="Ralph Wiggum",
            command="ralph_wiggum_loop.py",
            interval_minutes=1,
            enabled=True,
            run_on_start=False
        ))

        # Weekly Audit - Once per week
        self.tasks.append(ScheduledTask(
            name="Weekly Audit",
            command="weekly_audit.py",
            interval_minutes=10080,
            enabled=True,
            run_on_start=False
        ))

    def get_status(self) -> Dict:
        return {
            'running': self.running,
            'timestamp': datetime.now().isoformat(),
            'tasks': [task.to_dict() for task in self.tasks]
        }

    def save_status(self):
        with open(self.status_file, 'w') as f:
            json.dump(self.get_status(), f, indent=2)

    def load_status(self) -> Optional[Dict]:
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return None

    def print_status(self):
        status = self.load_status()
        if not status:
            print("No scheduler status found.")
            return

        print()
        print("=" * 70)
        print("📊 AI Employee Scheduler Status")
        print("=" * 70)
        print(f"Last Update: {status['timestamp']}")
        print()
        print(f"{'Task':<20} {'Interval':<10} {'Last Run':<20} {'Runs':<6} {'Errors':<6}")
        print("-" * 70)

        for task in status['tasks']:
            last = task['last_run'][:16] if task['last_run'] else 'Never'
            interval = f"{task['interval_minutes']}m"
            icon = "✅" if task['enabled'] else "⏸️"
            print(f"{icon} {task['name']:<18} {interval:<10} {last:<20} {task['run_count']:<6} {task['error_count']:<6}")
        print()

    def generate_crontab(self) -> str:
        """Generate crontab entries"""
        script_dir = Path(__file__).parent.resolve()
        python_path = sys.executable

        return f"""# AI Employee Scheduler - Generated {datetime.now().isoformat()}
# Add these entries to your crontab with: crontab -e

# Gmail Watcher - Every 2 minutes
*/2 * * * * cd {script_dir} && {python_path} gmail_watcher.py >> /tmp/gmail_watcher.log 2>&1

# LinkedIn Watcher - Every 5 minutes  
*/5 * * * * cd {script_dir} && {python_path} linkedin_watcher.py >> /tmp/linkedin_watcher.log 2>&1

# Reasoning Loop - Every 3 minutes
*/3 * * * * cd {script_dir} && {python_path} reasoning_loop.py >> /tmp/reasoning_loop.log 2>&1

# Ralph Wiggum - Every minute
* * * * * cd {script_dir} && {python_path} ralph_wiggum_loop.py >> /tmp/ralph_wiggum.log 2>&1

# Weekly Audit - Every Sunday at 8am
0 8 * * 0 cd {script_dir} && {python_path} weekly_audit.py >> /tmp/weekly_audit.log 2>&1
"""


def main():
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Scheduler')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--install', action='store_true', help='Generate crontab')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')

    args = parser.parse_args()
    scheduler = AIEmployeeScheduler(vault_path=args.vault)

    if args.status:
        scheduler.print_status()
    elif args.install:
        print(scheduler.generate_crontab())
    else:
        print()
        print("=" * 70)
        print("🤖 AI Employee Scheduler")
        print("=" * 70)
        print()
        print("Usage:")
        print("  python scheduler.py --status   # Show task status")
        print("  python scheduler.py --install  # Generate crontab entries")
        print()
        print("Tasks configured:")
        for task in scheduler.tasks:
            print(f"  • {task.name}: every {task.interval_minutes} minutes")
        print()


if __name__ == '__main__':
    main()
