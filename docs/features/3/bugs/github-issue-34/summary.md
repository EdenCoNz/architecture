# GitHub Issue #34 - Investigation Summary

## Quick Reference

**Status:** Root cause identified, solution documented
**Impact:** Test job failing in CI/CD pipeline (blocks PRs)
**Severity:** HIGH (blocks deployments)
**Complexity:** LOW (simple fix)

## The Problem in 30 Seconds

- CI/CD shows 92.67% coverage during tests ✅
- CI/CD shows 8% coverage during threshold check ❌
- Threshold check expects 80% minimum ❌
- Build fails with "Coverage 8% is below the required 80% threshold"

## Root Cause in One Sentence

Coverage config has `parallel = true` which creates multiple `.coverage.*` files, but the workflow runs `coverage report` WITHOUT first running `coverage combine`, resulting in incomplete coverage data (8% instead of 92.67%).

## The Fix (1 Line Change)

Add this step BEFORE the "Check coverage threshold" step in `.github/workflows/backend-ci.yml`:

```yaml
- name: Combine coverage data files
  run: poetry run coverage combine
```

## Why This Happens

1. `backend/pyproject.toml` has:
   ```toml
   [tool.coverage.run]
   parallel = true
   concurrency = ["thread", "multiprocessing"]
   ```

2. This creates `.coverage.*` files (one per process/thread)

3. Pytest-cov internally combines these during test execution (shows 92.67%)

4. Workflow's `coverage report` command doesn't combine them (shows 8%)

5. Solution: Run `coverage combine` before `coverage report`

## What to Do Next

See `investigation-report.md` for:
- Detailed analysis
- Multiple solution approaches with pros/cons
- Recommendations
- Implementation guidance

## Files Analyzed

- `/home/ed/Dev/architecture/backend/pyproject.toml` - Coverage config
- `/home/ed/Dev/architecture/.github/workflows/backend-ci.yml` - CI/CD workflow
- `/home/ed/Dev/architecture/backend/Makefile` - Test commands

## Recommended Solution

**Approach 1 + 3 Combined:**
1. Add `coverage combine` step before threshold check
2. Use `coverage report --fail-under=80` for native threshold validation
3. Minimal changes, maximum reliability

See investigation report for full details.
