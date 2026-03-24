> **Note:** This is a sample report generated from fake data in `examples/fake_users.json`.
> It demonstrates the real output format of okta-access-reviewer. No real user data is included.

# Okta Access Review Report

**Generated:** March 24, 2026 at 04:09 AM
**Tool:** okta-access-reviewer
**Model:** claude-opus-4-6

---



# Okta Access Review Report

**Review Date:** 2026-03-22 (inferred from most recent login activity)
**Organization:** AcmeCorp
**Analyst:** Senior IAM Security Analyst
**Scope:** All active user accounts (10 users reviewed)

---

## 1. Inactive Accounts (No Login in >90 Days)

The 90-day inactivity threshold is calculated as any `last_login` before approximately **2025-12-22**.

### 🔴 tom.nguyen@acmecorp.com (00u9i)
| Field | Value |
|---|---|
| **Last Login** | 2025-05-10 (~10 months ago) |
| **Status** | ACTIVE |
| **Account Age** | ~6.4 years (created 2019-11-01) |
| **Admin Roles** | `SUPER_ADMIN`, `APP_ADMIN` |
| **Apps (13)** | Slack, Google Workspace, Jira, Confluence, GitHub, AWS Console, Workday, ServiceNow, Okta Admin, Zoom, DocuSign, Tableau, PagerDuty |
| **Groups (8)** | Everyone, Engineering, Finance-ReadOnly, HR-ReadOnly, DevOps, Security-Team, Executives, Contractors |

**Why flagged:** This is the **highest-risk account in the organization**. Tom has not logged in for approximately 10 months yet retains `SUPER_ADMIN` and `APP_ADMIN` privileges, 13 application assignments spanning nearly every business function, and membership in 8 groups including sensitive groups like `Executives`, `Finance-ReadOnly`, `HR-ReadOnly`, and `Contractors`. The combination of inactivity and maximum privilege is a critical security exposure. If this account were compromised, an attacker would have unrestricted access to the entire Okta tenant and all integrated applications.

**Recommended Actions:**
1. **Immediately suspend the account** and revoke all active sessions/tokens.
2. Contact Tom's manager to determine employment status — the `Contractors` group membership combined with long tenure is unusual and may indicate a role change or separation that was never processed.
3. If still employed, **remove `SUPER_ADMIN` and `APP_ADMIN` roles immediately** pending a justification review.
4. Conduct a retroactive audit of any Okta admin actions performed by this account in the system log.
5. If the account is to be reactivated, re-provision with least-privilege access only after manager and security sign-off.

---

### 🔴 derek.walsh@acmecorp.com (00u4d)
| Field | Value |
|---|---|
| **Last Login** | 2025-06-30 (~9 months ago) |
| **Status** | ACTIVE |
| **Account Age** | ~5.5 years (created 2020-09-01) |
| **Admin Roles** | `SUPER_ADMIN` |
| **Apps (10)** | Slack, Google Workspace, Jira, GitHub, AWS Console, Datadog, PagerDuty, Confluence, Okta Admin, Zoom |
| **Groups (5)** | Everyone, Engineering, DevOps, Security-Team, Executives |

**Why flagged:** Derek holds `SUPER_ADMIN` — the highest privilege level in Okta — and has not logged in for approximately 9 months. An inactive `SUPER_ADMIN` account is a critical risk vector. His access to AWS Console, Okta Admin, and membership in the Security-Team and Executives groups amplifies the blast radius of any compromise.

**Recommended Actions:**
1. **Immediately suspend the account** and revoke all active sessions/tokens.
2. Contact Derek's manager to verify employment status and current role.
3. If still employed and active elsewhere, **remove `SUPER_ADMIN`** and reassign a scoped admin role only if a legitimate, documented need exists.
4. Audit Okta system logs for any activity associated with this account during the inactive period.

---

### 🟡 marcus.johnson@acmecorp.com (00u2b)
| Field | Value |
|---|---|
| **Last Login** | 2025-11-01 (~4.5 months ago) |
| **Status** | ACTIVE |
| **Admin Roles** | `ORG_ADMIN` |

**Why flagged:** Marcus last logged in approximately 4.5 months ago, exceeding the 90-day threshold. He holds `ORG_ADMIN` privileges (discussed further in Sections 2 and 3).

**Recommended Actions:**
1. Contact Marcus's manager to confirm active employment and need for continued access.
2. If still active, require a login/re-authentication within a defined grace period (e.g., 14 days) or disable the account.
3. See Sections 2 and 3 for additional privilege concerns.

---

### 🟡 priya.patel@acmecorp.com (00u3c)
| Field | Value |
|---|---|
| **Last Login** | 2025-08-14 (~7 months ago) |
| **Status** | ACTIVE |
| **Account Age** | ~5 years (created 2021-03-22) |
| **Admin Roles** | None |
| **Apps (4)** | Slack, Google Workspace, Workday, Jira |
| **Groups (3)** | Everyone, HR, Workday-Users |

