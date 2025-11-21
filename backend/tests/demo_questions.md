# Demo Questions for Testing

Use these questions to demonstrate the RAG system capabilities:

## Incident Response

1. **How do I handle a SEV-1 incident?**
   - Expected: Should cite incident response runbook, mention immediate acknowledgment, war room, IC assignment, etc.

2. **What's the difference between SEV-1 and SEV-2 incidents?**
   - Expected: Should explain severity definitions and response time differences

3. **Who should I escalate to if a SEV-1 isn't resolved in 30 minutes?**
   - Expected: Should cite VP Engineering as escalation contact

## Database Management

4. **What maintenance tasks should be run weekly on the database?**
   - Expected: Should list vacuum analysis, index health check, slow query review, backup verification

5. **How do I check current database connections?**
   - Expected: Should provide SQL query for checking connections

6. **What should I do if the database is not accepting connections?**
   - Expected: Should list troubleshooting steps from emergency procedures

## Deployment

7. **What is the standard deployment process?**
   - Expected: Should outline the multi-step deployment flow

8. **Can I deploy to production on Friday afternoon?**
   - Expected: Should mention no deployments after 12 PM on Fridays

9. **How do I rollback a deployment?**
   - Expected: Should explain quick rollback and manual rollback procedures

10. **What are feature flags and when should I use them?**
    - Expected: Should explain feature flags for risky changes and gradual rollout

## Access Management

11. **How do I request production database access?**
    - Expected: Should outline access request process and requirements

12. **What are the different access levels?**
    - Expected: Should list Levels 1-4 with descriptions

13. **How long does it take to get AWS console access approved?**
    - Expected: Should cite typical approval times (2-3 days for prod read)

## Security

14. **What are the password requirements?**
    - Expected: Should list 16 characters, password manager, unique, etc.

15. **What should I do if I lose my company laptop?**
    - Expected: Should list immediate reporting steps and remote wipe process

16. **Is MFA required for production systems?**
    - Expected: Should confirm MFA is required

## Cross-Document Questions

17. **What's the complete process from code review to production deployment?**
    - Expected: Should combine information from deployment docs

18. **What security measures are in place for production database access?**
    - Expected: Should combine access control and security policies

19. **How do I get on the on-call rotation?**
    - Expected: Should reference both access requests and incident response docs

## Edge Cases

20. **How do I deploy to the moon?**
    - Expected: Should indicate this information is not in the documentation

21. **What is the meaning of life?**
    - Expected: Should indicate this is outside the scope of documentation

