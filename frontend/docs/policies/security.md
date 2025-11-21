# Security Policy

Company security guidelines, best practices, and incident reporting procedures.

## Overview

Security is everyone's responsibility. This policy outlines the security standards and practices all employees must follow to protect company and customer data.

## Data Classification

### Public Data
- Marketing materials
- Public documentation
- Published blog posts

**Handling**: Can be freely shared externally

### Internal Data
- Internal processes and documentation
- Employee directories
- Internal communications

**Handling**: Can be shared within company, not externally

### Confidential Data
- Customer data and PII
- Financial information
- Strategic plans and roadmaps
- Source code

**Handling**: Need-to-know basis only, encrypted in transit and at rest

### Restricted Data
- Authentication credentials
- Encryption keys
- Security vulnerability details
- Personally Identifiable Information (PII)

**Handling**: Highly restricted access, requires VP approval, encrypted, audit logged

## Authentication and Access Control

### Password Requirements

All passwords must:
- Be at least 16 characters long
- Use a password manager (1Password provided)
- Be unique (never reuse passwords)
- Never be shared with anyone

### Multi-Factor Authentication (MFA)

**Required for**:
- All company accounts (Google Workspace, Slack, GitHub)
- Production system access
- AWS console access
- VPN connections
- Administrative access

**Recommended methods**:
1. Hardware security key (YubiKey - provided by company)
2. Authenticator app (Google Authenticator, Authy)
3. SMS (least preferred, only if others unavailable)

### SSH Keys

- Use Ed25519 or RSA 4096-bit keys
- Protect keys with strong passphrase
- Never commit private keys to version control
- Rotate keys annually
- Report lost or compromised keys immediately

### API Keys and Secrets

- Never commit to version control
- Store in 1Password or AWS Secrets Manager
- Rotate every 90 days
- Use environment variables for application access
- Revoke immediately when no longer needed

## Secure Development Practices

### Code Security

**Required**:
- Security scanning in CI/CD (Snyk, dependabot)
- Code review before merge (minimum 2 reviewers)
- No secrets in code or configuration files
- Input validation and sanitization
- Parameterized SQL queries (prevent SQL injection)
- Output encoding (prevent XSS)

**Dependency management**:
- Keep dependencies up to date
- Review security advisories weekly
- Update critical vulnerabilities within 48 hours
- Use `npm audit` or `pip-audit` in CI pipeline

### Infrastructure as Code

All infrastructure must be:
- Defined as code (Terraform, CloudFormation)
- Stored in version control
- Reviewed before deployment
- Scanned for security issues (tfsec, checkov)

Security defaults:
- Encryption at rest enabled
- Encryption in transit (TLS 1.3)
- Private subnets for databases
- Security groups with least-privilege access
- No public S3 buckets (ever)

### Database Security

**Access control**:
- Use principle of least privilege
- Applications use service accounts (not admin)
- Read replicas for read-only access
- Network-level restrictions (security groups)

**Encryption**:
- All production databases encrypted at rest
- TLS required for all connections
- Regular backup encryption verification

**Sensitive data handling**:
- PII encrypted at application level
- Credit card data never stored (use payment processor)
- Tokenization for sensitive data when possible
- Data anonymization for development/staging

## Network Security

### VPN Usage

**Required when**:
- Accessing production systems
- Working from public WiFi
- Accessing internal resources remotely

**VPN best practices**:
- Keep VPN client updated
- Connect before accessing internal resources
- Disconnect when not needed (to reduce attack surface)

### Firewall Rules

- Default deny all inbound traffic
- Whitelist specific IPs and ports as needed
- Regular review of firewall rules (quarterly)
- No 0.0.0.0/0 access to production systems

### Public WiFi

When using public WiFi:
- Always use company VPN
- Avoid accessing sensitive data if possible
- Verify network name (avoid spoofed networks)
- Disable file sharing and auto-connect

## Device Security

### Company Devices

**Requirements**:
- Full disk encryption enabled (FileVault, BitLocker)
- Automatic updates enabled
- Antivirus software installed and running
- Screen lock after 5 minutes of inactivity
- Strong password/PIN for device login

**Prohibited**:
- Jailbreaking or rooting devices
- Disabling security features
- Installing unauthorized software
- Storing company data on personal devices

