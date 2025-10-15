# GitHub Actions CI/CD: Best Practices and Recommendations (2024-2025)

**Date**: 2025-10-15
**Purpose**: Comprehensive reference guide for DevOps engineers implementing GitHub Actions CI/CD workflows

## Summary

GitHub Actions has evolved into a leading CI/CD platform in 2024-2025, with significant advances in security through OIDC authentication, comprehensive policy enforcement via SHA pinning, and performance optimization through enhanced caching capabilities. Key industry developments include the GitHub Actions cache backend rewrite (February 2025) improving performance and reliability, new policy features supporting SHA pinning and action blocking (August 2025), and widespread adoption of ephemeral runners with AWS CodeBuild integration. Security has become paramount with tools like StepSecurity's Harden-Runner providing EDR-like capabilities, while the platform continues expanding with improved monorepo support and advanced matrix strategies. The modern approach emphasizes credential-less deployments via OIDC, reusable workflows and composite actions for code organization, and comprehensive security scanning integrated directly into pipelines.

## Key Facts

**Platform Evolution:**
- Cache backend service rewritten from ground up (February 2025) for improved performance and reliability
- GitHub Actions policy enforcement now supports SHA pinning and explicit action blocking (August 2025)
- Billable minutes rounded per job to nearest minute; 1-second jobs cost 1 minute each
- Windows runners consume minutes at 2x rate, macOS at 10x rate compared to Linux
- Self-hosted runners with AWS CodeBuild eliminate infrastructure management overhead

**Security Standards:**
- OIDC integration eliminates long-lived credentials, with tokens expiring within 1 hour
- SHA pinning to full-length commit SHA is the only way to use actions as immutable releases
- Only 7% of 100 popular security projects pin all actions to SHAs (2024 analysis)
- Dependabot monitors actions for vulnerabilities but only works with semantic versioning, not SHA pinning
- Even pinned actions can be vulnerable if they contain unpinned internal dependencies

**Performance Metrics:**
- Organizations report 70-90% reduction in workflow debug time using act for local testing
- Caching dependencies can reduce build times by significant margins (rails/rails: 7 minutes to 1 minute with rubocop caching)
- Cache limited to 10GB per repository with GitHub Actions cache backend
- Self-hosted runners on AWS report 31% cost savings compared to GitHub-hosted runners
- Matrix jobs with fail-fast disabled can significantly increase feedback time

**Workflow Architecture:**
- Reusable workflows enable entire workflow reuse with multiple jobs; composite actions group steps into single reusable units
- Workflows are OR-triggered: multiple triggers mean workflow runs when any one condition is met
- Concurrency groups limited to 1 running + 1 pending job maximum; additional pending jobs are cancelled
- Default GitHub permissions (GITHUB_TOKEN) are too permissive; explicit permission configuration required
- Jobs run in parallel by default; use `needs` keyword for sequential execution

## Analysis

### 1. Core Concepts and Architecture (2024-2025)

**Workflow Fundamentals**

Workflows are configurable automated processes made up of one or more jobs, defined using YAML files in the `.github/workflows` directory. Each workflow is triggered by events (push, pull_request, workflow_dispatch, schedule, etc.) and executes on runners - either GitHub-hosted or self-hosted machines.

**Component Architecture:**

**Workflows**: Top-level configuration defining when and how automation executes. Workflows can be triggered manually, on schedule (cron), or by repository events. Workflows are defined per repository and stored in version control.

**Jobs**: Workflows contain one or more jobs that run on the same or different runners. By default, jobs run in parallel with no dependencies. Jobs can be configured to run sequentially using the `needs` keyword to establish dependencies. Each job runs in its own fresh virtual machine or container environment.

**Steps**: Each job contains steps that execute sequentially. Steps can either run shell scripts or use actions (reusable units of code). Since steps execute on the same runner, they can share data through the filesystem.

**Runners**: Servers that execute workflows. GitHub provides hosted runners for ubuntu, windows, and macos. Self-hosted runners give you control over hardware, operating system, and software. Runners handle only one job at a time.

**Actions**: Reusable units that can be shared across workflows and repositories. Actions can be created by GitHub, verified publishers, or the community. Actions reduce boilerplate and enable standardization.

**Key Architectural Patterns (2024):**

```yaml
name: Modern CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'tests/**'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual triggering

# Explicit permissions (least privilege)
permissions:
  contents: read
  issues: write
  pull-requests: write

# Prevent concurrent runs for same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-22.04  # Pin runner version
    timeout-minutes: 15  # Prevent runaway jobs

    steps:
      - uses: actions/checkout@v4  # Pin to v4, consider SHA pinning

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'  # Built-in caching

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: dist/
          retention-days: 7

  test:
    needs: build  # Sequential dependency
    runs-on: ubuntu-22.04
    strategy:
      matrix:
        node-version: [18, 20, 22]  # Matrix for parallel testing
      fail-fast: false  # Continue other matrix jobs on failure

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - run: npm ci
      - run: npm test

  deploy:
    needs: [build, test]  # Multiple dependencies
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-22.04
    environment: production  # Environment protection rules

    permissions:
      id-token: write  # Required for OIDC
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Deploy to AWS
        run: |
          aws s3 sync ./dist s3://my-bucket
```

**Event Triggers:**

Triggers are evaluated with OR logic - if multiple triggers are configured, the workflow runs when ANY trigger condition is met.

