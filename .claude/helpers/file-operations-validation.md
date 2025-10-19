# File Operations Validation Layer

## Purpose

This validation layer provides comprehensive, reusable validation functions for file operations across all commands and agents. It verifies file paths exist and are accessible, validates data structure before writes to prevent corruption, and checks git status before destructive operations.

Unlike the pre-flight validation system (which validates command prerequisites), this layer focuses on **safe file operations** during command execution, preventing partial failures and data corruption through proactive validation.

## Design Principles

1. **Validate Before Operating**: All file operations validated before execution
2. **Prevent Data Corruption**: Validate data structure before writing configuration files
3. **Clear Error Messages**: Specific error messages with file paths and expected structure
4. **Git Safety**: Check git status before commits, branch operations, and destructive changes
5. **Non-Blocking Options**: Support for optional validation with warnings vs hard failures
6. **Reusable Functions**: Modular validation functions usable across entire codebase

## Validation Categories

### 1. File Path Validation

Verify file paths exist and are accessible before file operations.

#### validatePathExists

**Purpose**: Confirm a file or directory path exists before attempting read/write operations.

**Input**:
- `path`: Absolute path to file or directory
- `type`: "file" | "directory" | "any" (default: "any")
- `purpose`: Optional description of what this path is for (improves error messages)

**Process**:
```bash
# For file validation
test -f "{path}" && echo "EXISTS" || echo "NOT_FOUND"

# For directory validation
test -d "{path}" && echo "EXISTS" || echo "NOT_FOUND"

# For any path validation
test -e "{path}" && echo "EXISTS" || echo "NOT_FOUND"
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message if validation fails (null otherwise)
- `resolved_path`: Absolute path if validation passes (null otherwise)

**Error Message Format**:
```
Error: Path not found

Path: {path}
Type: {expected type}
Purpose: {purpose if provided}

Remediation:
1. Verify the path is correct: {path}
2. Check parent directory exists:
   ls -la {parent_directory}
3. {type-specific remediation}

For file: Ensure file has been created before attempting to read
For directory: Create directory first with: mkdir -p {path}
```

**Example Usage**:
```javascript
// Validate feature log exists before reading
validatePathExists(
  path="/home/ed/Dev/architecture/docs/features/feature-log.json",
  type="file",
  purpose="Feature log containing all feature metadata"
)
→ { validation_result: "pass", error_message: null, resolved_path: "/home/ed/Dev/architecture/docs/features/feature-log.json" }

// Validate directory exists before writing file
validatePathExists(
  path="/home/ed/Dev/architecture/docs/features/5",
  type="directory",
  purpose="Feature #5 directory"
)
→ { validation_result: "fail", error_message: "Error: Path not found..." }
```

#### validatePathAccessible

**Purpose**: Confirm a path is accessible with required permissions before operations.

**Input**:
- `path`: Absolute path to file or directory
- `permission`: "read" | "write" | "execute" | "readwrite"
- `purpose`: Optional description

**Process**:
```bash
# For read permission
test -r "{path}" && echo "ACCESSIBLE" || echo "NOT_ACCESSIBLE"

# For write permission
test -w "{path}" && echo "ACCESSIBLE" || echo "NOT_ACCESSIBLE"

# For execute permission
test -x "{path}" && echo "ACCESSIBLE" || echo "NOT_ACCESSIBLE"

# For readwrite permission
test -r "{path}" && test -w "{path}" && echo "ACCESSIBLE" || echo "NOT_ACCESSIBLE"
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message if validation fails
- `actual_permissions`: Octal permission string (e.g., "644") if path exists

**Error Message Format**:
```
Error: Insufficient permissions

Path: {path}
Required: {permission}
Current: {actual_permissions}
Purpose: {purpose if provided}

Remediation:
1. Check current permissions:
   ls -la {path}
2. Update permissions if needed:
   chmod {suggested_permissions} {path}
3. Verify you have ownership:
   ls -la {parent_directory} | grep {filename}
```

**Example Usage**:
```javascript
// Validate can write to implementation log
validatePathAccessible(
  path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json",
  permission="write",
  purpose="Implementation log for Feature #5"
)
→ { validation_result: "pass", error_message: null, actual_permissions: "644" }
```

#### validatePathInProjectRoot

**Purpose**: Confirm a path is within the project root directory to prevent operations outside project.

**Input**:
- `path`: Absolute path to validate
- `project_root`: Project root directory (default: current git repository root)
- `purpose`: Optional description

**Process**:
```bash
# Get git repository root
git_root=$(git rev-parse --show-toplevel 2>/dev/null)

# Check if path starts with git root
echo "{path}" | grep -q "^${git_root}" && echo "INSIDE_PROJECT" || echo "OUTSIDE_PROJECT"
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message if validation fails
- `project_root`: Detected project root path

**Error Message Format**:
```
Error: Path outside project root

Path: {path}
Project Root: {project_root}
Purpose: {purpose if provided}

Remediation:
1. Verify you are operating on correct path
2. Project root is: {project_root}
3. All file operations must be within project root
4. Check for absolute vs relative path issues
```

**Example Usage**:
```javascript
// Validate path is within project before creating file
validatePathInProjectRoot(
  path="/home/ed/Dev/architecture/docs/features/5/user-stories.md",
  project_root="/home/ed/Dev/architecture",
  purpose="User stories file for Feature #5"
)
→ { validation_result: "pass", error_message: null, project_root: "/home/ed/Dev/architecture" }
```

#### validateParentDirectoryExists

**Purpose**: Confirm parent directory exists before creating files to prevent "No such file or directory" errors.

**Input**:
- `file_path`: Absolute path to file (not directory)
- `create_if_missing`: Boolean - auto-create parent directory if missing (default: false)
- `purpose`: Optional description

**Process**:
```bash
# Extract parent directory
parent_dir=$(dirname "{file_path}")

