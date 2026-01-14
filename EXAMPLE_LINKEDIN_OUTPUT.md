# Example LinkedIn Watcher Output

This file demonstrates the structured markdown files created by the LinkedIn Watcher.

---

## Example 1: High-Priority Message (Contains Keywords)

**Filename:** `LINKEDIN_MESSAGE_20260113_184500_Alex_Chen.md`

```markdown
---
source: linkedin
type: message
detected_at: 2026-01-13T18:45:00.123456
priority: high
status: pending
---

# LinkedIn Message

## Summary
New unread message from **Alex Chen** on LinkedIn
⚠️ **Contains monitored keywords**

## Details
- **From:** Alex Chen
- **Preview:** Hi! I'm reaching out about a potential AI consulting project. We're looking for someone with automation expertise to help streamline our operations. Would you be available for a brief call this week?
- **LinkedIn URL:** https://www.linkedin.com/messaging/

## Message Preview
```
Hi! I'm reaching out about a potential AI consulting project.
We're looking for someone with automation expertise to help
streamline our operations. Would you be available for a brief
call this week?
```

## Suggested Next Action
1. Open LinkedIn and read the full message
2. Assess if this is a business opportunity, spam, or personal connection
3. If relevant, draft a response for approval
4. If spam/irrelevant, archive or ignore

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic replies have been sent
- Human review and approval required before any response
- LinkedIn messages require manual action

## Keywords Detected
ai, consulting, project, automation

---
*Detected by LinkedIn Watcher: 20260113_184500*
*Human review required before any action*
```

---

## Example 2: Connection Request (High Priority - Keywords in Profile)

**Filename:** `LINKEDIN_CONNECTION_REQUEST_20260113_190000_Maria_Rodriguez.md`

```markdown
---
source: linkedin
type: connection_request
detected_at: 2026-01-13T19:00:00.789012
priority: high
status: pending
---

# LinkedIn Connection Request

## Summary
New connection request from **Maria Rodriguez**
⚠️ **Profile contains monitored keywords**

## Details
- **Name:** Maria Rodriguez
- **Headline/Role:** Senior Product Manager | AI & Automation Solutions | Open to freelance opportunities
- **LinkedIn URL:** https://www.linkedin.com/mynetwork/invitation-manager/

## Profile Information
**Headline:** Senior Product Manager | AI & Automation Solutions | Open to freelance opportunities

## Suggested Next Action
1. Open LinkedIn and view the requester's full profile
2. Check mutual connections and background
3. Assess if this connection aligns with business goals
4. Decide: Accept, Ignore, or Reply with message

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic acceptance or rejection
- Human review required for all connections
- Manual decision required

## Keywords Detected
ai, automation, freelance, opportunities

---
*Detected by LinkedIn Watcher: 20260113_190000*
*Manual review and action required*
```

---

## Example 3: Medium-Priority Message (No Keywords)

**Filename:** `LINKEDIN_MESSAGE_20260113_192000_Tom_Williams.md`

```markdown
---
source: linkedin
type: message
detected_at: 2026-01-13T19:20:00.456789
priority: medium
status: pending
---

# LinkedIn Message

## Summary
New unread message from **Tom Williams** on LinkedIn

## Details
- **From:** Tom Williams
- **Preview:** Hey! Long time no see. How have you been? Would love to catch up sometime.
- **LinkedIn URL:** https://www.linkedin.com/messaging/

## Message Preview
```
Hey! Long time no see. How have you been?
Would love to catch up sometime.
```

## Suggested Next Action
1. Open LinkedIn and read the full message
2. Assess if this is a business opportunity, spam, or personal connection
3. If relevant, draft a response for approval
4. If spam/irrelevant, archive or ignore

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic replies have been sent
- Human review and approval required before any response
- LinkedIn messages require manual action

## Keywords Detected
None

---
*Detected by LinkedIn Watcher: 20260113_192000*
*Human review required before any action*
```

---

## Example 4: Low-Priority Connection Request (No Keywords)

**Filename:** `LINKEDIN_CONNECTION_REQUEST_20260113_193000_David_Lee.md`

```markdown
---
source: linkedin
type: connection_request
detected_at: 2026-01-13T19:30:00.234567
priority: low
status: pending
---

# LinkedIn Connection Request

## Summary
New connection request from **David Lee**

## Details
- **Name:** David Lee
- **Headline/Role:** Software Engineer at TechCorp
- **LinkedIn URL:** https://www.linkedin.com/mynetwork/invitation-manager/

## Profile Information
**Headline:** Software Engineer at TechCorp

## Suggested Next Action
1. Open LinkedIn and view the requester's full profile
2. Check mutual connections and background
3. Assess if this connection aligns with business goals
4. Decide: Accept, Ignore, or Reply with message

## Notes
⚠️ **COMPLIANCE:** This is a READ-ONLY detection
- No automatic acceptance or rejection
- Human review required for all connections
- Manual decision required

## Keywords Detected
None

---
*Detected by LinkedIn Watcher: 20260113_193000*
*Manual review and action required*
```

---

## File Naming Convention

```
LINKEDIN_<TYPE>_<YYYYMMDD_HHMMSS>_<SAFE_NAME>.md

Examples:
- LINKEDIN_MESSAGE_20260113_184500_Alex_Chen.md
- LINKEDIN_CONNECTION_REQUEST_20260113_190000_Maria_Rodriguez.md
- LINKEDIN_KEYWORD_SIGNAL_20260113_195000_Business_Opportunity.md
```

---

## Priority Levels

- **HIGH:** Contains monitored keywords (hire, project, consulting, ai, automation, etc.)
- **MEDIUM:** Messages without keywords
- **LOW:** Connection requests without keywords

---

## Integration with Reasoning Loop

These files are automatically picked up by the Reasoning Loop, which creates Plan.md files with:
- Analysis of the opportunity
- Suggested response strategy
- Risk assessment
- Next steps for human approval

---

*Example outputs for LinkedIn Watcher - Silver Tier*
*All files are Reasoning Loop compatible*
