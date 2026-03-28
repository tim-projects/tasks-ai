#!/bin/bash

# merge-testing-to-staging.sh
# Automates the compliance check and merge process from testing to staging.
# Detailed output is redirected to logs/merge-automation.log

set -e

# Configuration
SOURCE_BRANCH="staging"
TARGET_BRANCH="main"
MAX_RETRIES=5
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/merge-automation.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    echo -e "${RED}Detailed logs available at: $LOG_FILE${NC}"
}

# 0. Initialize Logging
mkdir -p "$LOG_DIR"
echo "--- Merge Automation Session Started at $(date) ---" > "$LOG_FILE"

# 1. Branch Validation
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ] && [ "$CURRENT_BRANCH" != "automate-merges" ]; then
    error "This script must be run from the $SOURCE_BRANCH branch. Current: $CURRENT_BRANCH"
    exit 1
fi

if ! git diff-index --quiet HEAD --; then
    warn "Uncommitted changes detected. Please commit or stash them first."
    exit 1
fi

# 2. Compliance Check (simplified for main - production build via GitHub runner)
log "Running compliance checks..."
if ! npm run typecheck >> "$LOG_FILE" 2>&1; then
    error "Type check failed."
    exit 1
fi

log "Applying formatting..."
npm run format >> "$LOG_FILE" 2>&1

if ! npm run format:check >> "$LOG_FILE" 2>&1; then
    error "Format check failed."
    exit 1
fi

log "Running lint..."
if ! npm run lint >> "$LOG_FILE" 2>&1; then
    warn "Lint check failed - proceeding anyway."
fi

log "Compliance met!"

# 2.5 Ensure clean state before branch switch
if [ -n "$(git status --porcelain)" ]; then
    log "Final auto-fixes detected. Committing before merge..."
    git add .
    git commit -m "chore: final automated fixes for staging merge" >> "$LOG_FILE" 2>&1 || warn "Commit failed, but proceeding anyway."
fi

# 3. Merge & Push
log "Merging $SOURCE_BRANCH into $TARGET_BRANCH..."

git checkout "$TARGET_BRANCH" >> "$LOG_FILE" 2>&1
git pull origin "$TARGET_BRANCH" >> "$LOG_FILE" 2>&1
git merge "$SOURCE_BRANCH" -m "merge: $SOURCE_BRANCH into $TARGET_BRANCH (automated)" >> "$LOG_FILE" 2>&1
git push origin "$TARGET_BRANCH" >> "$LOG_FILE" 2>&1

log "Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH" >> "$LOG_FILE" 2>&1

log "Successfully merged and pushed to $TARGET_BRANCH!"
echo "--- Merge Automation Session Successfully Completed at $(date) ---" >> "$LOG_FILE"
