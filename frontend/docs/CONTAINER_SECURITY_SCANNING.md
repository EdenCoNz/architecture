# Container Security Scanning

This document describes the automated security scanning implemented for frontend container images in the CI/CD pipeline (Story 9.5).

## Overview

Container images are automatically scanned for security vulnerabilities, secrets, and misconfigurations using Trivy as part of the CI/CD pipeline. Both development and production containers are scanned to ensure security issues are identified before deployment.

## Scanner: Trivy

Trivy is an open-source security scanner that:
- Scans OS packages and application dependencies
- Detects known vulnerabilities (CVEs)
- Identifies exposed secrets in images
- Checks for misconfigurations
- Reports severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Provides remediation guidance
- Generates SARIF reports for GitHub Security integration

## What Gets Scanned

### Development Container (`frontend:dev`)
- Base image: node:20-alpine
- Installed OS packages (Alpine APK packages)
- Node.js dependencies from package.json
- Build tools (python3, make, g++)

### Production Container (`frontend:prod`)
- Base image: nginx:1.27-alpine
- Installed OS packages (Alpine APK packages)
- Built static assets (JavaScript, CSS, HTML)
- Nginx configuration

## Scan Types

1. **Vulnerabilities (vuln)**: Known security vulnerabilities in OS packages and dependencies
2. **Secrets (secret)**: Exposed secrets, API keys, credentials in image layers
3. **Misconfigurations (misconfig)**: Security misconfigurations in container settings

## Vulnerability Thresholds

The CI pipeline enforces different thresholds for development and production containers:

### Development Container Thresholds
- **CRITICAL**: Maximum 5 (fails build if exceeded)
- **HIGH**: Maximum 10 (warning only, build continues)
- **MEDIUM**: Reported but does not fail build
- **LOW**: Reported but does not fail build

**Rationale**: Development containers include build tools and development dependencies that may have more vulnerabilities. The threshold is more permissive to avoid blocking development workflows unnecessarily.

### Production Container Thresholds
- **CRITICAL**: Maximum 0 (fails build immediately if any found)
- **HIGH**: Maximum 5 (fails build if exceeded)
- **MEDIUM**: Reported but does not fail build
- **LOW**: Reported but does not fail build

**Rationale**: Production containers must have zero critical vulnerabilities. The stricter threshold ensures only secure images are deployed to production.

## Where Scan Results Are Available

### 1. GitHub Step Summary
After each scan, a detailed summary is added to the GitHub Actions Step Summary showing:
- Vulnerability counts by severity
- Detailed information for CRITICAL and HIGH vulnerabilities
- Threshold evaluation results
- Pass/fail status

### 2. GitHub Security Tab
SARIF scan results are uploaded to the GitHub Security tab (`Security` → `Code scanning alerts`) for:
- Long-term vulnerability tracking
- Security dashboard visibility
- Integration with GitHub's security features
- Historical trend analysis

### 3. Workflow Artifacts
Full scan results are stored as workflow artifacts for 30 days:
- `trivy-dev-scan-results-<SHA>`: Development container scan
  - `trivy-dev-results.sarif`: SARIF format for GitHub Security
  - `trivy-dev-results.json`: JSON format for parsing
- `trivy-prod-scan-results-<SHA>`: Production container scan
  - `trivy-prod-results.sarif`: SARIF format for GitHub Security
  - `trivy-prod-results.json`: JSON format for parsing

## CI/CD Integration

Security scanning is integrated into the frontend CI/CD workflow:

```
Build Container → Security Scan → (Pass/Fail)
```

### Job Flow
1. **Job 5-6**: Build development and production containers
2. **Job 7**: Security scan development container
3. **Job 8**: Security scan production container
4. **Job 9+**: Subsequent jobs (cleanup, security audit, etc.)

### Failure Behavior
- If security scan fails, the pipeline stops
- No subsequent jobs are executed
- Image is not available for deployment
- Detailed failure information is displayed in Step Summary

## Scan Results Interpretation

### Vulnerability Entry Format
```
[SEVERITY] CVE-ID - PackageName InstalledVersion → FixedVersion
  Title: Vulnerability Title
```

Example:
```
[CRITICAL] CVE-2023-12345 - openssl 3.0.0 → 3.0.7
  Title: Remote code execution in OpenSSL
```

### Severity Levels

- **CRITICAL**: Severe vulnerabilities requiring immediate attention
  - Often allow remote code execution or privilege escalation
  - Must be fixed before production deployment

- **HIGH**: Important vulnerabilities that should be addressed soon
  - May allow unauthorized access or data exposure
  - Should be fixed before production deployment