**Common Triggers:**
- `push`: Runs on commit/tag push
- `pull_request`: Runs on PR opened, synchronize, reopened (default types)
- `workflow_dispatch`: Enables manual execution via UI or API
- `schedule`: Cron-based execution
- `release`: Runs when release is published
- `workflow_call`: Enables reusable workflow invocation

**Advanced Trigger Configuration:**

```yaml
on:
  push:
    branches:
      - main
      - 'releases/**'
    paths:
      - 'src/**'
      - '!src/docs/**'  # Ignore docs changes
    tags:
      - v*

  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    branches:
      - main

  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### 2. Security Best Practices (2024-2025)

**OpenID Connect (OIDC) Authentication**

OIDC is the modern, recommended approach for cloud authentication, eliminating long-lived credentials entirely.

**Key Benefits:**
- No static credentials stored as secrets
- Short-lived tokens (typically 1 hour expiration)
- Automatic token rotation
- Granular access control via cloud provider IAM
- Reduced attack surface
- Simplified credential management

**Implementation Requirements:**

1. Workflow must request `id-token: write` permission
2. Cloud provider must have OIDC trust relationship configured
3. Use official cloud provider actions for authentication

**AWS Example:**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
      contents: read

    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
          # No static credentials needed!

      - name: Deploy
        run: aws s3 sync ./dist s3://my-bucket
```

**Cloud Provider Setup:**

Each cloud provider requires OIDC trust relationship configuration. Consult cloud provider documentation for:
- Creating OIDC identity provider pointing to GitHub Actions
- Configuring trust relationships with subject claim filters (repository, branch, environment)
- Setting appropriate IAM policies for deployment actions

**Note:** Infrastructure provisioning (Terraform, CloudFormation, etc.) is beyond GitHub Actions core expertise. Focus on the workflow configuration; consult IaC documentation for cloud provider setup.

**Supported Cloud Providers:**
- AWS (IAM roles with OIDC)
- Azure (Workload Identity Federation)
- Google Cloud Platform (Workload Identity Federation)
- HashiCorp Vault
- Other OIDC-compatible providers

**GITHUB_TOKEN Permissions (Least Privilege)**

Default GITHUB_TOKEN permissions are too permissive. Always configure explicit permissions.

**Organization/Repository Settings:**
Navigate to Settings → Actions → Workflow permissions and select "Read repository contents and packages permissions" as default.

**Workflow-Level Configuration:**

```yaml
# Recommended: Explicit permissions at workflow level
permissions: {}  # Start with no permissions

jobs:
  build:
    permissions:
      contents: read  # Only what's needed
      issues: write
      pull-requests: write

    steps:
      # Job has minimal required permissions
      - uses: actions/checkout@v4
```

**Available Permission Scopes:**
- `actions`: read, write
- `checks`: read, write
- `contents`: read, write
- `deployments`: read, write
- `id-token`: write (for OIDC)
- `issues`: read, write
- `packages`: read, write
- `pull-requests`: read, write
- `repository-projects`: read, write
- `security-events`: read, write
- `statuses`: read, write

**Best Practice Pattern:**

```yaml
# At top of workflow
permissions:
  contents: read  # Default for all jobs

jobs:
  deploy:
    permissions:
      contents: read
      id-token: write  # Only for deployment job
      deployments: write

  security-scan:
    permissions:
      contents: read
      security-events: write  # For SARIF upload
```

**Action Security: SHA Pinning**

SHA pinning is the only way to ensure immutable action execution.

**Why SHA Pinning Matters:**
- Tags are mutable; maintainers can change what v1 points to
- Compromised action repositories can introduce malicious code
- SHA pinning provides cryptographic verification
- Mitigates supply chain attacks

**Implementation:**

```yaml
# BAD: Mutable tag
- uses: actions/checkout@v4

# BETTER: Specific version tag
- uses: actions/checkout@v4.1.0

# BEST: Full-length SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.0

# Even better: SHA with comment explaining version
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.0
```

**Policy Enforcement (August 2025):**

Administrators can now enforce SHA pinning via allowed actions policy. Workflows using non-SHA-pinned actions will fail if policy is enabled.

**Limitations and Challenges:**

1. **Unpinnable Actions Problem**: Even SHA-pinned actions can introduce new code if they have unpinned dependencies internally
2. **Dependabot Limitation**: Dependabot only creates alerts for semantically versioned actions, not SHA-pinned ones
3. **Adoption Rate**: Only 7% of 100 popular security projects pin everything (2024 study)
4. **Maintenance Burden**: Manual SHA updates required; automation tools recommended

**Automation Tools for SHA Pinning:**
- **StepSecurity Secure Workflows**: Automated PR generation for pinning
- **Minder/Frizbee**: Action scanning and automated pinning
- **pinact**: CLI tool for action pinning

**Secrets Management Best Practices**

**Environment Separation:**

```yaml
jobs:
  deploy-staging:
    environment: staging  # Uses staging secrets
    steps:
      - run: echo "Deploying to staging"
        env:
          API_KEY: ${{ secrets.STAGING_API_KEY }}

  deploy-prod:
    environment: production  # Uses production secrets
    steps:
      - run: echo "Deploying to production"
        env:
          API_KEY: ${{ secrets.PROD_API_KEY }}
```

