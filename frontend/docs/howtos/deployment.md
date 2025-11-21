# Deployment Process

This guide covers the standard deployment process for pushing code changes to production.

## Prerequisites

Before deploying, ensure:

- [ ] Code has been reviewed and approved (minimum 2 approvals)
- [ ] All CI/CD checks pass (tests, linting, security scans)
- [ ] Changes have been tested in staging environment
- [ ] Deployment has been announced in #deployments channel
- [ ] You have necessary access credentials

## Deployment Environments

| Environment | Purpose | Auto-Deploy | Access |
|------------|---------|-------------|--------|
| Development | Active development | Yes, from `develop` branch | All engineers |
| Staging | Pre-production testing | Yes, from `main` branch | All engineers |
| Production | Live customer environment | Manual approval required | Release managers only |

## Standard Deployment Flow

### 1. Prepare for Deployment

Create a deployment checklist:

```markdown
- [ ] All tests passing
- [ ] Staging verification complete
- [ ] Database migrations reviewed (if any)
- [ ] Feature flags configured
- [ ] Rollback plan documented
- [ ] Stakeholders notified
```

### 2. Merge to Main Branch

```bash
git checkout main
git pull origin main
git merge --no-ff develop
git push origin main
```

This triggers automatic deployment to **staging**.

### 3. Verify Staging

Wait for staging deployment to complete (typically 5-10 minutes), then:

1. Check deployment status in CircleCI/GitHub Actions
2. Run smoke tests:
   ```bash
   npm run test:smoke -- --env=staging
   ```
3. Manually verify key user flows
4. Check error monitoring (Sentry) for new issues

### 4. Deploy to Production

Once staging verification is complete:

1. Navigate to deployment dashboard: https://deploy.company.com
2. Click "Deploy to Production"
3. Select the commit/tag to deploy
4. Add deployment notes (link to JIRA ticket, brief description)
5. Click "Confirm Deployment"

The deployment will:
- Create a release tag automatically
- Run database migrations (if any)
- Deploy with zero-downtime rolling update
- Run health checks before routing traffic

### 5. Monitor Deployment

Watch for the first 30 minutes post-deployment:

- **Error rates**: Check Sentry and CloudWatch
- **Response times**: Monitor in Grafana
- **Success rates**: Watch API success metrics
- **User reports**: Monitor #customer-support channel

### 6. Post-Deployment Verification

Run production smoke tests:
```bash
npm run test:smoke -- --env=production
```

Verify:
- [ ] Application is responsive
- [ ] Key features working (login, checkout, etc.)
- [ ] No spike in errors
- [ ] Database migrations completed successfully

### 7. Announce Completion

Post in #deployments:
```
✅ Deployment complete: v1.2.3
- Feature: [brief description]
- JIRA: PROJ-123
- Deployed by: @yourname
```

## Database Migrations

### Safe Migration Practices

1. **Always make migrations backward-compatible**
   - Add columns as nullable initially
   - Don't remove columns in same release as code changes

2. **Test migrations in staging with production data volume**
   ```bash
   # Estimate migration time
   EXPLAIN ANALYZE [migration SQL];
   ```

3. **For long-running migrations (> 1 minute)**
   - Schedule maintenance window
   - Consider background migration pattern
   - Use `CONCURRENTLY` for index creation

### Deployment with Migrations

```bash
# Migrations run automatically during deployment
# But you can run manually if needed:
npm run migrate -- --env=production
```

## Rollback Procedures

If issues are detected post-deployment:

### Quick Rollback (< 15 minutes since deploy)
```bash
# Via deployment dashboard
1. Click "Rollback" button
2. Select previous version
3. Confirm rollback
```

### Manual Rollback
```bash
git revert [commit-hash]
git push origin main
# Follow standard deployment process
```

### Database Rollback
⚠️ **Database rollbacks are complex and risky**

1. Stop application traffic
2. Restore from backup (if necessary)
3. Run down-migration scripts
4. Engage DBA for guidance

## Emergency Hotfix Process

For critical production bugs requiring immediate fix:

1. Create hotfix branch from production tag:
   ```bash
   git checkout -b hotfix/critical-bug v1.2.3
   ```

2. Implement minimal fix
3. Test locally and in staging
4. Fast-track code review (1 approval acceptable)
5. Deploy following standard process
6. Merge hotfix back to `main` and `develop`

## Deployment Schedule

- **Regular deployments**: Tuesday-Thursday, 10 AM - 3 PM PST
- **No deployments**: Fridays after 12 PM, weekends, or holidays
- **Emergency hotfixes**: Anytime, with manager approval

## Feature Flags

Use feature flags for risky changes:

```python
if feature_flag('new_checkout_flow'):
    # New implementation
else:
    # Old implementation
```

Toggle flags in: https://flags.company.com

Benefits:
- Deploy code without activating features
- Gradual rollout to percentage of users
- Quick disable if issues detected

## Common Issues

### Deployment Hangs
- Check CircleCI/GitHub Actions logs
- Verify no manual approval gates stuck
- Check cluster autoscaling events

### Health Checks Failing
- Review application logs
- Check database connectivity
- Verify environment variables set correctly

### Increased Error Rates Post-Deploy
1. Check Sentry for new error patterns
2. Review recent code changes
3. Consider immediate rollback if severe
4. Debug in staging environment

!!! tip "Best Practices"
    - Deploy small, incremental changes
    - Deploy early in the day when team is available
    - Always have a rollback plan
    - Use feature flags for risky changes
    - Communicate with your team