**Why flagged:** Priya has not logged in for approximately 7 months. While her access footprint is appropriately scoped for an HR role, the extended inactivity raises concerns about whether she has left the organization or is on extended leave.

**Recommended Actions:**
1. Contact HR/Priya's manager to verify employment status.
2. If on extended leave, suspend the account for the duration and reactivate upon return.
3. If separated from the organization, deactivate and deprovision immediately.

---

### 🟡 temp.contractor_bobsmith@acmecorp.com (00u5e)
| Field | Value |
|---|---|
| **Last Login** | 2025-09-03 (~6.5 months ago) |
| **Status** | ACTIVE |
| **Account Age** | ~1.2 years (created 2025-01-15) |
| **Admin Roles** | None |
| **Apps (8)** | Slack, Google Workspace, GitHub, AWS Console, Jira, Confluence, Datadog, PagerDuty |
| **Groups (4)** | Everyone, Engineering, DevOps, Contractors |

**Why flagged:** This is a **contractor account** (indicated by both the `temp.contractor_` login prefix and `Contractors` group membership) that has been inactive for approximately 6.5 months. Contractor accounts inherently carry higher risk due to reduced organizational oversight and should have shorter inactivity thresholds. This contractor retains access to critical infrastructure tools including **AWS Console**, **GitHub**, **Datadog**, and **PagerDuty** — all of which could cause significant damage if compromised.

**Recommended Actions:**
1. **Immediately disable the account.** Contractor accounts inactive for >90 days should be suspended by default per security best practice.
2. Verify with the contracting manager whether the engagement is still active.
3. If the contract has ended, fully deprovision and deactivate.
4. If still under contract, reactivate only after re-validating that each app assignment is currently needed. AWS Console and PagerDuty access for an inactive contractor is especially concerning.
5. **Establish a contractor access policy** with automatic expiration dates and shorter inactivity thresholds (e.g., 30 days).

---

## 2. Over-Provisioned Accounts

To establish a baseline, below is the distribution of app assignments and group memberships:

| User | Apps | Groups | Admin Roles |
|---|---|---|---|
| sarah.chen | 4 | 3 | — |
| **marcus.johnson** | **15** | **8** | ORG_ADMIN |
| priya.patel | 4 | 3 | — |
| derek.walsh | 10 | 5 | SUPER_ADMIN |
| temp.contractor_bobsmith | 8 | 4 | — |
| linda.torres | 5 | 3 | — |
| james.okafor | 6 | 3 | APP_ADMIN |
| rachel.kim | 4 | 3 | — |
| **tom.nguyen** | **13** | **8** | SUPER_ADMIN, APP_ADMIN |
| emily.brooks | 3 | 2 | — |

**Median apps:** ~5.5 | **Median groups:** ~3

---

### 🔴 marcus.johnson@acmecorp.com (00u2b) — 15 Apps, 8 Groups
**Why flagged:** Marcus has **the most app assignments of any user** (15 apps — nearly 3x the median) and **the most group memberships tied with Tom** (8 groups). His access spans nearly every functional area of the business:

- **Engineering/DevOps:** Jira, Confluence, GitHub, AWS Console, Datadog, PagerDuty
- **Finance:** Finance-ReadOnly group
- **HR:** HR-ReadOnly group, Workday
- **Sales:** Salesforce, Salesforce-Admins group
- **Executive:** Executives group
- **Security:** Security-Team group
- **IT Admin:** Okta Admin, ServiceNow, `ORG_ADMIN` role

This access pattern suggests significant **privilege accumulation over time** (account created 2022-06-15). It appears that access was added as Marcus moved across roles or took on projects but was never revoked. No single role in an organization should require Salesforce Admin access AND AWS Console AND Workday AND Finance/HR read-only access simultaneously.

**Recommended Actions:**
1. **Conduct a manager-validated access review.** Present Marcus's full access list to his current manager and ask them to justify each assignment.
2. Remove all app and group assignments that are not directly required for his **current** job function.
3. Specifically scrutinize:
   - `Salesforce-Admins` — Is he actively administering Salesforce, or is this legacy?
   - `Finance-ReadOnly` and `HR-ReadOnly` — These provide access to sensitive compensation and personnel data.
   - `ORG_ADMIN` — See Section 3.
4. Implement a periodic access recertification process (quarterly) to prevent this pattern from recurring.

---

### 🔴 tom.nguyen@acmecorp.com (00u9i) — 13 Apps, 8 Groups
**Why flagged:** (Also flagged in Sections 1 and 3.) Tom's access is nearly as broad as Marcus's, with 13 apps and 8 groups spanning Engineering, Finance, HR, DevOps, Security, and Executives. He is also in the `Contractors` group despite having an account created in 2019, suggesting a possible role/classification error. The combination of `SUPER_ADMIN` + `APP_ADMIN` + cross-functional access + long inactivity makes this the single most dangerous account in the tenant.