# Check if parent directory exists
test -d "${parent_dir}" && echo "EXISTS" || echo "NOT_FOUND"

# If create_if_missing=true and not exists
if [ ! -d "${parent_dir}" ]; then
  mkdir -p "${parent_dir}"
  echo "CREATED"
fi
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message if validation fails
- `parent_directory`: Parent directory path
- `action_taken`: "none" | "created" (if create_if_missing=true)

**Error Message Format**:
```
Error: Parent directory does not exist

File Path: {file_path}
Parent Directory: {parent_directory}
Purpose: {purpose if provided}

Remediation:
1. Create parent directory first:
   mkdir -p {parent_directory}
2. Verify parent directory created:
   ls -la {grandparent_directory}
3. Then create the file
```

**Example Usage**:
```javascript
// Validate parent exists before writing user stories
validateParentDirectoryExists(
  file_path="/home/ed/Dev/architecture/docs/features/6/user-stories.md",
  create_if_missing=false,
  purpose="User stories file for Feature #6"
)
→ { validation_result: "fail", error_message: "Error: Parent directory does not exist...", parent_directory: "/home/ed/Dev/architecture/docs/features/6", action_taken: "none" }

// Auto-create parent if missing
validateParentDirectoryExists(
  file_path="/home/ed/Dev/architecture/docs/features/6/user-stories.md",
  create_if_missing=true,
  purpose="User stories file for Feature #6"
)
→ { validation_result: "pass", error_message: null, parent_directory: "/home/ed/Dev/architecture/docs/features/6", action_taken: "created" }
```

### 2. Data Structure Validation

Validate data structure before writing to prevent corrupting configuration files.

#### validateJSONSyntax

**Purpose**: Validate JSON syntax before writing JSON files to prevent corruption.

**Input**:
- `json_string`: JSON string to validate
- `file_path`: Path where JSON will be written (for error messages)
- `purpose`: Optional description of what this JSON contains

**Process**:
```bash
# Use Python to validate JSON syntax
echo '{json_string}' | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message with line/column if validation fails
- `parsed_data`: Parsed JSON object if validation passes (null otherwise)

**Error Message Format**:
```
Error: Invalid JSON syntax

File: {file_path}
Purpose: {purpose if provided}
JSON Error: {specific error from python}
Line: {line_number}
Column: {column_number}

Remediation:
1. Review the JSON structure for syntax errors
2. Common issues:
   - Missing or extra commas
   - Unclosed brackets/braces
   - Invalid quotes (must use double quotes "")
   - Trailing commas in arrays/objects
3. Validate JSON using: echo '{json_string}' | python3 -m json.tool
4. Use online validator: jsonlint.com

Expected JSON structure:
{example structure if available}
```

**Example Usage**:
```javascript
// Validate implementation log entry before writing
const logEntry = JSON.stringify({
  storyNumber: 1,
  storyTitle: "Create User Interface",
  agent: "frontend-developer",
  status: "completed",
  completedAt: "2025-10-19T12:00:00Z"
});

validateJSONSyntax(
  json_string=logEntry,
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json",
  purpose="Implementation log entry for Story #1"
)
→ { validation_result: "pass", error_message: null, parsed_data: {...} }

// Detect invalid JSON
const invalidJSON = '{ "key": "value", }'; // Trailing comma
validateJSONSyntax(
  json_string=invalidJSON,
  file_path="/home/ed/Dev/architecture/test.json",
  purpose="Test file"
)
→ { validation_result: "fail", error_message: "Error: Invalid JSON syntax... Trailing comma...", parsed_data: null }
```

#### validateJSONSchema

**Purpose**: Validate JSON matches expected schema before writing to ensure data integrity.

**Input**:
- `json_data`: Parsed JSON object (not string)
- `schema_requirements`: Object describing required fields and types
- `file_path`: Path where JSON will be written
- `purpose`: Optional description

**Process**:
```javascript
// Pseudo-code for schema validation
for each field in schema_requirements:
  if field.required and not exists in json_data:
    validation fails - missing required field

  if field.type and json_data[field.name] type != field.type:
    validation fails - wrong type

  if field.pattern and json_data[field.name] doesn't match pattern:
    validation fails - pattern mismatch

  if field.enum and json_data[field.name] not in enum:
    validation fails - invalid enum value
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message listing all schema violations
- `missing_fields`: Array of missing required fields
- `type_errors`: Array of type mismatches
- `pattern_errors`: Array of pattern violations

**Error Message Format**:
```
Error: JSON schema validation failed

File: {file_path}
Purpose: {purpose if provided}

Schema Violations:
{for each violation:}
  - {field_name}: {violation description}
    Expected: {expected value/type/pattern}
    Actual: {actual value/type}

Required Fields:
{list of required fields from schema}

Remediation:
1. Review the schema requirements above
2. Add missing required fields
3. Fix type mismatches
4. Ensure values match expected patterns
5. Validate data before calling write operation
```

**Schema Requirements Format**:
```javascript
{
  "field_name": {
    "required": true|false,
    "type": "string"|"number"|"boolean"|"array"|"object",
    "pattern": "regex pattern for strings",
    "enum": ["value1", "value2"], // for enums
    "min": 0, // for numbers
    "max": 100, // for numbers
    "items": {...}, // for arrays (schema for items)
    "properties": {...} // for objects (nested schema)
  }
}
```

