# Incident Response Runbook

This runbook describes the process for responding to incidents in production systems.

## Severity Levels

### SEV-1 (Critical)
**Definition**: Complete service outage or critical functionality unavailable affecting all users.

**Response Time**: Immediate (< 5 minutes)

**Procedure**:
1. Acknowledge the incident in PagerDuty
2. Join the war room Zoom link (posted in #incidents channel)
3. Assign an Incident Commander (IC)
4. IC creates an incident doc from the template
5. Assign roles:
   - Technical Lead: diagnoses and coordinates fixes
   - Communications Lead: handles stakeholder updates
   - Scribe: documents timeline and actions
6. Update status page immediately
7. Post updates every 15 minutes in #incidents
8. Once resolved, schedule post-mortem within 48 hours

**Escalation**: If not resolved within 30 minutes, escalate to VP Engineering

### SEV-2 (High)
**Definition**: Partial service degradation or critical functionality impaired for subset of users.

**Response Time**: Within 15 minutes

**Procedure**:
1. Acknowledge the incident in PagerDuty
2. Create thread in #incidents channel
3. Assign a Technical Lead
4. Investigate and implement fix
5. Update status page if customer-facing
6. Post resolution summary in #incidents
7. Consider post-mortem if incident was complex

**Escalation**: If not resolved within 2 hours, escalate to Engineering Manager

### SEV-3 (Medium)
**Definition**: Minor service degradation, workaround available, or internal-only impact.

**Response Time**: Within 1 hour

**Procedure**:
1. Create ticket in JIRA
2. Post in #incidents channel
3. Investigate during business hours
4. Implement fix or workaround
5. Update ticket with resolution

## Communication Templates

### Initial Status Page Update
```
We are currently investigating reports of [issue description]. 
We will provide updates as we learn more.
```

### Resolution Update
```
The issue affecting [service/feature] has been resolved. 
Root cause: [brief explanation]
All systems are now operating normally.
```

## Key Contacts

- On-call Engineer: Check PagerDuty schedule
- Engineering Manager: Reach via Slack or PagerDuty
- VP Engineering: Emergency escalation only

## Tools and Access

- PagerDuty: https://company.pagerduty.com
- Status Page: https://status.company.com
- Monitoring Dashboard: https://grafana.company.com
- Log Aggregation: https://logs.company.com

## Post-Incident Process

After a SEV-1 or SEV-2 incident:

1. Schedule post-mortem meeting within 48 hours
2. Write post-mortem document (use template)
3. Identify action items with owners and due dates
4. Track action items to completion
5. Share learnings with engineering team

!!! warning "Remember"
    Always prioritize customer communication and service restoration over root cause analysis during active incidents.

