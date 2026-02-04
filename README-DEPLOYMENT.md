# Windsurf Hooker - Deployment Guide

## Quick Start

After cloning this repo to any PC, run:

```bash
./init
```

That's it. The init script will:
1. Install git hooks automatically
2. Run the first deployment
3. Set up auto-deployment for all future git operations

Auto-deployment triggers on:
- Pull changes (`git pull`)
- Checkout branches (`git checkout`)
- Merge branches (`git merge`)

## What Gets Deployed

### windsurf-hooks
- Deployed to: `/usr/local/share/windsurf-hooks`
- Deployed to: `/root/.codeium/hooks`
- Python hook scripts with executable permissions

### windsurf
- Deployed to: `/etc/windsurf`
- Configuration files and folders

## Permissions

All files are deployed with:
- **Directories**: 755 (rwxr-xr-x)
- **Files**: 644 (rw-r--r--)
- **Python hooks**: 755 (executable)
- **Owner**: root:root

## Manual Deployment

If you need to deploy manually without git hooks:

```bash
sudo ./deploy.sh
```

## Notes

- The deployment script requires **sudo** privileges
- Existing installations are automatically backed up with timestamps
- The script works from any directory within the repo
- Safe to run multiple times (idempotent with backups)

## Troubleshooting

### Sudo password prompts
If sudo prompts for a password during auto-deployment hooks, configure passwordless sudo for the deploy script:

```bash
sudo visudo
# Add this line:
# %sudo ALL=(ALL) NOPASSWD: /path/to/repo/deploy.sh
```

### Didn't run ./init?
If you forgot to run `./init` after cloning, just run it now and everything will set up automatically.
