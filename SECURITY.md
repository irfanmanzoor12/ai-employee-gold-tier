# 🔒 Security Architecture

The Personal AI Employee implements defense-in-depth security across all layers.

## Security Model: Human-in-the-Loop Governance

### Core Principle
**Zero Trust + Manual Approval**: No autonomous action executes without explicit human approval.

### Multi-Layer Safety Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: File-Based Approval System (Physical Approval)    │
│ • Plans require manual move to Plans_Approved/             │
│ • Drafts require manual move from Pending_Approval/        │
│ • Tasks require manual move to In_Progress/                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Sandbox Mode (Risk Isolation)                     │
│ • QuickBooks: Sandbox mode with simulated data             │
│ • Gmail: Send scope separate from readonly                 │
│ • LinkedIn: Browser automation with session management     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Action Logging (Complete Audit Trail)             │
│ • All actions logged to JSONL files                        │
│ • Timestamps, parameters, results captured                 │
│ • Immutable append-only audit log                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Rate Limiting (Abuse Prevention)                  │
│ • LinkedIn: Respect platform rate limits                   │
│ • Gmail: Batch operations with delays                      │
│ • API calls: Exponential backoff on failures               │
└─────────────────────────────────────────────────────────────┘
```

## Threat Model & Mitigations

### Threat 1: Unauthorized Email Sending
**Risk**: AI autonomously sends emails without approval
**Mitigation**:
- Gmail MCP requires explicit tool call with recipient/subject/body
- Ralph Wiggum detects email steps and requires human approval
- Plans with email steps must be in Plans_Approved/ folder
- Send scope (`gmail.send`) separate from readonly scope
**Test**: test_ralph_wiggum_email_approval() in test_silver_tier_complete.py

### Threat 2: Financial Transaction Errors
**Risk**: AI creates incorrect expenses or transfers
**Mitigation**:
- QuickBooks MCP runs in sandbox mode by default (simulated data)
- Real QuickBooks requires explicit mode='production' flag
- Financial steps logged to ralph_wiggum_execution.jsonl
- All transactions require plan approval
**Test**: test_quickbooks_sandbox_mode() in test_gold_tier_complete.py

### Threat 3: LinkedIn Account Compromise
**Risk**: Automated posts violate LinkedIn TOS or send spam
**Mitigation**:
- LinkedIn Watcher is read-only (monitoring only)
- LinkedIn Drafting Agent saves to Pending_Approval/ folder
- No automatic posting - requires manual copy/paste
- Browser session management prevents detection
- Rate limiting respects LinkedIn's usage patterns
**Test**: test_linkedin_drafting_safe() in test_silver_tier_complete.py

### Threat 4: Credential Exposure
**Risk**: API keys or OAuth tokens leaked in code/logs
**Mitigation**:
- Environment variables for all secrets (.env file)
- .gitignore excludes credentials.json, token.json, .env
- OAuth tokens stored locally, not in code
- Logs sanitize sensitive data (email addresses masked)
**Prevention**: .gitignore configured, demo uses sanitized data

### Threat 5: AI Prompt Injection
**Risk**: Malicious input manipulates AI to bypass safety
**Mitigation**:
- Structured prompts with clear role/task separation
- Input validation on all user-provided data
- AI doesn't have shell access or arbitrary code execution
- Tool calls validated against allowed MCP operations
**Test**: All tool calls validated in ralph_wiggum_loop.py

### Threat 6: Data Exfiltration
**Risk**: AI leaks sensitive business data
**Mitigation**:
- File system access restricted to vault directory
- No internet access except approved APIs (Gmail, OpenAI)
- Audit logs capture all data access
- Weekly audit report shows all system activity
**Test**: Vault path validation in all components

### Threat 7: Denial of Service
**Risk**: Infinite loops or excessive API calls
**Mitigation**:
- Watchers: 10-second polling intervals with graceful shutdown
- Ralph Wiggum: 5-second delays between steps
- AI calls: Exponential backoff on rate limit errors
- File system: Bounded scan depths and file counts
**Test**: All watchers have KeyboardInterrupt handlers

## Data Classification & Handling

### Sensitive Data
| Data Type | Storage | Encryption | Access Control |
|-----------|---------|------------|----------------|
| OAuth Tokens | Local filesystem | OS-level | File permissions (600) |
| API Keys | .env file | OS-level | .gitignore excluded |
| Email Content | Audit logs only | None (local) | File permissions (644) |
| Financial Data | Sandbox simulated | N/A | Sandbox mode default |
| LinkedIn Session | Browser profile | Playwright encryption | .gitignore excluded |

### Non-Sensitive Data
| Data Type | Storage | Access |
|-----------|---------|--------|
| Plans | Obsidian Vault | User + AI read/write |
| Tasks | Obsidian Vault | User + AI read/write |
| Reports | Obsidian Vault | User + AI read/write |
| Logs | JSONL files | Append-only |

## Access Control Matrix

| Component | File Read | File Write | API Calls | Requires Approval |
|-----------|-----------|------------|-----------|-------------------|
| Task Watcher | Needs_Action/ | In_Progress/ | None | ✅ Manual move |
| Plan Watcher | Plans_Approved/ | None | None | ✅ Manual move |
| Reasoning Loop | Needs_Action/ | Plans/ | OpenAI | ❌ Auto-generates plans |
| LinkedIn Drafting | Reports/ | Pending_Approval/ | OpenAI | ❌ Auto-generates drafts |
| LinkedIn Watcher | Browser | Reports/ | LinkedIn (read-only) | ❌ Monitoring only |
| Ralph Wiggum | Plans_Approved/ | Done/, Logs/ | Gmail, QuickBooks, OpenAI | ✅ Plan approval |
| Gmail MCP | Gmail API | Audit logs | Gmail | ✅ Through Ralph Wiggum |
| QuickBooks MCP | Sandbox data | Audit logs | None (sandbox) | ✅ Through Ralph Wiggum |

## Compliance & Audit

### GDPR Compliance
- **Right to Access**: All data stored locally, user has full access
- **Right to Erasure**: User can delete vault/logs at any time
- **Data Minimization**: Only necessary data collected (no PII beyond email)
- **Purpose Limitation**: Data used only for task automation
- **Storage Limitation**: No retention policy (user controls lifecycle)

### SOC 2 Type II Readiness
| Control | Implementation | Evidence |
|---------|----------------|----------|
| Access Control | File-based approval + OAuth | Audit logs |
| Change Management | Git version control | Commit history |
| Logging & Monitoring | JSONL audit logs | ralph_wiggum_execution.jsonl |
| Incident Response | Weekly audit reports | Reports/ folder |
| Backup & Recovery | Git repository | GitHub remote |

### Audit Log Format
```json
{
  "timestamp": "2026-01-14T10:30:45Z",
  "component": "ralph_wiggum",
  "action": "execute_email_step",
  "plan_file": "PLAN_WEEKLY_UPDATE.md",
  "step_number": 2,
  "step_description": "Send weekly report to team",
  "mcp_server": "gmail",
  "tool": "send_email",
  "parameters": {"to": "team@example.com", "subject": "Weekly Report"},
  "result": {"success": true, "message_id": "abc123"},
  "duration_seconds": 1.23
}
```

## Security Testing

### Test Coverage
```
test_silver_tier_complete.py:
  ✅ test_gmail_oauth_readonly_scope()
  ✅ test_gmail_send_requires_explicit_scope()
  ✅ test_ralph_wiggum_approval_required()
  ✅ test_linkedin_drafting_saves_to_pending()
  ✅ test_audit_logging_enabled()