**Prevent Secret Leakage:**

```yaml
# Secrets are automatically masked in logs, but be cautious
steps:
  - name: Use secret safely
    run: |
      # Good: Secret used in authenticated request
      curl -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" https://api.example.com

      # BAD: Secret could leak in error messages
      # curl https://api.example.com?token=${{ secrets.API_TOKEN }}

      # BAD: Logging secret directly
      # echo "Token is ${{ secrets.API_TOKEN }}"
```

**Secret Rotation Strategy:**
- Use fine-grained personal access tokens (PATs) with minimal permissions
- Rotate secrets regularly (quarterly minimum)
- Enable branch protection so only reviewed code can access secrets
- Use environments with required reviewers for production secrets
- Prefer OIDC over static credentials where possible

**Self-Hosted Runner Security**

**Critical Security Rules:**

1. **NEVER use self-hosted runners for public repositories** - Any user can open PR and compromise environment
2. **Use ephemeral, just-in-time (JIT) runners** - Maximum one job per runner instance
3. **Implement OS hardening** - Minimal software, security patches, monitoring
4. **Use short-lived credentials** - OIDC or temporary tokens, not static keys
5. **Network segmentation** - Isolate runners from sensitive infrastructure
6. **Runner groups** - Organize runners and restrict repository access

**Ephemeral Runner Pattern:**

```yaml
# Using GitHub REST API for JIT runners
- name: Create JIT runner
  run: |
    RUNNER_TOKEN=$(curl -X POST \
      -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
      https://api.github.com/repos/${{ github.repository }}/actions/runners/registration-token \
      | jq -r .token)

    # Deploy ephemeral runner that self-destructs after one job
    # Implementation varies by infrastructure
```

**Note:** Managed self-hosted runner services (AWS CodeBuild, cloud-specific solutions) are beyond GitHub Actions core expertise. Consult cloud provider documentation for integration details.

**Security Monitoring:**

```yaml
# Use StepSecurity Harden-Runner for runtime security
- name: Harden Runner
  uses: step-security/harden-runner@v2
  with:
    egress-policy: audit  # or 'block'
    allowed-endpoints: >
      api.github.com:443
      github.com:443
      registry.npmjs.org:443
```

**Harden-Runner Features:**
- Network egress monitoring and blocking
- File integrity monitoring
- Process activity monitoring
- Works like EDR for GitHub Actions
- Real-time threat detection

### 3. Workflow Patterns and Best Practices (2024-2025)

**Reusable Workflows vs Composite Actions**

**Reusable Workflows:**
- Reuse entire workflows with multiple jobs
- Called with `workflow_call` trigger
- Can use secrets, environments, and concurrency control
- Supports matrix strategy
- Takes up entire job in calling workflow

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy Workflow

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      deploy-key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          echo "Deploying ${{ inputs.image-tag }} to ${{ inputs.environment }}"
          # Actual deployment logic
        env:
          DEPLOY_KEY: ${{ secrets.deploy-key }}

# Calling workflow
jobs:
  call-deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
      image-tag: v1.2.3
    secrets:
      deploy-key: ${{ secrets.PROD_DEPLOY_KEY }}
```

**Composite Actions:**
- Group multiple steps into single action
- Used like any other action within a job step
- Can be run multiple times in same job
- More flexible composition
- Cannot use secrets directly (passed as inputs)
- Cannot contain full job configuration

```yaml
# .github/actions/setup-node-app/action.yml
name: Setup Node Application
description: Install Node.js and dependencies with caching

inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '20'

runs:
  using: composite
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci
      shell: bash

    - name: Run security audit
      run: npm audit --production
      shell: bash

# Using composite action
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-node-app
        with:
          node-version: '20'
      - run: npm run build
```

**When to Use Which:**

| Use Case | Reusable Workflow | Composite Action |
|----------|-------------------|------------------|
| Multiple jobs needed | ✅ | ❌ |
| Different runner types | ✅ | ❌ |
| Environment protection | ✅ | ❌ |
| Secrets needed | ✅ | Via inputs only |
| Share across repos | ✅ | ✅ |
| Use multiple times in job | ❌ | ✅ |
| Step-level reuse | ❌ | ✅ |
| DRY principle for steps | ❌ | ✅ |

**2024-2025 Recommendation**: Use both strategically. Composite actions for shared step sequences. Reusable workflows for standardized multi-job processes.

**Matrix Strategy**

Matrix strategy runs jobs across multiple configurations simultaneously.

**Basic Matrix:**

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20, 22]
        # Creates 9 jobs: 3 OS × 3 Node versions

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

**Advanced Matrix with Include/Exclude:**

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node-version: [18, 20, 22]

    # Add specific combinations
    include:
      - os: macos-latest
        node-version: 20
        experimental: true

    # Remove specific combinations
    exclude:
      - os: windows-latest
        node-version: 18

  # Control failure behavior
  fail-fast: false  # Continue other jobs on failure
  max-parallel: 5   # Limit concurrent jobs
```

**Dynamic Matrix:**

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}

    steps:
      - id: set-matrix
        run: |
          # Generate matrix dynamically
          MATRIX='{"include":[
            {"service":"api","path":"services/api"},
            {"service":"web","path":"services/web"},
            {"service":"worker","path":"services/worker"}
          ]}'
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  build:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}

    steps:
      - run: echo "Building ${{ matrix.service }} from ${{ matrix.path }}"
