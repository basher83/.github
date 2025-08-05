# 🏗️ Terraform Validation Workflow

**Status:** 📋 Planned  
**Expected Release:** Q4 2025  
**File:** `.github/workflows/terraform-validate.yml`

A comprehensive Infrastructure as Code (IaC) workflow for Terraform and OpenTofu that includes validation, security scanning, cost estimation, and best practice enforcement. This workflow ensures reliable and secure infrastructure deployments.

## 🎯 Overview

This workflow provides complete IaC quality assurance including syntax validation, security analysis, cost estimation, and policy compliance checking for Terraform and OpenTofu configurations.

### Key Features

- ✅ **Terraform & OpenTofu Support** - Full compatibility with both tools
- 🔐 **Security Scanning** - tfsec, Checkov, Terrascan integration
- 💰 **Cost Estimation** - Infracost integration for cost impact analysis
- 📏 **Policy Compliance** - OPA/Rego policy validation
- 🏷️ **Multi-Version Support** - Terraform 1.3, 1.4, 1.5, 1.6, latest
- 📋 **Plan Analysis** - Detailed plan output with change summaries
- 🔄 **State Management** - Remote state validation and drift detection
- ⚡ **Performance Optimization** - Provider caching and parallel execution

## 🚀 Quick Start

### Basic Usage

```yaml
name: Terraform Validation
on: [push, pull_request]

jobs:
  terraform:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "latest"
      working-directory: "terraform/"
```

### Advanced Configuration

```yaml
name: Infrastructure Validation
on:
  push:
    branches: [main]
    paths: ['terraform/**']
  pull_request:
    paths: ['terraform/**']

jobs:
  terraform:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "1.6.0"
      working-directory: "infrastructure/"
      enable-security-scan: true
      enable-cost-estimation: true
      enable-policy-check: true
      backend-config-file: "backend.hcl"
      var-file: "terraform.tfvars"
      plan-file: "terraform.plan"
      terraform-docs: true
      enable-drift-detection: true
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}
```

## ⚙️ Configuration Parameters

### Required Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `terraform-version` | string | Terraform version (1.3, 1.4, 1.5, 1.6, latest) |

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `working-directory` | string | `.` | Directory containing Terraform files |
| `tool` | string | `terraform` | Tool to use (terraform, tofu) |
| `enable-security-scan` | boolean | `true` | Run security scanning tools |
| `enable-cost-estimation` | boolean | `false` | Run Infracost analysis |
| `enable-policy-check` | boolean | `false` | Run OPA policy validation |
| `enable-drift-detection` | boolean | `false` | Check for configuration drift |
| `terraform-docs` | boolean | `false` | Generate Terraform documentation |
| `backend-config-file` | string | `` | Backend configuration file |
| `var-file` | string | `terraform.tfvars` | Variables file |
| `plan-file` | string | `terraform.plan` | Plan output file |
| `destroy-plan` | boolean | `false` | Generate destroy plan |
| `auto-approve-apply` | boolean | `false` | Auto-approve applies (dangerous!) |
| `parallelism` | number | `10` | Terraform parallelism setting |
| `timeout` | string | `30m` | Terraform operation timeout |
| `tfsec-config` | string | `.tfsec.yml` | tfsec configuration file |
| `checkov-config` | string | `.checkov.yml` | Checkov configuration file |
| `policy-directory` | string | `policies/` | OPA policies directory |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | No* | AWS access key (*required for AWS resources) |
| `AWS_SECRET_ACCESS_KEY` | No* | AWS secret key (*required for AWS resources) |
| `AZURE_CLIENT_ID` | No | Azure service principal client ID |
| `AZURE_CLIENT_SECRET` | No | Azure service principal secret |
| `AZURE_TENANT_ID` | No | Azure tenant ID |
| `GOOGLE_CREDENTIALS` | No | GCP service account JSON |
| `INFRACOST_API_KEY` | No | Infracost API key for cost estimation |
| `TF_API_TOKEN` | No | Terraform Cloud API token |