**Example Usage**:
```javascript
// Define implementation log entry schema
const implementationLogSchema = {
  storyNumber: { required: true, type: "number", min: 1 },
  storyTitle: { required: true, type: "string" },
  agent: { required: true, type: "string", enum: ["backend-developer", "frontend-developer", "devops-engineer", "ui-ux-designer", "meta-developer", "product-owner"] },
  status: { required: true, type: "string", enum: ["completed", "partial", "blocked", "failed"] },
  completedAt: { required: true, type: "string", pattern: "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$" },
  filesModified: { required: false, type: "array" },
  filesCreated: { required: false, type: "array" }
};

// Validate entry against schema
const logEntry = {
  storyNumber: 1,
  storyTitle: "Create User Interface",
  agent: "frontend-developer",
  status: "completed",
  completedAt: "2025-10-19T12:00:00Z",
  filesCreated: ["src/App.tsx"]
};

validateJSONSchema(
  json_data=logEntry,
  schema_requirements=implementationLogSchema,
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json",
  purpose="Implementation log entry"
)
→ { validation_result: "pass", error_message: null, missing_fields: [], type_errors: [], pattern_errors: [] }

// Detect schema violations
const invalidEntry = {
  storyNumber: "one", // Wrong type (string instead of number)
  storyTitle: "Create UI",
  agent: "invalid-agent", // Not in enum
  status: "completed"
  // Missing required field: completedAt
};

validateJSONSchema(
  json_data=invalidEntry,
  schema_requirements=implementationLogSchema,
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json",
  purpose="Implementation log entry"
)
→ {
  validation_result: "fail",
  error_message: "Error: JSON schema validation failed...",
  missing_fields: ["completedAt"],
  type_errors: [{ field: "storyNumber", expected: "number", actual: "string" }],
  pattern_errors: [{ field: "agent", expected: "one of [backend-developer, ...]", actual: "invalid-agent" }]
}
```

#### validateFeatureLogEntry

**Purpose**: High-level validation for feature log entries with complete schema checking.

**Input**:
- `feature_entry`: Parsed feature object
- `file_path`: Path to feature log (for error messages)

**Process**:
1. Validate JSON syntax (if string provided)
2. Validate against feature log schema:
   - Required fields: featureID, title, createdAt
   - Optional fields: userStoriesCreated, userStoriesImplemented, isSummarised, summarisedAt, state, stateHistory, actions
   - Type validation for all fields
   - Timestamp format validation (ISO 8601)
   - State enum validation if state field present
   - State history structure validation if stateHistory field present

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Detailed error message with all violations
- `validated_entry`: Entry with defaults filled in if validation passes

**Example Usage**:
```javascript
// Validate new feature entry
const newFeature = {
  featureID: "6",
  title: "Add User Authentication",
  createdAt: "2025-10-19T12:00:00Z",
  userStoriesCreated: null,
  userStoriesImplemented: null,
  isSummarised: false,
  summarisedAt: null,
  state: "planned",
  stateHistory: [
    {
      state: "planned",
      timestamp: "2025-10-19T12:00:00Z",
      triggeredBy: "/feature command",
      notes: "Feature created"
    }
  ],
  actions: []
};

validateFeatureLogEntry(
  feature_entry=newFeature,
  file_path="/home/ed/Dev/architecture/docs/features/feature-log.json"
)
→ { validation_result: "pass", error_message: null, validated_entry: {...} }
```

#### validateImplementationLogEntry

**Purpose**: High-level validation for implementation log entries with complete schema checking.

**Input**:
- `log_entry`: Parsed implementation log entry object
- `file_path`: Path to implementation log (for error messages)

**Process**:
1. Validate JSON syntax (if string provided)
2. Validate against implementation log schema:
   - Required fields: storyNumber, storyTitle, agent, status, completedAt
   - Optional fields: filesModified, filesCreated, actions, toolsUsed, issuesEncountered, notes, error (for failed stories)
   - Type validation for all fields
   - Agent enum validation
   - Status enum validation
   - Timestamp format validation

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Detailed error message with all violations
- `validated_entry`: Entry with defaults filled in if validation passes

**Example Usage**:
```javascript
// Validate implementation log entry
const logEntry = {
  storyNumber: 1,
  storyTitle: "Create User Interface",
  agent: "frontend-developer",
  status: "completed",
  completedAt: "2025-10-19T12:00:00Z",
  filesCreated: ["src/App.tsx", "src/App.test.tsx"],
  filesModified: [],
  actions: ["Created React component", "Added tests"],
  toolsUsed: ["Write", "Read"],
  issuesEncountered: [],
  notes: "Component follows Material UI patterns"
};

validateImplementationLogEntry(
  log_entry=logEntry,
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json"
)
→ { validation_result: "pass", error_message: null, validated_entry: {...} }
```

### 3. Git Status Validation

Check git repository status before destructive operations to prevent conflicts and data loss.

#### validateGitWorkingTreeClean

**Purpose**: Verify working tree is clean before operations that require clean state (e.g., branch switching, pulling).

**Input**:
- `allow_untracked`: Boolean - allow untracked files (default: true)
- `operation`: Description of operation requiring clean tree (for error messages)

**Process**:
```bash
# Get git status
git status --porcelain

# Parse output
# Lines starting with "??" are untracked files
# Any other lines are modifications/staged changes

# If allow_untracked=true:
#   Only fail if non-untracked changes exist
# If allow_untracked=false:
#   Fail if any changes exist
```

**Output**:
- `validation_result`: "pass" | "fail" | "warning"
- `error_message`: Error or warning message
- `modifications`: Array of modified files
- `untracked_files`: Array of untracked files
- `staged_changes`: Array of staged files

