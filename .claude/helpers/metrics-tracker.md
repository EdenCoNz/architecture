# Metrics Tracking System

## Purpose

This document defines the metrics tracking and analysis system for the architecture automation project. The system aggregates data from implementation logs and feature logs to provide insights into development velocity, agent performance, story complexity, and quality metrics.

## Metrics Schema

### Core Metrics Categories

#### 1. Story Completion Metrics
- **Story completion time**: Duration from story start to completion
- **Agent attribution**: Which agent completed each story
- **Story complexity**: File counts, action counts, tools used
- **Success rate**: Percentage of stories completed without retries
- **Error rate**: Percentage of stories that encountered issues

#### 2. Feature Velocity Metrics
- **Stories per feature**: Average number of stories per feature
- **Stories per day**: Implementation throughput over time
- **Features per week**: Feature completion rate
- **Time per feature**: Average duration from planning to deployment
- **Time per story**: Average duration per story by agent

#### 3. Agent Performance Metrics
- **Stories completed by agent**: Total count per agent
- **Average time per story by agent**: Performance comparison
- **Agent utilization**: Distribution of work across agents
- **Agent success rate**: Percentage of stories completed successfully
- **Agent expertise areas**: Most common story types per agent

#### 4. Quality Metrics
- **Issues encountered rate**: Percentage of stories with issues
- **Retry count**: How many stories required rework
- **Files modified per story**: Scope indicator
- **Tools used per story**: Complexity indicator
- **Actions per story**: Work volume indicator

#### 5. Trend Metrics
- **Velocity over time**: How throughput changes across features
- **Complexity trends**: Whether stories are getting simpler/harder
- **Quality trends**: Whether error rates are improving/degrading
- **Agent efficiency trends**: Whether agents are getting faster

### Metrics Storage Format

Metrics are stored in `/home/ed/Dev/architecture/docs/metrics/metrics.json`:

```json
{
  "generatedAt": "2025-10-19T12:00:00Z",
  "periodStart": "2025-10-15T00:00:00Z",
  "periodEnd": "2025-10-19T23:59:59Z",
  "summary": {
    "totalFeatures": 5,
    "totalStories": 45,
    "totalCompleted": 40,
    "totalInProgress": 5,
    "averageStoriesPerFeature": 9.0,
    "averageTimePerStory": "1.2 hours",
    "overallSuccessRate": 0.95
  },
  "agentMetrics": [
    {
      "agent": "backend-developer",
      "storiesCompleted": 15,
      "averageTimePerStory": "1.5 hours",
      "filesModifiedAverage": 4.2,
      "filesCreatedAverage": 8.1,
      "successRate": 0.93,
      "issuesEncountered": 2,
      "mostUsedTools": ["Write", "Bash", "Read"],
      "storyTypes": {
        "create": 6,
        "configure": 4,
        "implement": 3,
        "setup": 2
      }
    }
  ],
  "featureMetrics": [
    {
      "featureID": "1",
      "title": "Initialize Frontend Web Application",
      "storyCount": 8,
      "completedStories": 8,
      "totalDuration": "20 hours",
      "averageStoryDuration": "2.5 hours",
      "agentsInvolved": ["frontend-developer", "devops-engineer"],
      "state": "summarised",
      "planningToDeploymentTime": "20 hours"
    }
  ],
  "velocityMetrics": {
    "storiesPerDay": 2.8,
    "featuresPerWeek": 1.2,
    "averageFeatureDuration": "4.5 days",
    "trendDirection": "improving"
  },
  "qualityMetrics": {
    "overallIssueRate": 0.05,
    "retryCount": 1,
    "averageFilesPerStory": 6.3,
    "averageActionsPerStory": 8.1,
    "averageToolsPerStory": 3.2
  },
  "trendData": [
    {
      "featureID": "1",
      "storiesPerDay": 2.4,
      "averageStoryTime": "2.5 hours",
      "issueRate": 0.0
    },
    {
      "featureID": "2",
      "storiesPerDay": 2.6,
      "averageStoryTime": "1.7 hours",
      "issueRate": 0.08
    }
  ]
}
```

