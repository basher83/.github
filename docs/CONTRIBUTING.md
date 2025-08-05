# 🤝 Contributing to Reusable Workflows

Thank you for your interest in contributing to our reusable GitHub Actions workflows! This guide will help you understand how to contribute effectively to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Development Workflow](#development-workflow)
- [Workflow Standards](#workflow-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Requirements](#documentation-requirements)
- [Security Considerations](#security-considerations)
- [Submission Process](#submission-process)

## 🤝 Code of Conduct

This project follows the [GitHub Community Guidelines](https://docs.github.com/en/github/site-policy/github-community-guidelines). By participating, you agree to uphold these standards and help create a welcoming environment for all contributors.

### Our Standards

- **Be respectful** and inclusive in all interactions
- **Provide constructive feedback** and accept it gracefully
- **Focus on what's best** for the community and project
- **Show empathy** towards other community members
- **Learn from mistakes** and help others do the same

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- [ ] **GitHub account** with access to GitHub Actions
- [ ] **Basic understanding** of GitHub Actions and workflow syntax
- [ ] **Familiarity with YAML** and shell scripting
- [ ] **Knowledge of the technology** you're contributing workflows for
- [ ] **Git** installed and configured locally

### Development Environment Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/.github.git
   cd .github
   ```

2. **Set up upstream remote**
   ```bash
   git remote add upstream https://github.com/basher83/.github.git
   git fetch upstream
   ```

3. **Create a test repository** for workflow validation
   ```bash
   # Create a separate test repo to validate your workflows
   gh repo create test-workflows --private
   ```

## 🎯 Types of Contributions

We welcome various types of contributions:

### 1. New Workflow Development
- Create workflows for new technology stacks
- Add support for additional platforms or tools
- Implement requested features from issues

### 2. Workflow Improvements
- Enhance existing workflows with new features
- Optimize performance and resource usage
- Fix bugs or compatibility issues

### 3. Documentation
- Improve workflow documentation and examples
- Add usage tutorials and best practices
- Update README files and inline comments

### 4. Testing and Quality Assurance
- Add test cases for workflows
- Validate workflows against different project types
- Report and fix security vulnerabilities

### 5. Community Support
- Answer questions in discussions and issues
- Review pull requests from other contributors
- Help triage and prioritize issues

## 🔄 Development Workflow

### 1. Issue First

Before starting work:

- [ ] **Check existing issues** to avoid duplication
- [ ] **Create or comment on an issue** describing your proposed changes
- [ ] **Wait for feedback** from maintainers before starting significant work
- [ ] **Get assignment** or confirmation that the contribution is welcome

### 2. Branch Creation

```bash
# Always start from the latest main branch
git checkout main
git pull upstream main

# Create a descriptive feature branch
git checkout -b feature/python-quality-workflow
# OR
git checkout -b fix/ansible-lint-configuration
# OR
git checkout -b docs/improve-contributing-guide
```

### 3. Development Process

1. **Implement your changes** following our standards
2. **Test thoroughly** with real projects
3. **Update documentation** as needed
4. **Commit with clear messages** following conventional commits

```bash
# Conventional commit format
git commit -m "feat: add Python quality workflow with security scanning"
git commit -m "fix: resolve Ansible lint configuration issue"
git commit -m "docs: improve workflow usage examples"
```

### 4. Keep Your Branch Updated

```bash
# Regularly sync with upstream
git fetch upstream
git rebase upstream/main
```

## 📏 Workflow Standards

### File Organization

```
.github/
├── workflows/          # Main reusable workflows
│   ├── python-quality.yml
│   ├── ansible-lint.yml
│   └── docker-build.yml
├── use-workflows/      # Reference implementations
│   ├── use-python-quality.yml
│   └── use-ansible-lint.yml
└── workflow-templates/ # Organization templates
    ├── python-ci.yml
    └── ansible-ci.yml
```

### Naming Conventions

#### Workflow Files
- Use **kebab-case** for file names: `python-quality.yml`, `docker-build-push.yml`
- Be **descriptive and specific**: `terraform-validate.yml` not `tf.yml`
- Include **primary action** in the name: `build`, `test`, `deploy`, `validate`

#### Input Parameters
- Use **snake_case** for input names: `python_version`, `enable_security_scan`
- Provide **clear descriptions** and default values
- Group **related parameters** logically

#### Job and Step Names
- Use **descriptive, action-oriented** names
- Be **consistent** across similar workflows
- Include **context** when helpful: "Install Python dependencies", "Run security scan"

### Input/Output Standards

#### Required Inputs
```yaml
inputs:
  # Always required - no sensible default
  python-version:
    description: 'Python version to use for testing'
    required: true
    type: string
```

#### Optional Inputs with Defaults
```yaml
inputs:
  # Optional with sensible defaults
  coverage-threshold:
    description: 'Minimum coverage percentage required'
    required: false
    default: '80'
    type: string
  
  enable-security-scan:
    description: 'Enable security vulnerability scanning'
    required: false
    default: 'true'
    type: boolean
```

#### Outputs
```yaml
outputs:
  # Always provide useful outputs
  coverage-percentage:
    description: 'Actual coverage percentage achieved'
    value: ${{ jobs.test.outputs.coverage }}
  
  security-issues:
    description: 'Number of security issues found'
    value: ${{ jobs.security.outputs.issues }}
```

### Error Handling

#### Fail Fast Principles
```yaml
steps:
  - name: Validate inputs
    run: |
      if [[ -z "${{ inputs.python-version }}" ]]; then
        echo "Error: python-version is required"
        exit 1
      fi
```

#### Meaningful Error Messages
```yaml
  - name: Check coverage threshold
    run: |
      if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
        echo "❌ Coverage $COVERAGE% is below threshold $THRESHOLD%"
        echo "Please add more tests to reach the required coverage"
        exit 1
      fi
```

## 🧪 Testing Guidelines

### Pre-Submission Testing

Before submitting a pull request:

1. **Test with real projects** of varying complexity
2. **Validate all input combinations** including edge cases
3. **Test error conditions** and failure scenarios
4. **Verify outputs** are correct and useful
5. **Check performance** with realistic workloads

### Testing Framework

#### Create Test Repository
```bash
# Create a test repository structure
mkdir test-project
cd test-project

# Initialize with the technology stack you're testing
# For Python:
mkdir src tests
echo "def hello(): return 'world'" > src/main.py
echo "from src.main import hello; def test_hello(): assert hello() == 'world'" > tests/test_main.py

# Add workflow file
mkdir -p .github/workflows
cat > .github/workflows/test.yml << EOF
name: Test Workflow
on: [push]
jobs:
  test:
    uses: basher83/.github/.github/workflows/python-quality.yml@YOUR-BRANCH
    with:
      python-version: "3.11"
EOF
```

#### Validate Workflow Syntax
```bash
# Use GitHub CLI to validate syntax
gh workflow view .github/workflows/test.yml

# Or use act for local testing
act -n  # Dry run to validate syntax
```

### Test Matrix

Test your workflow with:

#### Different Input Combinations
- **Minimum required inputs** only
- **All optional inputs** specified
- **Edge case values** (empty strings, extreme numbers)
- **Invalid inputs** (verify proper error handling)

#### Various Project Types
- **Simple projects** - basic setup
- **Complex projects** - multiple dependencies, configurations
- **Edge cases** - empty projects, unusual structures
- **Real-world projects** - existing open source projects

#### Different Environments
- **Ubuntu** (latest and older versions)
- **Windows** (if applicable)
- **macOS** (if applicable)
- **Different runner sizes** (resource constraints)

### Performance Testing

#### Measure Key Metrics
- **Execution time** for different project sizes
- **Resource usage** (CPU, memory, disk)
- **Cache effectiveness** (hit rates, build time reduction)
- **Cost implications** (GitHub Actions minutes)

#### Optimize for Performance
```yaml
# Use caching effectively
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('requirements.txt') }}

# Minimize unnecessary work
- name: Check if tests are needed
  id: changes
  run: |
    if git diff --name-only HEAD~1 | grep -E '\.(py|txt)$'; then
      echo "needs-testing=true" >> $GITHUB_OUTPUT
    fi
```

## 📚 Documentation Requirements

### Inline Documentation

#### Workflow Comments
```yaml
name: Python Quality Checks
# This workflow provides comprehensive Python quality assurance including:
# - Code formatting (Black, isort)
# - Linting (Flake8, pylint)
# - Type checking (MyPy)
# - Security scanning (Bandit, Safety)
# - Testing and coverage (pytest, coverage.py)

on:
  workflow_call:
    inputs:
      python-version:
        description: |
          Python version to use for testing.
          Supports: 3.9, 3.10, 3.11, 3.12, latest
        required: true
        type: string
```

#### Step Documentation
```yaml
steps:
  - name: Install Python dependencies
    # Install project dependencies with pip caching for performance.
    # Uses requirements.txt by default, but can be overridden with inputs.
    run: |
      pip install --upgrade pip
      pip install -r ${{ inputs.requirements-file }}
```

### External Documentation

#### Workflow Documentation File
Each workflow must have a corresponding documentation file in `docs/workflows/`:

```markdown
# docs/workflows/python-quality.md

# 🐍 Python Quality Workflow

**Status:** ✅ Production Ready
**File:** `.github/workflows/python-quality.yml`

## Overview
[Detailed description of workflow purpose and features]

## Usage Examples
[Multiple real-world examples with full YAML]

## Configuration Parameters
[Complete parameter reference with types and defaults]

## Troubleshooting
[Common issues and solutions]
```

#### README Updates
Update the main README.md with:
- New workflow in the table
- Link to documentation
- Status badge if applicable

### Example Documentation

#### Comprehensive Usage Example
```yaml
# Include a complete, working example
name: Python CI
on: [push, pull_request]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      coverage-threshold: 85
      enable-security-scan: true
      requirements-file: "requirements-dev.txt"
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

#### Configuration File Examples
```yaml
# Show complete configuration file examples
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

## 🔒 Security Considerations

### Secure Workflow Design

#### Input Validation
```yaml
# Validate all inputs
- name: Validate Python version
  run: |
    case "${{ inputs.python-version }}" in
      3.9|3.10|3.11|3.12|latest) ;;
      *) echo "Invalid Python version"; exit 1 ;;
    esac
```

#### Secret Handling
```yaml
# Never log secrets
- name: Authenticate with registry
  run: echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USERNAME }}" --password-stdin
  # Note: This is safe because GitHub automatically masks secrets in logs
