# 🐳 Docker Build & Push Workflow

**Status:** 📋 Planned  
**Expected Release:** Q4 2025  
**File:** `.github/workflows/docker-build-push.yml`

A comprehensive Docker workflow for building, testing, and pushing multi-platform container images with security scanning, optimization, and registry support. This workflow ensures consistent, secure, and efficient container builds across all projects.

## 🎯 Overview

This workflow provides a complete Docker CI/CD pipeline that handles everything from building multi-architecture images to security scanning and registry deployment with advanced optimization features.

### Key Features

- 🏗️ **Multi-Platform Builds** - linux/amd64, linux/arm64, linux/arm/v7
- 🔐 **Security Scanning** - Trivy, Snyk, Docker Scout integration
- 📦 **Registry Support** - Docker Hub, GHCR, ECR, GCR, ACR
- 🏷️ **Smart Tagging** - Semantic versioning, branch-based, SHA-based
- ⚡ **Build Optimization** - Cache mounting, multi-stage optimization
- 🧪 **Container Testing** - Image vulnerability and functionality testing
- 📊 **Size Analysis** - Image size reporting and optimization suggestions
- 🚀 **Performance Monitoring** - Build time and resource usage tracking

## 🚀 Quick Start

### Basic Usage

```yaml
name: Docker Build
on: [push, pull_request]

jobs:
  docker:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp"
      registry: "ghcr.io"
```

### Advanced Configuration

```yaml
name: Production Docker Build
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  docker:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myorganization/myapp"
      registry: "docker.io"
      platforms: "linux/amd64,linux/arm64"
      enable-security-scan: true
      enable-sbom: true
      enable-attestation: true
      cache-mode: "registry"
      dockerfile-path: "./docker/Dockerfile"
      build-context: "."
      build-args: |
        BUILD_VERSION=${{ github.sha }}
        NODE_ENV=production
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

## ⚙️ Configuration Parameters

### Required Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `image-name` | string | Docker image name (with optional org/namespace) |
| `registry` | string | Container registry (docker.io, ghcr.io, etc.) |

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platforms` | string | `linux/amd64` | Target platforms for multi-arch builds |
| `dockerfile-path` | string | `Dockerfile` | Path to Dockerfile |
| `build-context` | string | `.` | Docker build context directory |
| `build-args` | string | `` | Build arguments (multiline string) |
| `target-stage` | string | `` | Target stage for multi-stage builds |
| `enable-security-scan` | boolean | `true` | Run security vulnerability scans |
| `enable-sbom` | boolean | `false` | Generate Software Bill of Materials |
| `enable-attestation` | boolean | `false` | Generate build attestations |
| `enable-cosign` | boolean | `false` | Sign images with Cosign |
| `cache-mode` | string | `gha` | Cache mode (gha, registry, local, disabled) |
| `cache-scope` | string | `buildkit` | Cache scope for build optimization |
| `push-on-pr` | boolean | `false` | Push images on pull requests |
| `tag-strategy` | string | `auto` | Tagging strategy (auto, semver, branch, sha) |
| `tag-prefix` | string | `` | Prefix for all tags |
| `tag-suffix` | string | `` | Suffix for all tags |
| `latest-tag` | boolean | `true` | Push 'latest' tag on main branch |
| `test-command` | string | `` | Command to test built image |
| `scan-severity` | string | `HIGH,CRITICAL` | Security scan severity levels |
| `max-image-size` | string | `1GB` | Maximum allowed image size |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `DOCKER_USERNAME` | Yes* | Registry username (*required for push) |
| `DOCKER_PASSWORD` | Yes* | Registry password/token (*required for push) |
| `COSIGN_PRIVATE_KEY` | No | Cosign private key for image signing |
| `COSIGN_PASSWORD` | No | Cosign key password |

### Outputs

| Output | Description |
|--------|-------------|
| `image-digest` | SHA256 digest of the built image |
| `image-tags` | Comma-separated list of image tags |
| `image-size` | Final image size in bytes |
| `build-time` | Total build time in seconds |
| `scan-results` | Security scan summary |
| `platforms-built` | Platforms successfully built |

## 🔧 Workflow Steps

### 1. Environment Setup
- Configure Docker Buildx with multi-platform support
- Set up QEMU for cross-platform emulation
- Authenticate with specified registry