### Outputs

| Output | Description |
|--------|-------------|
| `plan-exitcode` | Terraform plan exit code (0=no changes, 1=error, 2=changes) |
| `apply-exitcode` | Terraform apply exit code (if apply enabled) |
| `security-issues` | Number of security issues found |
| `cost-estimate` | Monthly cost estimate from Infracost |
| `resource-changes` | Summary of resource changes |
| `drift-detected` | Whether configuration drift was detected |

## 🔧 Workflow Steps

### 1. Environment Setup
- Install specified Terraform/OpenTofu version
- Configure provider credentials
- Set up backend configuration

### 2. Code Validation
```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform validate

# Initialize with backend
terraform init -backend-config=backend.hcl
```

### 3. Security Scanning

#### tfsec
```bash
tfsec . --format sarif --out tfsec-results.sarif \
  --config-file .tfsec.yml \
  --exclude-downloaded-modules
```

#### Checkov
```bash
checkov -d . --framework terraform \
  --output sarif --output-file checkov-results.sarif \
  --config-file .checkov.yml
```

#### Terrascan
```bash
terrascan scan -t terraform -d . \
  --output sarif --output-file terrascan-results.sarif
```

### 4. Plan Generation & Analysis
```bash
# Generate plan
terraform plan -var-file=terraform.tfvars \
  -out=terraform.plan \
  -detailed-exitcode

# Convert plan to JSON for analysis
terraform show -json terraform.plan > plan.json

# Analyze plan changes
terraform-plan-summary plan.json
```

### 5. Cost Estimation (Optional)
```bash
# Infracost breakdown
infracost breakdown --path . \
  --terraform-plan-path terraform.plan \
  --format json --out-file infracost.json

# Generate cost diff for PRs
infracost diff --path . \
  --terraform-plan-path terraform.plan \
  --format github-comment
```

### 6. Policy Validation (Optional)
```bash
# OPA policy validation
opa test policies/
conftest verify --policy policies/ plan.json
```

### 7. Documentation Generation (Optional)
```bash
# Generate terraform-docs
terraform-docs markdown table . > README.md

# Generate dependency graph
terraform graph | dot -Tsvg > graph.svg
```

### 8. Drift Detection (Optional)
```bash
# Compare current state with configuration
terraform plan -detailed-exitcode -refresh-only
```

## 📋 Project Setup Requirements

### Directory Structure
```
terraform-project/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── terraform.tfvars
├── terraform.tfvars.example
├── backend.hcl
├── modules/
│   ├── vpc/
│   ├── security-groups/
│   └── ec2/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
├── policies/
│   ├── security.rego
│   └── naming.rego
├── .tfsec.yml
├── .checkov.yml
└── README.md
```

### Configuration Files

#### versions.tf
```hcl
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
  
  backend "s3" {
    # Configuration loaded from backend.hcl
  }
}
```

#### backend.hcl
```hcl
bucket         = "my-terraform-state-bucket"
key            = "infrastructure/terraform.tfstate"
region         = "us-west-2"
encrypt        = true
dynamodb_table = "terraform-state-lock"

# Workspace support
workspace_key_prefix = "workspaces"
```

#### .tfsec.yml
```yaml
---
# tfsec configuration
severity_overrides:
  AVD-AWS-0001: HIGH
  AVD-AWS-0002: MEDIUM

exclude:
  - AVD-AWS-0100  # Ignore specific check

include:
  - checks/

minimum-severity: MEDIUM

exclude-downloaded-modules: true

soft-fail: false
```

#### .checkov.yml
```yaml
# Checkov configuration
branch: main
check:
  - CKV_AWS_*  # Include all AWS checks
  - CKV2_AWS_* # Include AWS composite checks

skip-check:
  - CKV_AWS_79  # Allow default security groups
  - CKV_AWS_23  # Allow unencrypted S3 buckets for logs

framework:
  - terraform
  - terraform_plan

output: sarif
quiet: true

download-external-modules: false
```

