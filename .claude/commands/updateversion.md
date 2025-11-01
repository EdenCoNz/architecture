---
description: Update version (major/minor/patch) in frontend and backend
model: claude-sonnet-4-5
---

## Purpose

Update the application version number following semantic versioning (MAJOR.MINOR.PATCH) across both frontend and backend codebases. This command ensures version synchronization between:
- `frontend/package.json` (version field)
- `backend/config/__init__.py` (__version__ variable)

## Variables

- `{{{ input }}}` - The version bump type: "major", "minor", or "patch"
- Current frontend version - Read from `frontend/package.json`
- Current backend version - Read from `backend/config/__init__.py`

## Semantic Versioning Rules

- **major**: Increment X in X.Y.Z, reset Y and Z to 0 (e.g., 1.2.3 → 2.0.0)
- **minor**: Increment Y in X.Y.Z, reset Z to 0 (e.g., 1.2.3 → 1.3.0)
- **patch**: Increment Z in X.Y.Z (e.g., 1.2.3 → 1.2.4)

## Instructions

- Validate the input argument (must be "major", "minor", or "patch")
- Read current versions from both files
- Verify versions are in sync before updating
- Calculate new version based on the bump type
- Update both files atomically
- Report the version change clearly

## Workflow

### Step 1: Validate Input

1. **Check bump type argument**:
   - Verify `{{{ input }}}` is provided and non-empty
   - Trim whitespace from the input
   - Convert to lowercase for comparison
   - Valid values: "major", "minor", "patch"
   - If invalid or not provided: STOP and display error:
     ```
     Error: Invalid version bump type.

     Usage:
       /updateversion <type>

     Valid types:
       major - Increment major version (X.0.0)
       minor - Increment minor version (X.Y.0)
       patch - Increment patch version (X.Y.Z)

     Examples:
       /updateversion major   # 1.2.3 → 2.0.0
       /updateversion minor   # 1.2.3 → 1.3.0
       /updateversion patch   # 1.2.3 → 1.2.4
     ```

2. **Store bump type**:
   - Store the validated bump type for use in Step 3
   - Display: "Preparing to bump {bump_type} version..."

### Step 2: Read Current Versions

1. **Read frontend version**:
   - Read `frontend/package.json`
   - Parse JSON to extract the "version" field
   - Validate format matches X.Y.Z (semantic versioning)
   - If file not found: STOP with error:
     ```
     Error: frontend/package.json not found
     Please ensure you are in the project root directory.
     ```
   - If version field missing or invalid format: STOP with error:
     ```
     Error: Invalid or missing version in frontend/package.json
     Expected format: "version": "X.Y.Z"
     ```

2. **Read backend version**:
   - Read `backend/config/__init__.py`
   - Search for line matching pattern: `__version__ = "X.Y.Z"`
   - Extract version string
   - Validate format matches X.Y.Z
   - If file not found: STOP with error:
     ```
     Error: backend/config/__init__.py not found
     Please ensure you are in the project root directory.
     ```
   - If __version__ missing or invalid format: STOP with error:
     ```
     Error: Invalid or missing __version__ in backend/config/__init__.py
     Expected format: __version__ = "X.Y.Z"
     ```

3. **Verify versions are in sync**:
   - Compare frontend version with backend version
   - If they differ: Display warning and ask user to confirm:
     ```
     ⚠️  Warning: Version mismatch detected!

     Frontend (package.json): {frontend_version}
     Backend (__init__.py):   {backend_version}

     This will sync both to the new version based on the backend version.
     Do you want to continue? (yes/no)
     ```
   - If user says no: STOP with message "Version update cancelled"
   - If versions match: Display "Current version: {version}"

4. **Store current version**:
   - Use backend version as the base for calculation (or frontend if backend not found)
   - Parse into components: major, minor, patch
   - Display: "Current version: {major}.{minor}.{patch}"

### Step 3: Calculate New Version

1. **Parse version components**:
   - Split version string by "." separator
   - Convert each part to integer: major, minor, patch
   - Validate all parts are non-negative integers
   - If parsing fails: STOP with error:
     ```
     Error: Failed to parse version "{version}"
     Version must be in format X.Y.Z where X, Y, Z are non-negative integers
     ```

2. **Calculate new version based on bump type**:
   - **If "major"**:
     - new_major = major + 1
     - new_minor = 0
     - new_patch = 0
   - **If "minor"**:
     - new_major = major
     - new_minor = minor + 1
     - new_patch = 0
   - **If "patch"**:
     - new_major = major
     - new_minor = minor
     - new_patch = patch + 1

3. **Format new version**:
   - new_version = "{new_major}.{new_minor}.{new_patch}"
   - Display version change:
     ```
     Version Update ({bump_type}):
       {major}.{minor}.{patch} → {new_major}.{new_minor}.{new_patch}
     ```

