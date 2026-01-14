#!/usr/bin/env python3
"""
Quick test script for LinkedIn Drafting Agent
Creates a test signal and generates a draft
"""
from linkedin_drafting_agent import LinkedInDraftingAgent
from pathlib import Path

print("=" * 70)
print("Testing LinkedIn Drafting Agent")
print("=" * 70)
print()

# Create test signal if needed
test_signal = Path('../AI_Employee_Vault/Needs_Action/LINKEDIN_TEST_FOR_DRAFTING.md')

if not test_signal.exists():
    print("Creating test LinkedIn signal...")
    test_signal.write_text("""---
source: linkedin
type: message
detected_at: 2026-01-13T19:00:00
priority: high
status: pending
---

# LinkedIn Message

## Summary
New message from potential client interested in AI consulting

## Details
- **From:** Test Client
- **Preview:** "Hi, I've been following your work with AI automation. We're a mid-size company looking to streamline our operations. Would love to discuss how AI could help us reduce manual work and improve efficiency. Are you available for a call?"
- **LinkedIn URL:** https://www.linkedin.com/messaging/

## Keywords Detected
ai, automation, consulting

---
*Test signal for drafting agent*
""")
    print(f"✅ Created: {test_signal.name}")
else:
    print(f"✅ Test signal exists: {test_signal.name}")

print()
print("Running drafting agent...")
print()

try:
    # Initialize agent
    agent = LinkedInDraftingAgent('../AI_Employee_Vault')

    # Process signals
    agent.process_signals()

    print()
    print("=" * 70)
    print("✅ Drafting Agent Test Complete!")
    print("=" * 70)
    print()
    print("Check results:")
    print("ls ../AI_Employee_Vault/Pending_Approval/DRAFT_LINKEDIN_*.md")
    print()
    print("View draft:")
    print("cat ../AI_Employee_Vault/Pending_Approval/DRAFT_LINKEDIN_TEST_FOR_DRAFTING.md")

except Exception as e:
    print()
    print("=" * 70)
    print("❌ Test Failed")
    print("=" * 70)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
