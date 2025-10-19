---
description: Display development metrics including story completion time by agent, feature velocity, quality metrics, and trends
---

# Metrics Command

Generate and display comprehensive development metrics including story completion time, agent performance, feature velocity, quality indicators, and trend analysis.

## Command Syntax

```bash
/metrics [flags]
```

### Flags

- No flags: Display summary report (default)
- `--detailed`: Display comprehensive report with all metrics breakdowns
- `--agent <name>`: Display agent-specific metrics (e.g., `--agent backend-developer`)
- `--trends`: Display trend analysis over time
- `--refresh`: Force metrics recalculation (ignore cache)
- `--export`: Export raw metrics JSON to output

## Error Handling

This command uses comprehensive error handling with specific error codes and recovery suggestions.

**Error Handling Reference**: See `.claude/helpers/command-error-handling.md` for complete error code documentation and `.claude/helpers/error-code-mapping.md` for validation error mapping.

**Common Errors**:
- ENV-001: Git repository not found → Initialize git or navigate to repository
- FS-001: Feature log or implementation logs not found → Run /feature and /implement
- FS-005: Invalid JSON in logs → Fix JSON syntax errors
- DATA-001: Missing required fields in story data → Skip invalid stories
- DATA-004: Invalid timestamp format → Skip stories with invalid timestamps
- FS-004: Cannot write metrics cache → Warning only, continue without cache
- INPUT-002: Invalid agent name → List available agents
- INPUT-006: Unknown flag → Show valid flags

**Error Handling Strategy**:
- All validation errors (Step 0) use standardized error codes
- Feature/implementation log errors are BLOCKING - cannot generate metrics without data
- Invalid JSON in single feature's log is WARNING - skip that feature, process others
- Missing fields in individual stories is WARNING - skip story, process others
- Cache write errors are WARNING - display metrics without caching
- No implementation logs is INFORMATIONAL - display helpful message

## Workflow

### Step 0: Pre-Flight Validation

**0.1 Load error handling and validation systems**

Read error handling system from `.claude/helpers/command-error-handling.md` to understand error codes, categories, and message formats.

Read error code mapping from `.claude/helpers/error-code-mapping.md` to map validation errors to error codes.

Read validation helper from `.claude/helpers/pre-flight-validation.md` to understand validation requirements and error message formats.

All validation errors in subsequent steps should include appropriate error codes from the error code mapping.

**0.2 Validate git repository exists**
Check that `.git/` directory exists.

ERROR if missing:
```
ERROR: Git repository not found
Status: No .git/ directory found in /home/ed/Dev/architecture
Command: /metrics
Remediation:
1. Ensure you are in the architecture project root directory
2. Initialize git repository if needed: git init
3. This command requires a git repository to track metrics
```

**0.3 Validate feature log exists**
Check that `docs/features/feature-log.json` exists and is valid JSON.

ERROR if missing:
```
ERROR: Feature log not found
Status: File does not exist at docs/features/feature-log.json
Command: /metrics
Remediation:
1. Run /feature command to create your first feature
2. Feature log is created automatically during first feature planning
3. Metrics require at least one feature to be tracked
```

ERROR if invalid JSON:
```
ERROR: Feature log has invalid JSON syntax
Status: JSON parse error in docs/features/feature-log.json
Command: /metrics
Remediation:
1. Validate JSON syntax: python3 -m json.tool docs/features/feature-log.json
2. Fix syntax errors identified by validator
3. Common issues: trailing commas, missing quotes, unclosed brackets
```

**0.4 Check for implementation logs**
Search for implementation logs in `docs/features/*/implementation-log.json`.

INFORMATIONAL if none found:
```
INFO: No implementation logs found
Status: No features have been implemented yet
Command: /metrics
Result: Metrics tracking requires at least one implemented story
Next Steps:
1. Run /implement <feature-id> to implement a feature
2. Implementation logs are created automatically during implementation
3. Metrics will be available after first story is completed
```