### Metrics Calculation Formulas

#### Story Completion Time
```
completionTime = completedAt - startTime (from implementation log)

Note: Current implementation logs don't track startTime, so we estimate based on:
- Sequential stories: startTime = previous story completedAt
- Parallel stories: startTime = phase start time
- First story: startTime = feature userStoriesImplemented (start of implementation)
```

#### Average Time Per Story
```
avgTimePerStory = sum(all story completion times) / total stories
```

#### Stories Per Day
```
storiesPerDay = total completed stories / days between first and last story
```

#### Features Per Week
```
featuresPerWeek = total features / weeks in period * 7
```

#### Success Rate
```
successRate = stories with status="completed" / total stories
```

#### Issue Rate
```
issueRate = stories with issuesEncountered.length > 0 / total stories
```

#### Agent Utilization
```
agentUtilization[agent] = stories by agent / total stories
```

## Metrics Aggregation Logic

### Data Sources

1. **Implementation Logs**: `docs/features/*/implementation-log.json`
   - Story completion data
   - Agent attribution
   - Files modified/created
   - Actions taken
   - Tools used
   - Issues encountered

2. **Feature Log**: `docs/features/feature-log.json`
   - Feature lifecycle timestamps
   - State transitions
   - Overall feature metadata

3. **Bug Implementation Logs**: `docs/features/*/bugs/*/implementation-log.json`
   - Bug fix metrics
   - Similar structure to feature implementation logs

### Aggregation Workflow

#### Step 1: Discover All Implementation Logs
```
1. Read feature log (docs/features/feature-log.json)
2. For each feature with userStoriesImplemented != null:
   a. Check for implementation log at docs/features/{featureID}/implementation-log.json
   b. Check for bug implementation logs at docs/features/{featureID}/bugs/*/implementation-log.json
3. Collect all log file paths
```

#### Step 2: Parse and Extract Story Data
```
For each implementation log:
1. Read JSON file
2. For each story entry:
   a. Extract storyNumber, storyTitle, agent, status, completedAt
   b. Extract filesModified, filesCreated (count them)
   c. Extract actions (count them)
   d. Extract toolsUsed (count unique tools)
   e. Extract issuesEncountered (count them)
   f. Calculate derived metrics
3. Store in aggregated data structure
```

#### Step 3: Calculate Time-Based Metrics
```
For each feature:
1. Sort stories by completedAt timestamp
2. For first story: estimatedStartTime = previous story completedAt or feature planning time
3. For each subsequent story:
   a. If sequential: startTime = previous completedAt
   b. If parallel: startTime = phase start (same as other parallel stories)
4. Calculate completionTime = completedAt - startTime
5. Sum all completion times for feature total duration
```

#### Step 4: Aggregate by Agent
```
1. Group all stories by agent field
2. For each agent:
   a. Count total stories
   b. Calculate average completion time
   c. Calculate average files modified/created
   d. Calculate success rate (completed vs failed status)
   e. Count issues encountered
   f. Identify most used tools (top 3-5)
   g. Categorize story types by title keywords
3. Store in agentMetrics array
```

#### Step 5: Calculate Velocity Metrics
```
1. Find earliest and latest story completedAt across all features
2. Calculate days in period
3. Calculate storiesPerDay = total stories / days
4. Calculate featuresPerWeek = features implemented / (days / 7)
5. Calculate averageFeatureDuration from feature planning to deployment
```

#### Step 6: Calculate Quality Metrics
```
1. Calculate overall issue rate = stories with issues / total stories
2. Count total retries (stories with status="failed" or issuesEncountered)
3. Calculate average files per story
4. Calculate average actions per story
5. Calculate average tools per story
```