### 2. Metadata Generation
```bash
# Generate tags based on strategy
docker/metadata-action@v5
  tags: |
    type=ref,event=branch
    type=ref,event=pr
    type=semver,pattern={{version}}
    type=semver,pattern={{major}}.{{minor}}
    type=sha,prefix={{branch}}-
```

### 3. Cache Configuration
```bash
# Registry cache mode
--cache-from type=registry,ref=user/app:buildcache
--cache-to type=registry,ref=user/app:buildcache,mode=max

# GitHub Actions cache mode  
--cache-from type=gha
--cache-to type=gha,mode=max
```

### 4. Multi-Platform Build
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from type=gha \
  --cache-to type=gha,mode=max \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=${{ github.sha }} \
  --target production \
  --push \
  .
```

### 5. Security Scanning
```bash
# Trivy vulnerability scan
trivy image --severity HIGH,CRITICAL \
  --format sarif \
  --output trivy-results.sarif \
  user/app:latest

# Docker Scout (if enabled)
docker scout cves user/app:latest

# Generate SBOM
docker buildx imagetools inspect user/app:latest --format "{{ json . }}"
```

### 6. Image Testing & Validation
```bash
# Basic functionality test
docker run --rm user/app:latest /app/healthcheck.sh

# Size validation
docker images user/app:latest --format "table {{.Size}}"

# Layer analysis
docker history user/app:latest --no-trunc
```

### 7. Image Signing (Optional)
```bash
# Cosign signing
cosign sign --key env://COSIGN_PRIVATE_KEY user/app@${{ outputs.digest }}

# Generate attestation
cosign attest --predicate attestation.json user/app@${{ outputs.digest }}
```

## 📋 Project Setup Requirements

### Directory Structure
```
project/
├── Dockerfile
├── .dockerignore
├── docker/
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── healthcheck.sh
├── docker-compose.yml
├── .hadolint.yaml
└── src/
    └── app/
```

### Dockerfile Best Practices

#### Multi-Stage Dockerfile
```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./

FROM base AS deps
RUN npm ci --only=production && npm cache clean --force

FROM base AS build
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runtime
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy dependencies and built application
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build --chown=nextjs:nodejs /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json

USER nextjs
EXPOSE 3000
ENV PORT 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["npm", "start"]
```

#### .dockerignore
```
# Dependencies
node_modules/
npm-debug.log*

# Build outputs
.next/
out/
dist/
build/

# Environment and secrets
.env*
!.env.example

# Version control
.git/
.gitignore

# Documentation
README.md
docs/

# Testing
coverage/
.nyc_output/
test/
*.test.js

# Development tools
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
Thumbs.db
```

#### .hadolint.yaml
```yaml
# Hadolint configuration for Dockerfile linting
ignored:
  - DL3008  # Pin versions in apt-get install
  - DL3009  # Delete apt-get lists after installing
  - DL3015  # Avoid additional packages by specifying --no-install-recommends

trustedRegistries:
  - docker.io
  - gcr.io
  - ghcr.io

allowedMaintainers:
  - security@mycompany.com
  - devops@mycompany.com
```

## 🎯 Usage Examples

### Example 1: Simple Web Application

```yaml
name: Build Web App
on: [push, pull_request]

jobs:
  docker:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "webapp"
      registry: "ghcr.io"
      platforms: "linux/amd64,linux/arm64"
      test-command: "curl -f http://localhost:3000/health"
    secrets:
      DOCKER_USERNAME: ${{ github.actor }}
      DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

### Example 2: Microservice with Multiple Environments

```yaml
name: Microservice CI/CD
on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  docker-dev:
    if: github.ref == 'refs/heads/develop'
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myservice"
      registry: "docker.io"
      tag-suffix: "-dev"
      target-stage: "development"
      push-on-pr: true

  docker-prod:
    if: startsWith(github.ref, 'refs/tags/v')
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myservice"
      registry: "docker.io"
      platforms: "linux/amd64,linux/arm64"
      target-stage: "production"
      enable-security-scan: true
      enable-sbom: true
      enable-cosign: true
    secrets:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
```

### Example 3: Multi-Service Monorepo

```yaml
name: Monorepo Docker Builds
on: [push, pull_request]

jobs:
  api:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/api"
      dockerfile-path: "services/api/Dockerfile"
      build-context: "services/api"
      
  frontend:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/frontend"
      dockerfile-path: "services/frontend/Dockerfile"
      build-context: "services/frontend"
      
  worker:
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/worker"
      dockerfile-path: "services/worker/Dockerfile"
      build-context: "services/worker"
```

## 🔍 Troubleshooting

