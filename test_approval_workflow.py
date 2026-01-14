"""
Test the complete HITL approval workflow
"""
from approval_system import ApprovalSystem
from pathlib import Path

# Initialize
approval = ApprovalSystem('../AI_Employee_Vault')

print("🔐 Checking Approval Requests...")
print("=" * 60)
print()

# Check status
status = approval.check_approvals()

print("📊 Current Status:")
print(f"   Pending review: {len(status['pending'])} requests")
print(f"   Approved: {len(status['approved'])} requests")
print(f"   Rejected: {len(status['rejected'])} requests")
print(f"   Expired: {len(status['expired'])} requests")
print()

# Process approved
if status['approved']:
    print("✅ Processing Approved Actions:")
    print()

    for approval_file in status['approved']:
        print(f"   📄 {approval_file.name}")

        # Process the approval
        action = approval.process_approved(approval_file)

        print(f"      Action: {action['action_type']}")
        print(f"      Details: {action['details']}")
        print(f"      Status: ✅ Ready to execute")
        print(f"      Approved at: {action['approved_at']}")
        print()

        # In real implementation, you would execute the action here
        # For now, just demonstrate the workflow
        print(f"      [Demo] Would execute: {action['action_type']}")
        print(f"      [Demo] With details: {action['details']}")
        print()

        # Archive the approval file
        approval_file.unlink()  # Delete from Approved/ (already archived)
        print(f"      📁 Archived to: Logs/approved/{approval_file.name}")
        print()

print("=" * 60)
print("✅ Approval workflow test complete!")
print()
print("📋 Summary:")
print(f"   - Processed {len(status['approved'])} approved actions")
print(f"   - {len(status['pending'])} requests still pending")
print(f"   - Check Logs/approval_requests.log for audit trail")