**Error Message Format**:
```
Error: Working tree has uncommitted changes

Operation: {operation}
Modified Files: {count}
{list of modified files}

Staged Changes: {count}
{list of staged files}

{if allow_untracked=false:}
Untracked Files: {count}
{list of untracked files}

Remediation:
1. Commit current changes:
   git add .
   git commit -m "WIP: description"
2. Or stash changes temporarily:
   git stash save "description"
3. Then retry {operation}
4. To restore stashed changes:
   git stash pop
```

**Example Usage**:
```javascript
// Check before branch switching
validateGitWorkingTreeClean(
  allow_untracked=true,
  operation="switching to feature branch"
)
→ {
  validation_result: "pass",
  error_message: null,
  modifications: [],
  untracked_files: ["temp.txt"],
  staged_changes: []
}

// Detect uncommitted changes
validateGitWorkingTreeClean(
  allow_untracked=false,
  operation="creating feature commit"
)
→ {
  validation_result: "fail",
  error_message: "Error: Working tree has uncommitted changes...",
  modifications: ["src/App.tsx"],
  untracked_files: ["temp.txt"],
  staged_changes: []
}
```

#### validateGitBranchState

**Purpose**: Verify git branch is in expected state before operations (e.g., not detached HEAD, correct branch).

**Input**:
- `expected_branch_pattern`: Regex pattern for expected branch name (optional)
- `allow_detached_head`: Boolean - allow detached HEAD state (default: false)
- `operation`: Description of operation requiring branch validation

**Process**:
```bash
# Get current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Check for detached HEAD
if [ "${current_branch}" = "HEAD" ]; then
  if allow_detached_head=false:
    validation fails - detached HEAD
fi

# Check branch pattern if provided
if [ -n "${expected_branch_pattern}" ]; then
  echo "${current_branch}" | grep -E "${expected_branch_pattern}"
  if not match:
    validation fails - unexpected branch
fi

# Check if branch is behind remote
git status -uno | grep "Your branch is behind"
if behind remote:
  validation warning - recommend pulling
fi
```

**Output**:
- `validation_result`: "pass" | "fail" | "warning"
- `error_message`: Error or warning message
- `current_branch`: Current branch name or "HEAD" if detached
- `is_detached`: Boolean - true if detached HEAD
- `is_behind_remote`: Boolean - true if branch behind remote
- `remote_ahead_by`: Number of commits remote is ahead (null if not behind)

**Error Message Format**:
```
Error: Git branch validation failed

Operation: {operation}
Current Branch: {current_branch}
Expected Pattern: {expected_branch_pattern if provided}
Issue: {detached HEAD | unexpected branch | behind remote}

Remediation:
{if detached HEAD:}
1. Checkout a branch:
   git checkout main
   OR
   git checkout -b feature/new-feature
2. If you want to keep changes, create a new branch first

{if unexpected branch:}
1. Switch to expected branch:
   git checkout {example expected branch}
2. Or create feature branch:
   git checkout -b feature/{feature-name}

{if behind remote:}
1. Pull latest changes:
   git pull
2. Resolve any conflicts if they occur
3. Then retry {operation}
```

**Example Usage**:
```javascript
// Validate on feature branch before implementing
validateGitBranchState(
  expected_branch_pattern="^(main|master|feature/.+)$",
  allow_detached_head=false,
  operation="starting feature implementation"
)
→ {
  validation_result: "pass",
  error_message: null,
  current_branch: "feature/5-agent-improvements",
  is_detached: false,
  is_behind_remote: false,
  remote_ahead_by: null
}

// Detect detached HEAD
validateGitBranchState(
  expected_branch_pattern="^(main|master|feature/.+)$",
  allow_detached_head=false,
  operation="committing changes"
)
→ {
  validation_result: "fail",
  error_message: "Error: Git branch validation failed... detached HEAD...",
  current_branch: "HEAD",
  is_detached: true,
  is_behind_remote: false,
  remote_ahead_by: null
}
```

#### validateGitCanCommit

**Purpose**: Comprehensive pre-commit validation checking all git requirements.

**Input**:
- `operation`: Description of commit operation (e.g., "committing feature implementation")
- `allow_on_main`: Boolean - allow commits directly to main/master (default: false)

**Process**:
1. Validate git repository exists (test -d .git)
2. Validate working tree has changes (git status --porcelain)
3. Validate not in detached HEAD state
4. If allow_on_main=false, validate not on main/master branch
5. Validate no uncommitted changes to critical files that shouldn't be committed (.env, credentials, secrets)
6. Validate commit will not create conflicts (optional check with remote)

**Output**:
- `validation_result`: "pass" | "fail" | "warning"
- `error_message`: Error or warning message
- `warnings`: Array of warning messages (e.g., committing to main, sensitive files)
- `changes_to_commit`: Object with counts of { modified, added, deleted }

**Error Message Format**:
```
Error: Cannot commit - validation failed

Operation: {operation}
Issues:
{for each issue:}
  - {issue description}

Remediation:
{specific remediation for each issue}
```

**Warning Message Format**:
```
Warning: Commit validation warnings

Operation: {operation}
Warnings:
{for each warning:}
  - {warning description}

Impact:
{description of potential issues}

Recommendation:
{recommended actions}

You may continue with commit, but addressing warnings is recommended.
```

