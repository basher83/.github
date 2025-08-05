# 🐍 Python Quality Workflow

**Status:** 🚧 In Development  
**Expected Release:** Q3 2025  
**File:** `.github/workflows/python-quality.yml`

A comprehensive Python CI/CD workflow that includes linting, testing, security scanning, and coverage reporting. This workflow is designed to maintain high code quality standards across all Python projects.

## 🎯 Overview

This workflow provides a complete Python quality assurance pipeline that can be customized for different project needs while maintaining consistent standards across all repositories.

### Key Features

- 🔍 **Multi-tool Linting** - Black, Flake8, MyPy, isort
- 🧪 **Comprehensive Testing** - pytest with coverage reporting
- 🔐 **Security Scanning** - Bandit, Safety, pip-audit
- 📊 **Coverage Analysis** - Configurable thresholds with detailed reports
- 🏗️ **Build Validation** - Package building and installation testing
- 🚀 **Multi-version Support** - Python 3.9, 3.10, 3.11, 3.12
- ⚡ **Caching Optimization** - pip, pre-commit, and dependency caching

## 🚀 Quick Start

### Basic Usage

```yaml
name: Python Quality Checks
on: [push, pull_request]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
```

### Advanced Configuration

```yaml
name: Comprehensive Python CI
on: [push, pull_request]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
      coverage-threshold: 85
      enable-security-scan: true
      enable-type-checking: true
      requirements-file: "requirements-dev.txt"
      test-directory: "tests/"
      source-directory: "src/"
```

## ⚙️ Configuration Parameters

