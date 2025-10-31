# Claude Code Agent Definitions: Comprehensive Best Practices Guide

**Date**: 2025-10-31
**Purpose**: Establishing authoritative best practices for structuring agent definitions in Claude Code environments, covering format, prompts, capabilities, scope, patterns, inter-agent communication, performance, and maintainability.

---

## Summary

Claude Code agents are specialized AI assistants defined through Markdown files with YAML frontmatter, operating with isolated context windows and curated tool permissions. The recommended approach prioritizes **single-responsibility design**, **token optimization**, **explicit tool scoping**, and **layered context engineering** through progressive disclosure. Effective agent definitions combine clear system prompts with carefully managed capabilities, hierarchical documentation via CLAUDE.md files, and multi-agent coordination patterns that emphasize human-in-the-loop control. The evolution from prompt engineering to **agent engineering** represents a fundamental shift toward designing reusable, composable specialists rather than monolithic generalists.

---

## Key Facts

### 1. Agent Definition File Structure

**File Format & Location** (verified: Anthropic docs, ClaudeLog)
- Agents are defined as Markdown files with YAML frontmatter stored in `.claude/agents/` directories
- Project-level agents: `.claude/agents/agent-name.md`
- User-level agents: `~/.claude/agents/agent-name.md`
- File structure is intentionally minimal—single Markdown file makes agents highly portable and version-controllable

**Required YAML Frontmatter** (verified: Anthropic, ClaudeLog)
- `name` (required): Identifies the agent—kept concise for rapid invocation
- `description` (required): Action-oriented description explaining agent's purpose; Claude uses this to decide activation
- `tools` (optional): Explicit list of allowed tools; **if omitted, agent gets access to ALL available tools** (security risk)

**System Prompt Location** (verified: Anthropic, ClaudeLog)
- System prompt follows the YAML frontmatter in the same Markdown file
- Prompt follows immediately after the closing `---` delimiter
- No separate prompt files—everything in one portable document

### 2. Recommended Agent Architecture Patterns

**Single Responsibility Principle** (verified: PubNub blog, Anthropic, ClaudeLog)
- Each agent should have one clear goal with defined inputs, outputs, and handoff rules
- Specialized agents outperform generalists; narrow focus improves tool selection accuracy
- Design focused, single-purpose agents initially—expand scope only through experimentation

**The Feedback Loop Structure** (verified: Anthropic Agent SDK docs)
1. **Gather Context**: Agent fetches and organizes relevant information
2. **Take Action**: Agent executes tasks using assigned tools
3. **Verify Work**: Agent evaluates output and flags issues before handoff

This loop maps directly to multi-phase workflows in broader systems.

**Three-Stage Pipeline Pattern** (verified: PubNub blog)
For complex projects, use role-based agent chains:
1. **PM Spec Agent** (high-level): Outputs structured requirements and acceptance criteria
2. **Architecture Agent** (mid-level): Produces decision records and validation
3. **Implementer Agent** (low-level): Delivers code with passing tests and documentation

Each stage has isolated context; humans explicitly trigger progression via hooks.

### 3. Token Optimization & Model Economics

**Initialization Cost Tiers** (verified: ClaudeLog agent engineering)
- **Lightweight agents**: < 3,000 tokens (minimal or no tools, focused prompts)
- **Medium-weight agents**: 10,000–15,000 tokens (5-8 tools, moderately detailed prompts)
- **Heavy agents**: 25,000+ tokens (15+ tools, extensive reference documentation)

**Model Selection Based on Use Case** (verified: ClaudeLog, 2025)
- **Haiku 4.5**: Recommended for frequent-use agents; achieves 90% of Sonnet 4.5's agentic coding performance at 2x speed and 3x cost savings
- **Sonnet 4.5**: Recommended for orchestration agents and final validation; better at complex reasoning
- **Extended Thinking**: Use trigger words ("think," "think hard," "think harder") to allocate progressively larger computation budgets (4k → 10k → 32k tokens)