**0.5 Validation summary**
Display validation results:
```
Pre-Flight Validation: PASSED
✓ Git repository exists
✓ Feature log exists and valid
✓ Found X implementation logs
✓ Ready to generate metrics
```

### Step 1: Parse Command Flags

Parse command arguments to determine report type:
- Default (no flags): `reportType = "summary"`
- `--detailed`: `reportType = "detailed"`
- `--agent <name>`: `reportType = "agent"`, `agentName = <name>`
- `--trends`: `reportType = "trends"`
- `--export`: `exportMode = true`
- `--refresh`: `forceRefresh = true`

If `--agent` flag provided without agent name:
```
ERROR: Missing agent name
Usage: /metrics --agent <agent-name>
Example: /metrics --agent backend-developer

Available agents:
- backend-developer
- frontend-developer
- devops-engineer
- ui-ux-designer
- product-owner
- meta-developer
```

### Step 2: Check Metrics Cache

**2.1 Check for cached metrics**
Look for cached metrics at `docs/metrics/metrics.json`.

**2.2 Check cache freshness**
If cache exists and `--refresh` flag NOT set:
- Read `generatedAt` timestamp from cached metrics
- Calculate age: `now - generatedAt`
- If age < 1 hour: use cached metrics
- If age >= 1 hour: regenerate metrics

**2.3 Decide on cache usage**
- If cache fresh: skip to Step 4 (Display Metrics)
- If cache stale or missing or `--refresh` flag: proceed to Step 3

### Step 3: Generate Metrics

**Load metrics aggregation logic**
Read metrics tracking system documentation from `.claude/helpers/metrics-tracker.md` to understand aggregation workflow and formulas.

**3.1 Discover all implementation logs**

Read feature log (`docs/features/feature-log.json`) to find all features.

For each feature with `userStoriesImplemented != null`:
1. Check for feature implementation log: `docs/features/{featureID}/implementation-log.json`
2. Check for bug implementation logs: `docs/features/{featureID}/bugs/*/implementation-log.json`
3. Add to list of log files to process

Output:
```
Discovering implementation logs...
✓ Found 5 features with implementation data
✓ Collected 10 implementation logs (5 features + 5 bugs)
```

**3.2 Parse and extract story data**

For each implementation log:
1. Read and parse JSON
2. For each story entry, extract:
   - `storyNumber`, `storyTitle`, `agent`, `status`, `completedAt`
   - Count `filesModified` and `filesCreated`
   - Count `actions` array length
   - Count unique items in `toolsUsed` array
   - Count `issuesEncountered` array length
   - Extract feature context (featureID, feature title)
3. Store in aggregated data structure

Keep running count and output progress:
```
Parsing implementation logs...
✓ Processed 45 stories across 10 logs
✓ Found 6 unique agents
✓ Date range: 2025-10-15 to 2025-10-19 (5 days)
```

**3.3 Calculate time-based metrics**

For each feature's stories:
1. Sort stories by `completedAt` timestamp chronologically
2. Estimate start times:
   - First story in feature: use feature `userStoriesCreated` timestamp as start
   - Sequential stories: `startTime = previous story completedAt`
   - Parallel stories (detect by identical/similar completedAt): use phase start (earliest completedAt in group)
3. Calculate `completionTime = completedAt - estimatedStartTime` for each story
4. Sum completion times for feature total duration
5. Calculate story-level and feature-level averages

Note: Store estimated times separately from actual timestamps to preserve data integrity.

**3.4 Aggregate by agent**

Group all stories by `agent` field:

For each agent:
1. Count total stories completed
2. Calculate average completion time (sum of estimated durations / count)
3. Calculate average files modified and created
4. Calculate success rate: `stories with status="completed" / total stories`
5. Sum issues encountered across all stories
6. Identify most used tools (count tool frequency, take top 5)
7. Categorize story types by title keywords:
   - "Create", "Initialize", "Add" → create
   - "Configure", "Set Up", "Setup" → configure
   - "Implement", "Build" → implement
   - "Design" → design
   - Other → other
8. Store in `agentMetrics` array

