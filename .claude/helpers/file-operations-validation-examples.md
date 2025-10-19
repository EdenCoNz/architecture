# File Operations Validation - Integration Examples

## Purpose

This document provides comprehensive, real-world examples of integrating the file operations validation layer into commands and agents. Each example demonstrates complete workflows with validation at every step.

## Example 1: Implementing Feature Log Write in /feature Command

### Scenario

The `/feature` command needs to create or update the feature log when planning a new feature. This operation requires:
- Creating parent directory if needed
- Loading existing log (if exists)
- Validating new entry structure
- Writing updated log safely

### Complete Integration

```markdown
## Step X: Update Feature Log

1. Load file operations validation system:
   Read .claude/helpers/file-operations-validation.md

2. Construct feature log path:
   ```
   feature_log_path="/home/ed/Dev/architecture/docs/features/feature-log.json"
   ```

3. Validate parent directory exists (create if missing):
   ```bash
   # Using validateParentDirectoryExists
   parent_dir=$(dirname "${feature_log_path}")

   if [ ! -d "${parent_dir}" ]; then
     mkdir -p "${parent_dir}"
     echo "Created directory: ${parent_dir}"
   fi

   # Verify directory created
   if [ ! -d "${parent_dir}" ]; then
     echo "Error: Failed to create parent directory: ${parent_dir}"
     exit 1
   fi
   ```

4. Construct new feature entry with all required fields:
   ```json
   {
     "featureID": "6",
     "title": "Add User Authentication",
     "createdAt": "2025-10-19T12:00:00Z",
     "userStoriesCreated": null,
     "userStoriesImplemented": null,
     "isSummarised": false,
     "summarisedAt": null,
     "state": "planned",
     "stateHistory": [
       {
         "state": "planned",
         "timestamp": "2025-10-19T12:00:00Z",
         "triggeredBy": "/feature command",
         "notes": "Feature created via /feature command"
       }
     ],
     "actions": []
   }
   ```

5. Validate new entry against schema:
   - Required fields present: featureID, title, createdAt ✓
   - Optional fields have correct types ✓
   - Timestamps in ISO 8601 format ✓
   - State is valid enum value ✓
   - State history array properly structured ✓

6. Load existing feature log (if exists):
   ```bash
   if [ -f "${feature_log_path}" ]; then
     # Validate JSON syntax before parsing
     if ! python3 -c "import json; json.load(open('${feature_log_path}'))" 2>&1; then
       echo "Error: Existing feature log contains invalid JSON"
       echo "File: ${feature_log_path}"
       echo ""
       echo "Remediation:"
       echo "1. Open ${feature_log_path} in a text editor"
       echo "2. Fix the JSON syntax error"
       echo "3. Validate using: python3 -m json.tool ${feature_log_path}"
       echo "4. Or restore from backup if available"
       exit 1
     fi

     # Read and parse existing log
     existing_log=$(cat "${feature_log_path}")
   else
     # Initialize new log structure
     existing_log='{"features":[]}'
   fi
   ```

7. Merge new entry into feature log:
   ```bash
   # Parse existing log, append new feature, re-serialize
   updated_log=$(echo "${existing_log}" | python3 -c "
   import sys, json
   log = json.load(sys.stdin)
   new_feature = ${new_feature_json}
   log['features'].append(new_feature)
   print(json.dumps(log, indent=2))
   ")
   ```

8. Validate complete log before writing:
   ```bash
   # Validate JSON syntax of updated log
   if ! echo "${updated_log}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1; then
     echo "Error: Updated feature log contains invalid JSON"
     echo "File: ${feature_log_path}"
     echo ""
     echo "Remediation:"
     echo "1. Check feature entry construction in Step 4"
     echo "2. Verify merge logic in Step 7"
     echo "3. This is likely a bug in the command - report to developer"
     exit 1
   fi
   ```

9. Write feature log using Write tool:
   ```
   Use Write tool with:
   - file_path: ${feature_log_path}
   - content: ${updated_log}
   ```

10. Verify write succeeded:
    ```bash
    if [ ! -f "${feature_log_path}" ]; then
      echo "Error: Failed to write feature log"
      echo "File: ${feature_log_path}"
      exit 1
    fi

    # Validate written file has valid JSON
    if ! python3 -c "import json; json.load(open('${feature_log_path}'))" 2>&1; then
      echo "Error: Written feature log contains invalid JSON"
      echo "File: ${feature_log_path}"
      echo "This indicates a write operation failure"
      exit 1
    fi

    echo "✓ Feature log updated successfully: ${feature_log_path}"
    ```

### Error Handling Example

```
If validation fails at step 5 (invalid entry):

Error: Feature entry validation failed

Field: createdAt
Expected: ISO 8601 timestamp (YYYY-MM-DDTHH:mm:ssZ)
Actual: "2025-10-19" (missing time component)

Remediation:
1. Update feature entry to include complete timestamp:
   "createdAt": "2025-10-19T12:00:00Z"
2. Ensure all timestamps follow ISO 8601 format
3. Use current UTC time for creation timestamp
```

```
If validation fails at step 6 (corrupt existing log):

Error: Existing feature log contains invalid JSON

File: /home/ed/Dev/architecture/docs/features/feature-log.json
JSON Error: Unexpected token '}' at line 23

Remediation:
1. Open /home/ed/Dev/architecture/docs/features/feature-log.json in a text editor
2. Fix the JSON syntax error at line 23
3. Validate using: python3 -m json.tool /home/ed/Dev/architecture/docs/features/feature-log.json
4. Or restore from backup: docs/features/feature-log.json.backup
5. Then re-run /feature command
```

## Example 2: Implementing Implementation Log Write in Agents

### Scenario

After completing a story, an agent needs to record the implementation in the implementation log. This requires:
- Validating log entry structure
- Creating parent directory if needed
- Appending to existing log array
- Atomic write to prevent corruption

### Complete Integration

```markdown
## Final Step: Record Implementation

1. Load file operations validation system:
   Read .claude/helpers/file-operations-validation.md

2. Determine implementation log path:
   ```
   # For feature
   impl_log_path="/home/ed/Dev/architecture/docs/features/${feature_id}/implementation-log.json"

   # For bug
   impl_log_path="/home/ed/Dev/architecture/docs/features/${feature_id}/bugs/${bug_id}/implementation-log.json"
   ```

3. Construct implementation log entry:
   ```json
   {
     "storyNumber": 1,
     "storyTitle": "Create User Registration Form",
     "agent": "frontend-developer",
     "status": "completed",
     "completedAt": "2025-10-19T14:30:00Z",
     "filesCreated": [
       "src/components/auth/RegistrationForm.tsx",
       "src/components/auth/RegistrationForm.test.tsx"
     ],
     "filesModified": [
       "src/App.tsx",
       "src/routes/index.tsx"
     ],
     "actions": [
       "Created registration form component with Material UI TextField components",
       "Added form validation using React Hook Form",
       "Implemented password strength indicator",
       "Added comprehensive unit tests covering validation logic"
     ],
     "toolsUsed": ["Write", "Read", "Edit", "Bash"],
     "issuesEncountered": [],
     "notes": "Component follows Material UI best practices and includes accessibility features"
   }
   ```

4. Validate log entry against schema:
   - Required fields present: storyNumber, storyTitle, agent, status, completedAt ✓
   - storyNumber is number and >= 1 ✓
   - agent is valid enum value ✓
   - status is valid enum value ✓
   - completedAt is ISO 8601 timestamp ✓
   - Arrays have correct types ✓

5. Validate entry using high-level validator:
   ```
   validateImplementationLogEntry(
     log_entry=${constructed_entry},
     file_path="${impl_log_path}"
   )

   If validation fails:
   - Display error message with specific violations
   - List missing required fields
   - Show type mismatches
   - STOP execution immediately
   ```

6. Validate parent directory exists (create if needed):
   ```bash
   parent_dir=$(dirname "${impl_log_path}")

   if [ ! -d "${parent_dir}" ]; then
     mkdir -p "${parent_dir}"
     echo "Created directory: ${parent_dir}"
   fi
   ```

7. Load existing implementation log (if exists):
   ```bash
   if [ -f "${impl_log_path}" ]; then
     # Validate JSON syntax
     if ! python3 -c "import json; json.load(open('${impl_log_path}'))" 2>&1; then
       echo "Error: Existing implementation log contains invalid JSON"
       echo "File: ${impl_log_path}"
       echo ""
       echo "Remediation:"
       echo "1. Fix JSON syntax in ${impl_log_path}"
       echo "2. Validate using: python3 -m json.tool ${impl_log_path}"
       echo "3. Or delete file to start fresh (will lose history)"
       exit 1
     fi

     # Read existing log
     existing_log=$(cat "${impl_log_path}")
   else
     # Initialize new log as empty array
     existing_log='[]'
   fi
   ```

8. Append new entry to log array:
   ```bash
   updated_log=$(echo "${existing_log}" | python3 -c "
   import sys, json
   log = json.load(sys.stdin)
   new_entry = ${log_entry_json}
   log.append(new_entry)
   print(json.dumps(log, indent=2))
   ")
   ```

9. Validate complete log before writing:
   ```bash
   if ! echo "${updated_log}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1; then
     echo "Error: Updated implementation log contains invalid JSON"
     echo "File: ${impl_log_path}"
     exit 1
   fi
   ```

10. Write implementation log atomically:
    ```
    Use Write tool with:
    - file_path: ${impl_log_path}
    - content: ${updated_log}
    ```

11. Verify write succeeded:
    ```bash
    if [ ! -f "${impl_log_path}" ]; then
      echo "Error: Failed to write implementation log"
      exit 1
    fi

    # Validate written file
    if ! python3 -c "import json; json.load(open('${impl_log_path}'))" 2>&1; then
      echo "Error: Written implementation log contains invalid JSON"
      exit 1
    fi

    echo "✓ Implementation recorded: ${impl_log_path}"
    ```

### Error Handling Example

```
If validation fails at step 4 (invalid entry):

Error: Implementation log entry validation failed

Field: agent
Expected: One of [backend-developer, frontend-developer, devops-engineer, ui-ux-designer, meta-developer, product-owner]
Actual: "frontend-dev"

Field: storyNumber
Expected: Number >= 1
Actual: "1" (string instead of number)

Remediation:
1. Fix agent field - use exact agent name from enum
2. Fix storyNumber type - use number not string
3. Review entry construction in agent workflow
4. Ensure all required fields present with correct types
```

## Example 3: Implementing Git Commit in /commit Command

### Scenario

The `/commit` command needs to safely create a git commit with validation to prevent common issues like detached HEAD, committing sensitive files, or committing to main.

### Complete Integration

```markdown
## Step 1: Validate Git State Before Commit

1. Load file operations validation system:
   Read .claude/helpers/file-operations-validation.md

2. Validate git repository exists:
   ```bash
   if [ ! -d ".git" ]; then
     echo "Error: Not a git repository"
     echo ""
     echo "Check: Git repository existence"
     echo "Status: No .git/ directory found"
     echo ""
     echo "Remediation:"
     echo "1. Navigate to your git repository directory"
     echo "2. If this is a new project, initialize git:"
     echo "   git init"
     echo "3. Verify you are in the correct directory:"
     echo "   pwd"
     exit 1
   fi
   ```

3. Validate working tree has changes:
   ```bash
   git_status=$(git status --porcelain)

   if [ -z "${git_status}" ]; then
     echo "Error: No changes to commit"
     echo ""
     echo "Check: Working directory modifications"
     echo "Status: Working tree is clean (no modifications)"
     echo ""
     echo "Remediation:"
     echo "1. Make changes to files before committing"
     echo "2. Verify you are in the correct directory"
     echo "3. Check git status:"
     echo "   git status"
     exit 1
   fi
   ```

4. Validate not in detached HEAD state:
   ```bash
   current_branch=$(git rev-parse --abbrev-ref HEAD)

   if [ "${current_branch}" = "HEAD" ]; then
     echo "Error: Repository is in detached HEAD state"
     echo ""
     echo "Check: Git HEAD reference"
     echo "Status: HEAD is detached"
     echo ""
     echo "Remediation:"
     echo "1. Checkout a branch to reattach HEAD:"
     echo "   git checkout main"
     echo "   OR"
     echo "   git checkout -b feature/new-feature"
     echo "2. If you want to keep changes, create a new branch first"
     exit 1
   fi
   ```

5. Check if committing to main (warning):
   ```bash
   if [ "${current_branch}" = "main" ] || [ "${current_branch}" = "master" ]; then
     echo "Warning: Committing directly to main branch"
     echo ""
     echo "Status: Current branch '${current_branch}' is main/master"
     echo ""
     echo "Recommendation:"
     echo "1. Feature implementations typically use feature branches:"
     echo "   git checkout -b feature/{feature-name}"
     echo "2. You may continue on current branch at your own risk"
     echo ""
     echo "Continuing with commit..."
   fi
   ```

6. Check for sensitive files in changes:
   ```bash
   # Get list of files to be committed
   files_to_commit=$(echo "${git_status}" | awk '{print $2}')

   # Check for sensitive file patterns
   sensitive_files=""
   for file in ${files_to_commit}; do
     case "${file}" in
       .env|.env.*|*credentials*|*secrets*|*password*|*.pem|*.key|*.p12)
         sensitive_files="${sensitive_files}${file}\n"
         ;;
     esac
   done

   if [ -n "${sensitive_files}" ]; then
     echo "Warning: Attempting to commit potentially sensitive files"
     echo ""
     echo "Detected sensitive file(s):"
     echo -e "${sensitive_files}"
     echo ""
     echo "Impact:"
     echo "These files may contain secrets, passwords, or API keys that"
     echo "should not be in version control."
     echo ""
     echo "Remediation:"
     echo "1. Remove sensitive files from staging:"
     echo "   git reset HEAD .env"
     echo "2. Add to .gitignore:"
     echo "   echo '.env' >> .gitignore"
     echo "3. Store sensitive values in environment variables"
     echo "4. Commit .gitignore changes:"
     echo "   git add .gitignore"
     echo "   git commit -m 'Add sensitive files to gitignore'"
     echo ""
     echo "If you are certain these files should be committed,"
     echo "you may continue at your own risk."
     echo ""
     read -p "Continue with commit? (y/N) " -n 1 -r
     echo
     if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       echo "Commit cancelled"
       exit 1
     fi
   fi
   ```

7. If all validations pass, proceed with commit:
   ```bash
   echo "✓ Git validation passed - proceeding with commit"
   echo ""
   echo "Validation Summary:"
   echo "  ✓ Git repository validated"
   echo "  ✓ Working tree has changes"
   echo "  ✓ Not in detached HEAD state"
   echo "  ✓ Current branch: ${current_branch}"
   if [ -n "${sensitive_files}" ]; then
     echo "  ⚠ Sensitive files detected (user confirmed)"
   fi
   echo ""
   ```

## Step 2: Execute Commit

8. Stage all changes:
   ```bash
   git add .
   ```

9. Create commit with provided message:
   ```bash
   git commit -m "${commit_message}"
   ```

10. Verify commit created:
    ```bash
    if [ $? -ne 0 ]; then
      echo "Error: Commit failed"
      exit 1
    fi

    echo "✓ Commit created successfully"
    git log -1 --oneline
    ```

11. If push flag provided, push to remote:
    ```bash
    if [ "${push_flag}" = "true" ]; then
      git push

      if [ $? -ne 0 ]; then
        echo "Warning: Push failed"
        echo "Commit created locally but not pushed to remote"
        echo "You may need to set upstream branch:"
        echo "  git push -u origin ${current_branch}"
      else
        echo "✓ Changes pushed to remote"
      fi
    fi
    ```
```