**Token Efficiency Principle** (verified: ClaudeLog)
Minimize initialization tokens for frequently-invoked agents. Careful prompt engineering in YAML descriptions and system prompts directly impacts both cost and responsiveness. Test agents in isolation to measure actual token consumption before deployment.

### 4. Tool Permissions & Capability Design

**Permission Model: Deny-All by Default** (verified: Anthropic docs, PubNub, Steve Kinney)
- Start with explicit empty tool list or minimal toolset
- Allowlist only the commands and directories an agent actually needs
- This prevents "permission sprawl"—the fastest path to unsafe autonomy
- Treat agent permissions like production IAM policies

**Tool Configuration Methods** (verified: Anthropic docs)
1. In-session "Always allow" selections
2. `/permissions` command within Claude Code
3. Manual JSON editing of agent definitions
4. CLI flags at invocation time

**Tool Scope Matrix** (verified: Anthropic, Steve Kinney, PubNub)

| Agent Type | Typical Tools | Read/Write Ratio | Examples |
|---|---|---|---|
| **Research/Reviewer** | agentic-search, file-read, semantic-search | 100% read | Code reviewers, analysts, documentation readers |
| **Implementer/Writer** | bash, file-edit, git, custom tools | 40% read / 60% write | Developers, content creators, data processors |
| **Orchestrator** | bash, git, custom delegation tools | Mixed | Project managers, pipeline coordinators |

### 5. System Prompt Best Practices

**Specificity Over Vagueness** (verified: Anthropic docs)
- Instead of: "Add tests for the authentication module"
- Use: "Write test cases covering: (1) logged-out user scenario, (2) invalid token handling, (3) expired session refresh. Avoid mocks; use integration test patterns with database transactions."
- Explicit constraints and edge cases reduce iteration cycles

**Prompt Engineering Hierarchy** (verified: Claude Docs)
In order of effectiveness:
1. **Clear, direct instructions** - Foundational; be unambiguous about agent responsibilities
2. **Examples (multishot prompting)** - Show 3-5 examples of correct behavior
3. **Chain-of-thought reasoning** - Ask agent to "think through the problem step by step"
4. **XML tags for structure** - Use `<task>`, `<constraints>`, `<output_format>` for clarity
5. **Role-based framing** - "You are a senior architect reviewing this design" establishes behavioral context

**System Prompt Structure Template** (verified across sources):
```markdown
# [Agent Name]

description: [Action-oriented, one sentence]
name: [Concise identifier]
tools: [Explicit list or omit if multiple needed]

---

## Role & Context
You are a [specific role] responsible for [clear scope]. You work within a [team structure/project context].

## Key Responsibilities
- [Specific responsibility with success criteria]
- [Another responsibility]
- [Constraint or limitation]

## Decision-Making Framework
When faced with [scenario type], you should [approach]. Prioritize [criteria] over [alternatives].

## Tool Usage Guidelines
- [Tool name]: Use when [specific condition]. Output format: [expected structure]
- [Another tool]: Used for [purpose], avoid [anti-pattern]

## Communication Protocol
- If uncertain, ask clarifying questions rather than assuming
- Always verify [critical action] before execution
- Report progress as [format expected by handoff point]

## Examples
[Show 1-3 examples of correct behavior in the agent's domain]
```

### 6. Prompt Activation & Tool SEO

**"Tool SEO" Principle** (verified: ClaudeLog)
- Include activation trigger phrases like "use PROACTIVELY" or "MUST BE USED" in agent descriptions
- Claude uses agent descriptions to decide activation; more specific descriptions activate more reliably
- Example description: "Code reviewer—PROACTIVELY reviews all pull requests for security vulnerabilities, performance issues, and architectural consistency"

