## Complete Git Commit Workflow (CLI)

### Phase 0: Set Up Your Workspace 🌿

**Step 0a: Check current branch**
```bash
git branch
```
*Shows: all local branches with * indicating current branch*

**Step 0b: Create/switch to feature branch (if needed)**
```bash
# Create and switch to new branch
git checkout -b feature/my-feature

# Or switch to existing branch
git checkout feature/my-feature
```

**Step 0c: Ensure you're up to date**
```bash
# Fetch latest changes from remote
git fetch origin

# If on main/master, pull latest
git pull origin main
```

***

### Phase 1: Assess the Damage 🔍

**Step 1: High-level overview**
```bash
git status
```
*Shows: untracked, modified, deleted files*

**Step 2: See what actually changed (summary)**
```bash
git diff --stat
```
*Shows: files changed with line counts (+/-)*

**Step 3: See detailed changes**
```bash
git diff
```
*Shows: actual code changes line-by-line*

**Optional: See untracked files content**
```bash
git status --short | grep '^??' | cut -c4- | xargs ls -la
```

***

### Phase 2: Analyze and Plan Commits 🧠

**Step 4: Review changes by file type/category**

```bash
# Check specific files
git diff path/to/specific/file.py

# Check all files in a directory
git diff src/api/

# Check files by pattern
git diff '*.json'
git diff '*.md'
```

**Step 5: Identify logical groupings**

Ask yourself:
- What are the **different types** of changes? (feat, fix, docs, etc.)
- What are the **different scopes**? (api, frontend, config, etc.)
- Which changes **depend on each other**?
- Which changes are **completely independent**?

***

### Phase 3: Create Logical Commits 📦

#### Commit 1 Example: Documentation Updates

**Step 6a: Stage only documentation files**
```bash
git add README.md docs/*.md
```

**Step 6b: Verify what you staged**
```bash
git diff --cached
```
*Shows: changes that will be committed*

**Step 6c: Commit with conventional format**
```bash
git commit -m "docs: update installation instructions and API documentation"

# Or use commit template if available (opens editor)
git commit  # Uses .gitmessage or global template if configured
```

***

#### Commit 2 Example: New Feature

**Step 7a: Stage feature files**
```bash
git add src/api/new-endpoint.py tests/test_new_endpoint.py
```

**Step 7b: Review staged changes**
```bash
git diff --cached
```

**Step 7c: Commit**
```bash
git commit -m "feat(api): add user profile endpoint"
```

***

#### Commit 3 Example: Bug Fix

**Step 8a: Stage specific bug fix**
```bash
git add src/parser/validator.py
```

**Step 8b: Review**
```bash
git diff --cached
```

**Step 8c: Commit**
```bash
git commit -m "fix(parser): handle null values in validation"
```

***

#### Commit 4 Example: Configuration Changes

**Step 9a: Stage config files**
```bash
git add renovate.json .github/workflows/*.yml
```

**Step 9b: Review**
```bash
git diff --cached
```

**Step 9c: Commit**
```bash
git commit -m "chore(ci): update renovate config and GitHub Actions"
```

***

### Phase 4: Handle Complex Scenarios 🎯

#### Scenario A: Need to commit only PART of a file (Interactive Staging)

```bash
# Stage changes interactively (patch mode)
git add -p src/app.py
```

*Git will show each change hunk and ask:*
- `y` = yes, stage this hunk
- `n` = no, don't stage
- `s` = split into smaller hunks
- `e` = manually edit the hunk
- `q` = quit

**Then commit:**
```bash
git commit -m "refactor(app): extract database connection logic"
```

**Stage remaining changes separately:**
```bash
git add -p src/app.py  # Stage the other hunks
git commit -m "feat(app): add caching layer"
```

***

#### Scenario B: Deleted files

```bash
# See what was deleted
git status | grep deleted

# Stage deletions
git add path/to/deleted/file.py

# Or stage all deletions and modifications at once
git add -u  # Stages modified and deleted files (NOT new untracked files)

# Commit
git commit -m "chore: remove deprecated utility functions"
```

**Note:** Staging options:
- `git add -u` = stages **modifications and deletions only** (ignores untracked files)
- `git add .` = stages **everything in current directory** (including untracked)
- `git add -A` = stages **all changes in entire repository** (including untracked)

***

#### Scenario C: New untracked files

```bash
# See untracked files
git status --short | grep '^??'

# Add specific untracked files
git add new-script.sh config/new-config.yaml

# Or interactively choose
git add -i
```

***

### Phase 5: Verify Your Work ✅

**Step 10: Check commit history**
```bash
git log --oneline -n 5
```