### Common Issues

#### Multi-Platform Build Failures
**Problem:** Builds fail for specific architectures.

**Solutions:**
1. Check base image compatibility:
   ```dockerfile
   # Use multi-arch base images
   FROM --platform=$BUILDPLATFORM node:18-alpine
   ```

2. Handle architecture-specific dependencies:
   ```dockerfile
   ARG TARGETPLATFORM
   RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
         apt-get install -y arm64-specific-package; \
       fi
   ```

#### Cache Misses
**Problem:** Builds don't use cache effectively.

**Solutions:**
1. Optimize layer ordering:
   ```dockerfile
   # Copy package files first (changes less frequently)
   COPY package*.json ./
   RUN npm install
   
   # Copy source code last (changes frequently)
   COPY . .
   ```

2. Use cache mounts:
   ```dockerfile
   RUN --mount=type=cache,target=/root/.npm \
       npm install --production
   ```

#### Registry Authentication Failures
**Problem:** Cannot push to registry.

**Solutions:**
1. Verify credentials format:
   ```yaml
   # For Docker Hub
   DOCKER_USERNAME: your-dockerhub-username
   DOCKER_PASSWORD: your-dockerhub-token  # Not password!
   
   # For GHCR
   DOCKER_USERNAME: ${{ github.actor }}
   DOCKER_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
   ```

2. Check registry permissions:
   ```bash
   # Test authentication locally
   echo $DOCKER_PASSWORD | docker login $REGISTRY -u $DOCKER_USERNAME --password-stdin
   ```

#### Large Image Sizes
**Problem:** Built images are too large.

**Solutions:**
1. Use multi-stage builds to exclude build dependencies
2. Use .dockerignore to exclude unnecessary files
3. Use minimal base images (alpine, distroless)
4. Clean up package caches:
   ```dockerfile
   RUN apt-get update && apt-get install -y package \
       && apt-get clean && rm -rf /var/lib/apt/lists/*
   ```

### Performance Optimization

#### Build Time Optimization
```yaml
# Use registry cache for better performance
with:
  cache-mode: "registry"
  cache-scope: "main"  # Separate cache per branch
```

#### Parallel Builds
```yaml
# Build multiple services in parallel
jobs:
  build-matrix:
    strategy:
      matrix:
        service: [api, frontend, worker]
    uses: basher83/.github/.github/workflows/docker-build-push.yml@main
    with:
      image-name: "myapp/${{ matrix.service }}"
      dockerfile-path: "services/${{ matrix.service }}/Dockerfile"
```

## 🚀 Advanced Features

### Container Signing with Cosign

```yaml
with:
  enable-cosign: true
secrets:
  COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
  COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
```

### Software Bill of Materials (SBOM)

```yaml
with:
  enable-sbom: true
  enable-attestation: true
```

### Custom Security Policies

```yaml
with:
  scan-severity: "MEDIUM,HIGH,CRITICAL"
  max-image-size: "500MB"
```

### Registry-Specific Features

#### Amazon ECR
```yaml
with:
  registry: "123456789012.dkr.ecr.us-west-2.amazonaws.com"
secrets:
  DOCKER_USERNAME: "AWS"
  DOCKER_PASSWORD: ${{ secrets.AWS_ECR_TOKEN }}
```

#### Google Container Registry
```yaml
with:
  registry: "gcr.io"
secrets:
  DOCKER_USERNAME: "_json_key"
  DOCKER_PASSWORD: ${{ secrets.GCR_JSON_KEY }}
```

## 📊 Metrics and Reporting

The workflow provides comprehensive metrics:

- **Build Performance** - Build time, cache hit rate, resource usage
- **Image Analysis** - Size, layers, vulnerabilities
- **Security Reports** - CVE findings, compliance status
- **Cost Analysis** - Build time cost, storage cost estimation

### Viewing Reports

1. **Build Logs**: Detailed build output with timing information
2. **Security Reports**: SARIF format for GitHub Security tab integration  
3. **Artifacts**: SBOM, attestations, and detailed scan results
4. **Annotations**: Automated PR comments with build summaries

## 🤝 Contributing

To contribute improvements to this workflow:

1. **Test with diverse Docker projects** - different languages, architectures
2. **Validate security features** - ensure scanning tools are current
3. **Benchmark performance** - measure build time improvements
4. **Update documentation** - include new registry support

---

*This workflow incorporates Docker and container security best practices, regularly updated for new platform features and security standards.*