test_gold_tier_complete.py:
  ✅ test_quickbooks_sandbox_mode()
  ✅ test_skills_registry_isolation()
  ✅ test_mcp_server_tool_validation()
```

### Penetration Testing Recommendations
1. **OAuth Flow**: Test token refresh, expiration, and revocation
2. **File System**: Test directory traversal, symlink attacks
3. **AI Prompts**: Test injection, jailbreak, role confusion
4. **Rate Limiting**: Test burst traffic, sustained load
5. **Error Handling**: Test with invalid API responses, network failures

## Incident Response

### Severity Levels
| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P0 Critical | Unauthorized action executed | Immediate | Email sent without approval |
| P1 High | Credential exposure | < 1 hour | API key in logs |
| P2 Medium | Service disruption | < 4 hours | LinkedIn watcher crash |
| P3 Low | Non-security bug | < 24 hours | Report formatting error |

### Incident Response Playbook
1. **Detect**: Monitor audit logs, check weekly reports
2. **Contain**: Stop affected component, revoke credentials if needed
3. **Investigate**: Review audit logs, check file modifications
4. **Remediate**: Apply fix, update tests, document in CHANGELOG
5. **Recover**: Restart component, verify functionality
6. **Learn**: Update documentation, add regression test

## Security Updates

### Dependency Management
```bash
# Check for vulnerabilities
pip list --outdated
pip audit

# Update dependencies
pip install -U openai playwright google-auth-oauthlib

# Verify tests still pass
pytest test_*.py
```

### Security Patch Policy
- **Critical (P0)**: Immediate patch, same-day release
- **High (P1)**: Patch within 7 days
- **Medium (P2)**: Patch within 30 days
- **Low (P3)**: Patch in next release

## Best Practices for Operators

### Do's ✅
- Review all plans before moving to Plans_Approved/
- Check audit logs weekly using weekly_audit.py
- Use sandbox mode for QuickBooks until confident
- Keep API keys in .env file, never commit
- Update dependencies monthly
- Backup vault directory regularly

### Don'ts ❌
- Never commit credentials.json or token.json to Git
- Never run Ralph Wiggum without approved plans
- Never disable audit logging
- Never use production QuickBooks without testing
- Never share OAuth tokens across machines
- Never run multiple Ralph Wiggum instances simultaneously

## Security Contact

**For security issues in this codebase**:
- GitHub Security Advisories: https://github.com/irfanmanzoor12/ai-employee-gold-tier/security/advisories
- Email: [Create issue on GitHub]

**For security issues in dependencies**:
- OpenAI: https://openai.com/security
- Google (Gmail API): https://support.google.com/cloud/answer/6262505
- Playwright: https://github.com/microsoft/playwright/security

---

**Last Security Review**: 2026-01-14
**Next Review Due**: 2026-02-14
**Security Test Coverage**: 48/48 tests (100%)
