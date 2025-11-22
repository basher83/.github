# Renovate Shared Configuration Implementation

## Problem Statement

Renovate configurations are duplicated across 20+ repositories with inconsistent settings. Most repos use basic `config:recommended` while three repos (Sombrero-Edge-Control, Zammad-MCP, docs) have advanced configurations tailored to specific use cases. Need centralized presets to share common patterns while allowing repository-specific customization.

## Current State Analysis

### Configuration Patterns Identified

**Basic Configuration (15 repos):**
- Triangulum-Prime, andromeda-orchestration, Supernova-MicroK8s-Infra, Hercules-Vault-Infra, scalr-deploy-kestra, scalr-hashistack, automation-scripts, my_tailnet_acl, docker, lunar-claude, Laniakea-Edge, iac
- Simple `config:recommended` extension only
- No customization, scheduling, or rate limiting

**Docker-Focused Configuration (1 repo):**
- Virgo-Core
- Extends: `config:recommended`, `docker:pinDigests`, `helpers:pinGitHubActionDigests`, `:configMigration`, `:pinDevDependencies`, `abandonments:recommended`
- Focus on Docker image digest pinning and GitHub Actions security

**Infrastructure-as-Code Advanced Configuration (1 repo):**
- Sombrero-Edge-Control
- Most comprehensive configuration with:
  - Semantic commits, dependency dashboard, Monday scheduling (UTC)
  - PR limits: 3 concurrent, not-pending creation
  - Auto-merge: Terraform patches, GitHub Actions patches/minor
  - Grouping: Ansible collections, GitHub Actions, Python deps
  - Custom managers: mise tools (terraform, packer, ansible-core), Packer plugins, Ansible Galaxy requirements
  - Approval required: Major Terraform updates, Proxmox provider majors
  - Labels: dependencies, renovate, security (for vulnerability alerts)

**Python Project Advanced Configuration (1 repo):**
- Zammad-MCP
- Python/MCP-specific with:
  - Semantic commits, preserve semver ranges, pin GitHub Actions digests
  - Labels: dependencies, renovate; Assignees: basher83
  - Auto-merge: Dev dependency patches/minor
  - Grouping: pytest packages, Python linters (black, ruff, mypy)
  - Approval required: Major MCP updates, major zammad-py updates
  - Python version cap: <=3.13 (3.14 compatibility issues)
  - PR limits: 3 concurrent, 2 hourly, not-pending creation
  - Custom commit prefixes: `chore(deps):` for prod, `chore(dev-deps):` for dev

**Documentation Site Configuration (1 repo):**
- docs
- Documentation-specific with:
  - Pin all except peer dependencies
  - Monday before 6am schedule (America/New_York)
  - Auto-merge: GitHub Actions patches, npm patches, security updates
  - Approval required: Major updates
  - PR limits: 5 concurrent, 2 hourly
  - Platform automerge enabled
  - Custom commit prefix: ⬆️
  - Labels: dependencies, automated, security, major-update
  - Assignees & reviewers: basher83

### Common Patterns Across Advanced Configs

1. **PR Rate Limiting**: All advanced configs use `prConcurrentLimit` (3-5) and some use `prHourlyLimit` (2)
2. **Scheduling**: Used in Sombrero (Monday early UTC) and docs (Monday before 6am EST)
3. **Auto-merge Strategy**: Patches/minor for trusted sources (GitHub Actions, dev deps)
4. **Approval Gates**: Major updates require manual review
5. **Grouping**: Related dependencies grouped (Ansible, Python linters, npm)
6. **Labels**: Consistent use of "dependencies" and "renovate" labels
7. **Security Alerts**: Vulnerability alerts enabled with special handling
8. **Semantic Commits**: Used in IaC and Python projects

## Proposed Solution

### Preset Architecture

Create layered presets in `.github/renovate/` directory:

**Base Preset (`default.json`):**
- Extends `config:recommended`, `workarounds:all`
- Common PR limits (3 concurrent, 2 hourly, not-pending)
- Standard labels (dependencies, renovate)
- Vulnerability alerts enabled with security label and auto-merge
- Semantic commits enabled
- Timezone: America/New_York (EST)
- Assignee: basher83
- Auto-merge: Security patches by default

**Specialized Presets:**

1. **`docker.json`** - Docker/container workflows
   - Pin Docker digests
   - Pin GitHub Actions digests
   - Enable config migration
   - Pin dev dependencies
   - Abandonments detection

2. **`infrastructure.json`** - Terraform/Ansible/IaC
   - Auto-merge: Terraform patches, GitHub Actions patches/minor, Ansible patch/minor
   - Group: Ansible collections, GitHub Actions
   - Approval gates: Major infrastructure updates (Terraform, Packer, critical providers)
   - Schedule: Monday early morning
   - Note: Relies on Renovate's native mise and ansible-galaxy managers (custom managers removed as redundant)

3. **`python.json`** - Python projects
   - Group: pytest packages, linters (black, ruff, mypy)
   - Auto-merge: Dev dependency patches/minor
   - Custom commit prefix for dev deps
   - pip_requirements file matching