**Recommended Actions:** See Section 1. All access should be revoked immediately pending a full review.

---

### 🟡 temp.contractor_bobsmith@acmecorp.com (00u5e) — 8 Apps, 4 Groups
**Why flagged:** A temporary contractor has access to 8 applications, which is above the median and notably broad for a non-employee. Contractors should be provisioned with the **minimum access necessary** for their specific deliverables. Access to **AWS Console** and **PagerDuty** in particular suggests production-level infrastructure access, which should require elevated scrutiny and explicit approval for contractors.

**Recommended Actions:** See Section 1. Disable and re-validate all assignments.

---

## 3. Admin Privilege Concerns

Four users in the organization hold Okta admin roles:

| User | Admin Role(s) | Status | Last Login | Concern Level |
|---|---|---|---|---|
| derek.walsh | `SUPER_ADMIN` | ACTIVE | 2025-06-30 (inactive) | 🔴 **Critical** |
| tom.nguyen | `SUPER_ADMIN`, `APP_ADMIN` | ACTIVE | 2025-05-10 (inactive) | 🔴 **Critical** |
| marcus.johnson | `ORG_ADMIN` | ACTIVE | 2025-11-01 (inactive) | 🔴 **High** |
| james.okafor | `APP_ADMIN` | ACTIVE | Never | 🔴 **High** |

---

### 🔴 tom.nguyen@acmecorp.com — `SUPER_ADMIN` + `APP_ADMIN`
**Why flagged:** Holding **two admin roles simultaneously** violates the principle of least privilege. `SUPER_ADMIN` already encompasses all `APP_ADMIN` permissions, making the `APP_ADMIN` assignment redundant — but its presence suggests uncontrolled privilege accumulation. Combined with 10+ months of inactivity, this is the **#1 priority finding** of this review.

**Recommended Actions:** Immediate suspension. See Section 1.

---

### 🔴 derek.walsh@acmecorp.com — `SUPER_ADMIN`
**Why flagged:** `SUPER_ADMIN` grants complete, unrestricted control over the Okta tenant — including the ability to modify all users, all apps, all policies, and all other admin accounts. Derek has been inactive for ~9 months. An unused `SUPER_ADMIN` account is functionally a dormant backdoor.

**Recommended Actions:** Immediate suspension. See Section 1.

---

### 🔴 marcus.johnson@acmecorp.com — `ORG_ADMIN`
**Why flagged:** `ORG_ADMIN` is the second-highest privilege level in Okta and grants the ability to manage most organizational settings, users, and applications. Marcus has been inactive for ~4.5 months and has an unusually broad access profile (15 apps, 8 groups). The combination of high privilege and high breadth of access with a period of inactivity is concerning. It is unclear from his group memberships (Engineering, Finance-ReadOnly, HR-ReadOnly, Salesforce-Admins, Executives) what his primary role is and whether `ORG_ADMIN` is justified.

**Recommended Actions:**
1. Verify with Marcus's manager whether the `ORG_ADMIN` role is required for his current function.
2. If admin duties are needed, consider downgrading to a **custom admin role** scoped to only the resources he needs to manage.
3. If Marcus is not in an IT/Security admin function, remove the role entirely.

---

### 🟡 james.okafor@acmecorp.com (00u7g) — `APP_ADMIN` (Never Logged In)
| Field | Value |
|---|---|
| **Last Login** | Never |
| **Status** | ACTIVE |
| **Account Age** | ~4 months (created 2025-12-01) |
| **Admin Roles** | `APP_ADMIN` |
| **Apps (6)** | Slack, Google Workspace, GitHub, AWS Console, Jira, Datadog |
| **Groups (3)** | Everyone, Engineering, DevOps |

**Why flagged:** James has an `APP_ADMIN` role assigned but has **never logged in**. This means an account with the ability to manage application configurations and assignments has never been validated by the actual user. If this account's credentials were intercepted during onboarding (e.g., activation email compromise), an attacker could administer applications without detection. Granting admin roles to accounts before first login is a risky practice.

**Recommended Actions:**
1. Verify with James's manager that this is a legitimate new hire/transfer who requires `APP_ADMIN`.
2. If legitimate, follow up on onboarding status — determine why he hasn't activated his account in 4 months.
3. **Remove the `APP_ADMIN` role** until after the user has successfully logged in and completed security onboarding (MFA enrollment, etc.).
4. If onboarding has stalled or the hire fell through, deactivate the account.

---

## 4. Never-Logged-In Accounts

### 🟡 linda.torres@acmecorp.com (00u6f)
| Field | Value |
|---|---|
| **Last Login** | Never |
| **Status** | ACTIVE |
| **Account Age** | ~2.5 months (created 2026-01-05) |
| **Admin Roles** | None |
| **Apps (5)** | Slack, Google Workspace, Workday, Salesforce, Tableau |
| **Groups (3)** | Everyone