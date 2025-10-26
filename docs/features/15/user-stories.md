# Feature 15: Phase 1 - Consolidate Docker Compose Files

**Feature ID:** 15
**Created:** 2025-10-27
**Status:** Planning

## Feature Description

Enable developers and operators to manage container orchestration through a simplified, non-redundant configuration structure by eliminating duplicate compose files across the repository while maintaining full functionality for all deployment environments (local, staging, production, testing).

This is Phase 1 of the Docker Simplification effort documented in docs/docker-simplification.md, focused specifically on removing redundant compose files and establishing a single source of truth for container orchestration.

## Business Value

- Eliminate confusion about which compose files to use
- Reduce maintenance burden by removing duplication
- Ensure configuration consistency across environments
- Improve developer onboarding experience
- Establish clear workflow patterns

## Acceptance Criteria (Feature Level)

- All redundant compose files removed from repository
- All services start successfully using consolidated configuration
- Environment-specific configurations validate correctly
- No breaking changes to existing workflows
- All health checks pass after consolidation
- Documentation updated to reflect new structure

---

## User Stories

### Story 15.1: Backup Current Configuration

**As a** DevOps engineer
**I want** to create a complete backup of the current Docker configuration
**So that** I can quickly restore the previous state if issues arise during consolidation

**Acceptance Criteria:**

- Given I am starting the consolidation process, when I create the backup, then a new git branch named "backup/pre-docker-simplification-phase1" is created with all current files
- Given the backup branch is created, when I push it to the remote repository, then it is available for team members to access if rollback is needed
- Given I need local file backups, when I create the backup directory, then all compose files and environment files are copied to a timestamped backup directory
- Given backups are created, when I verify their completeness, then I can confirm all 10 compose files are preserved

**Dependencies:** None

**Agent:** devops-engineer

---

### Story 15.2: Identify Canonical Compose File

**As a** DevOps engineer
**I want** to compare docker-compose.yml and docker-compose.unified.yml to identify the authoritative version
**So that** I can preserve the correct configuration when removing duplicates

**Acceptance Criteria:**

- Given both compose files exist, when I compare their contents, then I can identify which file contains the most complete and up-to-date service definitions
- Given differences exist between the files, when I analyze them, then I can determine which differences are significant and must be preserved
- Given I've identified the canonical file, when I document my findings, then the team understands which file will be kept and why
- Given important differences exist, when I merge them into the canonical file, then all necessary configuration is preserved

**Dependencies:** Story 15.1 (backup must exist first)

**Agent:** devops-engineer

---

### Story 15.3: Validate Current Configuration Works

**As a** DevOps engineer
**I want** to verify that the current compose files successfully start all services
**So that** I have a known-good baseline before making changes

**Acceptance Criteria:**

- Given I am using the canonical compose file, when I start all services, then all containers start without errors
- Given all services are running, when I check their health status, then all health checks pass
- Given I am testing environment configurations, when I validate staging configuration, then the compose config command reports no errors
- Given I am testing environment configurations, when I validate production configuration, then the compose config command reports no errors

**Dependencies:** Story 15.2 (must know which file is canonical)

**Agent:** devops-engineer

---

### Story 15.4: Remove Root-Level Duplicate Compose File

**As a** DevOps engineer
**I want** to remove docker-compose.unified.yml from the root directory
**So that** there is only one base compose file to maintain

**Acceptance Criteria:**

- Given the canonical compose file is identified, when I remove docker-compose.unified.yml, then only docker-compose.yml remains at the root level
- Given the file is removed, when developers run standard compose commands, then they work exactly as before using docker-compose.yml
- Given the file is removed, when I search the codebase for references to docker-compose.unified.yml, then I can identify any documentation or scripts that need updating
- Given documentation references exist, when I update them, then all references point to docker-compose.yml

**Dependencies:** Story 15.3 (current config must be validated first)

**Agent:** devops-engineer

---

### Story 15.5: Remove Backend Compose Files

**As a** DevOps engineer
**I want** to remove backend/docker-compose.yml and backend/docker-compose.production.yml
**So that** backend container configuration is managed only from the root compose files

**Acceptance Criteria:**

- Given root compose files define the complete stack, when I remove backend/docker-compose.yml, then backend service configuration is still available in the root compose file
- Given I've removed backend-specific compose files, when I remove backend/docker-compose.production.yml, then backend production configuration is still available in compose.production.yml
- Given the files are removed, when I attempt to run compose commands from the backend directory, then the system uses the root-level compose files instead
- Given the files are removed, when I search for documentation or scripts referencing these files, then I can update them to reference root-level files

**Dependencies:** Story 15.4 (root-level cleanup must be complete first)

**Agent:** devops-engineer

---

### Story 15.6: Remove Frontend Compose Files

**As a** DevOps engineer
**I want** to remove frontend/docker-compose.yml and frontend/docker-compose.prod.yml
**So that** frontend container configuration is managed only from the root compose files

**Acceptance Criteria:**

- Given root compose files define the complete stack, when I remove frontend/docker-compose.yml, then frontend service configuration is still available in the root compose file
- Given I've removed frontend-specific compose files, when I remove frontend/docker-compose.prod.yml, then frontend production configuration is still available in compose.production.yml
- Given the files are removed, when I attempt to run compose commands from the frontend directory, then the system uses the root-level compose files instead
- Given the files are removed, when I search for documentation or scripts referencing these files, then I can update them to reference root-level files

