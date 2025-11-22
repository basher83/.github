# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Purpose

This is a shared GitHub Actions workflow repository that provides reusable workflows and workflow templates for personal projects. It follows GitHub's reusable workflow pattern to centralize CI/CD automation across multiple repositories.

## Repository Architecture

### Directory Structure

**`.github/workflows/`** - Reusable workflows that other repositories call
- These are the "operational" workflows invoked via `workflow_call` trigger
- Current workflows: label syncing, Tailscale connectivity

**`.github/use-workflows/`** - Working example implementations
- Demonstrates how to consume the reusable workflows from remote repositories
- Use as reference when integrating workflows into other projects

**`.github/workflow-templates/`** - Organization-wide workflow templates
- Provides quick-add templates via GitHub's UI
- Includes both `.yml` workflow files and `.properties.json` metadata

**`docs/`** - Planning and tracking documentation
- Contains TODO.md with implementation roadmap

### Workflow Types

#### Label Management (`sync-labels.yml`)
- Downloads label definitions from central repository (`basher83/docs`)
- Uses `yq` to transform nested YAML structure into flat array
- Syncs labels using `micnncim/action-label-syncer` with pruning enabled
- Supports custom label definition URL via input parameter

**Key Implementation Detail:** The workflow transforms nested label categories into a flat array structure that the label-syncer action expects.

#### Tailscale Integration
- `tailscale-connect-to-tailnet.yml`: Establishes Tailscale connection for CI/CD runners
- `tailscale-policy.yml`: Tests and deploys Tailscale ACL policies with caching

Both use OAuth authentication via secrets and are designed as callable workflows.

## Common Commands

### Testing Workflows Locally
```bash
# Install act for local GitHub Actions testing
brew install act

# Run a workflow locally (if supported)
act workflow_dispatch -W .github/workflows/<workflow-name>.yml
```

### Validating YAML Workflows
```bash
# Lint GitHub Actions workflow files
brew install actionlint
actionlint .github/workflows/*.yml
actionlint .github/use-workflows/*.yml
```

### Working with yq (Label Transformation)
```bash
# Install yq for YAML processing
brew install yq

# Test label transformation locally
curl -sSL https://raw.githubusercontent.com/basher83/docs/main/mission-control/github-configs/label-definitions.yml -o label-definitions.yml
yq eval '[.[] | .[]]' label-definitions.yml > transformed-labels.yml
```

### Validating Renovate Configuration
```bash
# Validate renovate.json
npx --yes --package renovate -- renovate-config-validator
```

## Creating New Reusable Workflows

When adding new reusable workflows to this repository:

1. **Create the operational workflow** in `.github/workflows/`
   - Use `workflow_call` as the trigger
   - Define inputs and secrets as needed
   - Set appropriate permissions (least privilege)

2. **Create usage example** in `.github/use-workflows/`
   - Shows how external repositories would consume it
   - Include `workflow_dispatch` trigger for testing

3. **Create workflow template** (optional) in `.github/workflow-templates/`
   - Add both `.yml` and `.properties.json` files
   - Template appears in GitHub's "Actions" → "New workflow" UI

4. **Reference format for external repos:**
   ```yaml
   uses: basher83/.github/.github/workflows/<workflow-name>.yml@main
   ```

## Planned Workflows (from ROADMAP.md)

The repository is actively being expanded to support:

- **Python**: Quality checks, linting (black, flake8, mypy, bandit), pytest with coverage
- **Ansible**: Linting with ansible-lint, galaxy requirements validation
- **Docker**: Multi-platform builds, vulnerability scanning, registry publishing
- **Terraform/OpenTofu**: Validation, fmt, plan, tfsec security scanning
- **Security**: CodeQL SAST, dependency scanning, secret detection
- **Documentation**: MkDocs/Sphinx/Docusaurus builds with auto-deployment
- **Release**: Semantic versioning, automated release notes, GitHub releases
- **Dependencies**: Enhanced Renovate configurations with auto-merge

## Workflow Development Pattern

All workflows follow this pattern:
1. Validate inputs and prerequisites
2. Perform dry-run or validation step with detailed output
3. Execute main action
4. Provide post-action summary

This ensures transparency and makes troubleshooting easier when workflows are used across multiple repositories.


## Important Considerations

- **Secrets Management**: Workflows requiring secrets (Tailscale OAuth, GitHub tokens) expect them to be configured in the calling repository
- **Pruning Behavior**: The label sync workflow uses `prune: true`, which removes labels not in the central definition
- **Central Source of Truth**: Label definitions live in `basher83/docs` repository, not here
- **Workflow References**: Always pin to `@main` or specific commit SHA when calling reusable workflows from external repos
- **Renovate Presets**: Dependency management presets are maintained in the separate **[basher83/renovate-config](https://github.com/basher83/renovate-config)** repository
