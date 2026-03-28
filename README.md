# Tasks AI: The Git-Backed Task Manager for Modern Development

`tasks-ai` is a task management system that lives inside your Git repository. No external services, no sign-ups, no subscriptions. Your tasks live right next to your code.

## Why Use tasks-ai?

### 1. Your Tasks Are Always Synced
Unlike tools that live in the cloud, your tasks live in your repo. They're there when you `git clone`, they're there in your CI pipeline, they're there when you switch branches. No "sync" button needed.

### 2. Built for AI Collaboration
Working with AI agents? `tasks-ai` gives them a structured way to work on your project. They know what to do, what state each task is in, and how to report progress. Add the directive to your `AGENTS.md` and AI agents can autonomously manage work.

### 3. No Context Switching
Your tasks are just files. Browse them in your editor, grep them, diff them. The structured format is human-readable but also machine-parseable.

### 4. Enforced Workflow
The state machine prevents tasks from getting "stuck" in limbo. Each task has a clear lifecycle from idea → in progress → done.

## The States

```
BACKLOG → READY → PROGRESSING → TESTING → REVIEW → STAGING → LIVE → ARCHIVED
                                    ↓                    ↓
                               BLOCKED             REJECTED
```

- **BACKLOG**: New ideas and tasks
- **READY**: Approved, waiting to be worked on
- **PROGRESSING**: Active work (your agent should be here)
- **TESTING**: Code written, being verified
- **REVIEW**: Ready for human review
- **STAGING**: Approved, ready to ship
- **LIVE**: Deployed/released
- **ARCHIVED**: Done and retired
- **REJECTED**: Won't ship (abandoned)
- **BLOCKED**: Stuck on a dependency

## Quick Start

```bash
# Install
curl -sSL https://raw.githubusercontent.com/tim-projects/tasks-ai/main/install.sh | bash

# Initialize in your project
tasks-ai init

# Create a task
tasks-ai create "Add user login" \
  --story "As a user, I can log in so I can access my account" \
  --tech "Use existing auth provider, add session middleware" \
  --criteria "User can log in with email/password" \
  --plan "Add auth middleware" "Create login endpoint" "Add session handling"

# Start working
tasks-ai move 1 PROGRESSING

# ...do work...

# Move through states
tasks-ai move 1 TESTING
tasks-ai move 1 REVIEW
tasks-ai move 1 STAGING
tasks-ai move 1 ARCHIVED
```

## Features

| Feature | Description |
|---------|-------------|
| **Git Integration** | Tasks stored in dedicated worktree, auto-committed changes |
| **AI-Ready** | JSON output, structured fields, clear protocols for agents |
| **Zero Deps** | Pure Python standard library |
| **Flexible** | Work with CLI, editor, or scripts |
| **Track Progress** | Write notes directly to task files during work |

## Who Is This For?

- **Teams using AI agents** - Give agents a structured way to manage their work
- **Solo developers** - Lightweight task tracking without the bloat
- **Projects needing audit trails** - Every task change is a Git commit

---

*For help, run `tasks-ai -h`*