```

**Matrix Limitations:**
- When using `needs` with matrix jobs, dependent job waits for ALL matrix variants
- Cannot specify dependency on specific matrix combination
- Queue depth of 1: only 1 running + 1 pending job per concurrency group

**Workaround for Sequential Matrix Jobs:**
Use reusable workflows where each matrix variant calls complete workflow independently.

**Caching Strategies**

**GitHub Actions Cache (2025 Update):**

Cache backend rewritten from ground up (February 2025) for better performance and reliability.

**Limitations:**
- 10GB per repository
- Scoped to branch (cannot easily share across organization)
- 7-day retention if not accessed

**Setup Action Caching:**

Many setup actions have built-in caching:

```yaml
# Node.js with npm caching
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # Automatically caches node_modules

# Python with pip caching
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Java with Maven caching
- uses: actions/setup-java@v4
  with:
    java-version: '21'
    distribution: 'temurin'
    cache: 'maven'
```

**Manual Caching:**

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Install dependencies
  run: npm ci
```

**Cache Key Strategy:**
- Include OS in key: `${{ runner.os }}`
- Use file hashes for invalidation: `${{ hashFiles('**/pom.xml') }}`
- Provide restore-keys for fallback matches
- Make keys as specific as possible

**Cache Performance Example:**
rails/rails repository: rubocop workflow reduced from ~7 minutes to ~1 minute using cache action.

**Artifacts:**

Use for files needed after workflow completes or sharing between jobs:

```yaml
jobs:
  build:
    steps:
      - run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7

  test:
    needs: build
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - run: npm test
```

**Artifacts vs Cache:**
- **Artifacts**: Workflow-scoped, for exporting/sharing, stricter storage limits
- **Cache**: Repository-scoped, for speeding up builds, 10GB limit

**Concurrency Control**

Prevent multiple workflow runs for same branch/PR:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel previous run
```

**Important Limitations:**
- Queue depth limited to 1 pending job
- Only keeps most recent pending job
- Previous pending jobs cancelled automatically
- Not suitable when you need true queue behavior

**Deployment Use Case:**

```yaml
# Ensure only one deployment runs at a time
concurrency:
  group: production-deployment
  cancel-in-progress: false  # Queue deployments, don't cancel
```

**Per-Environment Concurrency:**

```yaml
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

**Path Filters (Monorepo Pattern)**

**Built-in Path Filtering:**

```yaml
on:
  push:
    paths:
      - 'services/api/**'
      - '!services/api/docs/**'  # Ignore docs

jobs:
  build-api:
    runs-on: ubuntu-latest
    steps:
      - run: echo "API changed"
```

**Limitations:**
- Limited to 300 files in diff
- If changes exceed 300 files, filter may not match

**dorny/paths-filter Action (Recommended for Monorepos):**

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
      worker: ${{ steps.filter.outputs.worker }}

    steps:
      - uses: actions/checkout@v4

      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'services/api/**'
            web:
              - 'services/web/**'
            worker:
              - 'services/worker/**'

  build-api:
    needs: changes
    if: needs.changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building API"

  build-web:
    needs: changes
    if: needs.changes.outputs.web == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building Web"

  build-worker:
    needs: changes
    if: needs.changes.outputs.worker == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building Worker"
```

**Matrix with Path Filters:**

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.set-matrix.outputs.services }}

    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api: 'services/api/**'
            web: 'services/web/**'
            worker: 'services/worker/**'

      - id: set-matrix
        run: |
          SERVICES='[]'
          if [[ '${{ steps.filter.outputs.api }}' == 'true' ]]; then
            SERVICES=$(echo $SERVICES | jq '. += ["api"]')
          fi
          if [[ '${{ steps.filter.outputs.web }}' == 'true' ]]; then
            SERVICES=$(echo $SERVICES | jq '. += ["web"]')
          fi
          if [[ '${{ steps.filter.outputs.worker }}' == 'true' ]]; then
            SERVICES=$(echo $SERVICES | jq '. += ["worker"]')
          fi
          echo "services={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  build:
    needs: changes
    if: needs.changes.outputs.services != '{"service":[]}'
    strategy:
      matrix: ${{ fromJSON(needs.changes.outputs.services) }}

    steps:
      - run: echo "Building ${{ matrix.service }}"
```

**Expressions and Conditionals**

**Context Variables:**

```yaml
steps:
  - name: Conditional step
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    run: echo "Deploying to production"

  - name: Use context variables
    run: |
      echo "Repository: ${{ github.repository }}"
      echo "SHA: ${{ github.sha }}"
      echo "Branch: ${{ github.ref_name }}"
      echo "Actor: ${{ github.actor }}"
```

**Common Contexts:**
- `github`: Event and workflow information
- `env`: Environment variables
- `secrets`: Repository/organization secrets
- `vars`: Repository/organization variables
- `job`: Current job information
- `steps`: Outputs from previous steps
- `runner`: Runner information
- `matrix`: Matrix strategy values

**Conditional Logic:**

```yaml
# Ternary-like with && and ||
- name: Set environment
  run: echo "ENV=${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}" >> $GITHUB_ENV

# Multiple conditions
- name: Complex condition
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/main' &&
    !contains(github.event.head_commit.message, '[skip ci]')
  run: echo "Running deployment"

# Check job status
- name: Notify on failure
  if: failure()
  run: echo "Job failed!"

- name: Always run cleanup
  if: always()
  run: echo "Cleanup running"
```