#### terraform.tfvars.example
```hcl
# Example variables file
environment = "dev"
region      = "us-west-2"
project     = "myproject"

vpc_cidr = "10.0.0.0/16"

instance_type = "t3.micro"
instance_count = 2

tags = {
  Environment = "development"
  Project     = "myproject"
  ManagedBy   = "terraform"
}
```

## 🎯 Usage Examples

### Example 1: Basic AWS Infrastructure

```yaml
name: AWS Infrastructure
on:
  push:
    branches: [main]
    paths: ['terraform/**']
  pull_request:
    paths: ['terraform/**']

jobs:
  terraform:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "1.6.0"
      working-directory: "terraform/"
      enable-security-scan: true
      var-file: "environments/dev/terraform.tfvars"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Example 2: Multi-Environment with Cost Estimation

```yaml
name: Multi-Environment Infrastructure
on: [push, pull_request]

jobs:
  terraform-dev:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "latest"
      working-directory: "terraform/"
      var-file: "environments/dev/terraform.tfvars"
      backend-config-file: "environments/dev/backend.hcl"
      enable-cost-estimation: true
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}

  terraform-prod:
    if: github.ref == 'refs/heads/main'
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "1.6.0"
      working-directory: "terraform/"
      var-file: "environments/prod/terraform.tfvars"
      backend-config-file: "environments/prod/backend.hcl"
      enable-security-scan: true
      enable-policy-check: true
      enable-drift-detection: true
```

### Example 3: OpenTofu with Custom Policies

```yaml
name: OpenTofu with Policies
on: [push, pull_request]

jobs:
  tofu:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      tool: "tofu"
      terraform-version: "1.6.0"
      working-directory: "infrastructure/"
      enable-policy-check: true
      policy-directory: "governance/policies/"
      terraform-docs: true
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Initialization Failures
**Problem:** `terraform init` fails with backend errors.

**Solutions:**
1. Verify backend configuration:
   ```hcl
   # backend.hcl
   bucket = "existing-s3-bucket"
   region = "us-west-2"
   # Ensure bucket exists and is accessible
   ```

2. Check credentials and permissions:
   ```bash
   # Test AWS access
   aws s3 ls s3://my-terraform-state-bucket
   aws dynamodb describe-table --table-name terraform-state-lock
   ```

#### Plan Failures with Provider Authentication
**Problem:** Terraform plan fails with authentication errors.

**Solutions:**
1. Verify required secrets are configured:
   ```yaml
   secrets:
     AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
     AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
     AWS_REGION: us-west-2  # or as workflow input
   ```

2. Use assume role for enhanced security:
   ```hcl
   provider "aws" {
     assume_role {
       role_arn = "arn:aws:iam::123456789012:role/TerraformRole"
     }
   }
   ```

#### Security Scan False Positives
**Problem:** Security tools report issues for intentional configurations.

**Solutions:**
1. Use inline suppressions:
   ```hcl
   resource "aws_s3_bucket" "logs" {
     bucket = "my-log-bucket"
     
     # tfsec:ignore:AVD-AWS-0089
     # Logs bucket intentionally allows public read
   }
   ```

2. Configure tool-specific ignores:
   ```yaml
   # .tfsec.yml
   exclude:
     - AVD-AWS-0089  # Public S3 bucket access
   ```

#### Cost Estimation Errors
**Problem:** Infracost fails to generate estimates.

**Solutions:**
1. Verify API key configuration:
   ```bash
   # Test Infracost authentication
   infracost auth login
   ```

2. Check supported resources:
   ```bash
   # Some resources may not have cost data
   infracost breakdown --path . --show-skipped
   ```

### Performance Optimization