**Dependencies:** Story 15.5 (backend cleanup must be complete first)

**Agent:** devops-engineer

---

### Story 15.7: Validate Consolidated Configuration

**As a** DevOps engineer
**I want** to verify that all services start successfully after consolidation
**So that** I can confirm no functionality was lost during cleanup

**Acceptance Criteria:**

- Given all redundant compose files are removed, when I run "docker compose up", then all services (database, cache, backend, frontend, proxy, worker) start without errors
- Given services are running, when I check their health status, then all health checks pass within expected timeframes
- Given I am testing environment-specific configurations, when I validate staging with "docker compose -f docker-compose.yml -f compose.staging.yml config", then no errors are reported
- Given I am testing environment-specific configurations, when I validate production with "docker compose -f docker-compose.yml -f compose.production.yml config", then no errors are reported

**Dependencies:** Story 15.6 (all file removal must be complete)

**Agent:** devops-engineer

---

### Story 15.8: Verify Service Functionality

**As a** developer
**I want** to confirm that all services function correctly after compose file consolidation
**So that** I know the application works end-to-end

**Acceptance Criteria:**

- Given all services are running, when I access the frontend application, then it loads successfully in the browser
- Given the frontend is loaded, when I interact with features that require backend API calls, then the requests succeed and return expected data
- Given the backend is running, when I access the API documentation endpoint, then it displays correctly
- Given the complete stack is running, when I test data persistence by creating and retrieving data, then all database operations succeed

**Dependencies:** Story 15.7 (consolidated config must be validated)

**Agent:** devops-engineer

---

### Story 15.9: Update Documentation

**As a** developer
**I want** clear documentation about the new compose file structure
**So that** I understand which files to use for different purposes

**Acceptance Criteria:**

- Given the consolidation is complete, when I read the project README, then it clearly states which compose files exist and their purposes
- Given I need to start the application locally, when I follow the documentation, then the instructions reference only existing compose files
- Given I need to deploy to staging or production, when I follow the documentation, then the commands use the correct compose file combinations
- Given I encounter issues, when I review the documentation, then rollback procedures are clearly documented with the backup branch name

**Dependencies:** Story 15.8 (verification must be complete)

**Agent:** devops-engineer

---

### Story 15.10: Communicate Changes to Team

**As a** team lead
**I want** to notify all team members about the compose file consolidation
**So that** everyone understands the new structure and knows how to get help if needed

**Acceptance Criteria:**

- Given the consolidation is complete, when I announce the changes, then team members know which compose files were removed and which remain
- Given team members need to update their local environments, when they read the announcement, then clear migration steps are provided
- Given team members encounter issues, when they need help, then they know how to access the backup configuration
- Given the changes affect workflows, when developers review their documentation, then they understand which commands to use going forward

**Dependencies:** Story 15.9 (documentation must be complete)

**Agent:** devops-engineer

---

## Execution Order

### Phase 1: Preparation (Sequential)
1. Story 15.1 - Backup Current Configuration
2. Story 15.2 - Identify Canonical Compose File
3. Story 15.3 - Validate Current Configuration Works

### Phase 2: File Removal (Sequential)
4. Story 15.4 - Remove Root-Level Duplicate Compose File
5. Story 15.5 - Remove Backend Compose Files
6. Story 15.6 - Remove Frontend Compose Files

### Phase 3: Validation (Sequential)
7. Story 15.7 - Validate Consolidated Configuration
8. Story 15.8 - Verify Service Functionality

### Phase 4: Documentation and Communication (Sequential)
9. Story 15.9 - Update Documentation
10. Story 15.10 - Communicate Changes to Team

---

## Story Quality Validation

### Atomicity Check
- All stories deliver one complete capability
- Each story can be completed independently
- No story contains "and" in its title
- Each story has 3-4 acceptance criteria maximum

### Generic & Implementation-Agnostic Check
- No framework or library mentions
- No specific technology stack requirements
- Stories describe WHAT users/operators need, not HOW
- Stories work regardless of underlying implementation
- All acceptance criteria are user-observable

### User-Focused Check
- All stories written from user perspective (As a... I want... So that...)
- All acceptance criteria use Given-When-Then pattern
- No technical implementation details
- Observable outcomes and behaviors only

---

## Risk Assessment

**Risk Level:** Medium

**Key Risks:**
- Existing workflows may reference removed compose files
- Team members may have local changes to removed files
- CI/CD pipelines may reference specific compose files

**Mitigation:**
- Complete backup created before any changes (Story 15.1)
- Validation at each step (Stories 15.3, 15.7, 15.8)
- Documentation updated before announcement (Story 15.9)
- Clear rollback procedure available

**Rollback Plan:**
- Restore from backup branch: `git checkout backup/pre-docker-simplification-phase1`
- Or restore individual files from timestamped backup directory

---

## Success Metrics

- 10 compose files → 5 compose files (50% reduction)
- Zero service startup failures after consolidation
- All environment configurations validate successfully
- All health checks pass
- Zero team member blockers during transition
- Clear, accurate documentation

---

## Notes

- This is Phase 1 of a larger Docker Simplification effort
- Phase 1 focuses ONLY on compose file consolidation
- Future phases will address:
  - Phase 2: Naming convention standardization
  - Phase 3: Environment file simplification
  - Phase 4: Helper script consolidation
  - Phase 5: CI/CD workflow optimization
- Changes are configuration-only, no code modifications required
