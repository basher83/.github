# ❓ Frequently Asked Questions

This FAQ addresses common questions about using, configuring, and troubleshooting the reusable GitHub Actions workflows.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Workflow Usage](#workflow-usage)
- [Configuration and Setup](#configuration-and-setup)
- [Troubleshooting](#troubleshooting)
- [Performance and Optimization](#performance-and-optimization)
- [Security and Best Practices](#security-and-best-practices)
- [Contributing and Development](#contributing-and-development)

---

## 🌟 General Questions

### What are reusable workflows and why should I use them?

**Reusable workflows** are GitHub Actions workflows that can be called from other repositories, allowing you to centralize your CI/CD logic and share it across multiple projects.

**Benefits:**
- ✅ **Consistency** - Same quality standards across all projects
- ✅ **Maintainability** - Update once, benefit everywhere
- ✅ **Reduced duplication** - No more copy-pasting workflow files
- ✅ **Best practices** - Pre-configured with security and optimization
- ✅ **Time savings** - Faster project setup and onboarding

**Example:**
```yaml
# Instead of maintaining 50+ identical workflow files
jobs:
  test:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
```

### How do reusable workflows differ from composite actions?

| Feature | Reusable Workflows | Composite Actions |
|---------|-------------------|-------------------|
| **Scope** | Complete job/workflow | Individual steps |
| **Runner** | Can specify runner type | Uses caller's runner |
| **Secrets** | Can access secrets directly | Requires explicit passing |
| **Outputs** | Job-level outputs | Step-level outputs |
| **Use Case** | Full CI/CD pipelines | Reusable step sequences |

**Use reusable workflows for:** Complete testing pipelines, deployment workflows, multi-step processes

**Use composite actions for:** Utility steps, setup tasks, small reusable components

### Which workflows are production-ready?

| Status | Workflows | Reliability |
|--------|-----------|-------------|
| ✅ **Production Ready** | Label Sync, Tailscale Connect | Battle-tested, stable |
| 🚧 **Beta** | Python Quality, Ansible Lint | Feature complete, may change |
| 📋 **Planned** | Docker Build, Terraform Validate | Coming soon |

Check the [roadmap](../ROADMAP.md) for the latest status updates.

---

## 🔧 Workflow Usage

### How do I reference a specific version of a workflow?

```yaml
jobs:
  test:
    # Latest stable version (recommended)
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    
    # Specific version tag (for critical workloads)
    uses: basher83/.github/.github/workflows/python-quality.yml@v1.2.3
    
    # Major version (stable API within major version)
    uses: basher83/.github/.github/workflows/python-quality.yml@v1
```

**Recommendation:** Use `@main` for most cases, `@v1.2.3` for critical production workloads.

### Can I use multiple reusable workflows in the same job?

**No**, each job can only use one reusable workflow. However, you can use multiple jobs:

```yaml
jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
  
  security:
    uses: basher83/.github/.github/workflows/security-scan.yml@main
    needs: quality  # Run after quality checks
  
  docker:
    uses: basher83/.github/.github/workflows/docker-build.yml@main
    needs: [quality, security]
```

### How do I pass secrets to reusable workflows?

```yaml
jobs:
  deploy:
    uses: basher83/.github/.github/workflows/deploy.yml@main
    with:
      environment: "production"
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      SSH_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
      
    # Or inherit all secrets (use carefully)
    secrets: inherit
```

### Can I override or customize workflow behavior?

**Yes**, through input parameters:

```yaml
jobs:
  custom-quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
      coverage-threshold: 95          # Higher than default
      enable-security-scan: false     # Disable if not needed
      requirements-file: "dev-requirements.txt"
      pytest-args: "--verbose --tb=short"
```

For more customization, you can:
1. **Fork the repository** and modify workflows
2. **Request new parameters** via GitHub issues
3. **Create composite actions** for specific customizations

---

## ⚙️ Configuration and Setup

### What secrets do I need to configure?

**Common secrets by workflow:**

#### Python Quality Workflow
```yaml
# Optional - for coverage reporting
secrets:
  CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

#### Docker Build Workflow
```yaml
# Required for pushing images
secrets:
  DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
  DOCKER_PASSWORD: ${{ secrets.DOCKER_TOKEN }}  # Use token, not password!
```

#### Terraform Workflow
```yaml
# Cloud provider credentials
secrets:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  # Optional - for cost estimation
  INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}
```

### How do I set up repository secrets?

1. **Go to your repository** on GitHub
2. **Click Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Add secret name and value**

**Best practices:**
- ✅ Use **descriptive names** (`DOCKER_TOKEN` not `TOKEN`)
- ✅ Use **tokens instead of passwords** when possible
- ✅ Set **appropriate scopes** for tokens
- ✅ **Rotate secrets regularly**
- ❌ Never **hardcode secrets** in workflow files

### What configuration files do I need?

**Python projects:**
```
pyproject.toml    # Black, isort, MyPy, coverage configuration
.flake8          # Flake8 linting rules
requirements.txt  # Dependencies
.gitignore       # Exclude files from version control
```

**Ansible projects:**
```
.ansible-lint     # Ansible-lint configuration
.yamllint        # YAML formatting rules
requirements.yml  # Galaxy dependencies
ansible.cfg      # Ansible configuration
```

**Docker projects:**
```
Dockerfile       # Container build instructions
.dockerignore    # Exclude files from build context
.hadolint.yaml   # Dockerfile linting rules
```

### How do I handle different environments (dev/staging/prod)?

**Option 1: Branch-based environments**
```yaml
jobs:
  deploy-dev:
    if: github.ref == 'refs/heads/develop'
    uses: basher83/.github/.github/workflows/deploy.yml@main
    with:
      environment: "development"
  
  deploy-prod:
    if: github.ref == 'refs/heads/main'
    uses: basher83/.github/.github/workflows/deploy.yml@main
    with:
      environment: "production"
```

**Option 2: Matrix strategy**
```yaml
jobs:
  deploy:
    strategy:
      matrix:
        environment: [dev, staging, prod]
    uses: basher83/.github/.github/workflows/deploy.yml@main
    with:
      environment: ${{ matrix.environment }}
```

**Option 3: Manual deployment with environments**
```yaml
jobs:
  deploy:
    uses: basher83/.github/.github/workflows/deploy.yml@main
    environment: production  # Requires manual approval
    with:
      target: "production"
```

---

## 🔍 Troubleshooting

### "Workflow not found" error

**Error:** `The workflow reference 'basher83/.github/.github/workflows/python-quality.yml@main' could not be found`

**Solutions:**
1. **Check the path** - Ensure the workflow file exists in the repository
2. **Verify branch/tag** - Use `@main` for latest or specific version tags
3. **Repository access** - Ensure your repository can access public workflows
4. **Typos** - Double-check the repository and file path spelling

```yaml
# ✅ Correct
uses: basher83/.github/.github/workflows/python-quality.yml@main

# ❌ Wrong path
uses: basher83/.github/workflows/python-quality.yml@main

# ❌ Wrong repository
uses: basher83/github-workflows/.github/workflows/python-quality.yml@main
```

### "Required input not provided" error

**Error:** `Required input 'python-version' not provided`

**Solution:** Add the required `with:` parameters:

```yaml
jobs:
  test:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"  # This was missing
```

**How to find required inputs:**
1. Check the [workflow documentation](workflows/)
2. Look at the workflow file directly on GitHub
3. Check error message for specific missing inputs

### Workflow fails with authentication errors

**Problem:** `Error: Failed to authenticate with registry`

**Solutions:**

#### For Docker Hub:
```yaml
secrets:
  DOCKER_USERNAME: your-dockerhub-username
  DOCKER_PASSWORD: ${{ secrets.DOCKERHUB_TOKEN }}  # Use token, not password
```

#### For GitHub Container Registry (GHCR):
```yaml
secrets:
  DOCKER_USERNAME: ${{ github.actor }}
  DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}  # Built-in token
```

#### For AWS ECR:
```yaml
secrets:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Tests pass locally but fail in workflows

**Common causes and solutions:**

#### Different Python versions
```yaml
# Use the same Python version locally and in CI
with:
  python-version: "3.11"  # Match your local version
```

#### Missing dependencies
```yaml
# Ensure all dependencies are in requirements files
# requirements.txt - runtime dependencies
# requirements-dev.txt - development dependencies
```

#### Environment differences
```yaml
# Set environment variables in workflow
env:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
  PYTHONPATH: src/
```

#### File path issues
```yaml
# Use relative paths from repository root
with:
  source-directory: "src/"      # Not "/src/" or "./src/"
  test-directory: "tests/"      # Not "/tests/"
```

### Coverage below threshold

**Problem:** `Coverage 75% is below threshold 80%`

**Solutions:**

1. **Add more tests** to reach the threshold
2. **Lower the threshold** temporarily:
   ```yaml
   with:
     coverage-threshold: 75  # Lower threshold
   ```
3. **Exclude files** from coverage:
   ```toml
   # pyproject.toml
   [tool.coverage.run]
   omit = [
     "*/tests/*",
     "*/migrations/*", 
     "manage.py"
   ]
   ```
4. **Add pragma comments** to exclude specific lines:
   ```python
   if __name__ == "__main__":  # pragma: no cover
       main()
   ```

### Large image sizes or slow builds

**Docker build optimization:**

1. **Use multi-stage builds:**
   ```dockerfile
   FROM node:18 AS build
   # Build steps here
   
   FROM node:18-alpine AS runtime
   COPY --from=build /app/dist ./dist
   ```

2. **Optimize .dockerignore:**
   ```
   node_modules/
   .git/
   *.md
   .env*
   ```

3. **Use smaller base images:**
   ```dockerfile
   FROM python:3.11-slim  # Instead of python:3.11
   FROM node:18-alpine    # Instead of node:18
   ```

4. **Enable caching:**
   ```yaml
   with:
     cache-mode: "registry"  # Use registry cache
   ```

---

## ⚡ Performance and Optimization

### How can I speed up my workflows?

#### 1. Use Caching Effectively
```yaml
# Workflows automatically cache dependencies, but you can add more:
- name: Cache pre-commit
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
```

#### 2. Optimize Dependencies
```yaml
# Use specific versions to improve cache hit rates
pip install black==23.1.0 flake8==6.0.0  # Instead of latest
```

#### 3. Parallel Execution
```yaml
# Run jobs in parallel when possible
jobs:
  test:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
  
  lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    # These run simultaneously
```

#### 4. Conditional Execution
```yaml
# Only run when relevant files change
on:
  push:
    paths: ['src/**', 'tests/**', 'requirements.txt']
```

### How do I optimize for cost?

#### 1. Choose Appropriate Runners
```yaml
jobs:
  test:
    runs-on: ubuntu-latest    # Cheapest option
    # Only use larger runners when necessary:
    # runs-on: ubuntu-latest-4-cores
    # runs-on: ubuntu-latest-8-cores
```

#### 2. Optimize Build Matrix
```yaml
# Test only necessary combinations
strategy:
  matrix:
    python-version: ["3.11", "3.12"]  # Not all versions
    os: [ubuntu-latest]                # Only Linux if sufficient
```

#### 3. Skip Redundant Runs
```yaml
# Skip CI on documentation-only changes
on:
  push:
    paths-ignore: ['docs/**', '*.md']
```

#### 4. Use Change Detection
```yaml
# Only build what changed (monorepos)
- uses: dorny/paths-filter@v2
  id: changes
  with:
    filters: |
      api:
        - 'services/api/**'
      frontend:
        - 'services/frontend/**'
```

---

## 🔒 Security and Best Practices

### How do I securely handle secrets?

#### Best Practices
1. **Use repository secrets** - Never hardcode in workflows
2. **Rotate regularly** - Set up automatic rotation if possible
3. **Minimum privileges** - Use tokens with least necessary permissions
4. **Separate environments** - Different secrets for dev/staging/prod

#### Secure Secret Usage
```yaml
# ✅ Good - Secret is masked in logs
- name: Login to registry
  run: echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USERNAME }}" --password-stdin

# ❌ Bad - Never do this
- name: Deploy
  run: deploy.sh ${{ secrets.API_KEY }}  # Visible in logs
```

### Are the workflows secure?

**Yes**, our workflows follow security best practices:

- ✅ **Pinned dependencies** - All actions pinned to specific versions
- ✅ **Security scanning** - Automated vulnerability detection
- ✅ **Minimal permissions** - Least privilege principle
- ✅ **Input validation** - All inputs validated
- ✅ **No secret logging** - Secrets are properly masked

**Security features:**
- **Dependency vulnerability scanning** with Bandit, Safety, pip-audit
- **Container security scanning** with Trivy, Docker Scout
- **Infrastructure security** with tfsec, Checkov
- **SAST integration** with CodeQL (when enabled)

### How do I report security vulnerabilities?

1. **Do NOT create public issues** for security vulnerabilities
2. **Use GitHub Security Advisories:**
   - Go to repository **Security** tab
   - Click **"Report a vulnerability"**
   - Provide detailed description and impact
3. **Or email directly** to security@[domain] (if provided)

**We commit to:**
- **24-48 hour** initial response time
- **Coordinated disclosure** process
- **Credit** to reporters (unless requested otherwise)

---

## 🤝 Contributing and Development

### How can I contribute new workflows?

1. **Check existing issues** for requested workflows
2. **Create an issue** describing the proposed workflow
3. **Follow the [Contributing Guide](CONTRIBUTING.md)** for detailed process
4. **Start with simple implementation** and iterate

**Most wanted workflows:**
- Language-specific quality checks (Go, Rust, Java)
- Cloud deployment workflows (AWS, Azure, GCP)
- Security scanning workflows
- Performance testing workflows

### How do I test workflows during development?

#### 1. Create Test Repository
```bash
# Create a separate test repository
gh repo create test-my-workflow --private
cd test-my-workflow

# Set up project structure for testing
mkdir src tests
echo "def hello(): return 'world'" > src/main.py
echo "from src.main import hello; def test_hello(): assert hello() == 'world'" > tests/test_main.py
```

#### 2. Reference Your Branch
```yaml
# .github/workflows/test.yml
jobs:
  test:
    uses: YOUR-USERNAME/.github/.github/workflows/python-quality.yml@your-feature-branch
    with:
      python-version: "3.11"
```

#### 3. Test Iteratively
```bash
# Make changes to workflow
git add .
git commit -m "Update workflow"
git push

# Test in your test repository
cd ../test-my-workflow
git commit --allow-empty -m "Trigger test"
git push
```

### Can I use these workflows in my organization?

**Yes!** Several options:

#### 1. Use Directly (Recommended)
```yaml
# Reference the public workflows directly
uses: basher83/.github/.github/workflows/python-quality.yml@main
```

#### 2. Fork and Customize
```bash
# Fork the repository to your organization
gh repo fork basher83/.github --org YOUR-ORG

# Then reference your fork
uses: YOUR-ORG/.github/.github/workflows/python-quality.yml@main
```

#### 3. Copy and Modify
- Copy workflows to your `.github` repository
- Modify as needed for your organization
- Maintain independently

### How do I stay updated with changes?

1. **Watch the repository** - Get notifications for releases
2. **Check the [roadmap](../ROADMAP.md)** - See upcoming features
3. **Follow releases** - Review changelog for breaking changes
4. **Join discussions** - Participate in feature discussions

#### Breaking Change Policy
- **6-month notice** for breaking changes
- **Migration guides** provided
- **Deprecation warnings** in workflow outputs
- **Backward compatibility** maintained within major versions

---

## 📞 Need More Help?

### Quick Links
- **[Getting Started Guide](getting-started.md)** - Complete onboarding
- **[Workflow Documentation](workflows/)** - Detailed workflow guides
- **[Usage Examples](examples/)** - Real-world implementations
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

### Community Support
- **[GitHub Discussions](https://github.com/basher83/.github/discussions)** - Ask questions, share ideas
- **[GitHub Issues](https://github.com/basher83/.github/issues)** - Report bugs, request features
- **[GitHub Actions Documentation](https://docs.github.com/en/actions)** - Official GitHub Actions docs

### Getting Help
1. **Search existing issues and discussions** first
2. **Provide complete information** when asking questions:
   - Workflow file content
   - Error messages
   - Repository setup
   - What you expected vs. what happened
3. **Use appropriate labels** when creating issues
4. **Be patient and respectful** - this is a community project

---

*This FAQ is regularly updated based on community questions. If you don't find your answer here, please ask in [GitHub Discussions](https://github.com/basher83/.github/discussions)!*