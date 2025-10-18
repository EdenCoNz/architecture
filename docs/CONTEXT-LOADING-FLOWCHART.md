# Context Loading System - Visual Flowchart

## Decision Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Receives Task                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
          ┌────────────────────────────┐
          │  PRIORITY 1: Check for     │
          │  Explicit Context?         │
          └────────┬──────────┬────────┘
                   │          │
              YES  │          │  NO
                   │          │
                   ▼          ▼
    ┌──────────────────┐   ┌──────────────────────────────┐
    │  Load ONLY       │   │  PRIORITY 2: Analyze Task    │
    │  Specified Files │   │  for Keywords                │
    └──────────┬───────┘   └──────┬───────────────────────┘
               │                   │
               │                   ▼
               │          ┌─────────────────────────────┐
               │          │  Read context-index.yml     │
               │          └──────┬──────────────────────┘
               │                 │
               │                 ▼
               │          ┌─────────────────────────────┐
               │          │  Extract Keywords from Task │
               │          │  Examples:                  │
               │          │  - "github actions"         │
               │          │  - "docker"                 │
               │          │  - "material ui"            │
               │          └──────┬──────────────────────┘
               │                 │
               │                 ▼
               │          ┌─────────────────────────────┐
               │          │  Match Keywords to Context  │
               │          │  Files Using Index          │
               │          └──────┬──────────┬───────────┘
               │                 │          │
               │            MATCH│          │NO MATCH
               │                 │          │
               │                 ▼          ▼
               │      ┌──────────────┐   ┌────────────────────┐
               │      │ Load Matched │   │ PRIORITY 3:        │
               │      │ Context Files│   │ Load Default       │
               │      │              │   │ Context (ALL files)│
               │      └──────┬───────┘   └─────────┬──────────┘
               │             │                     │
               └─────────────┼─────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  PRIORITY 4:         │
                  │  Load Always-Required│
                  │  Context             │
                  │  (e.g., .env files)  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Begin Task with     │
                  │  Loaded Context      │
                  └──────────────────────┘
```

## Example Flows

### Flow 1: GitHub Actions Task (Keyword Match)

```
Task: "Add code coverage to CI pipeline"
  │
  ├─ Priority 1: No explicit context ✗
  │
  ├─ Priority 2: Analyze keywords
  │   ├─ Extract: ["code coverage", "ci pipeline"]
  │   ├─ Look up in context-index.yml
  │   └─ Match: "ci pipeline" → github-actions.md ✓
  │
  ├─ Priority 3: Skip (keywords matched)
  │
  └─ Priority 4: Load .github/workflows/.env ✓

RESULT: Load github-actions.md + .env
SKIP: docker.md
SAVINGS: 32% tokens
```

### Flow 2: Docker + GitHub Actions (Multi-Match)

```
Task: "Build Docker images in GitHub Actions workflow"
  │
  ├─ Priority 1: No explicit context ✗
  │
  ├─ Priority 2: Analyze keywords
  │   ├─ Extract: ["docker", "github actions", "workflow"]
  │   ├─ Look up in context-index.yml
  │   └─ Match:
  │       ├─ "docker" → docker.md ✓
  │       └─ "github actions" → github-actions.md ✓
  │
  ├─ Priority 3: Skip (keywords matched)
  │
  └─ Priority 4: Load .github/workflows/.env ✓

RESULT: Load docker.md + github-actions.md + .env
SKIP: None (both needed)
SAVINGS: 0%
```

### Flow 3: Explicit Context Override

```
Task: "Context: context/devops/docker.md\n\nOptimize Dockerfile"
  │
  ├─ Priority 1: Explicit context specified ✓
  │   └─ Load ONLY: docker.md
  │
  ├─ Priority 2: Skip (explicit takes precedence)
  │
  ├─ Priority 3: Skip
  │
  └─ Priority 4: Load .github/workflows/.env (if applicable) ✓