**Activation Reliability Issues** (verified: Steve Kinney)
- Inconsistent triggering: Claude frequently overlooks appropriate agents unless explicitly named
- Fire-and-forget delegation remains unreliable; auto-selection only fires sometimes
- Narrow trigger patterns: Agents for highly specific scenarios may never activate
- **Mitigation**: Make descriptions broader and include action keywords; test activation patterns explicitly

### 7. CLAUDE.md: Hierarchical Context Engineering

**Purpose & Scope** (verified: Anthropic docs)
- Special file Claude Code automatically pulls into context on every invocation
- Encodes project conventions, test commands, directory layout, architecture notes
- Ensures agents converge on shared standards without explicit repetition

**Hierarchical Application** (verified: Anthropic, ClaudeLog)
Claude reads CLAUDE.md files in this order (most specific wins):
1. `~/.claude/CLAUDE.md` (user home)
2. `./CLAUDE.md` (project root)
3. Nested directory-specific files (for subdirectories)
4. Most specific, most nested file takes priority

**Recommended Content** (verified: Anthropic, multiple sources):
- **Branch naming conventions**: "Use `feature/`, `bugfix/`, `docs/` prefixes"
- **Merge vs. rebase policy**: "Rebase feature branches; merge to main with merge commits"
- **Test commands**: "Run `pytest tests/` before committing; coverage must exceed 85%"
- **Code style standards**: "Use Black formatter; max line length 100; type hints required"
- **Directory layout**: "Source code in `src/`, tests in `tests/`, docs in `docs/`"
- **Architecture notes**: "Database migrations in `migrations/`; follow Alembic patterns"
- **Unexpected behaviors**: "PostgreSQL slow on M1 Macs without optimization; see [link]"
- **Environment setup**: "Use `pyenv` for Python; `nvm` for Node; run `make setup`"

**Evolution Through Iteration** (verified: Steve Kinney)
- Don't create CLAUDE.md once and ignore it—treat as continuously refined prompt
- Experiment with what produces the best instruction following
- Run through prompt improvers; add emphasis keywords ("IMPORTANT," "YOU MUST") to strengthen adherence
- Monitor actual Claude behavior and adjust accordingly

### 8. Agent Capabilities Definition

**Core Capability Types** (verified: Anthropic Agent SDK docs)

1. **Context Management Tools**
   - Agentic search (broad file system queries)
   - Semantic search (specific content matching)
   - Subagents for parallel processing
   - Automatic context compaction for large codebases

2. **Execution Tools**
   - Custom tools (agent-specific executables)
   - Bash scripts (general-purpose computing)
   - Code generation (for complex, reusable operations)
   - Model Context Protocol (MCP) integrations (external services)

