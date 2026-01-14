#!/usr/bin/env python3
"""
Gold Tier - Complete Integration Test
Tests all Gold Tier components working together
"""
from pathlib import Path
import sys

print("=" * 70)
print("🏆 GOLD TIER - COMPLETE INTEGRATION TEST")
print("=" * 70)
print()

results = {'passed': [], 'failed': []}

def test_pass(name):
    results['passed'].append(name)
    print(f"✅ {name}")

def test_fail(name, reason):
    results['failed'].append(f"{name}: {reason}")
    print(f"❌ {name}: {reason}")

# Test 1: Agent Skills Framework
print("TEST 1: Agent Skills Framework")
print("-" * 70)
try:
    from skill_registry import SkillRegistry
    registry = SkillRegistry()
    count = registry.discover_skills()
    if count >= 2:
        test_pass(f"Skills discovered: {count} skills")
    else:
        test_fail("Skills discovery", f"Only {count} skills found")
except Exception as e:
    test_fail("Skills framework", str(e))
print()

# Test 2: Gmail MCP Server
print("TEST 2: Gmail MCP Server")
print("-" * 70)
try:
    from gmail_mcp_server import GmailMCPServer
    server = GmailMCPServer()
    tools = server.get_tools_definition()
    if len(tools) > 0:
        test_pass(f"Gmail MCP operational: {len(tools)} tools")
    else:
        test_fail("Gmail MCP", "No tools found")
except Exception as e:
    test_fail("Gmail MCP", str(e))
print()

# Test 3: QuickBooks MCP Server
print("TEST 3: QuickBooks MCP Server")
print("-" * 70)
try:
    from quickbooks_mcp_server import QuickBooksMCPServer
    server = QuickBooksMCPServer(mode='sandbox')
    tools = server.get_tools_definition()
    if len(tools) >= 4:
        test_pass(f"QuickBooks MCP operational: {len(tools)} tools")
    else:
        test_fail("QuickBooks MCP", f"Only {len(tools)} tools found")

    # Test financial data
    balances = server.get_account_balances()
    if balances.get('success'):
        test_pass(f"QuickBooks data access: ${balances['total_assets']:,.2f} assets")
    else:
        test_fail("QuickBooks data", "Failed to get balances")
except Exception as e:
    test_fail("QuickBooks MCP", str(e))
print()

# Test 4: Ralph Wiggum Loop
print("TEST 4: Ralph Wiggum Autonomous Loop")
print("-" * 70)
try:
    from ralph_wiggum_loop import RalphWiggumLoop
    loop = RalphWiggumLoop('../AI_Employee_Vault', check_interval=0)

    # Check MCP servers loaded
    if 'gmail' in loop.mcp_servers:
        test_pass("Gmail MCP integrated with Ralph Wiggum")
    else:
        test_fail("Gmail MCP integration", "Not loaded")

    if 'quickbooks' in loop.mcp_servers:
        test_pass("QuickBooks MCP integrated with Ralph Wiggum")
    else:
        test_fail("QuickBooks MCP integration", "Not loaded")

except Exception as e:
    test_fail("Ralph Wiggum", str(e))
print()

# Test 5: Weekly Audit Generator
print("TEST 5: Weekly Business Audit")
print("-" * 70)
try:
    from weekly_audit import WeeklyAuditGenerator
    generator = WeeklyAuditGenerator('../AI_Employee_Vault')

    # Test data collection
    financial = generator.collect_financial_data()
    if 'summary' in financial:
        test_pass(f"Financial data collection: ${financial['summary'].get('net_income', 0):,.2f} net income")
    else:
        test_fail("Financial data", "Failed to collect")

    tasks = generator.collect_task_completion_metrics()
    test_pass(f"Task metrics: {tasks['plans_executed']} plans executed")

except Exception as e:
    test_fail("Weekly Audit", str(e))
print()

# Test 6: Execution Logs
print("TEST 6: Execution Logs & Audit Trail")
print("-" * 70)
vault = Path('../AI_Employee_Vault')

ralph_log = vault / 'Logs' / 'ralph_wiggum_execution.jsonl'
if ralph_log.exists():
    lines = len(ralph_log.read_text().strip().split('\n'))
    test_pass(f"Ralph Wiggum logs: {lines} entries")
else:
    test_fail("Ralph Wiggum logs", "Not found")

skills_log = vault / 'Logs' / 'skills_execution.jsonl'
if skills_log.exists():
    lines = len(skills_log.read_text().strip().split('\n'))
    test_pass(f"Skills logs: {lines} entries")
else:
    test_fail("Skills logs", "Not found")

reports = list((vault / 'Reports').glob('WEEKLY_AUDIT_*.md'))
if reports:
    test_pass(f"Weekly reports: {len(reports)} generated")
else:
    test_fail("Weekly reports", "None found")
print()

# Test 7: Complete Workflow
print("TEST 7: Complete Workflow Verification")
print("-" * 70)

# Check all folders exist
folders = ['Needs_Action', 'Plans', 'Pending_Approval', 'Approved', 'Done', 'Reports', 'Logs']
for folder in folders:
    folder_path = vault / folder
    if folder_path.exists():
        count = len(list(folder_path.glob('*')))
        test_pass(f"{folder}/ exists: {count} items")
    else:
        test_fail(f"{folder}/", "Does not exist")

print()

# Summary
print("=" * 70)
print("🏆 GOLD TIER TEST SUMMARY")
print("=" * 70)
print()

total = len(results['passed']) + len(results['failed'])
pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0

print(f"Total Tests: {total}")
print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"Pass Rate: {pass_rate:.1f}%")
print()

if results['failed']:
    print("FAILED TESTS:")
    for failure in results['failed']:
        print(f"  ❌ {failure}")
    print()
    sys.exit(1)
else:
    print("=" * 70)
    print("🎉 GOLD TIER: ALL SYSTEMS OPERATIONAL!")
    print("=" * 70)
    print()
    print("✅ Agent Skills Framework: Working")
    print("✅ Gmail MCP Server: Working")
    print("✅ QuickBooks MCP Server: Working")
    print("✅ Ralph Wiggum Loop: Working")
    print("✅ Weekly Audit Generator: Working")
    print("✅ Complete Integration: Working")
    print()
    print("🏆 GOLD TIER COMPLETE - READY FOR SUBMISSION!")
    print()
    sys.exit(0)