RESULT: Load docker.md + .env
SKIP: github-actions.md (even if mentioned elsewhere)
SAVINGS: 68% tokens
```

### Flow 4: Default Fallback

```
Task: "Review our DevOps practices"
  │
  ├─ Priority 1: No explicit context ✗
  │
  ├─ Priority 2: Analyze keywords
  │   ├─ Extract: ["devops practices"]
  │   ├─ Look up in context-index.yml
  │   └─ No specific match ✗
  │
  ├─ Priority 3: Load default context ✓
  │   └─ Load ALL: context/devops/**/*
  │       ├─ docker.md
  │       └─ github-actions.md
  │
  └─ Priority 4: Load .github/workflows/.env ✓

RESULT: Load all DevOps context
SKIP: None (comprehensive task)
SAVINGS: 0%
```

## Agent-Specific Flows

### DevOps Engineer Context Loading

```
                    ┌──────────────────┐
                    │  Task Received   │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼────────┐       ┌───────▼──────────┐
         │ "github       │       │ "docker"         │
         │  actions"     │       │ "container"      │
         │ "workflow"    │       │ "dockerfile"     │
         │ "ci/cd"       │       │ "compose"        │
         └──────┬────────┘       └───────┬──────────┘
                │                        │
                ▼                        ▼
    ┌───────────────────┐   ┌───────────────────────┐
    │ github-actions.md │   │ docker.md             │
    │ (52KB)            │   │ (25KB)                │
    └───────────────────┘   └───────────────────────┘
                │                        │
                └───────────┬────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ ALWAYS:              │
                 │ .github/workflows/   │
                 │ .env                 │
                 └──────────────────────┘
```

### Frontend Developer Context Loading

```
                    ┌──────────────────┐
                    │  Task Received   │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼────────┐       ┌───────▼──────────┐
         │ "react"       │       │ "material ui"    │
         │ "typescript"  │       │ "mui"            │
         │ "component"   │       │ "theme"          │
         │ "hooks"       │       │ "sx prop"        │
         └──────┬────────┘       └───────┬──────────┘
                │                        │
                ▼                        ▼
    ┌─────────────────────────┐  ┌──────────────────┐
    │ react-typescript-       │  │ material-ui-     │
    │ best-practices.md       │  │ best-practices.md│
    │ (25KB)                  │  │ (15KB)           │
    └─────────────────────────┘  └──────────────────┘
```

### Backend Developer Context Loading

```
                    ┌──────────────────┐
                    │  Task Received   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ "django"         │
                    │ "drf"            │
                    │ "rest framework" │
                    │ "api"            │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌───────────────────────────┐
                 │ django-drf-mysql-         │
                 │ best-practices.md         │
                 │ (35KB)                    │
                 └───────────────────────────┘
```

## Keyword Matching Algorithm

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Read Context Index                              │
│ Load: context/context-index.yml                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Extract Keywords from Task                      │
│ - Convert task to lowercase                             │
│ - Tokenize into words/phrases                           │
│ - Remove stop words                                     │
│ - Extract relevant technical terms                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Match Keywords to Context Files                 │
│ For each keyword:                                       │
│   Check if keyword in context_file.keywords             │
│   If match: Add context_file to load_list              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 4: De-duplicate and Prioritize                     │
│ - Remove duplicate files                                │
│ - Order by relevance (keyword match count)              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Load Context Files                              │
│ Read each file in load_list                             │
└─────────────────────────────────────────────────────────┘
```

## Context Loading Efficiency

### Token Usage Comparison