**Example Usage**:
```javascript
// Validate before committing
validateGitCanCommit(
  operation="committing feature implementation",
  allow_on_main=false
)
→ {
  validation_result: "pass",
  error_message: null,
  warnings: [],
  changes_to_commit: { modified: 3, added: 2, deleted: 0 }
}

// Detect committing to main (warning)
validateGitCanCommit(
  operation="committing feature implementation",
  allow_on_main=false
)
→ {
  validation_result: "warning",
  error_message: null,
  warnings: ["Committing directly to main branch is not recommended. Consider using a feature branch."],
  changes_to_commit: { modified: 1, added: 0, deleted: 0 }
}

// Detect no changes to commit (error)
validateGitCanCommit(
  operation="creating commit",
  allow_on_main=true
)
→ {
  validation_result: "fail",
  error_message: "Error: Cannot commit - validation failed... No changes to commit...",
  warnings: [],
  changes_to_commit: { modified: 0, added: 0, deleted: 0 }
}
```

#### validateGitCanCreateBranch

**Purpose**: Validate git state before creating new branch.

**Input**:
- `branch_name`: Name of branch to create
- `require_clean_tree`: Boolean - require clean working tree (default: false)
- `operation`: Description of branch creation operation

**Process**:
1. Validate git repository exists
2. Validate branch name doesn't already exist (git branch --list)
3. Validate branch name follows naming convention (optional pattern check)
4. If require_clean_tree=true, validate working tree is clean
5. Validate current branch exists (not detached HEAD) unless creating from commit

**Output**:
- `validation_result`: "pass" | "fail" | "warning"
- `error_message`: Error or warning message
- `branch_exists`: Boolean - true if branch already exists
- `current_branch`: Current branch name

**Error Message Format**:
```
Error: Cannot create branch - validation failed

Branch Name: {branch_name}
Operation: {operation}
Issue: {specific issue}

Remediation:
{if branch exists:}
1. Use different branch name
2. Or checkout existing branch:
   git checkout {branch_name}
3. Or delete existing branch if no longer needed:
   git branch -d {branch_name}

{if invalid name:}
1. Use valid branch name format
2. Recommended format: feature/{feature-id}-{description}
3. Avoid spaces, special characters

{if dirty working tree:}
1. Commit or stash changes before creating branch
2. Or use --no-verify flag if appropriate
```

**Example Usage**:
```javascript
// Validate before creating feature branch
validateGitCanCreateBranch(
  branch_name="feature/6-user-authentication",
  require_clean_tree=false,
  operation="starting new feature"
)
→ {
  validation_result: "pass",
  error_message: null,
  branch_exists: false,
  current_branch: "main"
}

// Detect branch already exists
validateGitCanCreateBranch(
  branch_name="feature/5-agent-improvements",
  require_clean_tree=false,
  operation="creating feature branch"
)
→ {
  validation_result: "fail",
  error_message: "Error: Cannot create branch - validation failed... Branch already exists...",
  branch_exists: true,
  current_branch: "main"
}
```

### 4. Directory Structure Validation

Validate directory structure before operations that depend on specific layouts.

#### validateProjectStructure

**Purpose**: Verify project has expected directory structure before operations.

**Input**:
- `required_directories`: Array of directory paths that must exist
- `required_files`: Array of file paths that must exist
- `operation`: Description of operation requiring structure validation

**Process**:
```bash
# Check each required directory
for dir in required_directories:
  test -d "${dir}" || echo "MISSING: ${dir}"

# Check each required file
for file in required_files:
  test -f "${file}" || echo "MISSING: ${file}"
```

**Output**:
- `validation_result`: "pass" | "fail"
- `error_message`: Error message listing all missing paths
- `missing_directories`: Array of missing directory paths
- `missing_files`: Array of missing file paths

**Error Message Format**:
```
Error: Required project structure missing

Operation: {operation}

Missing Directories:
{for each missing directory:}
  - {directory_path}
    Purpose: {purpose if known}
    Create with: mkdir -p {directory_path}

Missing Files:
{for each missing file:}
  - {file_path}
    Purpose: {purpose if known}
    Create with: {creation command if known}

Remediation:
1. Create missing directories:
   {list of mkdir commands}
2. Create missing files:
   {list of creation commands}
3. Then retry {operation}
```

**Example Usage**:
```javascript
// Validate project structure for implement command
validateProjectStructure(
  required_directories=[
    ".claude/agents",
    ".claude/commands",
    ".claude/helpers",
    "docs/features"
  ],
  required_files=[
    "docs/features/feature-log.json"
  ],
  operation="executing /implement command"
)
→ {
  validation_result: "pass",
  error_message: null,
  missing_directories: [],
  missing_files: []
}

// Detect missing structure
validateProjectStructure(
  required_directories=[
    "context/backend",
    "context/frontend"
  ],
  required_files=[],
  operation="loading context files"
)
→ {
  validation_result: "fail",
  error_message: "Error: Required project structure missing...",
  missing_directories: ["context/backend"],
  missing_files: []
}
```

## Integration Guide for Commands and Agents

### When to Use File Operations Validation

Use this validation layer when:

1. **Reading Files**:
   - Before reading any file: `validatePathExists` + `validatePathAccessible`
   - Before reading JSON files: Add `validateJSONSyntax` after reading
   - Before reading from specific location: Add `validatePathInProjectRoot`

2. **Writing Files**:
   - Before writing any file: `validateParentDirectoryExists` + `validatePathAccessible`
   - Before writing JSON: `validateJSONSyntax` + `validateJSONSchema` or use high-level validators
   - Before overwriting: Check if file exists, optionally create backup

3. **Git Operations**:
   - Before commits: `validateGitCanCommit`
   - Before branch operations: `validateGitBranchState` or `validateGitCanCreateBranch`
   - Before merge/pull: `validateGitWorkingTreeClean`

4. **Directory Operations**:
   - Before operations requiring structure: `validateProjectStructure`
   - Before creating files in subdirectories: `validateParentDirectoryExists`

### Integration Pattern for File Write Operations

