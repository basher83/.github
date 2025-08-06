# 🚀 Reusable GitHub Actions Workflows

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Workflows](https://img.shields.io/badge/Workflows-5-blue.svg)](#available-workflows)
[![Documentation](https://img.shields.io/badge/Docs-Complete-green.svg)](docs/)

This repository serves as a **central hub for reusable GitHub Actions workflows** that can be called from your other repositories. Standardize and simplify your CI/CD and automation across all your projects with battle-tested, production-ready workflows.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Available Workflows](#-available-workflows)
- [Repository Structure](#-repository-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

## 🚀 Quick Start

### Using a Workflow in Your Repository

1. **Create a workflow file** in your repository (e.g., `.github/workflows/ci.yml`)
2. **Reference the reusable workflow** from this repository:

```yaml
name: CI Pipeline
on: [push, pull_request]

jobs:
  quality-checks:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
      coverage-threshold: 80
```

3. **Customize parameters** as needed for your project
4. **Commit and push** - your workflow will run automatically!

### Available Workflows

| Workflow | Description | Status | Documentation |
|----------|-------------|--------|---------------|
| 🏷️ **Sync Labels** | Synchronize repository labels from central config | ✅ Production | [docs/workflows/](docs/workflows/) |
| 🔐 **Tailscale Connect** | Connect GitHub runner to Tailscale tailnet | 🧪 Beta | [docs/workflows/](docs/workflows/) |
| 🐍 **Python Quality** | Comprehensive Python linting and testing | 🚧 Planned | [docs/workflows/python.md](docs/workflows/python.md) |
| 🎭 **Ansible Lint** | Ansible playbook validation and linting | 🚧 Planned | [docs/workflows/ansible.md](docs/workflows/ansible.md) |
| 🐳 **Docker Build** | Multi-platform Docker builds with security scanning | 🚧 Planned | [docs/workflows/docker.md](docs/workflows/docker.md) |

## 📁 Repository Structure

```
.github/
├── workflows/          # Operational workflows (called by remote repos)
├── use-workflows/      # Reference implementations for remote repos
└── workflow-templates/ # Organization-wide workflow templates

docs/
├── getting-started.md  # Comprehensive onboarding guide
├── workflows/          # Individual workflow documentation
├── examples/           # Practical usage examples
├── CONTRIBUTING.md     # Contribution guidelines
└── FAQ.md             # Frequently asked questions
```

## 📚 Documentation

- **[Getting Started Guide](docs/getting-started.md)** - Complete onboarding for new users
- **[Workflow Documentation](docs/workflows/)** - Detailed guides for each workflow
- **[Usage Examples](docs/examples/)** - Real-world implementation examples
- **[Roadmap](ROADMAP.md)** - Project timeline and upcoming features
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute to this project
- **[FAQ](docs/FAQ.md)** - Common questions and troubleshooting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details on:

- How to submit issues and feature requests
- Development workflow and coding standards
- Testing and documentation requirements

## 📈 Roadmap

See our [detailed roadmap](ROADMAP.md) for upcoming features and current progress. We're continuously expanding our workflow collection to cover more technology stacks and use cases.

---

*Built with ❤️ to streamline CI/CD across all projects*