### Error Handling Examples

```
Scenario 1: Detached HEAD detected

Error: Repository is in detached HEAD state

Check: Git HEAD reference
Status: HEAD is detached at commit abc1234

Remediation:
1. Checkout a branch to reattach HEAD:
   git checkout main
   OR
   git checkout -b feature/new-feature
2. If you want to keep changes, create a new branch first

→ Execution stops immediately, no commit attempted
```

```
Scenario 2: No changes to commit

Error: No changes to commit

Check: Working directory modifications
Status: Working tree is clean (no modifications)

Remediation:
1. Make changes to files before committing
2. Verify you are in the correct directory
3. Check git status:
   git status

→ Execution stops immediately
```

```
Scenario 3: Sensitive files detected (warning)

Warning: Attempting to commit potentially sensitive files

Detected sensitive file(s):
  .env
  backend/credentials.json

Impact:
These files may contain secrets, passwords, or API keys that
should not be in version control.

Remediation:
1. Remove sensitive files from staging:
   git reset HEAD .env backend/credentials.json
2. Add to .gitignore:
   echo '.env' >> .gitignore
   echo 'credentials.json' >> .gitignore
3. Store sensitive values in environment variables

If you are certain these files should be committed,
you may continue at your own risk.

Continue with commit? (y/N) n
Commit cancelled

→ User can choose to cancel or continue
```

