#!/usr/bin/env python3
"""
Silver Tier - Complete End-to-End Integration Test
Tests all components working together
"""
import os
import sys
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("🏆 SILVER TIER - END-TO-END INTEGRATION TEST")
print("=" * 70)
print()

# Test results tracking
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_passed(name):
    results['passed'].append(name)
    print(f"✅ PASS: {name}")

def test_failed(name, reason):
    results['failed'].append(f"{name}: {reason}")
    print(f"❌ FAIL: {name}")
    print(f"   Reason: {reason}")

def test_warning(name, reason):
    results['warnings'].append(f"{name}: {reason}")
    print(f"⚠️  WARN: {name}")
    print(f"   Reason: {reason}")

# ============================================================================
# TEST 1: Environment Setup
# ============================================================================
print("TEST 1: Environment Setup")
print("-" * 70)

# Check OpenAI API Key
if os.getenv('OPENAI_API_KEY'):
    test_passed("OpenAI API Key is set")
else:
    test_failed("OpenAI API Key", "OPENAI_API_KEY not set")

# Check Python environment
try:
    import openai
    test_passed("OpenAI SDK installed")
except ImportError:
    test_failed("OpenAI SDK", "Not installed")

try:
    from playwright.sync_api import sync_playwright
    test_passed("Playwright installed")
except ImportError:
    test_warning("Playwright", "Not installed (needed for LinkedIn Watcher)")

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    test_passed("Google API libraries installed")
except ImportError:
    test_warning("Google API", "Not installed (needed for Gmail Watcher)")

print()

# ============================================================================
# TEST 2: Vault Structure
# ============================================================================
print("TEST 2: Vault Structure")
print("-" * 70)

vault = Path('../AI_Employee_Vault')
required_folders = [
    'Needs_Action',
    'Plans',
    'Pending_Approval',
    'Done',
    'Approved',
    'Rejected'
]

for folder in required_folders:
    folder_path = vault / folder
    if folder_path.exists():
        test_passed(f"Folder exists: {folder}/")
    else:
        test_failed(f"Folder: {folder}/", "Does not exist")

# Check key files
if (vault / 'Company_Handbook.md').exists():
    test_passed("Company_Handbook.md exists")
else:
    test_warning("Company_Handbook.md", "Not found (used for context)")

if (vault / 'Dashboard.md').exists():
    test_passed("Dashboard.md exists")
else:
    test_warning("Dashboard.md", "Not found")

print()

# ============================================================================
# TEST 3: Core Components
# ============================================================================
print("TEST 3: Core Components")
print("-" * 70)

components = {
    'base_watcher.py': 'Base watcher abstraction',
    'reasoning_loop.py': 'Reasoning Loop (AI planning)',
    'linkedin_watcher.py': 'LinkedIn Watcher (read-only)',
    'linkedin_drafting_agent.py': 'LinkedIn Drafting Agent',
    'gmail_watcher.py': 'Gmail Watcher',
    'approval_system.py': 'Approval System'
}

for file, desc in components.items():
    if Path(file).exists():
        test_passed(f"{desc}: {file}")
    else:
        test_failed(desc, f"{file} not found")

# Check credentials
if Path('credentials.json').exists():
    test_passed("Gmail credentials.json exists")
else:
    test_warning("Gmail credentials", "credentials.json not found")

if Path('token.json').exists():
    test_passed("Gmail token.json exists (authenticated)")
else:
    test_warning("Gmail token", "token.json not found (not authenticated)")

print()

# ============================================================================
# TEST 4: Reasoning Loop
# ============================================================================
print("TEST 4: Reasoning Loop Integration")
print("-" * 70)

try:
    from reasoning_loop import ReasoningLoop
    test_passed("Reasoning Loop imports successfully")

    # Check if it can initialize
    try:
        loop = ReasoningLoop('../AI_Employee_Vault', check_interval=0)
        test_passed("Reasoning Loop initializes")
    except ValueError as e:
        if 'OPENAI_API_KEY' in str(e):
            test_failed("Reasoning Loop initialization", "API key not set")
        else:
            test_failed("Reasoning Loop initialization", str(e))
    except Exception as e:
        test_failed("Reasoning Loop initialization", str(e))

except ImportError as e:
    test_failed("Reasoning Loop import", str(e))

# Check if plans exist
plans = list(Path('../AI_Employee_Vault/Plans').glob('PLAN_*.md'))
if plans:
    test_passed(f"Plan files found: {len(plans)} plans")
    print(f"   Latest: {plans[-1].name}")
