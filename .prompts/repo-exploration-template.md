# Python Repository Exploration Template

## Overview
This template guides AI assistants through systematic exploration of Python repositories while maintaining state and progress across multiple chat sessions. It combines repository mapping with incremental analysis capabilities.

## Mode Selection Guidelines

### Analysis and Planning Phase
Use aider's architect mode for initial repository analysis and task generation. The architect mode's two-step process is valuable during this phase because it allows for:
- Comprehensive repository understanding
- Thoughtful task identification
- Careful consideration of dependencies
- Thorough validation before task list finalization

To activate architect mode:
```bash
aider --architect /path/to/repo
# or
/chat-mode architect  # within an active session
```

### Task Execution Phase
Switch to code mode for implementing the tasks defined in tasks.md. Code mode provides:
- Direct implementation of predefined tasks
- Single-pass execution without additional proposals
- Strict adherence to the existing task list
- Prevention of scope creep

To activate code mode:
```bash
aider --chat-mode code /path/to/repo
# or
/chat-mode code  # within an active session
```

IMPORTANT: Once tasks.md is generated in architect mode, switch to code mode for all subsequent task execution sessions. This mode change helps maintain focus on completing the defined tasks without introducing scope creep through additional suggestions or improvements.

## Repository Structure Analysis [⬜]
```markdown
### Basic Information [⬜]
- [ ] Repository name
- [ ] Main purpose
- [ ] License type
- [ ] Python version requirements
- [ ] Key dependencies

### Directory Structure [⬜]
- [ ] Generate directory tree
- [ ] Identify key components
- [ ] Document module organization
- [ ] Note special files (setup.py, requirements.txt, etc.)
```

## Code Analysis Plan [⬜]
```markdown
### Module Mapping [⬜]
- [ ] Core modules
- [ ] Supporting utilities
- [ ] Tests
- [ ] Configuration files

### Dependency Analysis [⬜]
- [ ] External dependencies
- [ ] Internal dependencies
- [ ] Module relationships
- [ ] Import hierarchy
```

## Detailed Analysis Sections [⬜]

### 1. Core Functionality [⬜]
```markdown
#### Main Components [⬜]
- [ ] Entry points
- [ ] Core classes
- [ ] Primary interfaces
- [ ] Key algorithms

#### Implementation Details [⬜]
- [ ] Architecture patterns
- [ ] Design patterns
- [ ] Error handling
- [ ] Performance considerations
```

### 2. API and Interfaces [⬜]
```markdown
#### Public Interfaces [⬜]
- [ ] API endpoints
- [ ] Public classes
- [ ] Exposed functions
- [ ] Configuration options

#### Integration Points [⬜]
- [ ] External service connections
- [ ] Plugin systems
- [ ] Extension mechanisms
```

### 3. Data Management [⬜]
```markdown
#### Data Structures [⬜]
- [ ] Key classes
- [ ] Data models
- [ ] Storage mechanisms

#### Data Flow [⬜]
- [ ] Input processing
- [ ] Data transformations
- [ ] Output handling
```

### 4. Testing and Quality [⬜]
```markdown
#### Test Coverage [⬜]
- [ ] Unit tests
- [ ] Integration tests
- [ ] Test utilities
- [ ] Mock objects

#### Quality Metrics [⬜]
- [ ] Code style
- [ ] Documentation quality
- [ ] Error handling
- [ ] Performance benchmarks
```

## Documentation Generation [⬜]

### 1. Planning [⬜]
```markdown
- [ ] Identify documentation needs
- [ ] Determine structure
- [ ] List key sections
- [ ] Define audience
```

### 2. Content Creation [⬜]
```markdown
- [ ] Write overview
- [ ] Document installation
- [ ] Create usage guide
- [ ] Add API documentation
```

### 3. Additional Materials [⬜]
```markdown
- [ ] Examples
- [ ] Tutorials
- [ ] Troubleshooting guide
- [ ] Contributing guidelines
```

## Progress Tracking

### Session Information
- Current Session: [Session number]
- Date: [Current date]
- Focus Areas: [List of areas being analyzed]
- Completed Items: [List of completed checkboxes]
- Next Steps: [List of next items to analyze]

### Completion Status
- [ ] Repository Structure Analysis
- [ ] Code Analysis Plan
- [ ] Detailed Analysis Sections
- [ ] Documentation Generation

## Usage Instructions

1. Start each session by updating the Session Information section
2. Mark completed items with [x]
3. Leave incomplete items with [ ]
4. Add notes under relevant sections as analysis progresses
5. Update Next Steps before ending each session
6. Track major findings and insights in each section

## Notes
- Add important findings here
- Document key decisions
- Note areas needing further investigation
- Record any challenges or blockers

## Task Generation [⬜]

### Analysis to Tasks Conversion [⬜]
```markdown
- [ ] Review completed analysis sections
- [ ] Identify required actions
- [ ] Categorize tasks by priority
- [ ] Define task dependencies
```

### Tasks.md Creation [⬜]
```markdown
- [ ] Generate tasks.md file with:
  - [ ] Clear task categories
  - [ ] Progress tracking checkboxes
  - [ ] Priority levels
  - [ ] Dependencies between tasks
  - [ ] Completion criteria
  - [ ] Required resources or references

IMPORTANT: The tasks.md file serves as an immutable contract once created:
- No new tasks may be added after initial creation
- No additional features may be suggested
- No new test cases may be introduced
- The ONLY permitted modification is updating task completion status ([x])
```

### Tasks Validation [⬜]
```markdown
- [ ] Verify task completeness before finalizing tasks.md
- [ ] Confirm all task dependencies are identified
- [ ] Check alignment with analysis findings
- [ ] Validate against project guidelines
- [ ] Confirm all necessary tasks are included before finalizing
- [ ] Review for potential scope creep or unnecessary additions

NOTE: This validation must be thorough and complete before finalizing tasks.md, as no new tasks can be added after creation. The tasks.md file becomes a fixed scope contract once generated.
```

## Recommendations
- List improvement suggestions
- Note potential optimizations
- Suggest architectural changes
- Document technical debt

Remember: This template is designed to be used across multiple sessions. Each session should begin by reviewing the previous session's progress and end by updating the status and next steps. The generated tasks.md file serves as the primary tracking mechanism for implementing recommendations and changes identified during the analysis.