#### Parallel Execution
```yaml
with:
  parallelism: 20  # Increase for larger configurations
```

#### Provider Caching
```bash
# Enable provider plugin caching
export TF_PLUGIN_CACHE_DIR=$HOME/.terraform.d/plugin-cache
mkdir -p $TF_PLUGIN_CACHE_DIR
```

#### Module Caching
```yaml
# Cache Terraform modules
- name: Cache Terraform modules
  uses: actions/cache@v4
  with:
    path: |
      ~/.terraform.d/plugin-cache
      **/.terraform/modules
    key: terraform-${{ hashFiles('**/*.tf') }}
```

## 🚀 Advanced Features

### Custom Policy Validation

#### OPA/Rego Policies
```rego
# policies/security.rego
package terraform.security

deny[msg] {
    resource := input.planned_values.root_module.resources[_]
    resource.type == "aws_s3_bucket"
    not resource.values.versioning[0].enabled
    
    msg := sprintf("S3 bucket '%s' must have versioning enabled", [resource.address])
}

deny[msg] {
    resource := input.planned_values.root_module.resources[_]
    resource.type == "aws_instance"
    not startswith(resource.values.instance_type, "t3")
    
    msg := sprintf("EC2 instance '%s' must use t3 instance types", [resource.address])
}
```

### Workspace Management

```yaml
# Multi-workspace validation
strategy:
  matrix:
    workspace: [dev, staging, prod]
with:
  working-directory: "terraform/"
  terraform-workspace: ${{ matrix.workspace }}
```

### State Management

#### State Validation
```bash
# Validate state file integrity
terraform state list
terraform state show aws_instance.example

# Check for orphaned resources
terraform refresh
terraform plan -refresh-only
```

#### State Migration
```bash
# Migrate state between backends
terraform init -migrate-state \
  -backend-config="bucket=new-state-bucket"
```

### Advanced Cost Analysis

#### Multi-Environment Cost Comparison
```yaml
- name: Cost Comparison
  run: |
    infracost diff \
      --path terraform/ \
      --terraform-var-file environments/dev/terraform.tfvars \
      --compare-to-path terraform/ \
      --terraform-var-file environments/prod/terraform.tfvars
```

## 📊 Metrics and Reporting

The workflow provides comprehensive metrics:

- **Validation Results** - Format, syntax, and semantic validation
- **Security Analysis** - Vulnerability findings by severity
- **Cost Impact** - Monthly cost estimates and diffs
- **Policy Compliance** - Policy violations and compliance score
- **Performance Metrics** - Plan/apply execution time
- **Resource Analysis** - Resource counts and types

### Viewing Reports

1. **Plan Output**: Detailed change analysis in workflow logs
2. **Security Reports**: SARIF format for GitHub Security tab
3. **Cost Reports**: Infracost breakdown and PR comments
4. **Policy Reports**: OPA evaluation results
5. **Documentation**: Auto-generated module documentation

### Integration with GitHub Features

#### PR Comments
The workflow automatically comments on PRs with:
- Plan summary and resource changes
- Cost impact analysis
- Security scan results
- Policy violations

#### Security Tab Integration
Security scan results are uploaded to GitHub's Security tab for:
- Historical tracking of security issues
- Integration with GitHub Advanced Security features
- Automated security alerts

## 🤝 Contributing

To contribute improvements to this workflow:

1. **Test with diverse Terraform configurations** - AWS, Azure, GCP
2. **Validate security scanning accuracy** - reduce false positives
3. **Improve cost estimation coverage** - support more resources
4. **Enhance policy examples** - provide governance templates

### Development Testing

```bash
# Clone and test locally
git clone https://github.com/basher83/.github.git
cd test-terraform-project

# Test individual components
terraform fmt -check
terraform validate
tfsec .
checkov -d .
```

---

*This workflow incorporates Terraform and infrastructure security best practices, regularly updated for new provider features and security standards.*