```markdown
## Writing Configuration File with Validation

1. Validate parent directory exists (create if missing)
   ```
   validateParentDirectoryExists(
     file_path="{absolute_path}",
     create_if_missing=true,
     purpose="{what this file is for}"
   )
   ```

2. Construct JSON data structure

3. Convert to JSON string

4. Validate JSON syntax
   ```
   validateJSONSyntax(
     json_string="{json_data}",
     file_path="{absolute_path}",
     purpose="{what this data represents}"
   )
   ```

5. Validate JSON schema (if applicable)
   ```
   validateJSONSchema(
     json_data="{parsed_json}",
     schema_requirements="{schema_definition}",
     file_path="{absolute_path}",
     purpose="{what this data represents}"
   )
   ```
   OR use high-level validator:
   ```
   validateFeatureLogEntry(...) or validateImplementationLogEntry(...)
   ```

6. If all validations pass:
   - Use Write tool to create file
   - Verify write succeeded
   - Optionally validate file exists and is readable

7. If any validation fails:
   - Display error message with remediation
   - STOP execution immediately
   - Do NOT attempt to write file
```

### Integration Pattern for File Read Operations

```markdown
## Reading Configuration File with Validation

1. Validate file path exists and is accessible
   ```
   validatePathExists(
     path="{absolute_path}",
     type="file",
     purpose="{what this file contains}"
   )
   ```

2. Validate can read file
   ```
   validatePathAccessible(
     path="{absolute_path}",
     permission="read",
     purpose="{what this file contains}"
   )
   ```

3. Validate path is within project root (security check)
   ```
   validatePathInProjectRoot(
     path="{absolute_path}",
     project_root="{git_root}",
     purpose="{what this file contains}"
   )
   ```

4. If all validations pass:
   - Use Read tool to read file contents
   - If JSON file: Validate JSON syntax on contents
   - If JSON file: Optionally validate schema
   - Parse and use data

5. If any validation fails:
   - Display error message with remediation
   - STOP execution immediately
   - Do NOT attempt to read file (will fail anyway)
```

### Integration Pattern for Git Operations

```markdown
## Git Commit Operation with Validation

1. Validate can commit
   ```
   validateGitCanCommit(
     operation="committing {description}",
     allow_on_main=false
   )
   ```

2. If validation passes:
   - Stage changes with git add
   - Create commit with git commit
   - Optionally push to remote

3. If validation fails:
   - Display error message
   - STOP execution immediately

4. If validation has warnings:
   - Display warnings
   - Allow user to decide whether to continue
   - If continuing, proceed with commit

## Git Branch Operation with Validation

1. Validate can create branch
   ```
   validateGitCanCreateBranch(
     branch_name="{new_branch_name}",
     require_clean_tree=false,
     operation="creating branch for {purpose}"
   )
   ```

2. If validation passes:
   - Create branch with git checkout -b
   - Verify branch created

3. If validation fails:
   - Display error message
   - STOP execution immediately
```

## Common Validation Workflows

### Workflow 1: Writing to Feature Log

```markdown
1. Load existing feature log (if exists)
   - validatePathExists for docs/features/feature-log.json (optional - may not exist yet)
   - If exists: Read + validateJSONSyntax

2. Construct new feature entry
   - Create JSON object with all required fields
   - Set appropriate defaults for optional fields

3. Validate new entry
   - validateFeatureLogEntry(feature_entry, file_path)

4. Merge into feature log
   - If log exists: Parse, append new entry, re-serialize
   - If log doesn't exist: Create new log with entry in array

5. Validate complete log before writing
   - validateJSONSyntax for complete log
   - Ensure features array is valid

6. Validate parent directory exists
   - validateParentDirectoryExists(create_if_missing=true)

7. Write feature log
   - Use Write tool
   - Verify write succeeded
```

### Workflow 2: Writing to Implementation Log

```markdown
1. Load existing implementation log (if exists)
   - validatePathExists for implementation-log.json (optional - may not exist yet)
   - If exists: Read + validateJSONSyntax + parse

2. Construct new log entry
   - Create JSON object with all required fields
   - Include arrays for files, actions, tools, issues

3. Validate new entry
   - validateImplementationLogEntry(log_entry, file_path)

4. Append to log array
   - If log exists: Parse array, append entry
   - If log doesn't exist: Create new array with entry

5. Validate complete log before writing
   - validateJSONSyntax for complete array

6. Validate parent directory exists
   - validateParentDirectoryExists(create_if_missing=true)

7. Write implementation log
   - Use Write tool
   - Verify write succeeded

8. Update feature log (mark story as implemented)
   - Follow "Writing to Feature Log" workflow
```

### Workflow 3: Creating Feature Directory Structure

```markdown
1. Validate parent directory exists
   - validatePathExists for docs/features/

2. Determine new feature directory
   - Get feature ID from feature log
   - Construct path: docs/features/{id}/

3. Validate directory doesn't exist
   - If exists: Error or warning (feature already exists)

4. Create feature directory
   - mkdir -p docs/features/{id}/

5. Verify directory created
   - validatePathExists for docs/features/{id}/

6. Create placeholder files if needed
   - Follow "Writing Configuration File" pattern for each file
```

### Workflow 4: Safe File Overwrite with Backup

```markdown
1. Validate file exists
   - validatePathExists for original file

2. Create backup
   - Construct backup path: {original}.backup or {original}.{timestamp}
   - validateParentDirectoryExists for backup
   - Copy original to backup (cp or read+write)
   - Verify backup created and matches original

3. Validate new data
   - validateJSONSyntax if JSON
   - validateJSONSchema if applicable

4. Write new file
   - Use Write tool
   - Verify write succeeded

5. Validate new file
   - validatePathExists
   - validateJSONSyntax if JSON
   - Optionally compare size/structure

6. If validation fails:
   - Restore from backup
   - Delete failed write
   - Report error
```

