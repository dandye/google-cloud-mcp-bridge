# External Submodules

Place git submodules (e.g. MCP servers, libraries, rules banks) in this directory.

## Managing Submodules in Git Worktrees

When adding submodules:
```bash
git submodule add <repo_url> external/<name>
```

**CRITICAL**: If removing a worktree that contains submodules, deinitialize them first:
```bash
git submodule deinit --all -f
```
before running `git worktree remove`.