**3.5 Calculate velocity metrics**

1. Find earliest story `completedAt` across all implementation logs
2. Find latest story `completedAt` across all implementation logs
3. Calculate days in period: `(latestCompletedAt - earliestCompletedAt) / 86400000`
4. Calculate `storiesPerDay = total completed stories / days`
5. Calculate `featuresPerWeek = features with userStoriesImplemented / (days / 7)`
6. Calculate `averageFeatureDuration` from each feature's planning to deployment time
7. Store in `velocityMetrics` object

**3.6 Calculate quality metrics**

1. Calculate `overallIssueRate = stories with issues / total stories`
2. Count retry attempts (stories with `status="failed"` in any log)
3. Calculate `averageFilesPerStory = sum(filesModified + filesCreated) / total stories`
4. Calculate `averageActionsPerStory = sum(action counts) / total stories`
5. Calculate `averageToolsPerStory = sum(unique tool counts) / total stories`
6. Store in `qualityMetrics` object

**3.7 Calculate trend data**

Sort features by implementation completion date.

For each feature in chronological order:
1. Calculate feature-specific `storiesPerDay`
2. Calculate feature-specific `averageStoryTime`
3. Calculate feature-specific `issueRate`
4. Calculate feature-specific `averageFilesPerStory`
5. Store in `trendData` array

Determine trend direction:
- Compare first 2 features vs last 2 features for velocity
- If last > first by >10%: trend = "improving"
- If last < first by >10%: trend = "degrading"
- Otherwise: trend = "stable"

**3.8 Generate summary statistics**

Calculate overall summary:
1. `totalFeatures = count of features in feature log`
2. `totalStories = count of all stories across all logs`
3. `totalCompleted = count of stories with status="completed"`
4. `totalInProgress = count of stories with status="in_progress" or "pending"`
5. `averageStoriesPerFeature = totalStories / totalFeatures`
6. `averageTimePerStory = sum of all estimated durations / totalStories`
7. `overallSuccessRate = totalCompleted / totalStories`
8. Store in `summary` object

**3.9 Write metrics file**

1. Create `docs/metrics/` directory if it doesn't exist
2. Construct complete metrics JSON object with all sections:
   - `generatedAt`: current timestamp (ISO 8601)
   - `periodStart`: earliest story completedAt
   - `periodEnd`: latest story completedAt
   - `summary`: summary statistics object
   - `agentMetrics`: array of agent performance objects
   - `featureMetrics`: array of feature breakdown objects
   - `velocityMetrics`: velocity calculations object
   - `qualityMetrics`: quality indicators object
   - `trendData`: array of trend data points
3. Write to `docs/metrics/metrics.json` with pretty formatting (2-space indent)
4. Validate JSON syntax after write

Output:
```
Generating metrics file...
✓ Created docs/metrics/ directory
✓ Wrote metrics.json (15.2 KB)
✓ Validated JSON syntax
```

### Step 4: Display Metrics Report

Load metrics from `docs/metrics/metrics.json` (either fresh or cached).

**4.1 Summary Report** (default, no flags)

Display comprehensive summary using this format:

```
=================================================================
                    ARCHITECTURE METRICS SUMMARY
=================================================================
Generated: {generatedAt formatted as YYYY-MM-DD HH:MM:SS UTC}
Period: {periodStart} to {periodEnd} ({days} days)

OVERALL PERFORMANCE
-------------------------------------------------------------------
Total Features:                {summary.totalFeatures}
Total Stories:                 {summary.totalStories}
Stories Completed:             {summary.totalCompleted}
Stories In Progress:           {summary.totalInProgress}
Average Stories/Feature:       {summary.averageStoriesPerFeature}
Average Time/Story:            {summary.averageTimePerStory}
Overall Success Rate:          {summary.overallSuccessRate * 100}%

VELOCITY METRICS
-------------------------------------------------------------------
Stories Per Day:               {velocityMetrics.storiesPerDay}
Features Per Week:             {velocityMetrics.featuresPerWeek}
Avg Feature Duration:          {velocityMetrics.averageFeatureDuration}
Trend:                         {velocityMetrics.trendDirection}
                               ↑ IMPROVING / → STABLE / ↓ DEGRADING

QUALITY METRICS
-------------------------------------------------------------------
Overall Issue Rate:            {qualityMetrics.overallIssueRate * 100}%
Retry Count:                   {qualityMetrics.retryCount}
Avg Files/Story:               {qualityMetrics.averageFilesPerStory}
Avg Actions/Story:             {qualityMetrics.averageActionsPerStory}
Avg Tools/Story:               {qualityMetrics.averageToolsPerStory}

TOP PERFORMING AGENTS
-------------------------------------------------------------------
{for top 5 agents by story count:}
{rank}. {agent.name:<25} {agent.storiesCompleted} stories    {agent.averageTimePerStory}    {agent.successRate * 100}% success

=================================================================
Run '/metrics --detailed' for comprehensive metrics
Run '/metrics --agent <name>' for agent-specific metrics
Run '/metrics --trends' for trend analysis
=================================================================
```

**4.2 Detailed Report** (`--detailed` flag)

Display detailed report including summary plus:

```
[Summary section as above]

FEATURE BREAKDOWN
-------------------------------------------------------------------
{for each feature in featureMetrics:}
Feature #{featureID}: {title}
  Stories:           {completedStories} completed
  Duration:          {totalDuration} (avg {averageStoryDuration})
  Agents:            {list of agents with story counts}
  Status:            {state}
  Issue Rate:        {issueRate}%

AGENT PERFORMANCE DETAILS
-------------------------------------------------------------------
{for each agent in agentMetrics:}
Agent: {agent.name}
  Stories Completed:      {storiesCompleted}
  Avg Time/Story:         {averageTimePerStory}
  Avg Files Modified:     {filesModifiedAverage}
  Avg Files Created:      {filesCreatedAverage}
  Success Rate:           {successRate * 100}%
  Issues Encountered:     {issuesEncountered}
  Most Used Tools:        {tool1} ({count1}), {tool2} ({count2}), {tool3} ({count3})
  Story Types:
    - {type1}:            {count1} stories
    - {type2}:            {count2} stories
    [...]

QUALITY BREAKDOWN BY FEATURE
-------------------------------------------------------------------
{for each feature:}
Feature #{featureID}: {issueRate}% issue rate, {retryCount} retries, {avgFilesPerStory} files/story

=================================================================
```

**4.3 Agent-Specific Report** (`--agent <name>` flag)

First validate agent exists in metrics:
```
if agent not found in agentMetrics:
  ERROR: Agent not found in metrics
  Available agents:
  - backend-developer
  - frontend-developer
  [... list all agents found in metrics ...]
```

Display agent-specific report:

```
=================================================================
              AGENT METRICS: {agentName}
=================================================================
Generated: {generatedAt formatted}

OVERALL PERFORMANCE
-------------------------------------------------------------------
Stories Completed:         {storiesCompleted}
Average Time/Story:        {averageTimePerStory}
Success Rate:              {successRate * 100}%
Issues Encountered:        {issuesEncountered} ({issueRate}% issue rate)

STORY BREAKDOWN
-------------------------------------------------------------------
{for each story completed by this agent across all features:}
Story #{storyNumber}: {storyTitle}
  Feature:         {featureID}
  Duration:        {estimatedDuration}
  Files Modified:  {filesModified.length}
  Files Created:   {filesCreated.length}
  Actions:         {actions.length}
  Tools:           {toolsUsed.join(", ")}
  Issues:          {issuesEncountered.length > 0 ? list them : "None"}
  Status:          {status === "completed" ? "✓ Completed" : "✗ Failed"}

COMPLEXITY METRICS
-------------------------------------------------------------------
Avg Files Modified:        {filesModifiedAverage}
Avg Files Created:         {filesCreatedAverage}
Total Files Changed:       {sum of all files modified and created}
Avg Actions/Story:         {average actions per story}
Avg Tools/Story:           {average unique tools per story}

TOOL USAGE
-------------------------------------------------------------------
{for each tool in mostUsedTools:}
{tool}:                    {count} stories ({percentage}%)

STORY TYPE DISTRIBUTION
-------------------------------------------------------------------
{for each story type:}
{type}:                    {count} stories ({percentage}%)

TREND ANALYSIS
-------------------------------------------------------------------
First {N} Stories:         {averageTime} avg
Last {N} Stories:          {averageTime} avg
Improvement:               {percentage change} {↑ faster / ↓ slower / → stable}

=================================================================
```

