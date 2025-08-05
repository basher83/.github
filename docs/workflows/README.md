# 🔧 Workflow Documentation

This directory contains detailed documentation for all available reusable GitHub Actions workflows. Each workflow is designed to be production-ready, well-tested, and easy to integrate into your projects.

## 📋 Quick Reference

| Status | Workflow | Description | File | Documentation |
|--------|----------|-------------|------|---------------|
| ✅ | **Sync Labels** | Standardize repository labels across projects | `sync-labels.yml` | [Details](#sync-labels) |
| ✅ | **Tailscale Connect** | Connect GitHub runners to Tailscale tailnet | `tailscale-connect-to-tailnet.yml` | [Details](#tailscale-connect) |
| 🚧 | **Python Quality** | Comprehensive Python CI/CD pipeline | `python-quality.yml` | [python.md](python.md) |
| 🚧 | **Ansible Lint** | Ansible playbook validation and linting | `ansible-lint.yml` | [ansible.md](ansible.md) |
| 📋 | **Docker Build** | Multi-platform Docker builds with security | `docker-build-push.yml` | [docker.md](docker.md) |
| 📋 | **Terraform Validate** | Infrastructure code validation | `terraform-validate.yml` | [terraform.md](terraform.md) |

**Legend:**
- ✅ **Production Ready** - Stable, tested, recommended for all users
- 🚧 **In Development** - Available for testing, may have breaking changes
- 📋 **Planned** - Coming soon, check roadmap for timeline

---

## ✅ Production Workflows

### Sync Labels

**File:** `.github/workflows/sync-labels.yml`  
**Status:** ✅ Production Ready  
**Purpose:** Synchronize repository labels from a central configuration

#### Features
- 🏷️ **Centralized label management** across all repositories
- 🔄 **Automatic synchronization** on schedule or manual trigger
- ⚙️ **Configurable label source** with fallback options
- 🔒 **Safe operation** - only adds/updates, never deletes existing labels

#### Usage Example

```yaml
name: Sync Repository Labels
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM UTC
  workflow_dispatch:

jobs:
  sync-labels:
    uses: basher83/.github/.github/workflows/sync-labels.yml@main
```

#### Inputs

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `label-config-url` | No | [Default config](https://raw.githubusercontent.com/basher83/docs/main/mission-control/github-configs/label-definitions.yml) | URL to YAML file containing label definitions |

#### Label Configuration Format

```yaml
labels:
  - name: "bug"
    color: "d73a4a"
    description: "Something isn't working"
  - name: "enhancement"
    color: "a2eeef"
    description: "New feature or request"
  - name: "documentation"
    color: "0075ca"
    description: "Improvements or additions to documentation"
```

#### Integration Tips
- **Schedule wisely**: Run weekly to keep labels in sync without overwhelming
- **Custom configs**: Host your own label configuration for organization-specific needs
- **Branch protection**: Consider requiring label sync success for main branch protection

---

### Tailscale Connect

**File:** `.github/workflows/tailscale-connect-to-tailnet.yml`  
**Status:** ✅ Production Ready (Beta)  
**Purpose:** Connect GitHub Actions runners to your Tailscale tailnet for secure access to private resources

#### Features
- 🔐 **Secure network access** to private resources during CI/CD
- 🚀 **Self-hosted runner support** for on-premises integrations
- ⚡ **Fast connection** with automatic cleanup
- 🛡️ **Ephemeral nodes** - runners are automatically removed after job completion

#### Usage Example

```yaml
name: Deploy to Private Infrastructure
on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Connect to Tailscale
        uses: basher83/.github/.github/workflows/tailscale-connect-to-tailnet.yml@main
        with:
          tailscale-authkey: ${{ secrets.TAILSCALE_AUTHKEY }}
      - name: Deploy to private server
        run: |
          ssh user@private-server.tailnet 'deploy-script.sh'
```

#### Inputs

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `tailscale-authkey` | Yes | - | Tailscale auth key (store in repository secrets) |
| `tailscale-version` | No | `latest` | Specific Tailscale version to install |

#### Setup Requirements

1. **Generate Auth Key**: Create an ephemeral auth key in your Tailscale admin panel
2. **Store as Secret**: Add the auth key as `TAILSCALE_AUTHKEY` in repository secrets
3. **Configure ACLs**: Ensure proper access controls in your Tailscale configuration

#### Security Considerations
- ✅ Use **ephemeral auth keys** to automatically clean up nodes
- ✅ Set **short expiration times** (1-24 hours) for auth keys
- ✅ Configure **minimal ACL permissions** for CI/CD access only
- ✅ Monitor **tailnet logs** for unexpected connections

---

## 🚧 Development Workflows

### Python Quality (Coming Soon)

**Status:** 🚧 In Development  
**Expected:** Q3 2025  
**Documentation:** [python.md](python.md)

Comprehensive Python quality checks including linting, testing, security scanning, and coverage reporting.

### Ansible Lint (Coming Soon)

**Status:** 🚧 In Development  
**Expected:** Q3 2025  
**Documentation:** [ansible.md](ansible.md)

Ansible playbook validation with configurable rules and multi-version support.

---

## 📋 Planned Workflows

### Docker Build & Push

**Status:** 📋 Planned  
**Expected:** Q4 2025  
**Documentation:** [docker.md](docker.md)

Multi-platform Docker builds with security scanning and registry support.

### Terraform Validate

**Status:** 📋 Planned  
**Expected:** Q4 2025  
**Documentation:** [terraform.md](terraform.md)

Infrastructure code validation with security scanning and cost estimation.

---

## 🔄 Workflow Lifecycle

### Stability Levels

1. **📋 Planned** - Requirements gathering and design phase
2. **🚧 In Development** - Implementation and testing phase
3. **🧪 Beta** - Feature complete, limited production use
4. **✅ Production Ready** - Stable, tested, recommended for all users
5. **⚠️ Deprecated** - Legacy workflow, migration path available
6. **🚫 Retired** - No longer supported or maintained

### Version Management

- **`@main`** - Latest stable version (recommended for production)
- **`@v1`, `@v2`** - Major version tags (stable API within major version)
- **`@v1.2.3`** - Specific version tags (pinned for critical workloads)

### Breaking Changes

Major version bumps (`v1` → `v2`) may include:
- Changes to input parameter names or types
- Changes to output format or structure
- Removal of deprecated features
- Changes to default behavior

We provide **6-month deprecation notice** for breaking changes and **migration guides** for all major version updates.

---

## 🛠️ Development Guidelines

### Contributing New Workflows

1. **Follow naming conventions** - Use descriptive, action-oriented names
2. **Include comprehensive documentation** - Both inline and separate docs
3. **Add usage examples** - Cover common use cases and edge cases
4. **Implement proper error handling** - Fail fast with clear error messages
5. **Include security considerations** - Document required secrets and permissions

### Testing Standards

- **Unit tests** for all reusable actions
- **Integration tests** with real repositories
- **Security scanning** for all workflow dependencies
- **Performance testing** for resource-intensive workflows

---

## 📞 Support

- **Documentation Issues**: Open an issue in this repository
- **Usage Questions**: Check the [FAQ](../FAQ.md) or start a discussion
- **Bug Reports**: Use the issue template with reproduction steps
- **Feature Requests**: Describe use case and expected behavior

---

*For detailed implementation guides, see the individual workflow documentation files in this directory.*