#### Step 7: Calculate Trend Data
```
1. Sort features by completion date
2. For each feature:
   a. Calculate feature-specific velocity
   b. Calculate feature-specific quality metrics
   c. Store in trendData array
3. Determine trend direction (improving/stable/degrading) by comparing first vs last features
```

#### Step 8: Generate Summary Statistics
```
1. Count total features, stories, completed, in-progress
2. Calculate overall averages
3. Calculate overall success rate
4. Store in summary section
```

#### Step 9: Write Metrics File
```
1. Create metrics directory if not exists (docs/metrics/)
2. Write metrics.json with all aggregated data
3. Set generatedAt timestamp
4. Include periodStart and periodEnd
```

## Metrics Report Format

The `/metrics` command produces three types of reports:

### 1. Summary Report (Default)
```
=================================================================
                    ARCHITECTURE METRICS SUMMARY
=================================================================
Generated: 2025-10-19 12:00:00 UTC
Period: 2025-10-15 00:00:00 to 2025-10-19 23:59:59 (5 days)

OVERALL PERFORMANCE
-------------------------------------------------------------------
Total Features:                5
Total Stories:                45
Stories Completed:            40
Stories In Progress:           5
Average Stories/Feature:     9.0
Average Time/Story:          1.2 hours
Overall Success Rate:       95.0%

VELOCITY METRICS
-------------------------------------------------------------------
Stories Per Day:             2.8
Features Per Week:           1.2
Avg Feature Duration:        4.5 days
Trend:                       ↑ IMPROVING

QUALITY METRICS
-------------------------------------------------------------------
Overall Issue Rate:          5.0%
Retry Count:                 1
Avg Files/Story:             6.3
Avg Actions/Story:           8.1
Avg Tools/Story:             3.2

TOP PERFORMING AGENTS
-------------------------------------------------------------------
1. backend-developer         15 stories    1.5 hrs/story    93% success
2. frontend-developer        12 stories    1.0 hrs/story    96% success
3. devops-engineer           8 stories     0.8 hrs/story    100% success

=================================================================
Run '/metrics --detailed' for comprehensive metrics
Run '/metrics --agent <name>' for agent-specific metrics
Run '/metrics --trends' for trend analysis
=================================================================
```

### 2. Detailed Report (--detailed flag)
```
=================================================================
                    DETAILED METRICS REPORT
=================================================================

[Summary section as above]

FEATURE BREAKDOWN
-------------------------------------------------------------------
Feature #1: Initialize Frontend Web Application
  Stories:           8 completed
  Duration:          20 hours (avg 2.5 hrs/story)
  Agents:            frontend-developer (6), devops-engineer (2)
  Status:            summarised
  Issue Rate:        0%

Feature #2: Dockerize Frontend Application
  Stories:           4 completed
  Duration:          4.5 hours (avg 1.1 hrs/story)
  Agents:            devops-engineer (3), frontend-developer (1)
  Status:            deployed
  Issue Rate:        8%

[... more features ...]

AGENT PERFORMANCE DETAILS
-------------------------------------------------------------------
Agent: backend-developer
  Stories Completed:      15
  Avg Time/Story:         1.5 hours
  Avg Files Modified:     4.2
  Avg Files Created:      8.1
  Success Rate:           93%
  Issues Encountered:     2
  Most Used Tools:        Write (12), Bash (10), Read (8)
  Story Types:
    - Create:             6 stories
    - Configure:          4 stories
    - Implement:          3 stories
    - Setup:              2 stories

[... more agents ...]

QUALITY BREAKDOWN BY FEATURE
-------------------------------------------------------------------
Feature #1: 0% issue rate, 0 retries, 8.2 files/story
Feature #2: 8% issue rate, 1 retry, 3.5 files/story
[... more features ...]

=================================================================
```

