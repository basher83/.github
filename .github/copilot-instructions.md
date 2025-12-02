# Copilot Instructions for basher83/.github Repository

## Repository Overview

This is a **reusable GitHub Actions workflows repository** serving as a central hub for standardized CI/CD workflows across `basher83` projects.

**Type**: GitHub Actions workflow library | **Languages**: YAML with shell scripts | **Size**: ~15 files, documentation-heavy | **No Build Process**: Only YAML workflows and documentation

## Architecture & Structure

### Directory Layout

```
.github/
├── workflows/              # Reusable workflows (called via workflow_call)
│   ├── sync-labels.yml            # Label synchronization workflow (PRODUCTION)
│   ├── tailscale-connect-to-tailnet.yml  # Tailscale connection (BETA)
│   └── tailscale-policy.yml       # Tailscale ACL deployment (BETA)
├── use-workflows/          # Reference examples showing how to consume workflows
│   └── use-sync-labels.yml        # Example consumer implementation
├── workflow-templates/     # Organization-wide templates (appear in GitHub UI)
│   ├── sync-labels.yml
│   └── sync-labels.properties.json
└── labels/
    └── label-definitions.yml      # Central label definitions (source of truth)

docs/
├── getting-started.md      # User onboarding guide
├── CONTRIBUTING.md         # Contribution guidelines  
├── FAQ.md                  # Common questions & troubleshooting
├── TODO.md                 # Implementation tracking (internal)
├── workflows/              # Individual workflow documentation
│   ├── sync-labels.md      # Label sync workflow details
│   ├── python.md           # Python workflow (planned)
│   ├── ansible.md          # Ansible workflow (planned)
│   ├── docker.md           # Docker workflow (planned)
│   └── terraform.md        # Terraform workflow (planned)
└── examples/
    └── README.md

README.md                   # Main repository overview
ROADMAP.md                  # Project timeline & progress tracking
WARP.md                     # WARP.dev specific guidance
LICENSE                     # MIT License
renovate.json               # Renovate dependency updates config
.gitignore                  # Python-focused .gitignore
```

### Key Files

- **`.github/workflows/sync-labels.yml`**: Production label sync workflow (15+ repos)
- **`.github/labels/label-definitions.yml`**: Central label definitions (nested YAML with 34 labels)
- **`docs/CONTRIBUTING.md`**: Comprehensive workflow development standards
- **`ROADMAP.md`**: 35% complete, Phase 2 in progress (Python & Ansible workflows Q3 2025)

## Workflow Reference Format

External repositories reference these workflows using:
```yaml
uses: basher83/.github/.github/workflows/<workflow-name>.yml@main
```

**CRITICAL**: Note the double `.github` in the path - this is correct and required.

## Validation & Testing

### No Traditional Build/Test Process

This repository has **NO**:
- package.json, Makefile, or build scripts
- Automated test suite or CI/CD on this repo
- Compilation or build artifacts

### Validation Tools (ALWAYS USE)

1. **YAML Syntax** (REQUIRED):
   ```bash
   yq eval '.' .github/workflows/<file>.yml  # Pre-installed at /usr/bin/yq
   ```

2. **Shell Scripts** (REQUIRED):
   ```bash
   shellcheck <script>  # Pre-installed at /usr/bin/shellcheck
   ```

3. **Label Transformation Test** (for sync-labels):
   ```bash
   curl -sSL https://raw.githubusercontent.com/basher83/.github/main/.github/labels/label-definitions.yml -o /tmp/test.yml
   yq eval '[.[] | .[]]' /tmp/test.yml | yq eval 'length' -  # Should output 34
   ```

4. **actionlint** (recommended, not pre-installed):
   ```bash
   # Install: brew install actionlint
   actionlint .github/workflows/*.yml
   ```

### Manual Testing

Test workflow changes by creating a consumer repo:
```yaml
jobs:
  test:
    uses: YOUR-USERNAME/.github/.github/workflows/<name>.yml@your-branch
```

## Critical Workflow Details

### sync-labels.yml (✅ Production, 15+ repos)

- Uses `yq v4.45.4` for YAML transformation: `yq eval '[.[] | .[]]'` (nested to flat)
- Default source: `.github/labels/label-definitions.yml` from this repo
- **CRITICAL**: `prune: true` removes labels NOT in central definition
- Random jitter (0-600s) on `schedule` events only (prevents thundering herd)
- Permissions: `issues: write`

### Tailscale Workflows (🧪 Beta)

**tailscale-connect-to-tailnet.yml**: Connects runners to Tailscale
- Secrets: `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`
- Pinned SHA: `tailscale/github-action@a392da0a182bba0e9613b6243ebd69529b1878aa`

**tailscale-policy.yml**: Tests/deploys ACL policies
- Deploys only on push to main
- Uses caching for version-cache.json
- Secrets: `TS_OAUTH_ID`, `TS_OAUTH_SECRET`, `TS_TAILNET`

## Workflow Development Standards

### Structure Pattern
```yaml
name: Descriptive Name
on:
  workflow_call:
    inputs: {}  # snake_case, clear descriptions, defaults
    secrets: {}
jobs:
  job-name:
    runs-on: ubuntu-latest
    permissions: {}  # Minimal/least privilege
    steps:
      - name: Clear purpose
        # Validate inputs early, fail fast
        # Meaningful errors (✅ ❌ 📊)
```

### Naming: kebab-case files (`python-quality.yml`), snake_case inputs (`python_version`)

### Security: Pin actions to SHA, minimal permissions, validate inputs, never log secrets

### Documentation Required:
1. Workflow doc in `docs/workflows/<name>.md` (usage, params, troubleshooting)
2. Update README.md (Available Workflows table)
3. Update ROADMAP.md (progress %)
4. Inline comments for complex logic

## Common Pitfalls & Critical Notes

### Double .github Path
✅ **CORRECT**: `uses: basher83/.github/.github/workflows/sync-labels.yml@main`
- Repository is named `.github`, workflows are in `.github/workflows/` within it

### Label Sync Prunes Unlisted Labels
- `prune: true` removes labels NOT in central definition (by design)
- Custom per-repo labels must be added to central definition

### Jitter Only on Scheduled Runs
- 0-600s delay only when `github.event_name == 'schedule'`
- `workflow_dispatch` runs immediately

## Development Workflow

1. Create feature branch
2. **Validate YAML**: `yq eval '.' <file>.yml`
3. Test in consumer repo (if possible)
4. Update docs (workflow doc + README + ROADMAP)
5. Create PR (manual review, no automated CI)

## Important Context for Coding Agents

**NO Code to Build/Test**: No npm/pip commands, no compilation, no test suite. Validation = YAML syntax + manual testing.

**Documentation-Heavy**: 90% documentation, 10% YAML. Clear docs prevent support overhead.

**Workflows Called, Not Run**: `.github/workflows/` files invoked via `workflow_call` from OTHER repos. Testing requires consumer repos.

**Breaking Changes Impact Many Repos**: Label sync used by 15+ repos. Follow semver, provide migration guides.

**Renovate**: Uses `basher83/renovate-config` presets, auto-updates GitHub Actions.

## Trust These Instructions

Based on thorough repository exploration. Verify by checking:
1. Files mentioned: `.github/workflows/`, `docs/`, etc.
2. Documentation: `docs/CONTRIBUTING.md`, `FAQ.md`, etc.
3. Workflow files: `.github/workflows/*.yml`

Only search if instructions are definitively wrong or for discovering new uncovered information.
