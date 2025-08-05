# 🎭 Ansible Lint Workflow

**Status:** 🚧 In Development  
**Expected Release:** Q3 2025  
**File:** `.github/workflows/ansible-lint.yml`

A comprehensive Ansible validation workflow that ensures playbooks, roles, and collections follow best practices and are free from common issues. This workflow helps maintain high-quality Ansible automation across all projects.

## 🎯 Overview

This workflow provides complete Ansible quality assurance including syntax validation, best practice checking, security analysis, and documentation validation.

### Key Features

- 🔍 **Ansible Lint** - Comprehensive rule checking with customizable rules
- ✅ **Syntax Validation** - YAML and Ansible syntax checking  
- 🔐 **Security Analysis** - ansible-vault and security best practices
- 📚 **Documentation Validation** - Role and playbook documentation checks
- 🏗️ **Multi-version Support** - Ansible 2.12, 2.13, 2.14, 2.15, latest
- 🚀 **Galaxy Integration** - Role and collection dependency validation
- ⚡ **Performance Optimization** - Caching and parallel execution

## 🚀 Quick Start

### Basic Usage

```yaml
name: Ansible Lint
on: [push, pull_request]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "latest"
```

### Advanced Configuration

```yaml
name: Comprehensive Ansible Validation
on: [push, pull_request]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "2.15"
      enable-galaxy-install: true
      enable-custom-rules: true
      config-file: ".ansible-lint"
      requirements-file: "requirements.yml"
      playbook-directory: "playbooks/"
      roles-directory: "roles/"
```

## ⚙️ Configuration Parameters

### Required Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `ansible-version` | string | Ansible version (2.12, 2.13, 2.14, 2.15, latest) |

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable-galaxy-install` | boolean | `true` | Install Galaxy requirements before linting |
| `enable-custom-rules` | boolean | `false` | Enable custom lint rules from repository |
| `config-file` | string | `.ansible-lint` | Path to ansible-lint configuration file |
| `requirements-file` | string | `requirements.yml` | Galaxy requirements file |
| `playbook-directory` | string | `playbooks/` | Directory containing playbooks |
| `roles-directory` | string | `roles/` | Directory containing roles |
| `collections-directory` | string | `collections/` | Directory containing collections |
| `inventory-file` | string | `inventory/hosts` | Inventory file for syntax validation |
| `vault-password-file` | string | `` | Vault password file (if using vault) |
| `extra-vars` | string | `{}` | Extra variables for playbook validation |
| `skip-rules` | string | `` | Comma-separated list of rules to skip |
| `enable-strict-mode` | boolean | `false` | Enable strict mode (warnings as errors) |

### Outputs

| Output | Description |
|--------|-------------|
| `lint-status` | Overall linting status (passed/failed) |
| `syntax-status` | Syntax validation status (passed/failed) |
| `galaxy-status` | Galaxy requirements status (passed/failed/skipped) |
| `violations-count` | Number of lint violations found |

## 🔧 Workflow Steps

### 1. Environment Setup
- Install specified Ansible version
- Set up Python and pip caching
- Install ansible-lint and dependencies

### 2. Galaxy Requirements (Optional)
```bash
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install -r requirements.yml
```

### 3. Syntax Validation
```bash
# Validate playbook syntax
ansible-playbook --syntax-check playbooks/*.yml

# Validate role syntax
ansible-lint roles/*/tasks/main.yml --syntax-check

# Validate YAML structure
yamllint playbooks/ roles/
```

### 4. Ansible Lint Analysis
```bash
# Run ansible-lint with configuration
ansible-lint -c .ansible-lint playbooks/ roles/

# Custom rules (if enabled)
ansible-lint --rules-dir custom-rules/ playbooks/ roles/
```

### 5. Security Analysis
```bash
# Check for vault usage best practices
ansible-lint --tags security playbooks/ roles/

# Validate vault files (if present)
ansible-vault view vault_file.yml --check
```

### 6. Documentation Validation
- Verify role README.md files
- Check meta/main.yml completeness
- Validate task documentation

## 📋 Project Setup Requirements

### Directory Structure
```
ansible-project/
├── playbooks/
│   ├── site.yml
│   └── deploy.yml
├── roles/
│   ├── common/
│   │   ├── tasks/main.yml
│   │   ├── handlers/main.yml
│   │   ├── meta/main.yml
│   │   └── README.md
│   └── webserver/
├── inventory/
│   ├── hosts
│   └── group_vars/
├── requirements.yml
├── .ansible-lint
├── .yamllint
└── ansible.cfg
```

### Configuration Files

#### .ansible-lint
```yaml
---
# Ansible-lint configuration
exclude_paths:
  - .cache/
  - .github/
  - molecule/
  - .ansible/

# Disable specific rules
skip_list:
  - yaml[line-length]  # Allow long lines in certain cases
  - name[casing]       # Allow flexible task naming

# Enable all rules by default
enable_list:
  - fqcn-builtins      # Use FQCN for builtin modules
  - no-log-password    # Ensure passwords are not logged

# Custom rules directory
rulesdir:
  - custom-rules/

# Treat warnings as errors in strict mode
strict: false

# Configure specific rule behavior
rules:
  line-length:
    max: 120
  comments:
    min-spaces-from-content: 1
```

#### .yamllint
```yaml
---
extends: default

rules:
  line-length:
    max: 120
    level: warning
  
  comments:
    min-spaces-from-content: 1
  
  document-start:
    present: true
  
  truthy:
    allowed-values: ['true', 'false', 'yes', 'no']
```

#### requirements.yml
```yaml
---
# Galaxy roles
roles:
  - name: geerlingguy.nginx
    version: 3.1.4
  - name: geerlingguy.docker
    version: 6.1.0

