#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
# Works from any directory by finding the repo root
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Fallback if called from git hooks or other locations
if [[ ! -d "${REPO_DIR}/windsurf-hooks" ]]; then
    REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null)" || REPO_DIR="$(pwd)"
fi

WINDSURF_HOOKS_SRC="${REPO_DIR}/windsurf-hooks"
WINDSURF_SRC="${REPO_DIR}/windsurf"

WINDSURF_HOOKS_DEST1="/usr/local/share/windsurf-hooks"
WINDSURF_HOOKS_DEST2="/root/.codeium/hooks"
WINDSURF_DEST="/etc/windsurf"

# User/Group for permissions (adjust if needed)
OWNER="root:root"
DIR_PERMS="755"
FILE_PERMS="644"
HOOK_PERMS="755"  # Hooks need to be executable

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

backup_existing() {
    local dest="$1"
    if [[ -e "$dest" ]]; then
        local backup="${dest}.backup.$(date +%s)"
        log_warn "Backing up existing $dest to $backup"
        mv "$dest" "$backup"
    fi
}

deploy_directory() {
    local src="$1"
    local dest="$2"
    
    if [[ ! -d "$src" ]]; then
        log_error "Source directory not found: $src"
        return 1
    fi
    
    log_info "Deploying $src to $dest"
    
    # Backup existing destination
    backup_existing "$dest"
    
    # Copy files
    mkdir -p "$(dirname "$dest")"
    cp -r "$src" "$dest"
    
    # Set permissions for directories
    find "$dest" -type d -exec chmod "$DIR_PERMS" {} \;
    
    # Set permissions for files
    find "$dest" -type f -exec chmod "$FILE_PERMS" {} \;
    
    # Make Python hooks executable
    find "$dest" -type f -name "*.py" -exec chmod "$HOOK_PERMS" {} \;
    
    # Change ownership
    chown -R "$OWNER" "$dest"
    
    log_info "Deployed to $dest with permissions set"
}

verify_deployment() {
    local dest="$1"
    
    if [[ ! -d "$dest" ]]; then
        log_error "Verification failed: $dest does not exist"
        return 1
    fi
    
    local owner_check=$(stat -c '%U:%G' "$dest")
    if [[ "$owner_check" != "$OWNER" ]]; then
        log_warn "Ownership may not be set correctly: $owner_check"
    fi
    
    log_info "Verification passed for $dest"
}

main() {
    log_info "Starting windsurf deployment..."
    
    check_root
    
    # Deploy windsurf-hooks to both locations
    deploy_directory "$WINDSURF_HOOKS_SRC" "$WINDSURF_HOOKS_DEST1"
    deploy_directory "$WINDSURF_HOOKS_SRC" "$WINDSURF_HOOKS_DEST2"
    
    # Deploy windsurf
    deploy_directory "$WINDSURF_SRC" "$WINDSURF_DEST"
    
    # Verify deployments
    verify_deployment "$WINDSURF_HOOKS_DEST1"
    verify_deployment "$WINDSURF_HOOKS_DEST2"
    verify_deployment "$WINDSURF_DEST"
    
    log_info "Deployment complete!"
    echo ""
    echo "Deployed to:"
    echo "  - $WINDSURF_HOOKS_DEST1"
    echo "  - $WINDSURF_HOOKS_DEST2"
    echo "  - $WINDSURF_DEST"
}

main "$@"