**Functions:**
- `contains(search, item)`: String/array contains check
- `startsWith(search, item)`: String starts with
- `endsWith(search, item)`: String ends with
- `format(string, ...)`: String formatting
- `join(array, separator)`: Array to string
- `toJSON(value)`: Convert to JSON
- `fromJSON(value)`: Parse JSON
- `hashFiles(pattern)`: Hash files matching pattern
- `success()`, `failure()`, `cancelled()`, `always()`: Job status

### 4. Performance Optimization (2024-2025)

**Cost Reduction Strategies**

**Billable Minute Optimization:**

Every started minute rounds to full minute. Ten 1-second jobs = 10 minutes billed.

**Strategies:**
1. **Group Short Jobs**: Combine multiple quick tasks into single job
2. **Set Timeouts**: Prevent runaway jobs (default 6 hours)
3. **Use Job Dependencies**: Only run subsequent jobs if prerequisites succeed
4. **Selective Triggering**: Use `on.paths` to run workflows only when relevant files change
5. **Appropriate Runner Size**: Match runner to workload (avoid over/under-provisioning)

**Runner Cost Comparison:**
- Linux: 1x cost multiplier
- Windows: 2x cost multiplier
- macOS: 10x cost multiplier

**Self-Hosted Runners:**
Self-hosted runners on AWS report 31% cost savings vs GitHub-hosted runners (2024 data).

**Timeout Configuration:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Fail after 15 minutes (default: 360)

    steps:
      - name: Build step
        timeout-minutes: 10  # Step-level timeout
        run: npm run build
```

**Conditional Job Execution:**

```yaml
jobs:
  expensive-tests:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e  # Only on main branch
```

**Docker Layer Caching**

**GitHub Actions Cache Backend:**

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: user/app:latest
    cache-from: type=gha  # Use GitHub Actions cache
    cache-to: type=gha,mode=max  # Cache all layers
```

**Limitations:**
- 10GB cache limit per repository
- Only scoped to workflow branch
- Cannot share across organization easily

**Registry Cache (Production Recommendation):**

```yaml
- name: Build with registry cache
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: user/app:latest
    cache-from: type=registry,ref=user/app:cache
    cache-to: type=registry,ref=user/app:cache,mode=max
```

**Benefits:**
- No size limitations
- Shareable across organization
- Works with external build systems
- Better for production use

**Cache Mode:**
- `mode=min`: Only caches final image layers (smaller)
- `mode=max`: Caches all intermediate layers (better cache hits)

**Inline Cache (Limited):**

```yaml
cache-from: type=inline
cache-to: type=inline
```

Only caches final stage layers, not intermediate stages in multi-stage builds. Significantly reduces cache hit effectiveness.

**Parallel Execution**

**Job Parallelization:**

```yaml
jobs:
  # These run in parallel by default
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:unit

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:integration

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - run: npm audit
```

**Sequential with Dependencies:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  test:
    needs: build  # Waits for build
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  deploy:
    needs: [build, test]  # Waits for both
    runs-on: ubuntu-latest
    steps:
      - run: npm run deploy
```

**Parallel Stages within Job:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # These run sequentially within the job
      - name: Unit tests
        run: npm run test:unit &  # Background

      - name: Lint
        run: npm run lint &  # Background

      - name: Wait for completion
        run: wait  # Wait for background jobs
```

### 5. Debugging and Local Testing (2024-2025)

**act - Local GitHub Actions Testing**

Act enables local workflow execution using Docker, dramatically reducing feedback time.

**Performance Impact:**
- Cloud workflow: 2-5 minutes typical
- act local execution: 5-20 seconds typical
- 70-90% reduction in total workflow debug time (reported by teams)

**Installation:**

```bash
# macOS
brew install act

# Linux
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Requires Docker installed and running
```

**Basic Usage:**

```bash
# List workflows
act -l

# Run default event (push)
act

# Run specific event
act pull_request

# Run specific workflow
act -W .github/workflows/ci.yml

# Run specific job
act -j build

# Verbose output for debugging
act -v

# Dry run (show what would run)
act -n
```

**Secrets in act:**

```bash
# Pass secrets via file
act --secret-file .secrets

# Pass individual secret
act -s GITHUB_TOKEN=your_token

# .secrets file format
GITHUB_TOKEN=ghp_xxxxx
NPM_TOKEN=npm_xxxxx
```

**Runner Specifications:**

```bash
# Use specific Docker image
act -P ubuntu-latest=node:20

# Use large runner
act -P ubuntu-latest=catthehacker/ubuntu:full-latest
```

**Limitations:**
- Not 100% identical to GitHub's environment
- Some GitHub-specific features unavailable
- Requires Docker (resource intensive)
- Limited support for self-hosted runner features

**Debugging Workflows**

**Enable Debug Logging:**

Set repository secrets:
- `ACTIONS_RUNNER_DEBUG`: true
- `ACTIONS_STEP_DEBUG`: true

Provides verbose logging for all workflow runs.

**Step-Level Debugging:**

