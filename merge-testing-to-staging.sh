#!/bin/bash

# merge-testing-to-staging.sh
# Automates the compliance check and merge process from testing to staging.
# Detailed output is redirected to logs/merge-automation.log

set -e

# Configuration
SOURCE_BRANCH="testing"
TARGET_BRANCH="staging"
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

# 2. Compliance Loop
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    log "Starting compliance loop (Attempt $((retry_count + 1))/$MAX_RETRIES)..."
    
    # Step A: Type Checking
    log "Running typecheck..."
    if ! npm run typecheck >> "$LOG_FILE" 2>&1; then
        error "Type check failed. These errors cannot be auto-fixed."
        exit 1
    fi

    # Step B: Formatting
    log "Applying formatting..."
    npm run format >> "$LOG_FILE" 2>&1

    # Step C: Linting
    log "Applying lint fixes..."
    npm run lint >> "$LOG_FILE" 2>&1 || warn "Some lint issues could not be auto-fixed. See logs."

    # Step D: Security Audit
    log "Running audit fix..."
    npm audit fix --yes >> "$LOG_FILE" 2>&1 || warn "Some audit issues could not be auto-fixed. See logs."

    # Step E: Build (skip for staging - uses Cloudflare Pages dev mode)
    if [ "$TARGET_BRANCH" = "staging" ]; then
        log "Skipping build for staging (uses Cloudflare Pages dev mode with --no-secrets)"
    else
        log "Running build..."
        if ! npm run build >> "$LOG_FILE" 2>&1; then
            error "Build failed. Please resolve manually."
            exit 1
        fi
    fi

    # Step F: Final Verification (skip for staging)
    if [ "$TARGET_BRANCH" = "staging" ]; then
        log "Skipping predeploy for staging (tests run separately via run_staging_validation.sh)"
        log "Compliance met!"
        break
    else
        log "Running full predeploy verification..."
        if npm run predeploy >> "$LOG_FILE" 2>&1; then
            log "Compliance met!"
            break
        else
            warn "Predeploy checks failed after auto-fixes."
            
            # Check if fixes made any changes to the worktree
            if ! git diff-index --quiet HEAD --; then
                log "Auto-fixes detected changes. Committing..."
                git add .
                git commit -m "chore: automated fixes for staging merge (format/lint/audit)" >> "$LOG_FILE" 2>&1
            else
                error "Compliance checks failed and no auto-fixes were possible."
                exit 1
            fi
        fi
    fi

    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    error "Reached maximum retries ($MAX_RETRIES) without reaching compliance."
    exit 1
fi

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