```

#### Least Privilege
```yaml
# Use minimal permissions
permissions:
  contents: read
  security-events: write  # Only if needed for security scanning
```

### Security Review Checklist

Before submitting:

- [ ] **No hardcoded secrets** or credentials
- [ ] **Input validation** for all user-provided data
- [ ] **Secure defaults** for all configuration options
- [ ] **Minimal permissions** specified
- [ ] **Third-party actions** pinned to specific versions
- [ ] **Security scanning** enabled where appropriate

### Dependency Management

#### Pin Action Versions
```yaml
# ✅ Good - pinned to specific version
- uses: actions/checkout@v4.1.1

# ❌ Bad - floating tag
- uses: actions/checkout@v4
```

#### Verify Third-Party Actions
```yaml
# Research and verify any third-party actions
- uses: well-known-org/trusted-action@v1.2.3
  # Verify: reputation, maintenance, security track record
```

## 📝 Submission Process

### Pull Request Checklist

Before submitting your pull request:

#### Code Quality
- [ ] **Workflow syntax** is valid (tested with `gh workflow view`)
- [ ] **Follows naming conventions** and style guide
- [ ] **Includes proper error handling** and meaningful messages
- [ ] **Has been tested** with real projects
- [ ] **Performance optimized** (caching, minimal steps)

#### Documentation
- [ ] **Inline comments** explain complex logic
- [ ] **Complete documentation file** in `docs/workflows/`
- [ ] **Usage examples** are accurate and comprehensive
- [ ] **README.md updated** with new workflow information
- [ ] **CHANGELOG.md updated** (if exists)

#### Testing
- [ ] **Tested with multiple projects** of varying complexity
- [ ] **Edge cases validated** (empty inputs, error conditions)
- [ ] **Performance impact assessed** and optimized
- [ ] **Security review completed** using checklist

#### Git Hygiene
- [ ] **Branch is up-to-date** with main
- [ ] **Commits are logical** and well-described
- [ ] **No merge commits** in feature branch (use rebase)
- [ ] **Conventional commit format** used

### Pull Request Template

When creating your pull request, include:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] New workflow
- [ ] Workflow improvement
- [ ] Bug fix
- [ ] Documentation update
- [ ] Breaking change

## Testing Performed
- [ ] Tested with [project-type] projects
- [ ] Validated error handling
- [ ] Performance tested
- [ ] Security reviewed

## Related Issues
Closes #123
Related to #456

## Breaking Changes
None / Describe any breaking changes

## Additional Notes
Any additional context or considerations
```

### Review Process

1. **Automated Checks** - CI will validate syntax and run basic tests
2. **Initial Review** - Maintainer will review for standards compliance
3. **Community Feedback** - Other contributors may provide input
4. **Testing Period** - Workflow may be tested in real environments
5. **Final Approval** - Maintainer approval and merge

### Post-Merge

After your contribution is merged:

1. **Monitor for issues** - Watch for any problems reported
2. **Respond to questions** - Help users who have questions about your workflow
3. **Iterate and improve** - Be open to feedback and future improvements

## 🎉 Recognition

Contributors are recognized in several ways:

- **GitHub Contributors** section
- **Release notes** for significant contributions
- **Community highlights** in discussions
- **Maintainer consideration** for frequent contributors

## 📞 Getting Help

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community discussion
- **Pull Request Comments** - Specific code review feedback

### Maintainer Contact

For sensitive issues or questions:
- Create a private security advisory for security issues
- Tag `@basher83` in discussions for urgent matters

---

**Thank you for contributing to make CI/CD better for everyone! 🚀**

*This guide is a living document. If you find areas for improvement, please submit a pull request to update it.*