- **MEDIUM**: Moderate vulnerabilities that should be reviewed
  - May have limited impact or require specific conditions to exploit
  - Should be triaged and fixed based on risk assessment

- **LOW**: Minor vulnerabilities with limited impact
  - Often have minimal security impact
  - Can be addressed as part of routine updates

## Remediation Workflow

When vulnerabilities are found:

1. **Review Scan Results**
   - Check GitHub Step Summary for vulnerability details
   - Review full report in workflow artifacts
   - Check GitHub Security tab for additional context

2. **Assess Impact**
   - Determine if vulnerability affects your application
   - Check if fixed version is available
   - Evaluate workarounds if no fix available

3. **Remediate**
   - **OS Packages**: Update base image to newer version
   - **Node Dependencies**: Run `npm audit fix` or update package.json
   - **Nginx**: Update nginx base image version
   - **No Fix Available**: Consider alternative packages or accept risk with justification

4. **Verify Fix**
   - Rebuild container with updates
   - Re-run security scan
   - Verify vulnerability count decreases

5. **Deploy**
   - Once scan passes thresholds, deploy updated container

## Local Testing

Test security scanning locally before pushing:

```bash
# Build the production container
cd frontend
docker build -t frontend:local-prod --target production \
  --build-arg VITE_API_URL=https://api.example.com \
  --build-arg VITE_APP_NAME="Frontend Application" \
  --build-arg VITE_APP_VERSION=1.0.0 .

# Install Trivy (if not already installed)
# Ubuntu/Debian:
sudo apt-get install wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Run Trivy scan
trivy image --severity CRITICAL,HIGH,MEDIUM,LOW frontend:local-prod

# Generate JSON report
trivy image --format json --output scan-results.json frontend:local-prod

# Check specific severity
trivy image --severity CRITICAL --exit-code 1 frontend:local-prod
```

## Threshold Configuration

Thresholds are configured in the CI workflow file. To modify:

1. Edit `.github/workflows/frontend-ci.yml`
2. Locate the security scan job (job 7 or 8)
3. Find the "Parse scan results" step
4. Modify threshold variables:
   ```bash
   THRESHOLD_CRITICAL=5  # Change this value
   THRESHOLD_HIGH=10     # Change this value
   ```
5. Commit and push changes

## Scan Frequency

Scans run automatically:
- On every push to feature branches
- On every pull request
- On manual workflow dispatch
- Scans use cached Trivy vulnerability database (updated automatically)

## Performance

- Scan duration: 2-5 minutes per container
- Runs in parallel with other jobs
- Uses GitHub Actions cache for Trivy database
- Does not significantly impact overall pipeline time

## Best Practices

1. **Fix Critical Vulnerabilities Immediately**: Never deploy containers with critical vulnerabilities
2. **Regular Updates**: Keep base images and dependencies up to date
3. **Review Medium/Low**: Triage and address based on actual risk to your application
4. **Monitor Trends**: Use GitHub Security tab to track vulnerability trends over time
5. **Test Locally**: Run Trivy locally before pushing to catch issues early
6. **Document Exceptions**: If accepting a vulnerability risk, document the decision
7. **Update Thresholds**: Adjust thresholds based on your security requirements and risk tolerance

## Troubleshooting

### Scan Fails with "Scan results file not found"
- Check if Trivy action succeeded
- Verify image was built and loaded correctly
- Check workflow logs for Trivy errors

### Too Many False Positives
- Review if vulnerabilities actually affect your application
- Consider using Trivy ignore file (.trivyignore) for known false positives
- Update thresholds if appropriate for your risk level

### Scan Takes Too Long
- Trivy database may be large; this is normal on first run
- Subsequent runs use cached database and are faster
- Consider increasing timeout if needed

### Production Build Fails Due to Vulnerabilities
- Review scan results in Step Summary
- Check if base image updates are available
- Consider temporary threshold increase with justification (not recommended)
- Update dependencies to fixed versions

## Additional Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [CVE Database](https://cve.mitre.org/)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [SARIF Format Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)

## Story Implementation

This security scanning implementation fulfills **Story 9.5: Container Image Security Scanning** from Feature #9, which requires:
- Automated scanning of container images for vulnerabilities ✓
- Reporting vulnerabilities with severity levels ✓
- Failing CI pipeline on critical vulnerabilities ✓
- Summary of security findings ✓
- Scanning both OS and application dependencies ✓
- Providing remediation guidance ✓
- Configurable thresholds for failing builds ✓
- Storing results for tracking over time ✓
