# **HAMMER IS BOSS.** LLM SUBMIT. POUND weak code through quality gates to LIVE BLADE! **CODE QUALITY 10X!**

<img src="hammer-icon.webp" width="300"/>

Your lite/small local or cloud LLM writes code. Without HAMMER you get toy prototypes that break in production. HAMMER blocks weak code with test and lint gates, forces complete specs, and tracks every change in git.

Agents can't skip steps. Result: shippable code that doesn't explode in production.

**Zero deps. Git-powered. One-line install.**

## Ship BETTER and CHEAPER with HAMMER: AI-Powered Git-Backed Project Management 🔨⚔️

`tasks` = complete system IN your repo.  
State machines + quality gates + audit trails + git worktrees.  
**Built for AI agents.**

## 🚀 One-Line Install

**HAMMER SMASH INSTALL!**
```bash
curl -sSL https://raw.githubusercontent.com/tim-projects/tasks/main/install.sh | bash
```
Installs to `~/.local/bin/tasks`. No sudo.

**Global HAMMER:**
```bash
curl -sSL https://raw.githubusercontent.com/tim-projects/tasks/main/install.sh | sudo bash -s -- -g
```

## 🛠️ Getting Started

**HAMMER DEMAND: Add to `AGENTS.md`: `MANAGE TASKS WITH HAMMER. OBEY HAMMER PROTOCOL.`**

**Agent autonomously runs:**
1. `tasks init` - Initialize system  
2. `tasks list` / `tasks create` - Discover/create tasks
3. `tasks move` - POUND through Git-native state machine

## 🔨 HAMMER STATE MACHINE

```
BACKLOG → READY → PROGRESSING → TESTING → REVIEW → STAGING → LIVE → ARCHIVED
                                              ↓                    ↓
                                         REJECTED              REJECTED
```

**HAMMER GATES BLOCK WEAK CODE:**
| Gate | Requirement |
|------|-------------|
| PROGRESSING | Complete story/tech/plan |
| TESTING | `check all` PASSES |
| REVIEW | Tests pass + branch pushed |
| LIVE | Merged to main |
| ARCHIVED | Merged to main |

## 💥 HAMMER vs Chaos

| Without HAMMER | With HAMMER |
|----------------|-------------|
| Scattered notes | **HAMMER AUDIT BLADE!** Git log every smash |
| Manual updates | **HAMMER STATE MACHINE!** Gates block weak code |
| Lost context | **HAMMER HISTORY FULL!** Every change tracked |
| "What's ready?" | **HAMMER PIPELINE CLEAR!** Testing → Live order |
| Agent chaos | **HAMMER ATOMIC ID!** Blockers + branch lock |

## 🛠️ HAMMER COMMANDS

### Task Management
```bash
tasks init                    # HAMMER BUILD SYSTEM!
tasks list                    # SHOW ALL BLADES!
tasks create "SMASH BUG"      # NEW BLADE!
tasks show 42                 # BLADE DETAIL!
tasks current                 # ACTIVE BLADE!
```

### POUND THROUGH GATES
```bash
tasks move 42 PROGRESSING     # START SMASH! (Creates branch)
tasks move 42 TESTING         # ✓ HAMMER LIKE! MOVE → TESTING ⚔️🔨
tasks move 42 LIVE            # 🔨 HAMMER SMASH GOOD! LIVE BLADE! ⚔️🔨
```

### QUALITY SMASH
```bash
check all                     # SMASH ALL CHECKS!
check lint --fix              # FIX WEAK CODE!
tasks run all                 # HAMMER VALIDATE EVERYTHING!
```

## 🎯 REAL HAMMER FLOW

```bash
tasks init                    # ✓ HAMMER LIKE! SYSTEM READY! ⚔️🔨
tasks create "SMASH LOGIN"    # NEW BLADE 42!
tasks move 42 PROGRESSING     # BRANCH CREATE!
check all                     # ✗ TEST BREAK! HAMMER SAY NO! FIX! 🔨
# LLM FIXES...
tasks move 42 TESTING         # ✓ HAMMER LIKE! MOVE → TESTING ⚔️🔨
tasks move 42 LIVE            # 🔨 HAMMER SMASH GOOD! LIVE BLADE! ⚔️🔨
```

## ⚙️ Task File (Git-Backed)

```yaml
***
Id: 42
Ti: SMASH LOGIN BUG
St: PROGRESSING
***
## Story
User cannot login special chars...

## Plan
1. FIX regex
2. TEST unicode
3. CHECK error msg
```

## 🔧 HAMMER CONFIG
```bash
tasks config detect           # HAMMER FIND TOOLS!
tasks config set repo.test pytest
```

## 🎉 Why HAMMER RULES?

- **No external services** - Pure git
- **Zero deps** - One-line install  
- **Agent-optimized** - JSON output, clear protocol
- **Enforced quality** - Gates BLOCK weak code
- **Full lifecycle** - Backlog → LIVE → ARCHIVED

**HAMMER IS BOSS. WEAK CODE SUBMIT. STRONG BLADES SHIP!** 🔨⚔️
```
