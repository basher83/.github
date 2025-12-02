# GitHub Sync Workflows

This document explains the shared sync workflows used across the `basher83` GitHub ecosystem, focusing on:

- Centralized label management
- How repositories consume the shared sync workflow
- How scheduling and jitter work to avoid “thundering herd” problems

The source of truth for these workflows lives in:

- [Sync labels workflow](https://github.com/basher83/.github/blob/main/.github/workflows/sync-labels.yml)
- [Label definitions](https://github.com/basher83/.github/blob/main/.github/labels/label-definitions.yml)
- [Label usage guide](https://github.com/basher83/docs/blob/main/mission-control/github-configs/label-usage-guide.md)

---

## Goals

- **Single source of truth** for labels and label behavior.
- **Reusable workflows** hosted in `basher83/.github` that any repo can call.
- **Consistent behavior** across all repos without duplicating logic.
- **Safe scheduling** that avoids 80+ repos running the same job at the exact same second.

---

## Architecture Overview

### 1. Central `.github` repository

The repo [`basher83/.github`](https://github.com/basher83/.github) acts as “mission control” for GitHub configuration:

- **Label definitions:**

  ```text
  .github/labels/label-definitions.yml
  ```

  This is a **nested** YAML file that groups labels into logical categories (status, type, priority, area, etc.).  
  It is the **canonical source of truth** for all labels across the ecosystem.

- **Shared label sync workflow:**

  ```text
  .github/workflows/sync-labels.yml
  ```

  This workflow:

  - Downloads the central label definitions.
  - Validates and transforms them into a flat list.
  - Uses `micnncim/action-label-syncer` to sync labels to the calling repository.
  - Optionally prunes labels not present in the central config.
  - Applies a **random jitter** on scheduled runs to avoid all repos syncing at once.

### 2. Consumer repositories

Each repo (e.g., [`basher83/docs`](https://github.com/basher83/docs)) has a small, local workflow that **calls** the shared workflow using `workflow_call`.

Example in `basher83/docs`:

```yaml
name: Sync Labels (shared)

on:
  workflow_dispatch:

  # Optional: scheduled sync to keep labels fresh
  schedule:
    - cron: '0 0 * * 1' # 00:00 on Monday

jobs:
  sync-labels:
    uses: basher83/.github/.github/workflows/sync-labels.yml@main
```

This means:

- All the logic for label syncing lives centrally in `.github`.
- Individual repos only define:
  - When to run the sync (manual, schedule, etc.).
  - (Optionally) a custom label definitions URL if they want something different.

---

## Central Label Sync Workflow Details

File: [`sync-labels.yml`](https://github.com/basher83/.github/blob/main/.github/workflows/sync-labels.yml)

### Triggers

The central workflow is defined with:

```yaml
on:
  workflow_call:
    inputs:
      label_definitions_url:
        required: false
        type: string
        default: "https://raw.githubusercontent.com/basher83/.github/main/.github/labels/label-definitions.yml"
```

- It is **not** triggered directly.
- It is only invoked via `workflow_call` from other repositories.
- Consumers can optionally override `label_definitions_url`, but by default they use the centralized `.github` label file.

### Permissions

```yaml
permissions:
  issues: write
```

- Minimal permissions required to manage labels.
- No extra scopes are granted.

### Steps Overview

1. **Random jitter (scheduled runs only)**

   ```yaml
   - name: Random jitter to avoid thundering herd (scheduled runs only)
     if: github.event_name == 'schedule'
     run: |
       JITTER=$(( RANDOM % 600 ))
       echo "Applying random jitter: ${JITTER}s"
       sleep "${JITTER}"
   ```

   - If the calling workflow was triggered by `schedule`, this adds a random delay between 0–10 minutes.
   - Manual `workflow_dispatch` calls are **not** delayed.
   - This prevents many repositories from hitting the labels API simultaneously.

2. **Checkout**

   ```yaml
   - name: Checkout this repository
     uses: actions/checkout@<pinned-sha> # v4.x
   ```

   - Normal checkout of the `.github` repo.
   - Used mainly so the workflow can run in a consistent environment.

3. **Install `yq`**

   ```yaml
   - name: Install yq
     run: |
       sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/download/v4.45.4/yq_linux_amd64
       sudo chmod +x /usr/local/bin/yq
   ```

   - Installs a pinned version of [`yq`](https://github.com/mikefarah/yq) for YAML processing.
   - Pinning ensures behavior stays consistent over time.

4. **Download central label definitions**

   ```yaml
   - name: Download central label definitions
     run: |
       LABEL_URL="${{ inputs.label_definitions_url }}"
       echo "Downloading label definitions from $LABEL_URL..."
       if ! curl -sSL -f -o label-definitions.yml "$LABEL_URL"; then
         echo "❌ Failed to download label definitions from central repository"
         exit 1
       fi
       echo "✅ Successfully downloaded label definitions"
   ```

   - Fetches the label definitions from the configured URL (default: `.github`).
   - Fails fast if the file cannot be downloaded.

5. **Validate source file**

   ```yaml
   - name: Validate source file
     run: |
       # Checks file exists, is valid YAML, and has at least one top-level key
       # Also prints the top-level categories found.
   ```

   - Ensures:
     - File exists.
     - YAML parses.
     - It has at least one category.
   - Prints the categories (e.g., `status`, `priority`, `type`, etc.) for visibility.

6. **Transform labels**

   ```yaml
   - name: Transform labels
     run: |
       # Transform nested structure to flat array: [ .[] | .[] ]
       # Validate output and show count + sample.
   ```

   - Converts the nested structure:

     ```yaml
     status:
       - name: "status:backlog"
         ...
     priority:
       - name: "priority:high"
         ...
     ```

     into a flat list:

     ```yaml
     - name: "status:backlog"
       ...
     - name: "priority:high"
       ...
     ```

   - This flattened list is what `action-label-syncer` expects.
   - Prints:
     - Total label count.
     - First few labels as a sample.

7. **Sync labels**

   ```yaml
   - name: Sync labels to this repository
     uses: micnncim/action-label-syncer@<pinned-sha> # v1.3.0
     with:
       manifest: transformed-labels.yml
       prune: true
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

   - Uses `micnncim/action-label-syncer` to apply labels to the calling repository.
   - `prune: true` ensures labels not present in the central config are **removed**.

8. **Post-sync summary**

   ```yaml
   - name: Post-sync summary
     if: always()
     run: |
       echo "🎉 Label sync completed!"
       echo "Repository: ${GITHUB_REPOSITORY}"
       echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
       echo "Triggered by: ${{ github.actor }}"
       echo ""
       echo "ℹ️ Note: Labels not defined in the central configuration have been removed due to prune=true"
   ```

   - Provides a small log summary at the end of every sync, including:
     - Repository
     - Timestamp
     - Actor
   - Reminder that labels are pruned to match the central configuration.

---

## How a Repo Consumes the Shared Workflow

### Standard usage (default labels from `.github`)

In a consuming repo (e.g., `basher83/docs`), define:

```yaml
name: Sync Labels (shared)

on:
  workflow_dispatch:

  schedule:
    - cron: '0 0 * * 1' # 00:00 on Monday

jobs:
  sync-labels:
    uses: basher83/.github/.github/workflows/sync-labels.yml@main
```

- `workflow_dispatch` lets you manually sync labels from the Actions tab.
- `schedule` runs it automatically at a specific time.
  - The **jitter step in the shared workflow** spreads out actual execution time.
- No inputs are passed, so it uses the central `.github` label definitions.

### Custom definitions (optional)

If a repo ever needs a different label set, it can override `label_definitions_url`:

```yaml
jobs:
  sync-labels:
    uses: basher83/.github/.github/workflows/sync-labels.yml@main
    with:
      label_definitions_url: "https://raw.githubusercontent.com/basher83/docs/main/path/to/alternative-label-definitions.yml"
```

This is **not the default pattern**, but supported if needed.

---

## Jitter and the “Thundering Herd” Problem

With many repos configured to run `sync-labels` on the same cron schedule, they could all:

- Start at the same minute.
- Hit the GitHub API at the same time.
- Compete for Actions runner capacity.

To mitigate this, the shared workflow includes:

```yaml
- name: Random jitter to avoid thundering herd (scheduled runs only)
  if: github.event_name == 'schedule'
  run: |
    JITTER=$(( RANDOM % 600 ))
    echo "Applying random jitter: ${JITTER}s"
    sleep "${JITTER}"
```

This:

- Applies a random delay of 0–600 seconds (0–10 minutes) **only** when the caller event is `schedule`.
- Manual runs (`workflow_dispatch`) skip the delay and run immediately.
- Spreads load across a small time window, avoiding 80+ repos syncing labels simultaneously.

---

## Best Practices for Using These Workflows

- **Treat `.github/labels/label-definitions.yml` as the single source of truth.**
  - All label changes should start there.
  - After changing labels, run the sync manually in at least one repo (e.g. `docs`) to confirm.

- **Use scheduled syncs sparingly.**
  - For core repos: daily or weekly scheduled syncs are useful.
  - For less active repos: manual-only sync is often sufficient.

- **Be careful with `prune: true`.**
  - Any labels not defined in the central definition will be removed from the consuming repo.
  - If you need per-repo custom labels, you can:
    - Add them to the central definition with a naming convention, or
    - Temporarily disable `prune` for that repo (by forking the workflow or using a different mechanism).

- **Document changes.**
  - When you make structural changes to the label system or workflows, update:
    - `label-definitions.yml`
    - [`label-usage-guide.md`](./label-usage-guide.md)
    - This `sync-workflows.md` file if behavior/architecture changes.

---

## Quick Reference

- **Central labels source of truth**  
  [`basher83/.github/.github/labels/label-definitions.yml`](https://github.com/basher83/.github/blob/main/.github/labels/label-definitions.yml)

- **Shared sync workflow**  
  [`basher83/.github/.github/workflows/sync-labels.yml`](https://github.com/basher83/.github/blob/main/.github/workflows/sync-labels.yml)

- **Docs repo consumer example**  
  [`basher83/docs/.github/workflows/sync-labels.yml`](../.github/workflows/sync-labels.yml) (this repo)

- **Label usage guide**  
  [`label-usage-guide.md`](./label-usage-guide.md)

These pieces together give you a centralized, documented, and reproducible label system for all `basher83` repositories.