### 3. Agent-Specific Report (--agent <name> flag)
```
=================================================================
              AGENT METRICS: backend-developer
=================================================================
Generated: 2025-10-19 12:00:00 UTC

OVERALL PERFORMANCE
-------------------------------------------------------------------
Stories Completed:         15
Average Time/Story:        1.5 hours
Success Rate:              93%
Issues Encountered:        2 (13% issue rate)

STORY BREAKDOWN
-------------------------------------------------------------------
Story #1: Initialize Backend Project with Build Configuration
  Feature:         3
  Duration:        2.5 hours
  Files Modified:  0
  Files Created:   24
  Actions:         8
  Tools:           Write, Bash
  Issues:          None
  Status:          ✓ Completed

[... all 15 stories ...]

COMPLEXITY METRICS
-------------------------------------------------------------------
Avg Files Modified:        4.2
Avg Files Created:         8.1
Total Files Changed:       185
Avg Actions/Story:         9.3
Avg Tools/Story:           3.1

TOOL USAGE
-------------------------------------------------------------------
Write:                     12 stories (80%)
Bash:                      10 stories (67%)
Read:                      8 stories (53%)
Edit:                      6 stories (40%)
Glob:                      3 stories (20%)

STORY TYPE DISTRIBUTION
-------------------------------------------------------------------
Create:                    6 stories (40%)
Configure:                 4 stories (27%)
Implement:                 3 stories (20%)
Setup:                     2 stories (13%)

TREND ANALYSIS
-------------------------------------------------------------------
First 5 Stories:           1.8 hrs/story avg
Last 5 Stories:            1.2 hrs/story avg
Improvement:               ↑ 33% faster

=================================================================
```

### 4. Trends Report (--trends flag)
```
=================================================================
                    METRICS TREND ANALYSIS
=================================================================
Generated: 2025-10-19 12:00:00 UTC

VELOCITY TRENDS
-------------------------------------------------------------------
Feature #1:  2.4 stories/day   2.5 hrs/story
Feature #2:  2.6 stories/day   1.7 hrs/story   ↑ +8% faster
Feature #3:  2.8 stories/day   1.5 hrs/story   ↑ +12% faster
Feature #4:  3.0 stories/day   1.1 hrs/story   ↑ +27% faster
Feature #5:  2.9 stories/day   1.2 hrs/story   ↓ -9% slower

Trend Direction:  ↑ IMPROVING (overall +21% velocity increase)

QUALITY TRENDS
-------------------------------------------------------------------
Feature #1:  0% issue rate    8.2 files/story
Feature #2:  8% issue rate    3.5 files/story
Feature #3:  0% issue rate    6.1 files/story
Feature #4:  0% issue rate    4.8 files/story
Feature #5:  5% issue rate    7.2 files/story

Trend Direction:  → STABLE (5% avg issue rate)

AGENT EFFICIENCY TRENDS
-------------------------------------------------------------------
backend-developer:
  Early Stories:   1.8 hrs/story avg
  Recent Stories:  1.2 hrs/story avg
  Improvement:     ↑ 33% faster

frontend-developer:
  Early Stories:   1.3 hrs/story avg
  Recent Stories:  0.9 hrs/story avg
  Improvement:     ↑ 31% faster

devops-engineer:
  Early Stories:   0.9 hrs/story avg
  Recent Stories:  0.8 hrs/story avg
  Improvement:     ↑ 11% faster

COMPLEXITY TRENDS
-------------------------------------------------------------------
Feature #1:  8.2 files/story   9.5 actions/story
Feature #2:  3.5 files/story   6.8 actions/story   ↓ Simpler
Feature #3:  6.1 files/story   8.2 actions/story   ↑ More complex
Feature #4:  4.8 files/story   7.1 actions/story   ↓ Simpler
Feature #5:  7.2 files/story   9.8 actions/story   ↑ More complex

Trend Direction:  → STABLE (avg 6.0 files/story)

=================================================================
```

## Integration with /metrics Command

The `/metrics` command uses the metrics aggregation logic to:

1. Check if cached metrics exist and are recent (< 1 hour old)
2. If cache is stale or missing:
   - Run aggregation workflow
   - Generate new metrics.json
   - Display report
