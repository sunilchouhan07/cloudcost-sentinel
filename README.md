# README.md — CloudCost Janitor

## Overview

CloudCost Janitor is a DevOps and FinOps automation project designed to detect and report orphaned or wasteful AWS resources in a LocalStack-based cloud environment. The project provisions infrastructure using Terraform, scans resources using a Python-based Janitor engine, and integrates automated cloud hygiene checks into GitHub Actions CI/CD workflows. The implementation focuses on safe remediation, reproducible infrastructure, tagging compliance, and multi-cloud extensibility.


Requirements:
- Python 3.11+
- Docker
- Terraform
- terraform-local

---

## How to run locally

### Clone the repository

```bash
git clone https://github.com/sunilchouhan07/cloudcost-janitor.git

cd cloudcost-janitor
```

---

### Start LocalStack

```bash
docker run --rm -d \
  -p 4566:4566 \
  --name localstack \
  localstack/localstack:3.5
```

---

### Verify LocalStack

```bash
docker ps
```

---

### Install Terraform Local Wrapper

```bash
pip install terraform-local
```

---

### Initialize Terraform

```bash
cd terraform

tflocal init
```

---

### Validate Terraform

```bash
terraform fmt -check

terraform validate
```

---

### Apply Infrastructure

```bash
tflocal apply -auto-approve
```

---

### Install Python Dependencies

```bash
cd ../janitor

pip install -r requirements.txt
```

---

### Run Cost Janitor (Dry Run)

```bash
python janitor.py --dry-run
```

---

### Run Cost Janitor (Delete Mode)

```bash
python janitor.py --delete
```

---

### Generated Outputs

The Janitor generates:
- `report.json`
- `report.md`

These files contain:
- orphan resource findings
- estimated monthly waste
- remediation recommendations
- tagging compliance issues

---

## CI/CD Workflow

The GitHub Actions pipeline:
- validates Terraform formatting and configuration
- provisions infrastructure in LocalStack
- executes the Cost Janitor in dry-run mode
- uploads report artifacts
- comments findings on pull requests
- intentionally exits non-zero when orphaned resources are detected to simulate governance enforcement

---

## Architecture

```text
                         +----------------------+
                         |   GitHub Actions     |
                         |----------------------|
                         | Terraform Validation |
                         | Janitor Execution    |
                         | Artifact Upload      |
                         +----------+-----------+
                                    |
                                    v
+------------------------------------------------------------------+
|                         CloudCost Janitor                        |
+------------------------------------------------------------------+
|                                                                  |
|  +------------------+      +-------------------------------+     |
|  | Terraform Stack  | ---> | LocalStack AWS Environment    |     |
|  +------------------+      +-------------------------------+     |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |                     Janitor Engine                         |  |
|  |------------------------------------------------------------|  |
|  | Resource Scanner | Policy Engine | Reporting | Safety Net |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
                                    |
                                    v
                         +----------------------+
                         | report.json / .md    |
                         +----------------------+
```

---

## Decisions & deviations

- SSH access from `0.0.0.0/0` was retained only for assignment compatibility and would be restricted in production environments.
- An unattached EBS volume was intentionally created to validate orphan detection functionality.
- Static pricing constants were used because LocalStack does not provide real AWS billing APIs.
- The Janitor intentionally returns a non-zero exit code during dry-run mode when orphaned resources are detected, enabling CI/CD enforcement behavior for cost-governance workflows.
- Terraform resources were split into reusable modules instead of a flat configuration for maintainability.
- Delete mode skips resources tagged with `Protected=true` to reduce accidental destructive operations.
- EC2 automatic termination was intentionally excluded from aggressive remediation logic due to outage risk.
- LocalStack was used instead of real AWS accounts to ensure zero-cost reproducibility.

---

## Trade-offs

Given one additional week, the project would be expanded with:
- Full GCP and Azure provider adapters
- Policy-as-Code integration using OPA/Rego
- Historical analytics dashboards
- Slack and PagerDuty alert integrations
- Multi-account AWS Organization scanning
- Approval-based remediation workflows
- Extended unit and integration test coverage
- Kubernetes and container cost analysis
- Parallelized scanning workers for large environments

The current implementation prioritizes:
- reproducibility
- Terraform correctness
- CI/CD reliability
- safe remediation logic
- schema-compliant reporting

over production-scale distributed architecture.

---

## AI usage disclosure

AI tools such as ChatGPT were used as engineering assistants for:
- Terraform troubleshooting
- GitHub Actions debugging
- refining documentation
- reviewing architecture decisions
- understanding LocalStack compatibility issues
- improving Terraform patterns such as `for_each`, S3 lifecycle configuration, and versioning logic

The project implementation itself was completed through a combination of manual development, iterative debugging, and AI-assisted research. Infrastructure provisioning, tagging strategy, LocalStack integration, CI/CD wiring, and orphan-detection behavior were manually tested and validated during development.

One incorrect AI suggestion involved overly permissive IAM delete permissions for EC2-related resources. This was identified during review because unrestricted termination access violated least-privilege principles and increased operational risk.

AI assistance was intentionally treated as a productivity and learning aid rather than a replacement for implementation validation or debugging.