```yaml
steps:
  - name: Debug information
    run: |
      echo "Event: ${{ github.event_name }}"
      echo "Ref: ${{ github.ref }}"
      echo "SHA: ${{ github.sha }}"
      echo "Actor: ${{ github.actor }}"
      env | sort

  - name: Debug with continue-on-error
    continue-on-error: true
    run: |
      # Test commands without failing workflow
      some-experimental-command
```

**Conditional Debugging:**

```yaml
- name: Debug only on failure
  if: failure()
  run: |
    echo "Previous step failed"
    cat logs/*.log
```

**SSH Debugging (action-tmate):**

```yaml
- name: Setup tmate session
  if: failure()  # Only on failure
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 30
```

Provides SSH access to runner for interactive debugging.

### 6. Deployment Strategies (2024-2025)

**Environment Protection Rules**

Environments enable deployment protection and approval workflows.

**Setup:**

Repository Settings → Environments → Create environment

**Protection Options:**
1. **Required Reviewers**: Up to 6 reviewers, only 1 needs to approve
2. **Wait Timer**: Delay deployment by specified time
3. **Deployment Branches**: Restrict which branches can deploy
4. **Custom Protection Rules**: External system integration via GitHub Apps

**Implementation:**

```yaml
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://prod.example.com

    steps:
      - name: Deploy
        run: ./deploy.sh production
```

**Manual Approval Workflow:**

When job reaches environment with required reviewers:
1. Workflow pauses
2. Reviewers notified
3. Reviewer approves/rejects in Actions UI
4. Workflow continues or stops based on decision

**Prevent Self-Review:**

Enable "Prevent self-review" option to ensure deployment initiators cannot approve their own deployments.

**Custom Protection Rules:**

Integrate external systems (monitoring, security scanners, etc.) to block deployments.

Example use cases:
- Check error rate in monitoring system
- Verify security scan results
- Ensure recent backup exists
- Validate compliance requirements

**Deployment Strategy Patterns**

GitHub Actions supports various deployment patterns through workflow configuration. The actual infrastructure deployment commands depend on your orchestration platform (Kubernetes, cloud services, etc.) and are beyond GitHub Actions core scope.

**Key GitHub Actions Features for Deployments:**

- **Environment Protection**: Use environments with required reviewers and wait timers
- **Conditional Execution**: Use `if` conditions to control deployment flow
- **Step Outputs**: Share deployment identifiers between steps
- **Job Dependencies**: Sequence deployment validation steps with `needs`
- **Timeout Controls**: Set limits to prevent hanging deployments
- **Continue on Error**: Allow non-critical steps to fail

**Example: Basic Deployment with Validation**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Deploy new version
        id: deploy
        run: ./deploy.sh ${{ github.sha }}

      - name: Health check
        id: health
        timeout-minutes: 5
        run: ./scripts/health-check.sh

      - name: Rollback on failure
        if: failure() && steps.deploy.outcome == 'success'
        run: |
          echo "Health check failed, rolling back"
          ./deploy.sh ${{ github.event.before }}
```

**Note:** Specific deployment strategies (blue-green, canary, rolling updates) require infrastructure-specific implementations. Consult orchestration platform documentation for command details.

### 7. Monitoring and Notifications (2024-2025)

**Status Badges**

Add workflow status to README:

```markdown
![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)

![CI](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg?branch=main)
```

**Slack Integration**

**Official GitHub App (Recommended):**

1. Install GitHub app in Slack workspace
2. Subscribe to repository: `/github subscribe org/repo`
3. Enable workflow notifications: `/github subscribe org/repo workflows:{event:"push","pull_request"}`

**Third-Party Actions:**

```yaml
- name: Slack Notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment to production complete",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Deployment of `${{ github.sha }}` to *production* completed\nStatus: ${{ job.status }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Conditional Notifications:**

```yaml
jobs:
  deploy:
    steps:
      - name: Deploy
        run: ./deploy.sh

      - name: Notify success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: '{"text":"✅ Deployment successful"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

      - name: Notify failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: '{"text":"❌ Deployment failed"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Email Notifications**

GitHub automatically sends email for workflow failures to workflow author.

Custom email via third-party action:

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.MAIL_USERNAME }}
    password: ${{ secrets.MAIL_PASSWORD }}
    subject: Deployment Complete - ${{ github.sha }}
    body: Deployment of ${{ github.repository }} completed successfully
    to: team@example.com
    from: GitHub Actions
```

**Workflow Run Analytics**

View workflow insights:
- Repository → Insights → Actions
- View run times, success rates, billing usage
- Identify slow workflows
- Track failure patterns

### 8. Advanced Patterns (2024-2025)

**Dynamic Workflow Generation**

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}

    steps:
      - uses: actions/checkout@v4

      - name: Generate matrix
        id: set-matrix
        run: |
          # Detect changed services in monorepo
          SERVICES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }} \
            | grep '^services/' \
            | cut -d/ -f2 \
            | sort -u \
            | jq -R -s -c 'split("\n")[:-1]')

          echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  build:
    needs: setup
    if: needs.setup.outputs.matrix != '{"service":[]}'
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}

    steps:
      - name: Build service
        run: |
          echo "Building ${{ matrix.service }}"
          cd services/${{ matrix.service }}
          make build
```

**Workflow Dependencies (workflow_run)**

Trigger workflow when another completes:

```yaml
name: Deploy

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest

    steps:
      - name: Deploy
        run: ./deploy.sh