3. If cache is fresh:
   - Read cached metrics.json
   - Display report

Command flags:
- `/metrics` - Summary report (default)
- `/metrics --detailed` - Detailed report with all breakdowns
- `/metrics --agent <name>` - Agent-specific metrics
- `/metrics --trends` - Trend analysis report
- `/metrics --refresh` - Force refresh (ignore cache)
- `/metrics --export` - Export metrics as JSON to stdout

## Best Practices

### When to Run Metrics

1. **After feature completion**: To track velocity and quality
2. **Weekly**: For trend analysis and team performance review
3. **Before planning**: To estimate capacity and complexity
4. **After issues**: To identify patterns and improvement areas

### Interpreting Metrics

#### Velocity Metrics
- **High stories/day**: Good throughput, but check quality metrics
- **Low stories/day**: May indicate complex features or learning curve
- **Improving trend**: Team getting more efficient
- **Degrading trend**: May indicate growing complexity or technical debt

#### Quality Metrics
- **Low issue rate (<5%)**: Excellent quality
- **Moderate issue rate (5-15%)**: Normal, acceptable
- **High issue rate (>15%)**: Review story atomicity and validation

#### Agent Metrics
- **High time/story**: Complex work or learning curve
- **Low time/story**: Efficiency or simpler stories
- **High tool usage**: Complex implementation
- **Low tool usage**: Straightforward work

### Optimization Opportunities

1. **High avg files/story**: Consider splitting stories into smaller units
2. **High issue rate**: Review atomicity validation effectiveness
3. **Degrading velocity**: Review complexity trends and technical debt
4. **Uneven agent utilization**: Consider workload balancing
5. **High retry count**: Improve pre-flight validation

## Future Enhancements

### Phase 1: Basic Metrics (Current)
- Story completion tracking
- Agent attribution
- Basic velocity and quality metrics

### Phase 2: Advanced Analytics
- Predictive velocity modeling
- Story complexity scoring
- Agent expertise heatmaps
- Anomaly detection (outlier stories)

### Phase 3: Visualization
- HTML dashboard generation
- Trend charts and graphs
- Interactive filtering
- Export to external analytics tools

### Phase 4: Real-Time Metrics
- Live metrics during implementation
- Progress indicators
- ETA calculations
- Real-time alerts for issues

## Maintenance

### Updating Metrics Schema
When adding new metric types:
1. Update metrics schema in this document
2. Update aggregation logic in `/metrics` command
3. Update report formats
4. Document new metrics in this file
5. Test with historical data
6. Create migration guide if breaking changes

### Cache Management
- Metrics cache stored at `docs/metrics/metrics.json`
- Cache expires after 1 hour
- Use `--refresh` flag to force regeneration
- Cache deleted on feature completion to ensure accuracy

### Performance Considerations
- Aggregation scales linearly with story count
- Typical aggregation time: <1 second for 100 stories
- Consider caching for large projects (>1000 stories)
- Use `--export` flag for external analysis tools

## Examples

### Example 1: Check Overall Progress
```bash
/metrics
```
Shows summary with overall velocity, quality, and top agents.

### Example 2: Analyze Specific Agent
```bash
/metrics --agent backend-developer
```
Shows detailed breakdown of all backend developer stories.

### Example 3: Export for Analysis
```bash
/metrics --export > metrics-export.json
```
Exports raw metrics JSON for external tools.

### Example 4: Force Refresh
```bash
/metrics --refresh --detailed
```
Forces new aggregation and shows detailed report.

### Example 5: Trend Analysis
```bash
/metrics --trends
```
Shows how velocity and quality change over time.

## Version History

- v1.0.0 (2025-10-19): Initial metrics tracking system
  - Story completion metrics
  - Agent performance metrics
  - Feature velocity metrics
  - Quality metrics
  - Trend analysis
  - Summary, detailed, agent-specific, and trends reports
