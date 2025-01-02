# Task Generation Guide

## Overview
This guide focuses on converting repository analysis into actionable tasks using aider's architect mode. It emphasizes creating a clear, immutable task list that will guide implementation in code mode.

## Mode Requirements
1. Initial Task Generation:
   ```bash
   aider --architect /path/to/repo
   # or
   /chat-mode architect  # within an active session
   ```

2. Implementation (after tasks.md creation):
   ```bash
   aider --chat-mode code /path/to/repo
   # or
   /chat-mode code  # within an active session
   ```

## Analysis to Tasks Conversion [⬜]

### 1. Review Analysis Findings [⬜]
```markdown
- [ ] Consolidate exploration notes
- [ ] Review identified components
- [ ] List key implementation needs
- [ ] Note technical requirements
```

### 2. Task Identification [⬜]
```markdown
- [ ] For each component:
  - [ ] List required changes
  - [ ] Identify implementation tasks
  - [ ] Note testing requirements
  - [ ] Document dependencies

- [ ] For each interface:
  - [ ] List API requirements
  - [ ] Note integration needs
  - [ ] Document validation tasks
```

### 3. Task Organization [⬜]
```markdown
- [ ] Group related tasks
- [ ] Establish dependencies
- [ ] Set priority levels
- [ ] Define completion criteria
```

## Tasks.md Generation [⬜]

### 1. Structure Definition [⬜]
```markdown
- [ ] Create clear categories
- [ ] Establish tracking format
- [ ] Define priority system
- [ ] Document dependencies
```

### 2. Task Documentation [⬜]
```markdown
For each task:
- [ ] Write clear description
- [ ] List acceptance criteria
- [ ] Note dependencies
- [ ] Specify required resources
- [ ] Define completion checklist
```

### 3. Implementation Order [⬜]
```markdown
- [ ] Create dependency graph
- [ ] Establish task sequence
- [ ] Note parallel opportunities
- [ ] Document blockers
```

## Task Validation [⬜]

### 1. Completeness Check [⬜]
```markdown
- [ ] Verify all components covered
- [ ] Check interface requirements
- [ ] Confirm testing coverage
- [ ] Validate dependencies
```

### 2. Clarity Review [⬜]
```markdown
- [ ] Check task descriptions
- [ ] Verify acceptance criteria
- [ ] Confirm resource requirements
- [ ] Validate completion steps
```

### 3. Final Verification [⬜]
```markdown
- [ ] Review entire task set
- [ ] Confirm scope boundaries
- [ ] Verify task independence
- [ ] Check for completeness
```

## Tasks.md Format

### Required Sections
1. Overview
   - Project scope
   - Goals and objectives
   - Key constraints

2. Task Categories
   - Implementation tasks
   - Testing requirements
   - Documentation needs
   - Integration tasks

3. For Each Task
   ```markdown
   ## [Task Category]
   ### Task Name [⬜]
   - Description: Clear task description
   - Priority: [High/Medium/Low]
   - Dependencies: [List of dependent tasks]
   - Acceptance Criteria:
     - [ ] Criterion 1
     - [ ] Criterion 2
   - Resources:
     - Required tools
     - Reference materials
   ```

## Important Rules

### Tasks.md Immutability
1. Once created, tasks.md becomes an immutable contract
2. No new tasks can be added after creation
3. No scope changes are permitted
4. Only completion status can be updated [⬜] -> [x]

### Scope Management
1. All tasks must be identified before finalization
2. No feature creep allowed after creation
3. No additional requirements can be added
4. All dependencies must be identified upfront

### Implementation Guidelines
1. Tasks must be implemented as defined
2. No scope expansion during coding
3. Stay within defined boundaries
4. Focus on completing defined tasks

Remember: The goal is to create a clear, complete, and immutable task list that will guide the implementation phase. Take time to ensure all necessary tasks are included before finalizing tasks.md, as no additions will be permitted afterward.