```

**Scheduled Maintenance**

```yaml
name: Nightly Cleanup

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  cleanup:
    runs-on: ubuntu-latest

    steps:
      - name: Clean old artifacts
        run: |
          # Delete artifacts older than 30 days
          gh api /repos/${{ github.repository }}/actions/artifacts \
            | jq -r '.artifacts[] | select(.created_at < (now - 2592000 | todate)) | .id' \
            | xargs -I {} gh api -X DELETE /repos/${{ github.repository }}/actions/artifacts/{}
        env:
          GH_TOKEN: ${{ github.token }}
```

**Multi-Cloud Deployments**

For deploying to multiple cloud providers, use separate jobs with appropriate authentication actions:

```yaml
jobs:
  deploy-cloud-a:
    runs-on: ubuntu-latest
    environment: production-cloud-a
    permissions:
      id-token: write  # For OIDC authentication

    steps:
      - uses: actions/checkout@v4
      - uses: <cloud-provider-auth-action>  # Use provider-specific action
        with:
          # Provider-specific authentication parameters
      - name: Deploy
        run: ./deploy-cloud-a.sh

  deploy-cloud-b:
    runs-on: ubuntu-latest
    environment: production-cloud-b
    permissions:
      id-token: write

    steps:
      - uses: actions/checkout@v4
      - uses: <cloud-provider-auth-action>
        with:
          # Provider-specific authentication parameters
      - name: Deploy
        run: ./deploy-cloud-b.sh
