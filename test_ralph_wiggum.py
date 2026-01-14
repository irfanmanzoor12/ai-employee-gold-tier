#!/usr/bin/env python3
"""
Test script for Ralph Wiggum Loop
Runs one iteration and shows results
"""
from ralph_wiggum_loop import RalphWiggumLoop

print("=" * 70)
print("🤖 Testing Ralph Wiggum Autonomous Loop")
print("=" * 70)
print()

# Create loop
print("Initializing Ralph Wiggum...")
loop = RalphWiggumLoop('../AI_Employee_Vault', check_interval=0)

print()
print("Running one iteration...")
print()

# Run once
loop.run_once()

print()
print("=" * 70)
print("✅ Test Complete!")
print("=" * 70)
print()
print("Check results:")
print("1. Email inbox: Should have received test email")
print("2. Execution log:")
print("   cat ../AI_Employee_Vault/Logs/ralph_wiggum_execution.jsonl")
print("3. Done folder:")
print("   ls ../AI_Employee_Vault/Done/PLAN_TEST_RALPH_WIGGUM.md")
print()
