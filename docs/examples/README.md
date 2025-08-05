# 📚 Usage Examples

This directory contains real-world examples of how to integrate and use the reusable workflows in different project scenarios. These examples demonstrate best practices and common patterns for various technology stacks.

## 📋 Quick Reference

| Example | Technology Stack | Complexity | Documentation |
|---------|------------------|------------|---------------|
| [Simple Python Package](#simple-python-package) | Python, pytest | ⭐ Beginner | Basic CI/CD setup |
| [Django Web Application](#django-web-application) | Django, PostgreSQL | ⭐⭐ Intermediate | Web app with database |
| [Microservices Monorepo](#microservices-monorepo) | Python, Docker, K8s | ⭐⭐⭐ Advanced | Multi-service repository |
| [Ansible Infrastructure](#ansible-infrastructure) | Ansible, Terraform | ⭐⭐ Intermediate | Infrastructure as Code |
| [Full-Stack Application](#full-stack-application) | React, Node.js, Docker | ⭐⭐⭐ Advanced | Complete application stack |
| [Machine Learning Pipeline](#machine-learning-pipeline) | Python, MLflow, Docker | ⭐⭐ Intermediate | ML model deployment |

---

## 🐍 Simple Python Package

**Scenario:** A basic Python library with unit tests and PyPI publishing.

### Repository Structure
```
my-python-package/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── pyproject.toml
├── requirements-dev.txt
└── .github/
    └── workflows/
        └── ci.yml
```

### Workflow Configuration

```yaml
# .github/workflows/ci.yml
name: Python Package CI

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      coverage-threshold: 85
      source-directory: "src/"
      test-directory: "tests/"
      enable-security-scan: true

  publish:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Build and publish
        run: |
          pip install build twine
          python -m build
          twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

### Key Features
- ✅ Automated quality checks on every PR
- ✅ Multi-Python version testing
- ✅ Security scanning with Bandit
- ✅ Automatic PyPI publishing on tags
- ✅ Coverage reporting

---

## 🌐 Django Web Application

**Scenario:** A Django web application with PostgreSQL database and Redis cache.

### Repository Structure
```
django-webapp/
├── myproject/
│   ├── settings/
│   ├── apps/
│   └── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docker-compose.yml
├── Dockerfile
└── .github/
    └── workflows/
        └── django-ci.yml
```

### Workflow Configuration

```yaml
# .github/workflows/django-ci.yml
name: Django Application CI

on: [push, pull_request]

services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: testdb
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

  redis:
    image: redis:7
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

jobs:
  test:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      requirements-file: "requirements/dev.txt"
      source-directory: "myproject/"
      test-directory: "myproject/tests/"
      pytest-args: "--ds=myproject.settings.test --reuse-db"
      coverage-threshold: 80
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
      REDIS_URL: redis://localhost:6379/0

  docker:
    needs: test
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/django-webapp"
      registry: "ghcr.io"
      dockerfile-path: "Dockerfile"
      test-command: "python manage.py check --deploy"
    secrets:
      DOCKER_USERNAME: ${{ github.actor }}
      DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

### Key Features
- ✅ Database and cache services for testing
- ✅ Django-specific test configuration
- ✅ Docker image building and testing
- ✅ Environment-specific settings validation

---

## 🏗️ Microservices Monorepo

**Scenario:** Multiple Python microservices in a single repository with shared dependencies.

### Repository Structure
```
microservices-monorepo/
├── services/
│   ├── user-service/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── order-service/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── notification-service/
├── shared/
│   └── common-utils/
├── docker-compose.yml
└── .github/
    └── workflows/
        └── microservices-ci.yml
```

### Workflow Configuration

```yaml
# .github/workflows/microservices-ci.yml
name: Microservices CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Detect changes to optimize builds
  changes:
    runs-on: ubuntu-latest
    outputs:
      user-service: ${{ steps.changes.outputs.user-service }}
      order-service: ${{ steps.changes.outputs.order-service }}
      notification-service: ${{ steps.changes.outputs.notification-service }}
      shared: ${{ steps.changes.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            user-service:
              - 'services/user-service/**'
              - 'shared/**'
            order-service:
              - 'services/order-service/**'
              - 'shared/**'
            notification-service:
              - 'services/notification-service/**'
              - 'shared/**'
            shared:
              - 'shared/**'

  # Test shared utilities
  test-shared:
    if: needs.changes.outputs.shared == 'true'
    needs: changes
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      working-directory: "shared/common-utils"
      coverage-threshold: 90

  # Test and build user service
  user-service:
    if: needs.changes.outputs.user-service == 'true'
    needs: [changes, test-shared]
    strategy:
      matrix:
        job-type: [test, docker]
    uses: |
      ${{ matrix.job-type == 'test' && 
          'basher83/.github/.github/workflows/python-quality.yml@main' || 
          'basher83/.github/.github/workflows/docker-build-push.yml@main' }}
    with: |
      ${{ matrix.job-type == 'test' && '{
        "python-version": "3.11",
        "working-directory": "services/user-service",
        "coverage-threshold": 85
      }' || '{
        "image-name": "myapp/user-service",
        "dockerfile-path": "services/user-service/Dockerfile",
        "build-context": "services/user-service",
        "registry": "ghcr.io"
      }' }}

  # Test and build order service
  order-service:
    if: needs.changes.outputs.order-service == 'true'
    needs: [changes, test-shared]
    strategy:
      matrix:
        job-type: [test, docker]
    uses: |
      ${{ matrix.job-type == 'test' && 
          'basher83/.github/.github/workflows/python-quality.yml@main' || 
          'basher83/.github/.github/workflows/docker-build-push.yml@main' }}
    with: |
      ${{ matrix.job-type == 'test' && '{
        "python-version": "3.11", 
        "working-directory": "services/order-service",
        "coverage-threshold": 85
      }' || '{
        "image-name": "myapp/order-service",
        "dockerfile-path": "services/order-service/Dockerfile", 
        "build-context": "services/order-service",
        "registry": "ghcr.io"
      }' }}

  # Integration tests
  integration:
    needs: [user-service, order-service, notification-service]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
          docker-compose -f docker-compose.test.yml down
```

### Key Features
- ✅ Smart change detection to optimize builds
- ✅ Parallel testing and building of services
- ✅ Shared dependency management
- ✅ Integration testing with Docker Compose
- ✅ Conditional builds based on changes

---

## 🎭 Ansible Infrastructure

**Scenario:** Infrastructure provisioning with Terraform and configuration with Ansible.

### Repository Structure
```
infrastructure-project/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/
│   ├── playbooks/
│   ├── roles/
│   ├── inventory/
│   └── requirements.yml
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
└── .github/
    └── workflows/
        └── infrastructure.yml
```

### Workflow Configuration

```yaml
# .github/workflows/infrastructure.yml
name: Infrastructure as Code

on:
  push:
    branches: [main]
    paths: ['terraform/**', 'ansible/**']
  pull_request:
    paths: ['terraform/**', 'ansible/**']

jobs:
  # Validate Terraform configuration
  terraform-validate:
    uses: basher83/.github/.github/workflows/terraform-validate.yml@main
    with:
      terraform-version: "1.6.0"
      working-directory: "terraform/"
      enable-security-scan: true
      enable-cost-estimation: true
      var-file: "environments/dev/terraform.tfvars"
      backend-config-file: "environments/dev/backend.hcl"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      INFRACOST_API_KEY: ${{ secrets.INFRACOST_API_KEY }}

  # Validate Ansible playbooks
  ansible-lint:
    uses: basher83/.github/.github/workflows/ansible-lint.yml@main
    with:
      ansible-version: "latest"
      working-directory: "ansible/"
      enable-galaxy-install: true
      config-file: "ansible/.ansible-lint"
      requirements-file: "ansible/requirements.yml"

  # Deploy to development environment
  deploy-dev:
    if: github.ref == 'refs/heads/main'
    needs: [terraform-validate, ansible-lint]
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"
      
      - name: Deploy infrastructure
        working-directory: terraform/
        run: |
          terraform init -backend-config=../environments/dev/backend.hcl
          terraform apply -var-file=../environments/dev/terraform.tfvars -auto-approve
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      
      - name: Configure with Ansible
        working-directory: ansible/
        run: |
          ansible-galaxy install -r requirements.yml
          ansible-playbook -i inventory/dev playbooks/site.yml
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### Key Features
- ✅ Infrastructure validation before deployment
- ✅ Cost estimation for infrastructure changes
- ✅ Security scanning for both Terraform and Ansible
- ✅ Environment-specific deployments
- ✅ Automated infrastructure provisioning and configuration

---

## 🚀 Full-Stack Application

**Scenario:** Complete application with React frontend, Node.js API, and PostgreSQL database.

### Repository Structure
```
fullstack-app/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── migrations/
├── docker-compose.yml
├── k8s/
│   ├── frontend.yaml
│   ├── backend.yaml
│   └── database.yaml
└── .github/
    └── workflows/
        └── fullstack.yml
```

### Workflow Configuration

```yaml
# .github/workflows/fullstack.yml
name: Full-Stack Application CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Detect changes
  changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.changes.outputs.frontend }}
      backend: ${{ steps.changes.outputs.backend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            frontend:
              - 'frontend/**'
            backend:
              - 'backend/**'

  # Test and build frontend
  frontend:
    if: needs.changes.outputs.frontend == 'true'
    needs: changes
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install and test
        working-directory: frontend/
        run: |
          npm ci
          npm run lint
          npm run test -- --coverage --watchAll=false
          npm run build
      
      - name: Build Docker image
        if: github.ref == 'refs/heads/main'
        uses: basher83/.github/.github/workflows/docker-build-push.yml@main
        with:
          image-name: "myapp/frontend"
          dockerfile-path: "frontend/Dockerfile"
          build-context: "frontend/"
          registry: "ghcr.io"
        secrets:
          DOCKER_USERNAME: ${{ github.actor }}
          DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  # Test and build backend
  backend:
    if: needs.changes.outputs.backend == 'true'
    needs: changes
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: backend/package-lock.json
      
      - name: Install and test
        working-directory: backend/
        run: |
          npm ci
          npm run lint
          npm run test -- --coverage
          npm run build
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
      
      - name: Build Docker image
        if: github.ref == 'refs/heads/main'
        uses: basher83/.github/.github/workflows/docker-build-push.yml@main
        with:
          image-name: "myapp/backend"
          dockerfile-path: "backend/Dockerfile"
          build-context: "backend/"
          registry: "ghcr.io"
        secrets:
          DOCKER_USERNAME: ${{ github.actor }}
          DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  # Integration tests
  integration:
    needs: [frontend, backend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml up --build -d
          npm run test:e2e
          docker-compose -f docker-compose.test.yml down

  # Deploy to staging
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    needs: [integration]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/ --namespace=staging
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}

  # Deploy to production
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: [integration]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/ --namespace=production
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
```

### Key Features
- ✅ Separate frontend and backend testing
- ✅ Change detection for optimized builds
- ✅ Integration testing with Docker Compose
- ✅ Environment-specific deployments
- ✅ Container image building and registry push

---

## 🤖 Machine Learning Pipeline

**Scenario:** ML model training, validation, and deployment pipeline.

### Repository Structure
```
ml-pipeline/
├── src/
│   ├── data/
│   ├── models/
│   ├── training/
│   └── inference/
├── notebooks/
├── tests/
├── requirements/
│   ├── base.txt
│   ├── training.txt
│   └── inference.txt
├── Dockerfile.training
├── Dockerfile.inference
└── .github/
    └── workflows/
        └── ml-pipeline.yml
```

### Workflow Configuration

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main, develop]
    paths: ['src/**', 'requirements/**']
  pull_request:
    paths: ['src/**', 'requirements/**']

jobs:
  # Code quality checks
  quality:
    uses: basher83/.github/.github/workflows/python-quality.yml@main
    with:
      python-version: "3.11"
      requirements-file: "requirements/base.txt"
      source-directory: "src/"
      test-directory: "tests/"
      coverage-threshold: 80

  # Data validation
  data-validation:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: pip install -r requirements/base.txt
      
      - name: Validate data schema
        run: python src/data/validate_schema.py
      
      - name: Check data quality
        run: python src/data/quality_checks.py

  # Model training (on main branch only)
  train-model:
    if: github.ref == 'refs/heads/main'
    needs: [quality, data-validation]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install training dependencies
        run: pip install -r requirements/training.txt
      
      - name: Train model
        run: python src/training/train.py
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          MLFLOW_TRACKING_USERNAME: ${{ secrets.MLFLOW_USERNAME }}
          MLFLOW_TRACKING_PASSWORD: ${{ secrets.MLFLOW_PASSWORD }}
      
      - name: Validate model performance
        run: python src/training/validate.py

  # Build inference container
  build-inference:
    needs: train-model
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/ml-inference"
      dockerfile-path: "Dockerfile.inference"
      registry: "ghcr.io"
      test-command: "python -m pytest tests/test_inference.py"
    secrets:
      DOCKER_USERNAME: ${{ github.actor }}
      DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}

  # Model deployment
  deploy-model:
    if: github.ref == 'refs/heads/main'
    needs: build-inference
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to model serving platform
        run: |
          # Deploy to your ML serving platform
          # e.g., SageMaker, MLflow, Kubeflow, etc.
          echo "Deploying model to production"
```

### Key Features
- ✅ Comprehensive code quality checks
- ✅ Data validation and quality checks
- ✅ Model training with MLflow tracking
- ✅ Model performance validation
- ✅ Containerized inference deployment
- ✅ Environment-specific model deployment

---

## 💡 Best Practices Summary

### General Guidelines
1. **Use change detection** to optimize builds in monorepos
2. **Separate concerns** - different jobs for different responsibilities
3. **Cache dependencies** to speed up builds
4. **Use environment protection** for production deployments
5. **Include integration tests** for multi-component systems

### Security Considerations
1. **Use repository secrets** for sensitive data
2. **Enable security scanning** on all workflows
3. **Use minimal container base images**
4. **Implement least-privilege access**
5. **Sign and verify container images**

### Performance Optimization
1. **Parallel execution** where possible
2. **Smart caching strategies**
3. **Conditional job execution**
4. **Resource-appropriate runners**
5. **Efficient Docker layer ordering**

---

*These examples demonstrate real-world usage patterns and can be adapted to your specific project needs. For more detailed configuration options, see the individual workflow documentation.*