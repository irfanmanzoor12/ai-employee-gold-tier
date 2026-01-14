#!/usr/bin/env python3
"""Quick test script for reasoning loop"""
from reasoning_loop import ReasoningLoop

print("🧠 Testing Reasoning Loop...")
print("="*70)

loop = ReasoningLoop('../AI_Employee_Vault')
loop.process_tasks()

print()
print("="*70)
print("✅ Reasoning loop executed successfully!")
print("="*70)
print()
print("Check results:")
print("ls ../AI_Employee_Vault/Plans/")