### Personal Devices (BYOD)

If allowed for your role:
- Must enroll in Mobile Device Management (MDM)
- Company data in separate container
- Remote wipe capability
- Same security requirements as company devices

### Lost or Stolen Devices

**Immediately**:
1. Report to IT security: security@company.com or #security-incidents
2. Remote wipe will be initiated
3. Change passwords for all accounts
4. File police report (if stolen)

## Incident Response

### What to Report

Report immediately if you:
- Suspect a security breach
- Receive a phishing email
- Lose a company device
- Accidentally expose credentials or sensitive data
- Notice unusual account activity
- Find a security vulnerability

### How to Report

**Critical incidents** (active breach, data exposure):
1. Email: security@company.com
2. Slack: Post in #security-incidents
3. Page on-call security engineer (PagerDuty)

**Non-critical** (suspicious email, potential vulnerability):
1. Email: security@company.com
2. Slack: #security-incidents

### Information to Include

- What happened
- When did you notice it
- What systems/data are affected
- Any actions already taken
- Your contact information

### Response Timeline

- **Critical**: Security team responds within 15 minutes
- **High**: Response within 2 hours
- **Medium**: Response within 1 business day

## Phishing and Social Engineering

### How to Identify Phishing

**Red flags**:
- Unexpected emails requesting credentials or sensitive data
- Urgent language or threats
- Suspicious sender addresses
- Generic greetings ("Dear user")
- Spelling and grammar errors
- Mismatched or suspicious links
- Unexpected attachments

**When in doubt**:
- Hover over links (don't click) to see real destination
- Check sender email carefully
- Contact sender via alternate method to verify
- Forward suspicious emails to security@company.com

### Social Engineering

**Be cautious of**:
- Phone calls requesting credentials or access
- Impersonation of IT support or management
- Requests to bypass normal procedures
- Pressure or urgency to act quickly

**Never**:
- Share passwords over phone, email, or chat
- Grant access without proper approval process
- Click links in unsolicited emails
- Download attachments from unknown sources

## Data Protection

### Customer Data

**Principles**:
- Collect only what's necessary
- Retain only as long as needed
- Delete securely when no longer required
- Never use production data in development/testing

**Access**:
- Logged and audited
- Need-to-know basis only
- Regular access reviews
- Anonymize for analytics when possible

### Personal Identifiable Information (PII)

**Includes**:
- Names, email addresses, phone numbers
- IP addresses, device IDs
- Financial information
- Health information
- Biometric data

**Requirements**:
- Encrypt in transit and at rest
- Minimize collection and retention
- Allow user access, correction, and deletion
- Comply with GDPR, CCPA, and other regulations

### Data Breaches

If customer data is potentially exposed:
1. Immediately report to security team
2. Security team activates incident response plan
3. Legal and compliance notified
4. Customer notification within 72 hours (if required)
5. Post-incident review and remediation

## Compliance and Training

### Required Training

**All employees**:
- Security awareness training (annually)
- Phishing simulation tests (quarterly)
- Policy acknowledgment (upon hire and annually)

**Developers**:
- Secure coding practices (upon hire)
- OWASP Top 10 (annually)
- Security testing tools training

**Managers**:
- Data handling and classification
- Incident response procedures

### Audits and Reviews

- Annual security audit by external firm
- Quarterly internal security reviews
- Continuous vulnerability scanning
- Penetration testing (annually)
- Access reviews (quarterly)

### Policy Violations

Violations may result in:
- Verbal or written warning
- Mandatory additional training
- Access revocation
- Suspension or termination
- Legal action (for criminal violations)

## Security Resources

### Internal Channels

- **#security-incidents**: Report security issues
- **#security-questions**: Ask security questions
- **#security-updates**: Security announcements

### Contacts

- **Security Team**: security@company.com
- **On-call Security Engineer**: Page via PagerDuty
- **VP Engineering**: vpe@company.com
- **Legal**: legal@company.com

### External Resources

- OWASP: https://owasp.org
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- SANS Security Resources: https://www.sans.org

## Review and Updates

This policy is reviewed quarterly and updated as needed. Last updated: November 2025.

!!! tip "Security First"
    When in doubt about security, always err on the side of caution. It's better to ask and be safe than to risk a security incident.