## Example 4: Implementing Safe File Overwrite with Backup

### Scenario

When updating an existing configuration file (like feature-log.json), create a backup before overwriting to enable recovery if something goes wrong.

### Complete Integration

```markdown
## Step X: Update Configuration File Safely

1. Load file operations validation system:
   Read .claude/helpers/file-operations-validation.md

2. Define file path:
   ```
   config_file="/home/ed/Dev/architecture/docs/features/feature-log.json"
   ```

3. Validate file exists:
   ```bash
   if [ ! -f "${config_file}" ]; then
     echo "Error: Configuration file not found"
     echo "File: ${config_file}"
     exit 1
   fi
   ```

4. Validate file is readable:
   ```bash
   if [ ! -r "${config_file}" ]; then
     echo "Error: Cannot read configuration file"
     echo "File: ${config_file}"
     echo "Permissions: $(ls -la ${config_file})"
     echo ""
     echo "Remediation:"
     echo "1. Check file permissions"
     echo "2. Update permissions:"
     echo "   chmod 644 ${config_file}"
     exit 1
   fi
   ```

5. Create backup with timestamp:
   ```bash
   timestamp=$(date +%Y%m%d_%H%M%S)
   backup_file="${config_file}.backup.${timestamp}"

   cp "${config_file}" "${backup_file}"

   if [ ! -f "${backup_file}" ]; then
     echo "Error: Failed to create backup"
     echo "Original: ${config_file}"
     echo "Backup: ${backup_file}"
     exit 1
   fi

   echo "✓ Backup created: ${backup_file}"
   ```

6. Verify backup matches original:
   ```bash
   if ! diff "${config_file}" "${backup_file}" > /dev/null; then
     echo "Error: Backup does not match original"
     echo "This should not happen - investigation required"
     exit 1
   fi
   ```

7. Read and validate existing file:
   ```bash
   existing_content=$(cat "${config_file}")

   if ! echo "${existing_content}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1; then
     echo "Error: Existing file contains invalid JSON"
     echo "File: ${config_file}"
     echo "Backup preserved at: ${backup_file}"
     exit 1
   fi
   ```

8. Construct updated content:
   ```
   # Perform modifications to existing_content
   updated_content=...
   ```

9. Validate updated content:
   ```bash
   if ! echo "${updated_content}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1; then
     echo "Error: Updated content contains invalid JSON"
     echo "File: ${config_file}"
     echo "Backup preserved at: ${backup_file}"
     echo "Original file not modified"
     exit 1
   fi
   ```

10. Write updated content:
    ```
    Use Write tool with:
    - file_path: ${config_file}
    - content: ${updated_content}
    ```

11. Verify write succeeded:
    ```bash
    if [ ! -f "${config_file}" ]; then
      echo "Error: File disappeared after write"
      echo "Restoring from backup..."
      cp "${backup_file}" "${config_file}"
      exit 1
    fi

    # Validate written file
    written_content=$(cat "${config_file}")
    if ! echo "${written_content}" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1; then
      echo "Error: Written file contains invalid JSON"
      echo "Restoring from backup..."
      cp "${backup_file}" "${config_file}"
      exit 1
    fi

    # Verify content matches expected
    if [ "${written_content}" != "${updated_content}" ]; then
      echo "Warning: Written content does not match expected"
      echo "Restoring from backup..."
      cp "${backup_file}" "${config_file}"
      exit 1
    fi

    echo "✓ File updated successfully: ${config_file}"
    echo "✓ Backup available at: ${backup_file}"
    ```

12. Optionally clean up old backups:
    ```bash
    # Keep only 5 most recent backups
    backup_dir=$(dirname "${config_file}")
    backup_base=$(basename "${config_file}")

    ls -t "${backup_dir}/${backup_base}.backup."* 2>/dev/null | tail -n +6 | xargs rm -f
    echo "✓ Old backups cleaned up (keeping 5 most recent)"
    ```
```

