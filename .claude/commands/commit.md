---
description: Stage all changes and create a git commit
args:
  - name: message
    description: The commit message
    required: true
  - name: push
    description: Optional - use "push" to push changes after committing
    required: false
model: claude-sonnet-4-5
---

## Purpose

This command stages all changes in the working directory and creates a git commit with the provided message. Optionally, it can push the changes to the remote repository if "push" is specified as the second argument.

## Variables

- `{{{ args.message }}}` - The commit message to use for the git commit
- `{{{ args.push }}}` - Optional parameter - if set to "push", will push changes after committing

## Instructions

- MUST stage all changes using `git add .` before committing
- MUST use the provided message exactly as given
- MUST NOT modify or enhance the commit message
- MUST follow Git Safety Protocol from the Bash tool documentation
- MUST NOT skip hooks or use --no-verify unless explicitly requested

## Workflow

### Step 1: Stage all changes

Use the Bash tool to run `git add .` to stage all changes in the working directory.

### Step 2: Create the commit

Use the Bash tool to run `git commit -m "{{{ args.message }}}"` with the provided message.

Use a HEREDOC format to ensure proper formatting:
```
git commit -m "$(cat <<'EOF'
{{{ args.message }}}
EOF
)"
```

### Step 3: Push to remote (conditional)

Check if `{{{ args.push }}}` is set to "push":
- If yes, run `git push` to push the committed changes to the remote repository
- If no or empty, skip this step

### Step 4: Verify the result

Run `git status` to confirm the commit was created successfully and show the current state.

## Report

Report back to the user:
- Confirmation that changes were staged
- Confirmation that the commit was created
- The commit message used
- Whether changes were pushed (if push argument was provided)
- Current git status