### Required Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `python-version` | string | Python version to use (3.9, 3.10, 3.11, 3.12) |

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coverage-threshold` | number | `80` | Minimum coverage percentage required |
| `enable-security-scan` | boolean | `true` | Run security vulnerability scans |
| `enable-type-checking` | boolean | `true` | Run MyPy type checking |
| `requirements-file` | string | `requirements.txt` | Path to requirements file |
| `test-directory` | string | `tests/` | Directory containing tests |
| `source-directory` | string | `src/` | Directory containing source code |
| `lint-config-file` | string | `pyproject.toml` | Configuration file for linting tools |
| `pytest-args` | string | `-v` | Additional arguments for pytest |
| `black-args` | string | `--check --diff` | Additional arguments for Black |
| `flake8-config` | string | `.flake8` | Flake8 configuration file |
| `mypy-config` | string | `myproject.toml` | MyPy configuration file |
| `bandit-config` | string | `.bandit` | Bandit configuration file |

### Outputs

| Output | Description |
|--------|-------------|
| `coverage-percentage` | Actual coverage percentage achieved |
| `lint-status` | Overall linting status (passed/failed) |
| `test-status` | Test execution status (passed/failed) |
| `security-status` | Security scan status (passed/failed/skipped) |

## 🔧 Workflow Steps

### 1. Environment Setup
- Install specified Python version
- Set up pip caching for faster builds
- Install build dependencies

### 2. Dependency Installation
- Install package dependencies from requirements file
- Install development dependencies for testing
- Cache installed packages for subsequent runs

### 3. Code Quality Checks

#### Formatting (Black)
```bash
black --check --diff src/ tests/
```

#### Import Sorting (isort)
```bash
isort --check-only --diff src/ tests/
```

#### Linting (Flake8)
```bash
flake8 src/ tests/
```

#### Type Checking (MyPy)
```bash
mypy src/
```

### 4. Testing & Coverage

#### Test Execution
```bash
pytest tests/ --cov=src/ --cov-report=xml --cov-report=html
```

#### Coverage Analysis
- Generate coverage reports in multiple formats
- Validate against configured threshold
- Upload coverage data to external services (if configured)

### 5. Security Scanning

#### Static Security Analysis (Bandit)
```bash
bandit -r src/ -f json -o bandit-report.json
```

#### Dependency Vulnerability Scanning
```bash
pip-audit --desc --format=json --output=security-report.json
safety check --json
```

### 6. Build Validation
```bash
python -m build
pip install dist/*.whl
python -c "import your_package; print('Import successful')"
```

## 📋 Project Setup Requirements

### Directory Structure
```
your-project/
├── src/
│   └── your_package/
│       └── __init__.py
├── tests/
│   └── test_*.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .flake8
└── README.md
```

### Configuration Files

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

#### .flake8
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv
```

#### requirements-dev.txt
```txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
isort>=5.0.0
mypy>=1.0.0
bandit>=1.7.0
pip-audit>=2.0.0
safety>=2.0.0
build>=0.10.0
```

## 🎯 Usage Examples

### Example 1: Basic Python Package

```yaml
name: Python Package CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      coverage-threshold: 90
      source-directory: "mypackage/"
      test-directory: "tests/"
```

### Example 2: Multi-Version Testing

```yaml
name: Python Multi-Version CI
on: [push, pull_request]

jobs:
  quality:
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: ${{ matrix.python-version }}
      coverage-threshold: 85
```

### Example 3: Django Project

```yaml
name: Django Project CI
on: [push, pull_request]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
      requirements-file: "requirements/dev.txt"
      source-directory: "myproject/"
      test-directory: "myproject/tests/"
      pytest-args: "--ds=myproject.settings.test -v"
      coverage-threshold: 80
```

## 🔍 Troubleshooting

### Common Issues

#### Import Errors During Testing
**Problem:** Tests fail with import errors despite successful installation.

**Solution:**
```yaml
# Add PYTHONPATH to environment
with:
  pytest-args: "--pythonpath=src -v"
```

#### Coverage Below Threshold
**Problem:** Coverage check fails even with good test coverage.

**Solutions:**
1. Exclude test files from coverage:
   ```toml
   [tool.coverage.run]
   omit = ["*/tests/*", "*/test_*.py"]
   ```

2. Add pragmas to exclude specific lines:
   ```python
   if __name__ == "__main__":  # pragma: no cover
       main()
   ```

#### Type Checking Failures
**Problem:** MyPy reports type errors in dependencies.

**Solution:**
```toml
[tool.mypy]
ignore_missing_imports = true
# OR for specific packages
[[tool.mypy.overrides]]
module = "some_third_party_package.*"
ignore_missing_imports = true
```

#### Security Scan False Positives
**Problem:** Bandit reports false positive security issues.

**Solution:**
```python
# Use bandit skip comments
password = "test_password"  # nosec B105
```

### Performance Optimization

#### Caching Dependencies
The workflow automatically caches pip dependencies, but you can optimize further:

```yaml
# In your repository's workflow
- name: Cache pre-commit
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
```

#### Parallel Testing
For large test suites, consider pytest-xdist:

```yaml
with:
  pytest-args: "-n auto --dist worksteal"
```

## 🚀 Advanced Features

### Integration with External Services

#### Code Coverage (Codecov)
```yaml
jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.12"
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

#### Code Quality (SonarCloud)
```yaml
# Additional step after workflow
- name: SonarCloud Scan
  uses: SonarSource/sonarcloud-github-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Custom Test Commands

```yaml
with:
  pytest-args: >
    --cov=src 
    --cov-report=xml 
    --cov-report=html 
    --cov-fail-under=85
    --doctest-modules
    --junitxml=test-results.xml
```

## 📊 Metrics and Reporting

The workflow generates several reports:

- **Coverage Report** - HTML and XML formats
- **Test Results** - JUnit XML for integration with GitHub
- **Security Report** - JSON format with vulnerability details
- **Lint Report** - Detailed output for all linting tools

### Viewing Reports

1. **Coverage**: Check the workflow artifacts for HTML coverage report
2. **Security**: View JSON reports in workflow logs
3. **Tests**: GitHub automatically displays test results in PR checks

## 🤝 Contributing

This workflow is part of the central reusable workflows repository. To contribute improvements:

1. **Fork the repository** and create a feature branch
2. **Test changes** with real Python projects
3. **Update documentation** to reflect new features
4. **Submit a pull request** with detailed description

### Development Setup

```bash
git clone https://github.com/basher83/.github.git
cd .github
# Make changes to .github/workflows/python-quality.yml
# Test with a sample Python project
```

---

*This workflow is continuously improved based on Python community best practices and user feedback.*