### Recovery Example

```
If write fails and restore from backup is needed:

Error: Written file contains invalid JSON

Restoring from backup...
✓ Restored from: /home/ed/Dev/architecture/docs/features/feature-log.json.backup.20251019_143000

Analysis:
- Original file preserved in backup
- Invalid write detected before accepting
- Automatic restore prevented data loss
- User can investigate issue and retry
```

## Example 5: Creating Feature Directory Structure

### Scenario

When planning a new feature, create the complete directory structure with all required files.

### Complete Integration

```markdown
## Step X: Create Feature Directory Structure

1. Load file operations validation system:
   Read .claude/helpers/file-operations-validation.md

2. Determine feature ID:
   ```
   feature_id="6"
   ```

3. Validate features parent directory exists:
   ```bash
   features_dir="/home/ed/Dev/architecture/docs/features"

   if [ ! -d "${features_dir}" ]; then
     echo "Error: Features directory not found"
     echo "Directory: ${features_dir}"
     echo ""
     echo "Remediation:"
     echo "1. Create features directory:"
     echo "   mkdir -p ${features_dir}"
     exit 1
   fi
   ```

4. Construct feature directory path:
   ```
   feature_dir="${features_dir}/${feature_id}"
   ```

5. Validate feature directory doesn't already exist:
   ```bash
   if [ -d "${feature_dir}" ]; then
     echo "Warning: Feature directory already exists"
     echo "Directory: ${feature_dir}"
     echo ""
     echo "This may indicate feature ${feature_id} was already created."
     echo "Check feature log to verify."
     echo ""
     read -p "Continue anyway? (y/N) " -n 1 -r
     echo
     if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       echo "Directory creation cancelled"
       exit 1
     fi
   fi
   ```

6. Create feature directory:
   ```bash
   mkdir -p "${feature_dir}"

   if [ ! -d "${feature_dir}" ]; then
     echo "Error: Failed to create feature directory"
     echo "Directory: ${feature_dir}"
     exit 1
   fi

   echo "✓ Created directory: ${feature_dir}"
   ```

7. Create subdirectories:
   ```bash
   subdirs=("research" "design" "bugs")

   for subdir in "${subdirs[@]}"; do
     subdir_path="${feature_dir}/${subdir}"
     mkdir -p "${subdir_path}"

     if [ ! -d "${subdir_path}" ]; then
       echo "Error: Failed to create subdirectory: ${subdir_path}"
       exit 1
     fi

     echo "✓ Created subdirectory: ${subdir}"
   done
   ```

8. Create placeholder user-stories.md:
   ```bash
   user_stories_path="${feature_dir}/user-stories.md"

   # Validate parent directory exists (should exist from step 6)
   if [ ! -d "${feature_dir}" ]; then
     echo "Error: Feature directory missing"
     exit 1
   fi

   # Create placeholder content
   user_stories_content="# Feature ${feature_id}: ${feature_title}