**4.4 Trends Report** (`--trends` flag)

Display trend analysis:

```
=================================================================
                    METRICS TREND ANALYSIS
=================================================================
Generated: {generatedAt formatted}

VELOCITY TRENDS
-------------------------------------------------------------------
{for each feature in chronological order:}
Feature #{featureID}:  {storiesPerDay} stories/day   {avgStoryTime}
                       {if not first: show % change and direction}

Trend Direction:  {↑ IMPROVING / → STABLE / ↓ DEGRADING} ({overall % change})

QUALITY TRENDS
-------------------------------------------------------------------
{for each feature:}
Feature #{featureID}:  {issueRate}% issue rate    {avgFilesPerStory} files/story
                       {if not first: show change}

Trend Direction:  {↑ IMPROVING / → STABLE / ↓ DEGRADING} ({overall avg issue rate})

AGENT EFFICIENCY TRENDS
-------------------------------------------------------------------
{for each agent with >5 stories:}
{agent.name}:
  Early Stories:   {first 30% avg time}
  Recent Stories:  {last 30% avg time}
  Improvement:     {percentage change} {↑ faster / ↓ slower / → stable}

COMPLEXITY TRENDS
-------------------------------------------------------------------
{for each feature:}
Feature #{featureID}:  {avgFiles} files/story   {avgActions} actions/story
                       {if not first: ↑ More complex / ↓ Simpler / → Stable}

Trend Direction:  {↑ INCREASING / → STABLE / ↓ DECREASING} (avg {value} files/story)

=================================================================
```

**4.5 Export Mode** (`--export` flag)

If `--export` flag is set:
1. Read metrics JSON from `docs/metrics/metrics.json`
2. Output raw JSON to stdout (no formatting, just the JSON object)
3. Do NOT display any other output (no headers, no summaries)

This allows piping to other tools:
```bash
/metrics --export > metrics-export.json
/metrics --export | python3 analysis-script.py
```

### Step 5: Report Summary

After displaying metrics report (except in export mode):

```
Metrics Report Complete
-------------------------------------------------------------------
Report Type:        {summary / detailed / agent / trends}
Stories Analyzed:   {totalStories}
Date Range:         {periodStart} to {periodEnd} ({days} days)
Cache Status:       {fresh / regenerated}
Generated At:       {timestamp}

{if not using cache:}
✓ Metrics cached at docs/metrics/metrics.json (valid for 1 hour)

Available Commands:
- /metrics --detailed          Comprehensive breakdown
- /metrics --agent <name>      Agent-specific analysis
- /metrics --trends            Trend analysis over time
- /metrics --refresh           Force recalculation
- /metrics --export            Export raw JSON
```

## Error Handling

### Missing Implementation Logs
If feature has `userStoriesImplemented` timestamp but no implementation log:
```
WARNING: Missing implementation log for Feature #{featureID}
Expected: docs/features/{featureID}/implementation-log.json
Impact: Feature will be excluded from metrics
Action: Verify implementation log exists or update feature log status
```

