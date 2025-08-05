# Reusable Workflow Definitions

This repository serves as a central location for reusable GitHub Actions workflows that can be called from your other repositories. Use these to standardize and simplify your CI/CD and automation across projects.

---

## 1. Sync Labels

**Definition:**  
This workflow pulls and syncs repository labels from a central source:  
`https://raw.githubusercontent.com/basher83/docs/main/mission-control/github-configs/label-definitions.yml`  
You can point to alternate label definitions if needed. **Note:** Changing the label source affects all downstream workflows using this action.

**Status:**  
[![Sync Labels](https://github.com/basher83/my_tailnet_acl/actions/workflows/use-sync-labels.yml/badge.svg)](https://github.com/basher83/my_tailnet_acl/actions/workflows/use-sync-labels.yml)

**Workflow file:**  
- `sync-labels.yml`

---

## 2. Tailscale: Connect to Tailnet

**Definition:**  
A workflow to connect a GitHub Actions runner to your Tailscale Tailnet.

**Status:**  
_Not yet tested_

**Workflow file:**  
- `tailscale-connect-to-tailnet.yml`

---

## 3. Tailscale Policy

**Definition:**  
A GitOps workflow to sync a Tailscale policy file.

**Status:**  
**Not recommended for use in multiple repositories.**  
This workflow is not intended for broad usage across projects and is not a typical candidate for this central workflows repo.

**Workflow file:**  
- `tailscale-policy.yml`

---