# Galaxy collections  
collections:
  - name: community.general
    version: ">=5.0.0"
  - name: ansible.posix
    version: ">=1.4.0"
  - name: community.docker
    version: ">=3.0.0"
```

#### ansible.cfg
```ini
[defaults]
host_key_checking = False
inventory = inventory/hosts
roles_path = roles/
collections_paths = collections/
gathering = smart
fact_caching = memory
fact_caching_timeout = 86400

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

## 🎯 Usage Examples

### Example 1: Basic Ansible Role

```yaml
name: Ansible Role CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "latest"
      roles-directory: "."
      enable-galaxy-install: false
```

### Example 2: Multi-Version Testing

```yaml
name: Ansible Multi-Version CI
on: [push, pull_request]

jobs:
  ansible-lint:
    strategy:
      matrix:
        ansible-version: ["2.13", "2.14", "2.15", "latest"]
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: ${{ matrix.ansible-version }}
      enable-strict-mode: true
```

### Example 3: Collection Development

```yaml
name: Ansible Collection CI
on: [push, pull_request]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "latest"
      collections-directory: "."
      enable-custom-rules: true
      config-file: ".ansible-lint"
```

### Example 4: Playbook with Vault

```yaml
name: Playbook with Vault CI
on: [push, pull_request]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "2.15"
      playbook-directory: "playbooks/"
      vault-password-file: ".vault-pass"
    secrets:
      VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
```

## 🔍 Troubleshooting

### Common Issues

#### Galaxy Requirements Installation Fails
**Problem:** Dependencies fail to install from Galaxy.

**Solutions:**
1. Check requirements.yml syntax:
   ```yaml
   ---
   roles:
     - name: role.name
       version: "1.0.0"  # Use quotes for version numbers
   ```

2. Use specific versions instead of ranges:
   ```yaml
   collections:
     - name: community.general
       version: "5.8.0"  # Instead of ">=5.0.0"
   ```

#### Lint Rules Too Strict
**Problem:** ansible-lint reports many violations for legacy code.

**Solutions:**
1. Gradually adopt rules:
   ```yaml
   # .ansible-lint
   skip_list:
     - yaml[line-length]
     - name[casing]
     - risky-file-permissions
   ```

2. Use rule-specific ignores:
   ```yaml
   - name: Install package  # noqa name[casing]
     package:
       name: nginx
       state: present
   ```

#### YAML Syntax Errors
**Problem:** yamllint reports formatting issues.

**Solution:**
```yaml
# .yamllint - Relax specific rules
rules:
  line-length:
    max: 200  # Increase limit
  indentation:
    spaces: 2
    indent-sequences: true
```

#### Custom Rules Not Found
**Problem:** Custom lint rules directory not recognized.

**Solution:**
```yaml
# .ansible-lint
rulesdir:
  - ./custom-rules/  # Use relative path
  - /absolute/path/to/rules/  # Or absolute path
```

### Performance Optimization

#### Cache Galaxy Dependencies
```yaml
# Enable in workflow
with:
  enable-galaxy-install: true
  # Galaxy cache is automatically handled
```

#### Parallel Linting
For large projects, lint in parallel:
```yaml
jobs:
  lint-playbooks:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      playbook-directory: "playbooks/"
  
  lint-roles:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      roles-directory: "roles/"
```

## 🚀 Advanced Features

### Custom Lint Rules

Create custom rules for organization-specific standards:

```python
# custom-rules/my_custom_rule.py
from ansiblelint.rules import AnsibleLintRule

class MyCustomRule(AnsibleLintRule):
    id = 'CUSTOM001'
    shortdesc = 'Custom organization rule'
    description = 'All tasks must have tags'
    severity = 'MEDIUM'
    tags = ['custom']
    version_added = 'v1.0.0'

    def matchtask(self, task, file=None):
        if 'tags' not in task:
            return True
        return False
```

### Integration with External Tools

#### Molecule Testing
```yaml
name: Molecule Test
on: [push, pull_request]

jobs:
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "latest"
  
  molecule:
    needs: ansible-lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Molecule
        run: molecule test
```

#### Security Scanning with ansible-security
```yaml
# Additional security step
- name: Security Analysis
  run: |
    pip install ansible-security
    ansible-security scan playbooks/
```

### Vault Management

#### Using GitHub Secrets for Vault
```yaml
# In your workflow
with:
  vault-password-file: ".vault-pass"
secrets:
  VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
```

#### Vault Best Practices
```yaml
# Example vault usage in playbook
- name: Deploy application
  vars:
    db_password: "{{ vault_db_password }}"
  tasks:
    - name: Configure database
      template:
        src: db.conf.j2
        dest: /etc/app/db.conf
        mode: '0600'
      no_log: true  # Prevent password logging
```

## 📊 Metrics and Reporting

The workflow generates comprehensive reports:

- **Lint Report** - Detailed violations with line numbers
- **Syntax Report** - YAML and Ansible syntax validation results
- **Security Report** - Security-related findings
- **Galaxy Report** - Dependency installation status

### Viewing Reports

1. **Console Output**: Detailed lint results in workflow logs
2. **Annotations**: GitHub automatically annotates files with issues
3. **Artifacts**: Download detailed reports as workflow artifacts

## 🤝 Contributing

To contribute improvements to this workflow:

1. **Test with real Ansible projects** of varying complexity
2. **Update documentation** for new features or rule changes
3. **Consider backward compatibility** for existing users
4. **Add examples** for new configuration options

### Development Testing

```bash
# Clone the workflows repository
git clone https://github.com/basher83/.github.git

# Test with a sample Ansible project
cd test-ansible-project
ansible-lint --version
ansible-lint .
```

---

*This workflow incorporates Ansible community best practices and is regularly updated to support new Ansible features and lint rules.*