## Best Practices

### 1. Validation Order

Always validate in this order:
1. Path existence and accessibility (fail fast if path issues)
2. Data structure and syntax (catch data issues before write)
3. Git status (check before destructive operations)
4. Business logic (command-specific validation)

### 2. Error Handling

- **Hard Failures**: File not found, JSON syntax error, git repository missing, detached HEAD
- **Soft Warnings**: Working tree dirty, branch behind remote, committing to main, sensitive files

### 3. Performance Considerations

- Cache validation results within a command execution when same check needed multiple times
- Run file existence checks before reading file contents (fail fast)
- Use bash tests (test -f, test -d) for fast file system checks
- Only parse JSON when absolutely necessary (syntax check first, schema check second)

### 4. Security Considerations

- Always validate paths are within project root (prevent directory traversal)
- Check for sensitive files before commits (.env, credentials, secrets, .pem, .key)
- Validate write permissions before attempting writes
- Use absolute paths to prevent relative path confusion

### 5. Atomicity and Consistency

- Validate ALL requirements before starting any file operations
- Use backups for overwrites of critical files
- Validate file contents after writes for critical files
- Atomic log writes (construct complete array/object, validate, write once)

## Examples

### Example 1: Safe Feature Log Write

```javascript
// BEFORE (no validation - risky)
const newFeature = { featureID: "6", title: "Add Auth" };
const featureLog = JSON.parse(readFile("docs/features/feature-log.json"));
featureLog.features.push(newFeature);
writeFile("docs/features/feature-log.json", JSON.stringify(featureLog));
// RISK: JSON syntax error, missing fields, schema violation, corrupt file

// AFTER (with validation - safe)
// Step 1: Validate parent directory
validateParentDirectoryExists(
  file_path="/home/ed/Dev/architecture/docs/features/feature-log.json",
  create_if_missing=true,
  purpose="Feature log parent directory"
);

// Step 2: Construct entry
const newFeature = {
  featureID: "6",
  title: "Add User Authentication",
  createdAt: "2025-10-19T12:00:00Z",
  userStoriesCreated: null,
  userStoriesImplemented: null,
  isSummarised: false,
  summarisedAt: null,
  state: "planned",
  stateHistory: [
    {
      state: "planned",
      timestamp: "2025-10-19T12:00:00Z",
      triggeredBy: "/feature command",
      notes: "Feature created"
    }
  ],
  actions: []
};

// Step 3: Validate entry
const entryValidation = validateFeatureLogEntry(
  feature_entry=newFeature,
  file_path="/home/ed/Dev/architecture/docs/features/feature-log.json"
);
if (entryValidation.validation_result === "fail") {
  // Display error and stop
  console.error(entryValidation.error_message);
  return;
}

// Step 4: Load existing log
let featureLog = { features: [] };
if (fileExists("docs/features/feature-log.json")) {
  const logContent = readFile("docs/features/feature-log.json");
  const syntaxValidation = validateJSONSyntax(
    json_string=logContent,
    file_path="/home/ed/Dev/architecture/docs/features/feature-log.json",
    purpose="Existing feature log"
  );
  if (syntaxValidation.validation_result === "fail") {
    console.error(syntaxValidation.error_message);
    return;
  }
  featureLog = syntaxValidation.parsed_data;
}

// Step 5: Append entry
featureLog.features.push(newFeature);

// Step 6: Validate complete log
const logString = JSON.stringify(featureLog, null, 2);
const finalValidation = validateJSONSyntax(
  json_string=logString,
  file_path="/home/ed/Dev/architecture/docs/features/feature-log.json",
  purpose="Updated feature log"
);
if (finalValidation.validation_result === "fail") {
  console.error(finalValidation.error_message);
  return;
}

// Step 7: Write file
writeFile("/home/ed/Dev/architecture/docs/features/feature-log.json", logString);

// SUCCESS: All validation passed, file safely written
```

### Example 2: Safe Implementation Log Append

```javascript
// BEFORE (no validation - risky)
const logEntry = { storyNumber: 1, status: "completed" };
const implLog = JSON.parse(readFile("impl-log.json"));
implLog.push(logEntry);
writeFile("impl-log.json", JSON.stringify(implLog));
// RISK: Missing required fields, invalid types, corrupt JSON

// AFTER (with validation - safe)
// Step 1: Construct complete entry
const logEntry = {
  storyNumber: 1,
  storyTitle: "Create User Interface",
  agent: "frontend-developer",
  status: "completed",
  completedAt: "2025-10-19T12:00:00Z",
  filesCreated: ["src/App.tsx", "src/App.test.tsx"],
  filesModified: [],
  actions: ["Created React component with Material UI", "Added comprehensive tests"],
  toolsUsed: ["Write", "Read", "Bash"],
  issuesEncountered: [],
  notes: "Component follows Material UI best practices"
};

// Step 2: Validate entry
const entryValidation = validateImplementationLogEntry(
  log_entry=logEntry,
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json"
);
if (entryValidation.validation_result === "fail") {
  console.error(entryValidation.error_message);
  return;
}

// Step 3: Validate parent directory
validateParentDirectoryExists(
  file_path="/home/ed/Dev/architecture/docs/features/5/implementation-log.json",
  create_if_missing=true,
  purpose="Implementation log directory for Feature #5"
);

// Step 4: Load existing log
let implLog = [];
const logPath = "/home/ed/Dev/architecture/docs/features/5/implementation-log.json";
if (fileExists(logPath)) {
  const logContent = readFile(logPath);
  const syntaxValidation = validateJSONSyntax(
    json_string=logContent,
    file_path=logPath,
    purpose="Existing implementation log"
  );
  if (syntaxValidation.validation_result === "fail") {
    console.error(syntaxValidation.error_message);
    return;
  }
  implLog = syntaxValidation.parsed_data;
}

// Step 5: Append entry
implLog.push(logEntry);

// Step 6: Validate complete log
const logString = JSON.stringify(implLog, null, 2);
const finalValidation = validateJSONSyntax(
  json_string=logString,
  file_path=logPath,
  purpose="Updated implementation log"
);
if (finalValidation.validation_result === "fail") {
  console.error(finalValidation.error_message);
  return;
}

// Step 7: Write file
writeFile(logPath, logString);

// SUCCESS: Entry validated and appended safely
```