## Execution Order

[To be populated by product owner]

## User Stories

[To be populated by product owner]
"

   # Write user stories file
   echo "${user_stories_content}" > "${user_stories_path}"

   if [ ! -f "${user_stories_path}" ]; then
     echo "Error: Failed to create user stories file"
     echo "File: ${user_stories_path}"
     exit 1
   fi

   echo "✓ Created user stories placeholder: ${user_stories_path}"
   ```

9. Verify directory structure:
   ```bash
   echo ""
   echo "Feature directory structure:"
   tree -L 2 "${feature_dir}"

   # Or without tree command:
   find "${feature_dir}" -maxdepth 2 -type d | sort
   ```

10. Report created structure:
    ```
    ✓ Feature directory structure created successfully

    Directory: /home/ed/Dev/architecture/docs/features/6

    Structure:
      /home/ed/Dev/architecture/docs/features/6/
      /home/ed/Dev/architecture/docs/features/6/research/
      /home/ed/Dev/architecture/docs/features/6/design/
      /home/ed/Dev/architecture/docs/features/6/bugs/
      /home/ed/Dev/architecture/docs/features/6/user-stories.md

    Next Steps:
    1. Product owner will populate user stories
    2. Implementation will begin after stories approved
    ```
```

## Best Practices Summary