3. **Verification Methods**
   - Rule-based feedback (linting, static analysis)
   - Visual feedback (screenshots, diffs)
   - LLM-as-judge evaluation (Claude reviewing Claude's work)

**Tool Design Principles** (verified: Armin Ronacher, Anthropic)
- **Speed matters most**: Fast tool execution with minimal useless output beats feature-rich but slow tools
- **Clear error messages**: Agents understand when misuse occurs and adjust behavior
- **Robustness**: Tools must handle unexpected usage patterns gracefully
- **Comprehensive logging**: Critical for debugging; agents read logs to diagnose issues independently

### 9. Multi-Agent Coordination & Specialization

**Automatic Delegation Pattern** (verified: Anthropic, ClaudeLog)
- Orchestrator agents intelligently route tasks to specialists based on task descriptions
- No manual invocation required—Claude decides which agent to use
- Isolated context windows prevent context poisoning between different tasks
- Each agent operates independently, reducing memory overhead

**Human-in-the-Loop Integration** (verified: PubNub blog)
- Rather than autonomous chains, use hooks to suggest next steps
- Humans must explicitly paste commands before proceeding (prevents runaway automation)
- Use lifecycle hooks (SubagentStop, Stop) that read queue files and print suggested next commands
- Creates auditable trails: status transitions, design decisions, proof of testing

**Artifact Tracking Across Agents** (verified: PubNub)
- Use consistent "slugs" (identifiers) across queues, working notes, and Architecture Decision Records (ADRs)
- Example: `FEATURE-42-auth-refactor` used in PR title, ADR filename, queue entries
- Enables traceability from specification through implementation and verification

**Parallel Processing Pattern** (verified: Anthropic docs)
- Run separate Claude instances with independent contexts (one writing code, another reviewing)
- Use git worktrees for isolated branches without merge conflicts
- Enables simultaneous progress on different tasks without context contamination

### 10. Common Anti-Patterns to Avoid

**Activation Problems** (verified: Steve Kinney)
- ❌ Inconsistent triggering: Claude ignores agents even with solid descriptions
- ❌ Narrow triggers: Agents designed for overly specific scenarios never activate
- **Fix**: Make descriptions broader, include action keywords, test explicitly

**State & Context Issues** (verified: Steve Kinney)
- ❌ Lost context on rejection: System spawns fresh agent instance; all specialized context vanishes
- ❌ No interactive dialogue: Cannot ask clarifying questions mid-execution
- **Fix**: Design for iterative improvement, not one-shot execution

**Scaling Failures** (verified: Steve Kinney, ClaudeLog)
- ❌ Token consumption: Large agent fleets (10-15+) exceed 200k token budgets; exceed 1 hour execution
- ❌ Performance dilution: Overlapping agent responsibilities cause ping-ponging and duplicate work
- ❌ Verbose auto-generated prompts: `/agents` wizard creates sprawling prompts consuming context
- **Fix**: Start with lightweight, focused agents; use Haiku 4.5 for frequent-use agents

**Tool & Permission Issues** (verified: Steve Kinney, Anthropic)
- ❌ Tool-scope confusion: Granting all agents access to all tools creates noise
- ❌ Permission sprawl: Fastest path to unsafe autonomy
- **Fix**: Explicit deny-all, allowlist only necessary tools; review quarterly

**Documentation Mistakes** (verified: Steve Kinney, multiple sources)
- ❌ No CLAUDE.md: Claude behaves inconsistently like working with different developers
- ❌ Static documentation: CLAUDE.md created once, never iterated on
- ❌ Pattern drift: Architectural standards gradually erode; violation frequency grows exponentially with codebase size
- **Fix**: Treat documentation as continuously refined; emphasize standards in system prompts

**Output & Definition Issues** (verified: Steve Kinney)
- ❌ Shallow outputs: Well-configured agents return single-sentence verdicts instead of requested deep analysis
- ❌ Tool confusion: Agents misuse tools, producing errors that compound over time
- **Fix**: Include concrete verification methods; ask agents to check their own work before handoff

### 11. Agent Scope & Specialization Guidelines

**When to Create a New Agent** (verified: ClaudeLog, Anthropic)
- ✅ Clear responsibility boundary that differs from existing agents
- ✅ Specialized tool requirements (e.g., always needs database access, never needs git)
- ✅ Different decision-making framework or expertise domain
- ✅ Frequent enough to benefit from persistent context
- ❌ Overlapping responsibilities with existing agents (causes ping-ponging)
- ❌ Tools available to only one agent (centralize if possible)

**Scope Definition Matrix** (verified across sources):

| Dimension | Narrow Scope | Broad Scope |
|---|---|---|
| **Responsibility** | One specific task type | Multiple related task types |
| **Tools** | 2-4 focused tools | 10+ diverse tools |
| **Activation** | Highly specific conditions | Broad range of conditions |
| **Token Weight** | Lightweight (< 3k tokens) | Heavy (25k+ tokens) |
| **Recommended Use** | Frequent invocation | Rare, complex orchestration |

**Specialization Example: Three-Tier System** (verified: PubNub, Anthropic)

1. **Spec Agent** (Lightweight, Haiku 4.5)
   - Responsibility: Parse requirements, clarify ambiguities
   - Tools: agentic-search, file-read, CLAUDE.md access
   - Scope: Requirements discovery and documentation only
   - Output: Structured requirement document with acceptance criteria

2. **Architecture Agent** (Medium, Sonnet 4.5)
   - Responsibility: Design systems, make technology decisions
   - Tools: bash (no write), code-search, codebase-analysis
   - Scope: Technical design and validation
   - Output: Architecture Decision Record (ADR) with trade-off analysis

3. **Implementer Agent** (Medium, Haiku 4.5 or Sonnet)
   - Responsibility: Write and test code
   - Tools: bash, file-edit, git, custom-test-runner
   - Scope: Code implementation only
   - Output: Passing tests, clean code, ready-to-merge commits

### 12. Performance & Efficiency Considerations

**Initialization Speed Optimization** (verified: ClaudeLog)
- Each tool in agent definition adds initialization overhead
- Test agents in isolation to measure actual token consumption before deployment
- Lightweight agents (< 3k tokens) initialize in seconds; heavy agents (25k+) may take minutes
- Use Haiku 4.5 as default for frequent-use agents; switch to Sonnet only when necessary

**Context Window Management** (verified: Anthropic, ClaudeLog)
- Subagents have isolated context windows, separate from delegating agent
- Prevents context poisoning; enables larger projects without global context explosion
- Automatic context compaction available when limits approach
- Use `agentic-search` as default (fast, efficient); add `semantic-search` only if performance bottlenecks emerge

**Extended Thinking Allocation** (verified: Simon Willison, Anthropic docs)
Trigger words automatically allocate extended thinking budgets:
- `"think"` → 4,000 tokens of reasoning
- `"think hard"` → 10,000 tokens
- `"think harder"` → 31,999 tokens (maximum)
- `"ultrathink"` → 31,999 tokens

Use sparingly for agents that need complex reasoning; automatic thinking increases latency.

**Parallel vs. Sequential Execution** (verified: Anthropic)
- **Parallel**: Multiple agents with isolated contexts (faster, higher cost)
- **Sequential**: Agents pass context via files/ADRs (slower, lower cost)
- Choose based on latency budget and cost constraints

### 13. Documentation & Maintainability Best Practices

**In-Code Documentation Standards** (verified: Anthropic, ClaudeLog)
- System prompts should be self-documenting (clear structure, explicit constraints)
- Include examples of correct behavior within system prompt
- Document decision-making framework explicitly—why this agent makes certain choices
- Reference external documentation (CLAUDE.md, ADRs) rather than duplicating

**Versioning & Change Management** (verified: Anthropic)
- Store agent definitions in git alongside code
- Treat agent changes like code changes: review, test, document
- Include changelog entries when modifying agent behavior
- Tag stable agent versions if distributed to teams

**Testing Agents in Isolation** (verified: Steve Kinney, Anthropic)
- Test agent activation triggers explicitly (ensure it fires when expected)
- Test tool selection accuracy (agent chooses correct tools for task types)
- Test output quality and format compliance
- Compare performance across model versions (Haiku vs. Sonnet)
- Benchmark token consumption and latency

**Skill System for Reusable Capability Bundles** (verified: Anthropic, ClaudeLog)
Skills are "organized directories containing instructions, scripts, and resources":
- **SKILL.md**: Contains metadata (name, description) and core prompt
- **scripts/**: Executable Python/Bash scripts for specific tasks
- **references/**: Documentation loaded into context as needed
- **assets/**: Templates and binary files

**Progressive Disclosure Design** (verified: Anthropic):
- Level 1: Metadata (name/description) always pre-loaded
- Level 2: Full SKILL.md content loaded when Claude determines relevance
- Level 3+: Referenced files loaded only as needed

This design allows unbounded context since agents with filesystem access don't need everything simultaneously.

---

## Analysis

The research reveals that Claude Code agent engineering represents a paradigm shift from **monolithic prompt optimization** to **composable, specialized agent systems**. Three key insights emerge:

**1. Structural Simplicity as Feature**: The single Markdown file with YAML frontmatter design is intentionally minimal, making agents instantly portable, git-trackable, and shareable. This contrasts with complex configuration systems; Claude Code prioritizes simplicity for team collaboration and version control.

**2. Token Efficiency as Strategic Concern**: With Haiku 4.5's 2024-2025 introduction, token optimization moved from "nice-to-have" to essential. The shift from Sonnet-exclusive to Haiku-primary for frequent agents (saving 3x cost while maintaining 90% performance) fundamentally changes agent architecture decisions. Lightweight agents (< 3k tokens) are now preferred over monolithic ones.

**3. Security Through Explicit Permission Scoping**: The "deny-all by default" permission model treats agent access like production infrastructure—not ad-hoc tool access. This directly addresses the most common scaling failure: permission sprawl leading to unsafe autonomy. The research emphasizes that early permission granularity prevents exponential complexity later.

The multi-agent coordination patterns (three-tier pipeline, human-in-the-loop hooks, artifact tracking) represent learned solutions to real failures documented in production systems. Organizations that implement these patterns report better traceability, fewer runaway automation incidents, and improved iteration cycles.

---

## Action Items

### Immediate (Setup & Foundation)

1. **Create a standard agent template** in your project
   - Save as `.claude/agents/_template.md`
   - Include: role definition, responsibility section, decision-making framework, tool usage guidelines, examples
   - Use this template for all new agents to ensure consistency

2. **Establish a comprehensive CLAUDE.md** in your project root
   - Include: branch naming, merge policy, test commands, code style, directory layout, architecture notes
   - Iterate on effectiveness over 2-3 weeks; add emphasis keywords ("IMPORTANT") for critical standards
   - Commit to git; review quarterly for drift

3. **Audit existing agent permissions**
   - For each agent in `.claude/agents/`, review the `tools:` field
   - Remove agents with `tools:` omitted (these get ALL tools—potential security risk)
   - Document rationale for each allowed tool in comments

### Short-term (Optimization & Testing)

4. **Measure and optimize agent initialization costs**
   - Run each agent in isolation with token counting enabled
   - Record: initialization tokens, execution tokens, total latency
   - For agents > 10k tokens, investigate prompt compression opportunities
   - Establish baseline to detect performance regressions

5. **Implement a three-tier agent architecture** if using multi-agent workflows
   - **Tier 1 (Spec/Research)**: Lightweight, read-only, Haiku 4.5
   - **Tier 2 (Architecture)**: Medium-weight, analysis-focused, Sonnet 4.5
   - **Tier 3 (Implementation)**: Medium-weight, execution-focused, Haiku 4.5 or Sonnet
   - Define handoff points and output formats for each tier

6. **Test agent activation reliability**
   - Create test scenarios for each agent
   - Verify: agent activates when expected, activates with consistent behavior, produces requested output format
   - If inconsistent, broaden description and add action keywords ("PROACTIVELY," "MUST BE USED")

### Medium-term (Documentation & Patterns)

7. **Document agent roles and responsibilities**
   - Create a AGENTS.md file listing all agents, their scope, tools, and when to invoke them manually
   - Include examples: "Use [AgentName] when..." for each agent
   - Commit alongside agent files for team reference

8. **Establish inter-agent communication protocol**
   - Define artifact format (markdown, JSON, structured ADRs) for agent handoffs
   - Use consistent "slugs" (identifiers) across multiple agents working on same task
   - Document: which agents produce which artifacts, expected fields, validation rules

9. **Implement agent verification patterns**
   - For critical agents, add verification steps: "Review your work against these criteria before handoff"
   - Use rule-based feedback (linting, unit tests) where possible
   - Consider LLM-as-judge for subjective quality (e.g., code review agent reviewing another agent's code)

10. **Build team-shared agent library** (if distributed team)
    - Store approved agents in centralized location (shared `.claude/agents/` directory or repository)
    - Include: system prompt, usage guide, known limitations, change history
    - Establish review process for new agents before team adoption

### Long-term (Scaling & Evolution)

11. **Monitor for pattern drift** in codebase standards adherence
    - Quarterly review: Are teams following architectural standards encoded in CLAUDE.md?
    - Add emphasis to CLAUDE.md sections with drifting standards
    - Consider augmenting agents with explicit checks for common violations

12. **Evaluate agent fleet performance**
    - Collect metrics: activation frequency, token consumption, handoff success rate, iteration count
    - Identify underutilized agents (candidates for deprecation)
    - Identify overloaded agents (candidates for splitting into specialists)

13. **Invest in custom tools for agent efficiency**
    - Prioritize tools that solve repeated friction points
    - Design for speed and clear error messaging (agents learn from errors)
    - Log comprehensive debugging information; agents read logs to self-diagnose

---

## Sources

1. **Claude Code Best Practices** (Anthropic, 2025)
   - https://www.anthropic.com/engineering/claude-code-best-practices
   - Authoritative guidance on environment configuration, multi-phase workflows, tool integration

2. **Building Agents with the Claude Agent SDK** (Anthropic, 2025)
   - https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
   - Core architecture patterns: gather context, take action, verify work feedback loop

3. **Equipping Agents for the Real World with Agent Skills** (Anthropic, 2025)
   - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
   - Progressive disclosure design, SKILL.md structure, skill organization patterns

4. **ClaudeLog - Custom Agents** (ClaudeLog, 2025)
   - https://claudelog.com/mechanics/custom-agents/
   - Practical definition structure, YAML frontmatter requirements, activation patterns

5. **ClaudeLog - Agent Engineering** (ClaudeLog, 2025)
   - https://claudelog.com/mechanics/agent-engineering/
   - Token optimization tiers, Haiku 4.5 cost/performance trade-offs, agent classification matrix

6. **Best Practices for Claude Code Subagents** (PubNub, 2024)
   - https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/
   - Multi-agent workflows, three-stage pipeline, human-in-the-loop integration, artifact tracking

7. **Common Sub-Agent Anti-Patterns and Pitfalls** (Steve Kinney, 2024)
   - https://stevekinney.com/courses/ai-development/subagent-anti-patterns
   - Documented failures: activation issues, state loss, scaling challenges, documentation mistakes

8. **Claude Code: Best Practices for Agentic Coding** (Simon Willison, 2025)
   - https://simonwillison.net/2025/Apr/19/claude-code-best-practices/
   - Extended thinking allocation patterns, trigger word mechanisms

9. **Agentic Coding Recommendations** (Armin Ronacher, 2025)
   - https://lucumr.pocoo.org/2025/6/12/agentic-coding/
   - Tool design principles, code quality standards, operational practices for agent compatibility

10. **Prompt Engineering Overview** (Claude Docs, 2025)
    - https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
    - Foundational prompt engineering hierarchy, techniques in order of effectiveness

---

## Caveats

**Agent Activation Remains Probabilistic**: Despite best practices, Claude's agent selection is not deterministic. Even well-configured agents with clear descriptions may not activate reliably unless explicitly named. The research recommends testing activation patterns explicitly rather than assuming descriptions alone guarantee invocation.

**Limited Research on Cross-Organization Agent Sharing**: While documentation covers internal team patterns, there is limited guidance on distributing agents across organizations or managing breaking changes in shared agent libraries. The field is still evolving; treat agent versioning guidance as provisional.

**Extended Thinking Overhead Not Fully Quantified**: While trigger words for extended thinking are documented, the research does not provide comprehensive latency/cost trade-off analysis for agents using "think harder" vs. standard reasoning. Benchmark these patterns in your specific use case before adoption at scale.

**Token Efficiency Data is Model-Specific**: The Haiku 4.5 cost/performance advantages referenced (3x savings, 90% performance) are specific to October 2025 pricing. As model costs and capabilities evolve, re-baseline these assumptions quarterly.