else:
    test_warning("Plan files", "No plans found yet")

print()

# ============================================================================
# TEST 5: LinkedIn Drafting Agent
# ============================================================================
print("TEST 5: LinkedIn Drafting Agent Integration")
print("-" * 70)

try:
    from linkedin_drafting_agent import LinkedInDraftingAgent
    test_passed("LinkedIn Drafting Agent imports successfully")

    try:
        agent = LinkedInDraftingAgent('../AI_Employee_Vault', check_interval=0)
        test_passed("LinkedIn Drafting Agent initializes")
    except ValueError as e:
        if 'OPENAI_API_KEY' in str(e):
            test_failed("Drafting Agent initialization", "API key not set")
        else:
            test_failed("Drafting Agent initialization", str(e))
    except Exception as e:
        test_failed("Drafting Agent initialization", str(e))

except ImportError as e:
    test_failed("LinkedIn Drafting Agent import", str(e))

# Check if drafts exist
drafts = list(Path('../AI_Employee_Vault/Pending_Approval').glob('DRAFT_*.md'))
if drafts:
    test_passed(f"Draft files found: {len(drafts)} drafts")
    print(f"   Latest: {drafts[-1].name}")
else:
    test_warning("Draft files", "No drafts found yet")

print()

# ============================================================================
# TEST 6: Workflow Integration
# ============================================================================
print("TEST 6: Complete Workflow Verification")
print("-" * 70)

# Check Needs_Action has tasks
tasks = list(Path('../AI_Employee_Vault/Needs_Action').glob('*.md'))
if tasks:
    test_passed(f"Tasks in Needs_Action: {len(tasks)} tasks")
else:
    test_warning("Needs_Action tasks", "No tasks found")

# Check Plans folder
plans = list(Path('../AI_Employee_Vault/Plans').glob('*.md'))
if plans:
    test_passed(f"Plans generated: {len(plans)} plans")
else:
    test_warning("Plans", "No plans generated yet")

# Check Pending_Approval has drafts
drafts = list(Path('../AI_Employee_Vault/Pending_Approval').glob('*.md'))
if drafts:
    test_passed(f"Drafts pending approval: {len(drafts)} drafts")
else:
    test_warning("Pending drafts", "No drafts awaiting approval")

# Verify workflow linkage
linkedin_tasks = list(Path('../AI_Employee_Vault/Needs_Action').glob('LINKEDIN_*.md'))
linkedin_drafts = list(Path('../AI_Employee_Vault/Pending_Approval').glob('DRAFT_LINKEDIN_*.md'))

if linkedin_tasks and linkedin_drafts:
    test_passed("LinkedIn workflow: Signal → Draft pipeline working")
elif linkedin_tasks and not linkedin_drafts:
    test_warning("LinkedIn workflow", "Signals exist but no drafts yet")
else:
    test_warning("LinkedIn workflow", "No LinkedIn signals detected yet")

print()

# ============================================================================
# TEST SUMMARY
# ============================================================================
print("=" * 70)
print("🏆 SILVER TIER - TEST SUMMARY")
print("=" * 70)
print()

total_tests = len(results['passed']) + len(results['failed']) + len(results['warnings'])
pass_rate = (len(results['passed']) / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⚠️  Warnings: {len(results['warnings'])}")
print(f"Pass Rate: {pass_rate:.1f}%")
print()

if results['failed']:
    print("FAILED TESTS:")
    for failure in results['failed']:
        print(f"  ❌ {failure}")
    print()

if results['warnings']:
    print("WARNINGS:")
    for warning in results['warnings']:
        print(f"  ⚠️  {warning}")
    print()

# Determine overall status
if len(results['failed']) == 0:
    print("=" * 70)
    print("🎉 SILVER TIER STATUS: COMPLETE")
    print("=" * 70)
    print()
    print("All core components are operational!")
    print("Your AI Employee system is ready for use.")
    print()
    print("Next Steps:")
    print("1. Review the generated Plans/ and Pending_Approval/ folders")
    print("2. Run watchers: gmail_watcher.py, linkedin_watcher.py")
    print("3. Run reasoning loop: reasoning_loop.py")
    print("4. Run drafting agent: linkedin_drafting_agent.py")
    print()
    sys.exit(0)
else:
    print("=" * 70)
    print("⚠️  SILVER TIER STATUS: ISSUES DETECTED")
    print("=" * 70)
    print()
    print("Some components need attention before declaring complete.")
    print("Review the failed tests above and address them.")
    print()
    sys.exit(1)
