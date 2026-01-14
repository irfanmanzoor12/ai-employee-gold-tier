"""
Human-in-the-Loop (HITL) Approval System
Manages approval requests for sensitive actions
"""
from pathlib import Path
from datetime import datetime, timedelta
import json
import shutil


class ApprovalSystem:
    """Manages approval workflow for sensitive actions"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.rejected.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

    def create_approval_request(
        self,
        action_type: str,
        details: dict,
        reason: str,
        priority: str = 'medium',
        expires_hours: int = 24
    ) -> Path:
        """
        Create an approval request file

        Args:
            action_type: Type of action (email, payment, post, delete, etc.)
            details: Dictionary with action-specific details
            reason: Why this action needs approval
            priority: low, medium, high, urgent
            expires_hours: Hours until request expires

        Returns:
            Path to created approval file
        """
        timestamp = datetime.now()
        expires = timestamp + timedelta(hours=expires_hours)

        # Generate filename
        safe_type = action_type.replace(' ', '_').lower()
        filename = f'APPROVAL_{safe_type}_{timestamp.strftime("%Y%m%d_%H%M%S")}.md'
        filepath = self.pending_approval / filename

        # Build approval request content
        content = f"""---
type: approval_request
action: {action_type}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
priority: {priority}
status: pending
---

# Approval Required: {action_type}

## ⚠️ Action Details

{self._format_details(details)}

## 📋 Reason
{reason}

## ⏰ Priority: {priority.upper()}
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Expires:** {expires.strftime('%Y-%m-%d %H:%M:%S')} ({expires_hours} hours)

---

## 🔐 How to Approve or Reject

### To APPROVE this action:
1. Move this file to: `Approved/` folder
2. The AI will execute the action automatically

### To REJECT this action:
1. Move this file to: `Rejected/` folder
2. The AI will cancel the action

### To REQUEST CHANGES:
1. Edit the details above
2. Keep file in `Pending_Approval/`
3. Add a note in the "Modifications" section below

---

## 📝 Modifications (Optional)
<!-- Add any changes you want to the action here -->

---

## 📊 Audit Trail
- **Requested by:** AI Employee
- **Request ID:** {filename.replace('.md', '')}
- **Vault:** {self.vault_path}

---

*Approval request created automatically*
*Do NOT delete this file - move it to Approved/ or Rejected/*
"""

        # Write file
        filepath.write_text(content)

        # Log the request
        self._log_request(filename, action_type, priority)

        return filepath

    def check_approvals(self) -> dict:
        """
        Check for approved or rejected requests

        Returns:
            dict with 'approved' and 'rejected' lists of approval files
        """
        result = {
            'approved': [],
            'rejected': [],
            'pending': [],
            'expired': []
        }

        # Check approved
        for file in self.approved.glob('APPROVAL_*.md'):
            result['approved'].append(file)

        # Check rejected
        for file in self.rejected.glob('APPROVAL_*.md'):
            result['rejected'].append(file)

        # Check pending (and find expired)
        for file in self.pending_approval.glob('APPROVAL_*.md'):
            if self._is_expired(file):
                result['expired'].append(file)
            else:
                result['pending'].append(file)

        return result

    def process_approved(self, approval_file: Path) -> dict:
        """
        Process an approved request

        Returns:
            dict with action details to execute
        """
        content = approval_file.read_text()

        # Extract metadata
        action_type = self._extract_field(content, 'action')
        created = self._extract_field(content, 'created')

        # Parse action details from markdown
        details = self._parse_details(content)

        # Archive the approval
        archive_path = self.logs / 'approved' / approval_file.name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(approval_file, archive_path)

        # Log execution
        self._log_execution(approval_file.name, 'approved', action_type)

        return {
            'action_type': action_type,
            'details': details,
            'approved_at': datetime.now().isoformat(),
            'original_request': created,
            'approval_file': str(approval_file)
        }

    def process_rejected(self, approval_file: Path):
        """Process a rejected request"""
        action_type = self._extract_field(approval_file.read_text(), 'action')

        # Archive the rejection
        archive_path = self.logs / 'rejected' / approval_file.name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(approval_file, archive_path)

        # Log rejection
        self._log_execution(approval_file.name, 'rejected', action_type)

    def cleanup_expired(self):
        """Move expired requests to rejected"""
        expired = self.check_approvals()['expired']

        for file in expired:
            dest = self.rejected / file.name
            shutil.move(str(file), str(dest))
            self._log_execution(file.name, 'expired', 'unknown')

        return len(expired)

    # Helper methods

    def _format_details(self, details: dict) -> str:
        """Format details dictionary as markdown"""
        lines = []
        for key, value in details.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- **{formatted_key}:** {value}")
        return '\n'.join(lines)

    def _extract_field(self, content: str, field: str) -> str:
        """Extract field from YAML frontmatter"""
        for line in content.split('\n'):
            if line.startswith(f'{field}:'):
                return line.split(':', 1)[1].strip()
        return ''

    def _parse_details(self, content: str) -> dict:
        """Parse action details from markdown content"""
        details = {}
        in_details = False

        for line in content.split('\n'):
            if '## ⚠️ Action Details' in line:
                in_details = True
                continue
            if in_details:
                if line.startswith('##'):
                    break
                if line.startswith('- **'):
                    # Parse "- **Key:** Value"
                    parts = line.replace('- **', '').split(':**', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower().replace(' ', '_')
                        value = parts[1].strip()
                        details[key] = value

        return details

    def _is_expired(self, file: Path) -> bool:
        """Check if approval request has expired"""
        content = file.read_text()
        expires = self._extract_field(content, 'expires')

        if expires:
            try:
                expires_dt = datetime.fromisoformat(expires)
                return datetime.now() > expires_dt
            except:
                pass

        return False

    def _log_request(self, filename: str, action_type: str, priority: str):
        """Log approval request creation"""
        log_file = self.logs / 'approval_requests.log'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'request_created',
            'filename': filename,
            'action_type': action_type,
            'priority': priority
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_execution(self, filename: str, action: str, action_type: str):
        """Log approval execution"""
        log_file = self.logs / 'approval_requests.log'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': f'request_{action}',
            'filename': filename,
            'action_type': action_type
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# Example usage
if __name__ == '__main__':
    # Initialize system
    approval = ApprovalSystem('../AI_Employee_Vault')

    # Example: Create an email approval request
    approval_file = approval.create_approval_request(
        action_type='send_email',
        details={
            'to': 'client@example.com',
            'subject': 'Project Update',
            'body': 'Hello, here is the weekly project update...',
            'attachments': 'report.pdf'
        },
        reason='Automated weekly report email to client',
        priority='medium'
    )

    print(f"✅ Approval request created: {approval_file.name}")
    print(f"📁 Location: {approval_file}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review the approval file")
    print(f"   2. Move to Approved/ to execute")
    print(f"   3. Move to Rejected/ to cancel")