4. **Store new version**:
   - Store new_version string for use in Step 4

### Step 4: Update Files

1. **Update frontend/package.json**:
   - Read the current file content
   - Use the Edit tool to replace the old version with the new version
   - Find line: `  "version": "{old_version}",`
   - Replace with: `  "version": "{new_version}",`
   - Preserve exact formatting (indentation, quotes, comma)
   - Verify the edit was successful
   - If edit fails: STOP with error and provide manual instructions

2. **Update backend/config/__init__.py**:
   - Read the current file content
   - Use the Edit tool to replace the old version with the new version
   - Find line: `__version__ = "{old_version}"`
   - Replace with: `__version__ = "{new_version}"`
   - Preserve exact formatting (quotes, spacing)
   - Verify the edit was successful
   - If edit fails: STOP with error and provide manual instructions

3. **Verify updates**:
   - Re-read both files to confirm the changes
   - Verify frontend version matches new_version
   - Verify backend version matches new_version
   - If verification fails: Display warning:
     ```
     ⚠️  Warning: Version update may have failed
     Please manually verify:
       - frontend/package.json: "version": "{new_version}"
       - backend/config/__init__.py: __version__ = "{new_version}"
     ```

4. **Report success**:
   - Display:
     ```
     ✅ Version updated successfully!

     Files updated:
       • frontend/package.json
       • backend/config/__init__.py

     Version change: {old_version} → {new_version}
     ```

### Step 5: Show Git Status

1. **Check git status**:
   - Run `git status --short` to show modified files
   - Display the output to user
   - Show that both files have been modified

2. **Suggest next steps**:
   - Display:
     ```
     Next steps:
       1. Review the changes: git diff
       2. Commit the changes: /push "Bump version to {new_version}"
       3. Or manually commit: git add . && git commit -m "Bump version to {new_version}"
     ```

## Report

Provide a summary with the following sections:

### Version Update Summary
- Bump type: {bump_type}
- Old version: {old_version}
- New version: {new_version}
- Files updated: 2

### Files Modified
- ✅ frontend/package.json
  - Old: `"version": "{old_version}"`
  - New: `"version": "{new_version}"`

- ✅ backend/config/__init__.py
  - Old: `__version__ = "{old_version}"`
  - New: `__version__ = "{new_version}"`

### Git Status
- Modified files: 2
- Ready to commit: Yes

### Next Steps
- Review changes with: `git diff`
- Commit with: `/push "Bump version to {new_version}"`
- Or use: `git add . && git commit -m "Bump version to {new_version}"`

## Error Handling

### Common Failure Scenarios

1. **Invalid bump type**:
   - Display error with usage instructions and examples
   - List valid bump types: major, minor, patch

2. **Files not found**:
   - Check if user is in the correct directory (project root)
   - Provide the expected file paths
   - Suggest running `pwd` to verify location

3. **Version format invalid**:
   - Display the current invalid format found
   - Explain the expected format: X.Y.Z
   - Suggest manual correction before retrying

4. **Version mismatch between files**:
   - Display both versions clearly
   - Warn user about the mismatch
   - Ask for confirmation before proceeding
   - Use one version as the base (prefer backend)

5. **Parse errors**:
   - Display the version string that failed to parse
   - Explain the expected numeric format
   - Suggest checking for typos or extra characters

6. **Edit failures**:
   - Display the specific file that failed to update
   - Provide the exact search string that wasn't found
   - Offer manual update instructions:
     ```
     Please manually update {file}:
       Find: {old_string}
       Replace with: {new_string}
     ```

7. **Verification failures**:
   - List which file(s) failed verification
   - Show expected vs actual values
   - Suggest manual verification steps

8. **Output**:
## Post UpdateVersion Push
**Payload**:
{
    "frontendVersion":{new-version},
    ""backendVersion":{new-version}
}

## Self-Verification Checklist

Before finalizing, verify:

- [ ] Bump type validated (major/minor/patch)
- [ ] frontend/package.json read successfully
- [ ] backend/config/__init__.py read successfully
- [ ] Current versions parsed into major.minor.patch
- [ ] Version sync checked (or mismatch handled)
- [ ] New version calculated correctly based on bump type
- [ ] frontend/package.json updated with exact formatting
- [ ] backend/config/__init__.py updated with exact formatting
- [ ] Both file updates verified by re-reading
- [ ] Both files contain the same new version
- [ ] Git status displayed showing modified files
- [ ] Clear summary provided to user
- [ ] Next steps suggested (diff, commit, push)
- [ ] All errors captured and reported clearly
- [ ] Manual recovery instructions provided for each failure type