### 1. Always Validate Before Operating

- Never write files without validating parent directory exists
- Never parse JSON without validating syntax first
- Never commit without validating git state
- Fail fast on validation errors

### 2. Provide Clear Error Messages

- Include file paths in all error messages
- Show current vs expected values
- Provide specific remediation steps
- Include command examples for fixes

### 3. Use Atomic Operations

- Validate complete data structure before writing
- Write entire file at once (not incremental)
- Verify write succeeded before proceeding
- Create backups for critical file overwrites

### 4. Handle Edge Cases

- File doesn't exist (first run scenarios)
- Directory doesn't exist (create with mkdir -p)
- File exists but is invalid (offer remediation)
- Permissions issues (show ls -la output)

### 5. Maintain Consistency

- Always use absolute paths
- Always validate within project root
- Always use ISO 8601 timestamps
- Always validate JSON syntax before and after writes

## Quick Integration Checklist

Before writing any file:
- [ ] Validate parent directory exists (create if needed)
- [ ] Construct complete data structure
- [ ] Validate data structure (JSON syntax + schema)
- [ ] Load existing file if appending (validate first)
- [ ] Merge/append new data
- [ ] Validate complete updated data
- [ ] Write file
- [ ] Verify write succeeded
- [ ] Validate written file

Before reading any file:
- [ ] Validate path exists
- [ ] Validate path is accessible (read permission)
- [ ] Validate path is within project root
- [ ] Read file
- [ ] Validate content (JSON syntax if JSON)
- [ ] Parse and use data

Before git operations:
- [ ] Validate git repository exists
- [ ] Validate working tree state appropriate for operation
- [ ] Validate branch state (not detached HEAD, correct branch)
- [ ] Check for sensitive files (if committing)
- [ ] Execute git operation
- [ ] Verify operation succeeded

## Version History

- v1.0.0 (2025-10-19): Initial integration examples
  - Feature log write example
  - Implementation log write example
  - Git commit validation example
  - Safe file overwrite example
  - Directory structure creation example
  - Best practices and checklists