Continue processing other features (don't fail entire metrics generation).

### Invalid JSON in Implementation Log
If implementation log has invalid JSON:
```
WARNING: Invalid JSON in implementation log
File: docs/features/{featureID}/implementation-log.json
Error: {JSON parse error message}
Impact: Feature will be excluded from metrics
Action: Validate and fix JSON syntax
```

Continue processing other features.

### Missing Required Fields
If story entry is missing required fields (`storyNumber`, `agent`, `status`):
```
WARNING: Incomplete story data
File: docs/features/{featureID}/implementation-log.json
Story: {storyNumber or index}
Missing: {list of missing fields}
Impact: Story will be excluded from metrics
```

Skip the story, continue with others.

### Invalid Timestamps
If `completedAt` is not a valid ISO 8601 timestamp:
```
WARNING: Invalid timestamp
File: docs/features/{featureID}/implementation-log.json
Story: {storyNumber}
Value: {completedAt value}
Impact: Story completion time cannot be calculated
```

Include story in counts but exclude from time-based metrics.

### Division by Zero
If calculations would result in division by zero (e.g., 0 stories, 0 days):
- Use "N/A" or 0 in report
- Add note: "Insufficient data for calculation"

### File System Errors
If unable to write metrics cache:
```
WARNING: Cannot write metrics cache
Error: {error message}
Impact: Metrics will be recalculated on every run (slower)
Action: Check write permissions on docs/metrics/ directory
```

Continue displaying metrics (don't fail the command).

## Integration Points

### Related Commands

- `/feature`: Creates features tracked in metrics
- `/implement`: Creates implementation logs analyzed for metrics
- `/summarise`: Updates feature state affecting metrics

### Data Dependencies

- **Feature Log** (`docs/features/feature-log.json`): Feature metadata and timestamps
- **Implementation Logs** (`docs/features/*/implementation-log.json`): Story completion data
- **Bug Logs** (`docs/features/*/bugs/*/implementation-log.json`): Bug fix data

### Helper Files

- `.claude/helpers/metrics-tracker.md`: Metrics schema and calculation formulas
- `.claude/helpers/pre-flight-validation.md`: Validation functions

## Best Practices

### When to Use

1. **After implementing features**: Track velocity and identify bottlenecks
2. **Weekly**: Monitor trends and team performance
3. **Before planning**: Estimate capacity based on historical velocity
4. **After issues**: Analyze quality metrics and improvement areas

### Interpreting Results

#### Velocity Metrics
- High stories/day indicates good throughput
- Check quality metrics to ensure speed doesn't sacrifice quality
- Improving trend shows team efficiency gains

#### Quality Metrics
- Issue rate <5% is excellent
- Issue rate >15% may indicate story atomicity problems
- High avg files/story suggests stories may be too large

#### Agent Metrics
- Compare time/story across agents to identify expertise areas
- High tool usage may indicate complex implementation
- Success rate should be >90% for most agents

### Optimization

- Use `--refresh` sparingly (metrics cache reduces load)
- Use `--export` for custom analysis or dashboards
- Use agent-specific reports to identify training needs
- Use trends report to track improvement initiatives

## Examples

### Example 1: Quick Overview
```
User: /metrics
System: Displays summary report with overall performance, velocity, quality, and top agents
```

### Example 2: Deep Dive
```
User: /metrics --detailed
System: Displays comprehensive report with feature breakdowns, agent details, and quality analysis
```

### Example 3: Agent Analysis
```
User: /metrics --agent backend-developer
System: Displays all stories completed by backend-developer with complexity and tool usage analysis
```

### Example 4: Track Progress
```
User: /metrics --trends
System: Shows how velocity and quality have changed across features over time
```

### Example 5: Export for Analysis
```
User: /metrics --export > analysis/metrics.json
System: Exports raw metrics JSON for use with external analytics tools
```

### Example 6: Force Refresh
```
User: /metrics --refresh --detailed
System: Regenerates metrics from scratch and displays detailed report
```

## Notes

- Metrics are estimated based on available timestamp data
- Story start times are estimated (not tracked explicitly)
- Parallel stories are detected heuristically
- Cache expires after 1 hour to balance performance and accuracy
- All durations are estimated (actual time may vary with interruptions)

## Version History

- v1.0.0 (2025-10-19): Initial metrics command
  - Summary, detailed, agent, and trends reports
  - Metrics caching with 1-hour expiration
  - Export capability for external analysis
  - Comprehensive error handling
