"""
Test script for File Watcher
Creates a test file to verify the watcher is working
"""
from pathlib import Path
from datetime import datetime
import time

# Paths
DROP_FOLDER = Path('../AI_Employee_Vault/Drop_Folder')
NEEDS_ACTION = Path('../AI_Employee_Vault/Needs_Action')

def create_test_file():
    """Create a test file in the drop folder"""
    DROP_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_file = DROP_FOLDER / f'test_file_{timestamp}.txt'

    content = f"""Test File for AI Employee
Created: {datetime.now().isoformat()}

This is a test file to verify the File Watcher is working correctly.

If you see a corresponding .md file in the Needs_Action folder,
then your watcher is successfully detecting new files!
"""

    test_file.write_text(content)
    print(f"✅ Created test file: {test_file.name}")
    print(f"   Location: {test_file}")
    print(f"\n⏳ Waiting 2 seconds for watcher to detect...")

    time.sleep(2)

    # Check if task file was created
    task_files = list(NEEDS_ACTION.glob('FILE_*.md'))
    if task_files:
        print(f"\n🎉 Success! Watcher created task file:")
        for task_file in sorted(task_files)[-1:]:  # Show most recent
            print(f"   {task_file.name}")
    else:
        print(f"\n⚠️  No task file found yet. Is the watcher running?")
        print(f"   Run: cd watchers && uv run python file_watcher.py")


if __name__ == '__main__':
    print("Testing File Watcher...")
    print("=" * 50)
    create_test_file()
