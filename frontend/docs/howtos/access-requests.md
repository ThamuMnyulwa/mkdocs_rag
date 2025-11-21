# Access Requests

How to request access to various systems, databases, and resources.

## Overview

All access requests follow a standard approval workflow based on the principle of least privilege. Access is granted based on job role and specific business needs.

## System Access Levels

### Level 1: Standard Employee Access
**Automatic upon hire** - Provisioned by IT during onboarding

- Company email and calendar
- Slack workspace
- JIRA and Confluence
- GitHub (read-only to public repos)
- VPN access

### Level 2: Developer Access
**Requires manager approval**

- GitHub write access to relevant repositories
- AWS console (read-only)
- Development and staging environment access
- CI/CD pipeline access (CircleCI/GitHub Actions)
- Development databases

### Level 3: Production Access
**Requires VP Engineering approval**

- Production environment access (read-only)
- Production database read replicas
- Monitoring and logging systems (Grafana, CloudWatch, Sentry)
- PagerDuty on-call rotation

### Level 4: Production Write Access
**Requires VP Engineering + Security approval**

- Production database write access
- Production server SSH access
- Infrastructure as Code repositories
- Deployment permissions

## Request Process

### 1. Submit Access Request

Navigate to: https://access.company.com

Fill out the form:
- **System/Resource**: Select from dropdown
- **Access Level**: Read, Write, or Admin
- **Business Justification**: Explain why you need this access
- **Duration**: Temporary (specify end date) or Permanent
- **Manager**: Your direct manager (auto-populated)

### 2. Approval Chain

Requests are routed automatically:

```
Employee → Manager → System Owner → Security (if needed) → IT Provisioning
```

**Typical approval times**:
- Standard access: 1 business day
- Production read access: 2-3 business days
- Production write access: 3-5 business days

### 3. Access Provisioned

You'll receive email notification when access is granted with:
- Login instructions
- Access expiration date (if temporary)
- Usage guidelines and policies

### 4. Confirm Access

Test your new access and confirm in the access request ticket.

## Common Access Requests

### Production Database Access

**Read-only access** (for debugging, data analysis):

1. Submit access request with specific use case
2. Complete database access training (required first time)
3. Receive connection credentials via 1Password
4. Access via read replica only

Connection string format:
```
postgresql://username:password@prod-replica.company.com:5432/production
```

⚠️ **Never query production primary database directly**

**Write access** (DBAs and emergency use only):

- Requires annual background check
- Requires completion of data handling training
- Subject to audit logging
- Must follow change control process

### AWS Console Access

**Developer access**:
- Read-only to most services
- Write access to development account only
- MFA required

**Production access**:
- Read-only to specific services needed for your role
- MFA required
- Session duration: 8 hours
- All actions logged to CloudTrail

Request template:
```
System: AWS Console - Production Account
Access Level: Read-only
Services needed: EC2, RDS, CloudWatch, S3
Justification: Need to monitor application performance and debug production issues
Duration: Permanent (tied to on-call rotation)
```

### GitHub Repository Access

**Write access to existing repositories**:

1. Submit access request listing specific repositories
2. Manager approval required
3. Access granted to your GitHub account
4. You'll be added to the appropriate team

**Creating new repositories**:

1. Use repository template: https://github.com/company/template-repo
2. Repository must be private by default
3. Requires manager approval
4. Follow naming convention: `team-name-project-name`

### VPN Access Levels

**Standard VPN**:
- Access to internal network and development resources
- Granted to all employees

**Production VPN**:
- Access to production network segments
- Requires production access approval
- Client certificate authentication
- Limited to on-call engineers and SRE team

### PagerDuty On-Call Access

Required for on-call rotation:

1. Complete incident response training
2. Manager submits request on your behalf
3. Added to escalation policy
4. Receives PagerDuty account with SMS/phone notifications configured

On-call rotation expectations:
- 7-day rotation
- < 5 minute acknowledgment for SEV-1
- < 15 minute acknowledgment for SEV-2
- Compensated with on-call bonus

## Temporary Access

For contractors or temporary project needs:

- Maximum duration: 90 days
- Must specify exact end date
- Automatically revoked on end date
- Can be extended with new approval

## Access Reviews

All access is reviewed quarterly:

- Managers review team member access levels
- Unused access is automatically revoked
- Access no longer needed for role is removed
- Compliance generates audit report

## Revoking Access

### Self-Service Revocation
If you no longer need access:
1. Go to https://access.company.com
2. Select "My Access"
3. Click "Revoke" next to the access you want to remove

### Automatic Revocation
Access is automatically revoked when:
- Employee leaves company (immediate)
- Contractor contract ends (immediate)
- Temporary access expires
- 90 days of inactivity

### Emergency Revocation
Security team can immediately revoke access in case of:
- Security incident
- Policy violation
- Employee termination

## Troubleshooting

### Access Request Stuck in Approval
- Check with your manager first
- After 5 business days, escalate to IT support
- For urgent requests, contact #it-support in Slack

### Access Not Working After Approval
- Wait 30 minutes for provisioning to complete
- Clear browser cache and retry
- For VPN issues, download latest VPN client
- Contact #it-support if still not working

### Lost or Forgot Credentials
- Use "Forgot Password" flow for most systems
- For shared credentials, check team 1Password vault
- For certificate-based auth, request new certificate

### Need Emergency Production Access
1. Contact on-call engineer via PagerDuty
2. Manager must approve via Slack in #access-requests
3. VP Engineering must acknowledge
4. Access granted for 24 hours
5. Full request must be submitted next business day

## Security Policies

- **Never share credentials** - Request individual access instead
- **Use MFA** - Required for all production systems
- **Follow least privilege** - Request minimum access needed
- **Report suspicious access** - Contact security@company.com
- **Access reviews** - Respond promptly to quarterly reviews

!!! warning "Compliance"
    Unauthorized access to production systems is a violation of company policy and may result in disciplinary action. All access is logged and audited.