### Example 3: Git Commit with Validation

```javascript
// BEFORE (no validation - risky)
git add .
git commit -m "Update feature"
git push
// RISK: Detached HEAD, no changes, committing to main, sensitive files, conflicts

// AFTER (with validation - safe)
// Step 1: Validate can commit
const commitValidation = validateGitCanCommit(
  operation="committing feature implementation",
  allow_on_main=false
);

// Step 2: Handle validation result
if (commitValidation.validation_result === "fail") {
  console.error(commitValidation.error_message);
  return;
}

if (commitValidation.validation_result === "warning") {
  console.warn(commitValidation.error_message);
  console.warn("Warnings detected:");
  commitValidation.warnings.forEach(w => console.warn(`  - ${w}`));
  console.warn("Continuing anyway...");
}

// Step 3: Validate branch state
const branchValidation = validateGitBranchState(
  expected_branch_pattern="^feature/.+$",
  allow_detached_head=false,
  operation="committing changes"
);

if (branchValidation.validation_result === "fail") {
  console.error(branchValidation.error_message);
  return;
}

// Step 4: Proceed with commit
git add .
git commit -m "Implementation of Feature #5 Story #1

- Created user interface component
- Added comprehensive tests
- Followed Material UI patterns"

// Step 5: Push to remote
git push

// SUCCESS: All validations passed, safe commit
```

## Quick Reference

### Validation Functions by Use Case

| Use Case | Validation Functions | Order |
|----------|---------------------|-------|
| Read JSON file | `validatePathExists` → `validatePathAccessible` → `validatePathInProjectRoot` → Read → `validateJSONSyntax` | 1-2-3-4-5 |
| Write JSON file | `validateParentDirectoryExists` → Construct data → `validateJSONSyntax` → `validateJSONSchema` → Write | 1-2-3-4-5 |
| Write feature log | `validateParentDirectoryExists` → Construct entry → `validateFeatureLogEntry` → Load existing → Append → Validate complete → Write | 1-2-3-4-5-6-7 |
| Write implementation log | `validateParentDirectoryExists` → Construct entry → `validateImplementationLogEntry` → Load existing → Append → Validate complete → Write | 1-2-3-4-5-6-7 |
| Git commit | `validateGitCanCommit` → `validateGitBranchState` → Stage → Commit → Push | 1-2-3-4-5 |
| Git branch create | `validateGitCanCreateBranch` → Create branch → Verify | 1-2-3 |
| Create directory | `validatePathExists` (parent) → Create directory → Verify | 1-2-3 |
| Project structure | `validateProjectStructure` → Proceed with operation | 1-2 |

### Error vs Warning Decision Matrix

| Condition | Severity | Action |
|-----------|----------|--------|
| File not found | Error | Stop execution |
| Invalid JSON syntax | Error | Stop execution |
| Missing required field | Error | Stop execution |
| Git repository missing | Error | Stop execution |
| Detached HEAD state | Error | Stop execution |
| Working tree has changes | Warning | Continue with caution |
| Branch behind remote | Warning | Continue (suggest pulling) |
| Committing to main | Warning | Continue (discourage) |
| Sensitive files detected | Warning | Continue (with remediation guidance) |
| Untracked files | Warning | Continue (inform user) |

### Validation Checklist

Before any file write operation:
- [ ] Parent directory exists (create if needed)
- [ ] Path is within project root
- [ ] Have write permissions
- [ ] Data structure is valid (JSON syntax)
- [ ] Data matches schema (required fields, correct types)
- [ ] Backup created if overwriting critical file

Before any file read operation:
- [ ] File path exists
- [ ] Have read permissions
- [ ] Path is within project root
- [ ] File contents are valid (JSON syntax if JSON)

Before any git operation:
- [ ] Git repository exists
- [ ] Working tree state is appropriate
- [ ] Branch state is valid
- [ ] No sensitive files being committed (if committing)
- [ ] Not in detached HEAD state (usually)

## Maintenance and Evolution

### Adding New Validation Functions

When adding new validation functions:

1. **Define clear purpose**: What is being validated and why?
2. **Document inputs and outputs**: Use consistent schema format
3. **Provide error messages**: Follow standard format with remediation
4. **Add examples**: Show success and failure cases
5. **Update integration guide**: Add to appropriate workflow section
6. **Update quick reference**: Add to validation functions table

### Schema Evolution

When validation schemas need to change:

1. **Backward compatibility**: Ensure existing valid data still validates
2. **Optional fields**: Add new requirements as optional first
3. **Migration path**: Provide guidance for updating existing data
4. **Version tracking**: Document schema version changes
5. **Gradual rollout**: Allow both old and new formats during transition

## Version History

- v1.0.0 (2025-10-19): Initial validation layer implementation
  - File path validation functions
  - Data structure validation functions
  - Git status validation functions
  - Directory structure validation
  - Integration guide and examples
  - Quick reference and best practices