**Step 11: See what's still uncommitted**
```bash
git status
```

**Step 12: If anything left, repeat phases 3-4**

***

### Phase 6: Push to Remote 🚀

**Step 13: Review all commits before pushing**
```bash
# See commits that will be pushed
git log origin/main..HEAD --oneline

# Or if you're on a feature branch
git log origin/feature/my-feature..HEAD --oneline
```

**Step 14: Push your commits**
```bash
# First time pushing a new branch
git push -u origin feature/my-feature

# Subsequent pushes (after -u is set)
git push

# Force push (use with caution - only for your own branches)
git push --force-with-lease  # Safer than --force
```

**Step 15: Create Pull Request**
- Go to GitHub/GitLab
- Create PR from your feature branch to main
- Or use `gh` CLI:

```bash
gh pr create --title "feat: add user profiles" --body "Implements user profile management"
```

***

## Real-World Example: Complete Session

Let's say you have this mess:

```bash
$ git status
On branch feature/user-api

Changes not staged for commit:
  modified:   README.md
  modified:   src/api/users.py
  modified:   src/api/auth.py
  modified:   src/utils/validator.py
  modified:   tests/test_users.py
  modified:   renovate.json
  deleted:    src/legacy/old_auth.py

Untracked files:
  docs/api-guide.md
  src/api/profiles.py
  tests/test_profiles.py
```

### Here's how you'd handle it:

```bash
# 1. ASSESS
git status
git diff --stat

# 2. DOCUMENTATION FIRST
git add README.md
git add docs/api-guide.md
git diff --cached  # Review
git commit -m "docs: add API usage guide and update README"

# 3. NEW FEATURE - Profiles
git add src/api/profiles.py tests/test_profiles.py
git diff --cached  # Review
git commit -m "feat(api): add user profile management endpoint"

# 4. ENHANCEMENT - Existing feature
git add src/api/users.py tests/test_users.py
git diff --cached  # Review
git commit -m "feat(api): add pagination to users endpoint"

# 5. BUG FIX
git add src/utils/validator.py
git diff --cached  # Review
git commit -m "fix(validator): handle edge case in email validation"

# 6. REFACTOR - Auth changes
git add src/api/auth.py
git add src/legacy/old_auth.py  # Stage the deletion
git diff --cached  # Review
git commit -m "refactor(auth): migrate to new authentication module"

# 7. CONFIG/CHORE
git add renovate.json
git diff --cached  # Review
git commit -m "chore(deps): enable automerge for patch updates"

# 8. VERIFY
git status  # Should show "nothing to commit"
git log --oneline -n 7  # See your beautiful commits
```

***

## Useful Aliases to Speed This Up

Add to `~/.gitconfig`:

```gitconfig
[alias]
    # Quick status
    s = status --short
    
    # Show changes summary
    summary = diff --stat
    
    # Show staged changes
    staged = diff --cached
    
    # Interactive staging
    stage = add -p
    
    # Undo staging
    unstage = reset HEAD --
    
    # Commit with type
    cmt = "!f() { git commit -m \"$1: $2\"; }; f"
    
    # Better log
    lg = log --oneline --decorate --graph -n 10
    
    # What changed in each file
    changed = diff --name-status
    
    # See commits ready to push
    unpushed = log origin/main..HEAD --oneline
    
    # Quick branch switch
    co = checkout
    
    # Create and switch to new branch
    cob = checkout -b
```

**Usage examples:**
```bash
git s              # Quick status
git summary        # See changes overview
git staged         # Review what's staged
git stage file.py  # Interactive staging
git unstage file.py  # Undo staging
git lg             # Pretty log
```

***

## Pro Tips 💡

1. **Use `git add -p` liberally** - It's your best friend for surgical commits
2. **Always review before committing** - `git diff --cached` is mandatory
3. **Commit early, commit often** - Small commits are easier to review/revert
4. **Don't mix types** - Keep feat, fix, docs, etc. in separate commits
5. **Write the commit message first** - If you can't describe it clearly, maybe it's not atomic enough
6. **Check your branch** - Always verify you're on the right branch before committing
7. **Pull before push** - Fetch/pull latest changes before pushing to avoid conflicts
8. **Use `--force-with-lease`** - Safer than `--force` when you need to force push

***

## Time-Saving Command Sequence

For experienced users, this becomes muscle memory:

```bash
git status && \
git diff --stat && \
git add <files> && \
git diff --cached && \
git commit -m "type(scope): message"
```

Or in your case with Warp:
```bash
git status && git diff --stat  # Review
git add <files>  # Stage
# Then use your "Conventional Commit" workflow for committing
```

This is the **real-world workflow** that every developer uses daily! 🚀