4. **`python-mcp.json`** - Python MCP projects
   - Blocks Python 3.14+ (MCP SDK incompatibility)
   - Approval required for major MCP package updates
   - Special handling for zammad-py and mcp package majors
   - Pin GitHub Actions digests

5. **`documentation.json`** - Docs sites (MkDocs, Docusaurus, etc)
   - Pin all except peer dependencies
   - Auto-merge: patches and security
   - Higher PR concurrent limit (5)
   - Platform automerge enabled
   - Monday before 6am schedule
   - Note: No emoji by default - set at repo level if desired

6. **`github-actions-security.json`** - GitHub Actions hardening
   - Pin Actions to commit SHA
   - Auto-merge digest updates
   - Group all Actions together

### Directory Structure

```
.github/
├── renovate.json              # This repo's config (extends local>basher83/.github:base)
├── renovate/
│   ├── default.json          # Base preset (referenced as local>basher83/.github)
│   ├── docker.json           # Docker-specific preset
│   ├── infrastructure.json   # IaC preset (Terraform, Ansible, Packer)
│   ├── python.json           # Python project preset
│   ├── python-mcp.json       # Python MCP project preset (3.14 blocking)
│   ├── documentation.json    # Documentation site preset
│   └── github-actions-security.json  # Actions security hardening
└── WARP.md                    # Update with Renovate preset documentation
```

### Reference Format for Other Repos

**Basic projects:**
```json
{
  "extends": ["local>basher83/.github"]
}
```

**Docker projects:**
```json
{
  "extends": [
    "local>basher83/.github",
    "local>basher83/.github:docker"
  ]
}
```

**Infrastructure projects:**
```json
{
  "extends": [
    "local>basher83/.github",
    "local>basher83/.github:infrastructure"
  ]
}
```

**Python projects:**
```json
{
  "extends": [
    "local>basher83/.github",
    "local>basher83/.github:python"
  ]
}
```

**Python MCP projects (Zammad-MCP):**
```json
{
  "extends": [
    "local>basher83/.github",
    "local>basher83/.github:python-mcp",
    "local>basher83/.github:github-actions-security"
  ]
}
```

**Multi-stack projects (example: Sombrero-Edge-Control):**
```json
{
  "extends": [
    "local>basher83/.github",
    "local>basher83/.github:infrastructure",
    "local>basher83/.github:python",
    "local>basher83/.github:github-actions-security"
  ],
  "packageRules": [
    // Repository-specific overrides
  ]
}
```

## Implementation Steps

1. Create `.github/renovate/` directory structure
2. Create `default.json` base preset with common settings and expanded auto-merge
3. Create specialized presets (docker, infrastructure, python, python-mcp, documentation, github-actions-security)
4. Update `.github/renovate.json` to extend from `local>basher83/.github`
5. Validate all preset files using `renovate-config-validator` (see https://docs.renovatebot.com/config-validation/)
6. Update WARP.md with Renovate preset documentation
7. Create migration guide for updating existing repositories

## Validation Strategy

1. Run `npx renovate-config-validator` on all preset files
2. Test preset resolution locally using Renovate dry-run
3. Update this repository first as proof-of-concept
4. Gradually migrate 2-3 test repositories
5. Monitor for configuration errors and adjust presets
6. Roll out to remaining repositories

## Benefits

1. **Single Source of Truth**: Change shared settings once, applies everywhere
2. **Consistency**: All repos follow same patterns for PR limits, labels, scheduling
3. **Flexibility**: Repos can extend multiple presets and add custom rules
4. **Visibility**: Configuration remains transparent in each repo's extends array
5. **Maintainability**: Easier to evolve patterns (e.g., add new manager support)
6. **Type Safety**: Each preset has clear purpose and scope

## Migration Considerations

1. **Repository-Specific Rules**: Complex configs like Sombrero-Edge-Control will keep repo-specific packageRules for unique needs (Proxmox provider)
2. **Python 3.14 Blocking**: Centralized in `python-mcp.json` preset for MCP SDK incompatibility - any Python project using MCP SDK should extend this preset
3. **Timezone**: Base preset uses America/New_York (EST) - override at repo level if needed
4. **Commit Prefixes**: No emoji by default in presets - add custom emoji (like ⬆️) at repo level if desired
5. **Backwards Compatibility**: All repos will continue working; migration is opt-in
6. **Auto-merge Strategy**: Expanded to reduce manual PR management - patches/minor for trusted dependencies, security updates always auto-merge

## Key Discoveries During Implementation

### Native Manager Support

Renovate has **native support** for the following, eliminating the need for custom regex managers:

- **mise** - Native `mise` manager automatically updates `.mise.toml` files
- **Ansible Galaxy** - Native `ansible-galaxy` manager handles `requirements.yml` files

**Previous custom regex managers were redundant and have been removed from the shared preset.**

### Recommended Renovate Presets

The base preset leverages official Renovate presets:
- `config:recommended` - Best practices from maintainers
- `workarounds:all` - Crowd-sourced fixes for known package issues (Alpine, Java LTS, Node, Maven, etc.)
