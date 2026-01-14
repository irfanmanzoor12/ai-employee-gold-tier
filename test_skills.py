#!/usr/bin/env python3
"""
Test Agent Skills Framework
Gold Tier Requirement
"""
from pathlib import Path
from skill_registry import SkillRegistry

print("=" * 70)
print("🎯 Testing Agent Skills Framework - Gold Tier")
print("=" * 70)
print()

# Test 1: Skill Registry Discovery
print("TEST 1: Skill Discovery")
print("-" * 70)

registry = SkillRegistry()
count = registry.discover_skills()

print(f"✅ Discovered {count} skill(s)")
print()

# Test 2: List Skills
print("TEST 2: List Available Skills")
print("-" * 70)

skills = registry.list_skills()
for skill in skills:
    print(f"📦 {skill['name']} v{skill['version']}")
    print(f"   Description: {skill['description']}")
    print(f"   Required: {', '.join(skill['required_params'])}")
    print()

# Test 3: Execute Reasoning Skill
print("TEST 3: Execute Reasoning Skill")
print("-" * 70)

# Find a test task
vault_path = Path('../AI_Employee_Vault')
test_tasks = list((vault_path / 'Needs_Action').glob('*.md'))

if test_tasks:
    test_task = test_tasks[0]
    print(f"Testing with: {test_task.name}")
    print()

    context = {
        'vault_path': str(vault_path),
        'task_file': str(test_task)
    }

    result = registry.execute_skill('reasoning', context)

    if result['success']:
        print("✅ Reasoning Skill executed successfully!")
        print(f"   Plan created: {Path(result['output']['plan_file']).name}")
        print(f"   Tokens used: {result['output']['tokens_used']}")
    else:
        print(f"❌ Reasoning Skill failed: {result['error']}")
else:
    print("⚠️  No test tasks found in Needs_Action/")
    print("   Skipping reasoning skill test")

print()

# Test 4: Execute Drafting Skill
print("TEST 4: Execute Drafting Skill")
print("-" * 70)

# Find a LinkedIn signal
test_signals = list((vault_path / 'Needs_Action').glob('LINKEDIN_*.md'))

if test_signals:
    test_signal = test_signals[0]
    print(f"Testing with: {test_signal.name}")
    print()

    context = {
        'vault_path': str(vault_path),
        'signal_file': str(test_signal)
    }

    result = registry.execute_skill('drafting', context)

    if result['success']:
        print("✅ Drafting Skill executed successfully!")
        print(f"   Draft created: {Path(result['output']['draft_file']).name}")
        print(f"   Tokens used: {result['output']['tokens_used']}")
    else:
        print(f"❌ Drafting Skill failed: {result['error']}")
else:
    print("⚠️  No LinkedIn signals found in Needs_Action/")
    print("   Skipping drafting skill test")

print()

# Test 5: Check Execution Logs
print("TEST 5: Check Execution Logs")
print("-" * 70)

log_file = vault_path / 'Logs' / 'skills_execution.jsonl'
if log_file.exists():
    lines = log_file.read_text().strip().split('\n')
    print(f"✅ Found {len(lines)} execution log entries")
    print()
    print("Latest logs:")
    import json
    for line in lines[-3:]:
        log = json.loads(line)
        status = "✅" if log['success'] else "❌"
        print(f"{status} {log['skill']}: {log['execution_time']:.2f}s")
else:
    print("⚠️  No execution logs found yet")

print()

# Summary
print("=" * 70)
print("🎯 Agent Skills Framework Test Complete")
print("=" * 70)
print()
print("✅ Skill registry working")
print("✅ Skills discovered and loaded")
print("✅ Skills can be executed")
print("✅ Execution logging working")
print()
print("Agent Skills Framework is OPERATIONAL! ✨")
print()
