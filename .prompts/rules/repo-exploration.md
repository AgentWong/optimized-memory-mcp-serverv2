# Repository Exploration Guide

## Overview
This guide focuses on systematic exploration of Python repositories using aider's repomap function. It emphasizes incremental analysis to avoid context window limitations while maintaining comprehensive understanding.

## Mode Selection
Use aider's architect mode for repository exploration:
```bash
aider --architect /path/to/repo
# or
/chat-mode architect  # within an active session
```

## Repository Structure Analysis [⬜]

### Basic Information [⬜]
- [ ] Repository name and URL
- [ ] Main purpose and scope
- [ ] License type
- [ ] Python version requirements
- [ ] Key dependencies (from setup.py/requirements.txt)

### Incremental Directory Exploration [⬜]
```markdown
1. Root Level Analysis [⬜]
   - [ ] Use repomap to list root directory contents
   - [ ] Identify key configuration files
   - [ ] Note special files (setup.py, requirements.txt, etc.)
   - [ ] Document repository structure overview

2. Module-by-Module Exploration [⬜]
   - [ ] List all top-level modules
   - [ ] For each module:
     - [ ] Use repomap to explore structure
     - [ ] Document purpose and responsibilities
     - [ ] Note key files and their roles
     - [ ] Identify internal dependencies

3. Test Directory Analysis [⬜]
   - [ ] Map test directory structure
   - [ ] Identify test categories
   - [ ] Document test file organization
   - [ ] Note testing utilities and helpers
```

## Code Analysis Plan [⬜]

### Incremental Module Analysis [⬜]
```markdown
1. Core Modules [⬜]
   - [ ] Identify entry points
   - [ ] Map primary interfaces
   - [ ] Document key classes
   - [ ] Note important algorithms

2. Supporting Utilities [⬜]
   - [ ] List utility modules
   - [ ] Document helper functions
   - [ ] Note shared resources

3. External Interfaces [⬜]
   - [ ] Identify API endpoints
   - [ ] Document integration points
   - [ ] Note configuration options
```

### Dependency Mapping [⬜]
```markdown
1. External Dependencies [⬜]
   - [ ] List required packages
   - [ ] Document version constraints
   - [ ] Note optional dependencies

2. Internal Dependencies [⬜]
   - [ ] Map import relationships
   - [ ] Document module dependencies
   - [ ] Note circular dependencies
```

## Progress Tracking

### Session Management
- Current Session: [Session number]
- Date: [Current date]
- Current Focus: [Module/component being analyzed]
- Completed Items: [List of completed checkboxes]
- Next Steps: [Next modules/components to analyze]

### Exploration Notes
- Document key findings for each module
- Note areas needing deeper investigation
- Record potential issues or concerns
- Track questions for follow-up

## Best Practices

### Using Repomap Effectively
1. Start with high-level directory structure
2. Explore one module at a time
3. Document findings immediately
4. Note relationships between components
5. Track progress systematically

### Managing Context
1. Focus on one component at a time
2. Use incremental exploration
3. Document relationships without loading full content
4. Reference file paths instead of content
5. Save detailed analysis for task generation phase

Remember: The goal is to understand the repository structure and relationships without exceeding context limitations. Detailed implementation analysis should be deferred to the task generation phase.