```

**Note:** Cloud provider authentication actions (aws-actions/configure-aws-credentials, azure/login, google-github-actions/auth) have provider-specific configurations. Consult cloud provider documentation for setup details.

## Action Items

1. **Audit Existing Workflows**: Review all workflows for security best practices. Identify use of mutable action tags, excessive GITHUB_TOKEN permissions, hardcoded secrets, and missing timeout configurations. Document current state and prioritize security fixes.

2. **Implement OIDC Authentication**: Migrate from static cloud credentials to OIDC-based authentication for AWS, Azure, or GCP. Configure cloud provider trust relationships, update workflows to use `id-token: write` permission, and test in non-production environment first.

3. **Pin Actions to SHA**: Implement SHA pinning for all third-party actions. Use automation tools (StepSecurity, Minder, or pinact) to generate pinning PRs. Establish policy enforcement if on GitHub Enterprise to mandate SHA pinning organization-wide.

4. **Configure Explicit Permissions**: Remove default permissive GITHUB_TOKEN permissions. Set organization/repository default to read-only. Add explicit permission configuration to all workflows at job level with minimal required scopes.

5. **Implement Caching Strategy**: Add dependency caching to all workflows using setup actions with built-in cache support (setup-node, setup-python, setup-java) or manual cache action. Monitor cache hit rates and adjust key strategies for optimal performance.

6. **Create Reusable Workflows**: Identify common patterns across workflows and extract into reusable workflows or composite actions. Store in `.github/workflows` for reusable workflows or `.github/actions` for composite actions. Document usage patterns.

7. **Set Up Environment Protection**: Create environments for production deployments with required reviewers and wait timers. Configure deployment branch restrictions. Test approval workflow in staging before applying to production.

8. **Enable Monitoring and Notifications**: Set up Slack or email notifications for critical workflow failures. Add status badges to repository README. Configure deployment notifications to track production releases.

9. **Optimize for Cost**: Implement timeout configurations on all jobs and steps (recommend 3x average duration). Group short jobs to avoid per-minute rounding penalty. Use path filters to selectively trigger workflows. Consider self-hosted runners for high-volume workflows.

10. **Implement Security Scanning**: Integrate security scanning actions (OWASP Dependency-Check, Trivy, Snyk) into all workflows. Configure quality gates to fail builds on high-severity vulnerabilities. Set up automated security advisory monitoring.

11. **Document Standards**: Create organization-wide workflow standards document. Include action pinning requirements, permission guidelines, caching strategies, and deployment patterns. Train team on new practices.

12. **Set Up Local Testing**: Install and configure act for local workflow testing. Create documentation for developers on local testing workflow. Establish pre-push hooks to test workflows before committing.

## Sources

- [GitHub Docs - Workflow Syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) - Official workflow YAML syntax reference
- [GitHub Docs - Understanding GitHub Actions](https://docs.github.com/articles/getting-started-with-github-actions) - Core concepts and architecture
- [GitHub Docs - Events that Trigger Workflows](https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows) - Complete event trigger documentation
- [GitHub Docs - OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect) - OIDC security hardening guide
- [GitHub Docs - Security Hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) - Comprehensive security best practices
- [GitHub Changelog - Actions Policy SHA Pinning](https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/) - Policy enforcement features (August 2025)
- [GitHub Changelog - Actions Cache Rewrite](https://github.blog/changelog/2019-11-04-github-actions-adds-dependency-caching/) - Cache backend improvements (February 2025)
- [StepSecurity Blog - GitHub Actions Security Best Practices](https://www.stepsecurity.io/blog/github-actions-security-best-practices) - Security expert recommendations with checklist
- [StepSecurity Blog - Pinning Guide](https://www.stepsecurity.io/blog/pinning-github-actions-for-enhanced-security-a-complete-guide) - Comprehensive SHA pinning guide
- [Wiz Blog - Hardening GitHub Actions](https://www.wiz.io/blog/github-actions-security-guide) - Lessons from recent attacks
- [Palo Alto Networks - Unpinnable Actions](https://www.paloaltonetworks.com/blog/prisma-cloud/unpinnable-actions-github-security/) - Security research on action pinning limitations
- [Orca Security - GitHub Action Compromise](https://orca.security/resources/blog/github-action-tj-actions-changed-files-compromised/) - Real-world security incident (March 2025)
- [Docker Docs - GitHub Actions Cache](https://docs.docker.com/build/ci/github-actions/cache/) - Docker layer caching strategies
- [Depot Blog - Docker Layer Caching](https://depot.dev/blog/docker-layer-caching-in-github-actions) - Performance optimization guide
- [Blacksmith Blog - Docker Caching Guide](https://www.blacksmith.sh/blog/cache-is-king-a-guide-for-docker-layer-caching-in-github-actions) - Production caching patterns
- [Earthly Blog - Reusable Workflows](https://earthly.dev/blog/github-actions-reusable-workflows/) - Best practices for workflow reuse
- [Octopus Blog - GitHub Actions 2025 Guide](https://octopus.com/devops/github-actions/) - Complete 2025 overview
- [Codefresh - GitHub Actions Triggers](https://codefresh.io/learn/github-actions/github-actions-triggers-5-ways-to-trigger-a-workflow-with-code/) - Trigger patterns and examples
- [Codefresh - GitHub Actions Matrix](https://codefresh.io/learn/github-actions/github-actions-matrix/) - Matrix strategy guide
- [RunsOn - Matrix Strategy](https://runs-on.com/github-actions/the-matrix-strategy/) - Advanced matrix patterns
- [RunsOn - Triggers](https://runs-on.com/github-actions/triggers/) - Comprehensive trigger documentation
- [Graphite - Monorepo with GitHub Actions](https://graphite.dev/guides/monorepo-with-github-actions) - Monorepo workflow strategies
- [Graphite - CI/CD Best Practices](https://graphite.dev/guides/in-depth-guide-ci-cd-best-practices) - Industry-standard practices
- [GitHub - nektos/act](https://github.com/nektos/act) - Local workflow testing tool
- [GitHub - dorny/paths-filter](https://github.com/dorny/paths-filter) - Path-based conditional execution
- [GitHub - step-security/harden-runner](https://github.com/step-security/harden-runner) - Runtime security for workflows
- [NetApp Blog - 5 GitHub Actions CI/CD Best Practices](https://bluexp.netapp.com/blog/cvo-blg-5-github-actions-cicd-best-practices) - Production deployment patterns
- [Mergify Blog - Cutting Costs with GitHub Actions](https://articles.mergify.com/cutting-costs-with-github-actions-efficient-ci-strategies/) - Cost optimization strategies
- [Blacksmith Blog - Reduce GitHub Actions Spend](https://www.blacksmith.sh/blog/how-to-reduce-spend-in-github-actions) - Detailed cost reduction guide
- [cloudonaut - Reduce GitHub Actions Costs](https://cloudonaut.io/how-to-reduce-costs-for-github-actions/) - AWS integration cost analysis
- [AWS DevOps Blog - Self-Hosted Runners at Scale](https://aws.amazon.com/blogs/devops/best-practices-working-with-self-hosted-github-action-runners-at-scale-on-aws/) - Enterprise runner patterns
- [Medium - GitHub Actions and the Pinning Problem](https://medium.com/@adan.alvarez/github-actions-and-the-pinning-problem-what-100-security-projects-reveal-54a3a9dcc902) - Security research findings

## Caveats

**Research Currency**
- All recommendations current as of October 2025
- GitHub Actions features evolve rapidly; verify current documentation for critical implementations
- Cache backend improvements (February 2025) may show different performance characteristics in future releases
- Policy enforcement features (August 2025) may not be available on all GitHub plans

**Security Considerations**
- SHA pinning provides immutability but doesn't guarantee safety if pinned actions have unpinned dependencies
- OIDC implementation requires careful trust configuration; test thoroughly in non-production first
- Dependabot limitation with SHA pinning means manual monitoring required for pinned actions
- Self-hosted runner security recommendations assume properly configured network segmentation

**Performance Variability**
- Caching performance depends on network speed, runner location, and cache size
- Cost savings from self-hosted runners vary significantly by workload and infrastructure costs
- Matrix job parallelization benefits depend on available runner capacity
- Local testing with act not 100% equivalent to GitHub-hosted environment

**Implementation Limitations**
- Concurrency groups limited to 1 running + 1 pending job maximum
- Path filters limited to 300 files in diff
- GitHub Actions cache limited to 10GB per repository
- Matrix jobs with `needs` wait for all variants to complete

**Organization-Specific Requirements**
- Enterprise security policies may require additional hardening beyond these recommendations
- Compliance requirements (SOC2, HIPAA, etc.) may mandate specific controls
- Large-scale implementations (1000+ workflows) require additional architecture considerations
- Migration from other CI/CD platforms requires platform-specific strategies

**Feature Availability**
- Some features (policy enforcement, advanced environments) require GitHub Enterprise
- Self-hosted runner features vary by hosting infrastructure
- OIDC support depends on cloud provider capabilities
- Reusable workflow features may have different limitations in GitHub Enterprise Server