```
┌─────────────────────────────────────────────────────────┐
│                   OLD APPROACH (Load All)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DevOps Agent:                                   │  │
│  │  ├─ github-actions.md (52KB)  ◄── Always loaded │  │
│  │  └─ docker.md (25KB)          ◄── Always loaded │  │
│  │  Total: 77KB                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend Agent:                                 │  │
│  │  ├─ react-typescript.md (25KB)  ◄── Always      │  │
│  │  └─ material-ui.md (15KB)       ◄── Always      │  │
│  │  Total: 40KB                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│             NEW APPROACH (Selective Loading)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Task: "Improve CI pipeline"                     │  │
│  │  ├─ github-actions.md (52KB)  ◄── Loaded        │  │
│  │  └─ docker.md (25KB)          ◄── SKIPPED ✓     │  │
│  │  Total: 52KB (32% savings)                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Task: "Create MUI theme"                        │  │
│  │  ├─ react-typescript.md (25KB)  ◄── SKIPPED ✓   │  │
│  │  └─ material-ui.md (15KB)       ◄── Loaded      │  │
│  │  Total: 15KB (63% savings)                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## /implement Command Flow

### Old Flow

```
/implement feature 2
       │
       ├─ Read user-stories.md
       │
       ├─ Story #1: UI Design
       │   └─ Launch ui-ux-designer
       │       └─ Load ALL design context
       │
       ├─ Story #2: Frontend
       │   └─ Launch frontend-developer
       │       └─ Load ALL frontend context (40KB)
       │
       ├─ Story #3: Backend
       │   └─ Launch backend-developer
       │       └─ Load ALL backend context (35KB)
       │
       └─ Story #4: CI/CD
           └─ Launch devops-engineer
               └─ Load ALL devops context (77KB)

Total Context: 152KB
```

### New Flow (Optimized)

```
/implement feature 2
       │
       ├─ Read user-stories.md
       │
       ├─ Story #1: UI Design (Material UI focus)
       │   ├─ Parse keywords: "material ui", "theme"
       │   ├─ Match: material-ui.md
       │   └─ Launch ui-ux-designer
       │       └─ Load ONLY material-ui.md (15KB)
       │
       ├─ Story #2: Frontend (React components)
       │   ├─ Parse keywords: "react components"
       │   ├─ Match: react-typescript.md
       │   └─ Launch frontend-developer
       │       └─ Load react-typescript.md (25KB)
       │
       ├─ Story #3: Backend (Django API)
       │   ├─ Parse keywords: "django api"
       │   ├─ Match: django-drf.md
       │   └─ Launch backend-developer
       │       └─ Load django-drf.md (35KB)
       │
       └─ Story #4: CI/CD (GitHub Actions only)
           ├─ Parse keywords: "github actions", "ci pipeline"
           ├─ Match: github-actions.md
           └─ Launch devops-engineer
               └─ Load github-actions.md (52KB)

Total Context: 127KB (16% savings)

If Story #4 was "Build Docker in CI":
└─ Match: github-actions.md + docker.md
    Total: 152KB (0% savings, both needed)
```

## Summary: Before & After

### Before
```
Agent invoked → Load ALL context/{type}/**/* → Execute task
                        ↑
                  Wasteful for specific tasks
```

### After
```
Agent invoked → Check explicit context
                  ↓ No explicit?
              Analyze keywords
                  ↓ Match?
              Load matched context
                  ↓ No match?
              Load default (all)
                  ↓
              Execute task with optimal context
```

## Key Benefits Visualization

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌───────────────┐                                     │
│  │ Token Savings │ 30-40% for specific tasks           │
│  └───────────────┘                                     │
│                                                         │
│  ┌───────────────┐                                     │
│  │ Better Focus  │ Agent gets exactly what it needs    │
│  └───────────────┘                                     │
│                                                         │
│  ┌───────────────┐                                     │
│  │ Flexibility   │ Explicit, keywords, or default      │
│  └───────────────┘                                     │
│                                                         │
│  ┌───────────────┐                                     │
│  │ Maintainable  │ Central index, easy updates         │
│  └───────────────┘                                     │
│                                                         │
│  ┌───────────────┐                                     │
│  │ Scalable      │ Grows with project complexity       │
│  └───────────────┘                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
