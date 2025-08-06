# 🚀 Getting Started with Reusable Workflows

Welcome to the central hub for reusable GitHub Actions workflows! This guide will help you get up and running quickly with our battle-tested CI/CD workflows.

## 📋 Table of Contents

- [What Are Reusable Workflows?](#what-are-reusable-workflows)
- [Prerequisites](#prerequisites)
- [Your First Workflow](#your-first-workflow)
- [Available Workflows](#available-workflows)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## 🤔 What Are Reusable Workflows?

Reusable workflows allow you to define CI/CD logic once and use it across multiple repositories. Instead of copying and pasting workflow files, you can:

- ✅ **Reference workflows from this central repository**
- ✅ **Automatically get updates and improvements**
- ✅ **Maintain consistency across all your projects**
- ✅ **Reduce maintenance overhead**

## ✅ Prerequisites

Before you start, ensure you have:

- [ ] A GitHub repository where you want to add CI/CD
- [ ] Basic familiarity with [GitHub Actions](https://docs.github.com/en/actions)
- [ ] Understanding of YAML syntax
- [ ] Repository permissions to create/modify workflows

## 🎯 Your First Workflow

Let's start with the simplest and most useful workflow: **Label Synchronization**.

### Step 1: Create the Workflow File

In your repository, create `.github/workflows/sync-labels.yml`:

```yaml
name: Sync Repository Labels

on:
  schedule:
    # Run weekly on Sundays at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch: # Allow manual triggering

jobs:
  sync-labels:
    name: Sync Labels
    uses: basher83/.github/.github/workflows/sync-labels.yml@main
```

### Step 2: Commit and Test

1. **Commit the file** to your repository
2. **Go to Actions tab** in your GitHub repository
3. **Manually trigger** the workflow using "Run workflow" button
4. **Watch the magic happen** - your labels will be synchronized!

### Step 3: Verify Results

Check your repository's labels section. You should see standardized labels that match across all your repositories using this workflow.

## 🛠️ Available Workflows

### Production Ready ✅

| Workflow | File | Use Case | Documentation |
|----------|------|----------|---------------|
| **Label Sync** | `sync-labels.yml` | Standardize repository labels | [View Details](workflows/README.md#sync-labels) |
| **Tailscale Connect** | `tailscale-connect-to-tailnet.yml` | Connect runners to Tailscale | [View Details](workflows/README.md#tailscale-connect) |

### Coming Soon 🚧

| Workflow | Status | Use Case | ETA |
|----------|--------|----------|-----|
| **Python Quality** | In Development | Python linting, testing, security | Q3 2025 |
| **Ansible Lint** | In Development | Ansible playbook validation | Q3 2025 |
| **Docker Build** | Planned | Multi-platform container builds | Q4 2025 |
| **Terraform Validate** | Planned | Infrastructure validation | Q4 2025 |

## 🎨 Common Patterns

### Pattern 1: Basic Workflow Usage

```yaml
name: My Workflow
on: [push, pull_request]

jobs:
  my-job:
    uses: basher83/.github/.github/workflows/WORKFLOW_NAME.yml@main
```

### Pattern 2: Workflow with Parameters

```yaml
name: Python CI
on: [push, pull_request]

jobs:
  quality-checks:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
      coverage-threshold: 80
      run-security-scan: true
```

### Pattern 3: Conditional Workflow Execution

```yaml
name: Conditional Deployment
on: [push]

jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    uses: basher83/.github/.github/workflows/deploy.yml@main
    with:
      environment: production
```

### Pattern 4: Matrix Strategy with Reusable Workflows

```yaml
name: Multi-Version Testing
on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: ${{ matrix.python-version }}
```

## 🔧 Troubleshooting

### Common Issues

#### "Workflow not found" Error
- ✅ **Check the workflow path** - ensure it exists in this repository
- ✅ **Verify the branch/tag** - use `@main` for latest or specific tags
- ✅ **Check repository permissions** - ensure your repo can access public workflows

#### "Required input not provided" Error
- ✅ **Review workflow documentation** - check required `with:` parameters
- ✅ **Validate YAML syntax** - ensure proper indentation and structure

#### "Workflow failed" Issues
- ✅ **Check workflow logs** - click on the failed job for detailed output
- ✅ **Verify repository secrets** - some workflows require authentication tokens
- ✅ **Review input parameters** - ensure values match expected formats

### Getting Help

1. **Check the [FAQ](FAQ.md)** for common questions
2. **Review [workflow documentation](workflows/)** for specific workflows
3. **Look at [example implementations](examples/)** for reference
4. **Open an issue** in this repository for bugs or feature requests

## 🚀 Next Steps

Now that you have your first workflow running, consider:

### Expand Your CI/CD Pipeline
- **Add more workflows** as they become available
- **Combine multiple workflows** for comprehensive coverage
- **Set up notifications** for workflow failures

### Customize for Your Needs
- **Review workflow parameters** to match your project requirements
- **Set up repository secrets** for workflows that need authentication
- **Configure branch protection rules** to require workflow success

### Stay Updated
- **Watch this repository** for new workflow releases
- **Check the [roadmap](../ROADMAP.md)** for upcoming features
- **Join discussions** about new workflow ideas

### Contribute Back
- **Share feedback** on existing workflows
- **Suggest improvements** or new workflow ideas
- **Contribute documentation** improvements
- **Submit pull requests** for bug fixes

## 📚 Additional Resources

- **[Workflow Documentation](workflows/)** - Detailed guides for each workflow
- **[Usage Examples](examples/)** - Real-world implementation examples
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to this project
- **[GitHub Actions Documentation](https://docs.github.com/en/actions)** - Official GitHub Actions docs

---

*Ready to standardize your CI/CD? Pick a workflow and get started! 🎉*