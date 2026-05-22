
### Video Link

https://drive.google.com/file/d/10xjH1xk4cPyjpGVI3gw9WnY5fkXhSF8S/view?usp=sharing

---

### Walkthrough Transcript / Summary

The walkthrough demonstrates:

1. Repository overview and project structure
2. Starting LocalStack using Docker
3. Terraform initialization and infrastructure provisioning using tflocal apply
4. Provisioned resources including:
    - VPC
    - public subnets
    - EC2 instances
    - S3 bucket
    - unattached EBS volume
5. Running the Cost Janitor in --dry-run mode
6. Generated report.json and report.md outputs
7. GitHub Actions CI/CD workflow execution
8. Design decisions, safety controls, and trade-offs
9. Future improvements including multi-cloud support and approval-based remediation workflows

---

### Key Design Decisions Mentioned
- Reusable Terraform module structure
- Safe delete behavior using Protected=true
- Static pricing constants for offline reproducibility
- CI/CD governance enforcement through non-zero dry-run - exit codes
- LocalStack-based zero-cost reproducible testing environment

---

### Known LocalStack Limitation

During implementation, certain S3 lifecycle rule behaviors showed inconsistent support in LocalStack 3.5. The limitation was documented and handled as an emulator compatibility constraint rather than a Terraform issue.