# — CloudCost Janitor

## 1. Multi-Cloud Architecture Strategy

NimbusKart plans to expand to GCP and later Azure. To avoid rewriting the core Janitor logic for every cloud provider, the system follows a Provider-Adapter Architecture that separates:
- cloud-specific API integrations
- normalization logic
- policy evaluation
- remediation workflows
- reporting

This design allows the Janitor Core to remain cloud-agnostic while adapters handle provider-specific implementations.

### Architectural Blueprint

```text
                    +----------------------+
                    |   Janitor Core       |
                    |----------------------|
                    | Policy Engine        |
                    | Reporting Engine     |
                    | Cost Estimation      |
                    | Safety Rules         |
                    +----------+-----------+
                               |
        -------------------------------------------------
        |                       |                       |
+---------------+     +----------------+     +----------------+
| AWS Adapter   |     | GCP Adapter    |     | Azure Adapter  |
|---------------|     |----------------|     |----------------|
| boto3         |     | google sdk     |     | azure sdk      |
| EC2 scanner   |     | compute scan   |     | vm scanner     |
| EBS scanner   |     | disk scanner   |     | disk scanner   |
| S3 scanner    |     | GCS scanner    |     | blob scanner   |
+---------------+     +----------------+     +----------------+
```

### Core Interface Design

The Janitor Core never directly communicates with cloud SDKs. Each adapter implements a common interface and normalizes provider-specific resources into a unified schema.

```python
class CloudProvider:

    def list_compute_resources(self):
        pass

    def list_storage_resources(self):
        pass

    def delete_resource(self, resource_id):
        pass
```

### Policy Engine

The Policy Engine evaluates normalized resources against configurable rules such as:

- orphan thresholds
- missing mandatory tags
- protected-resource exceptions
- stale resource age
- deletion eligibility

This separation allows policies to remain reusable across AWS, GCP, and Azure without rewriting cloud-specific logic.

The Janitor should remain idempotent, ensuring repeated scans do not create duplicate remediation actions or inconsistent state transitions.

### Data Normalization Example

AWS EBS:

```json
{
  "resource_type": "block_storage",
  "attached": false
}
```

GCP Persistent Disk:

```json
{
  "resource_type": "block_storage",
  "attached": false
}
```

Both become standardized findings evaluated by the same policy engine.

### Benefits of This Design

- Easier multi-cloud expansion
- Reduced code duplication
- Easier testing and mocking
- Safer remediation logic
- Better separation of concerns
- Cleaner long-term maintainability

---

## 2. IAM Permissions & Security

The Janitor enforces the Principle of Least Privilege by separating read-only and destructive operations.

### Dry Run Mode (Read-Only)

Dry-run mode only scans resources and generates reports.

#### Required Capabilities

- Describe EC2 instances
- Describe EBS volumes
- Describe Elastic IPs
- Read tags
- Read S3 metadata

### Minimal Read-Only IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2ReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "ec2:DescribeTags"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3ReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketTagging"
      ],
      "Resource": "*"
    }
  ]
}
```

### Delete Mode (Destructive)

Delete mode additionally requires:
- `ec2:DeleteVolume`
- `ec2:ReleaseAddress`

ec2:TerminateInstances should be restricted to explicitly approved non-production environments because automatic instance termination is high risk.

### Security Controls

Delete permissions should be isolated into a separate IAM role protected with:
- MFA enforcement
- approval workflow
- short-lived credentials
- audit logging

Production systems should avoid permanent delete access wherever possible.

---

## 3. Safety Nets & Guardrails

Naïve auto-deletion can easily create outages or irreversible data loss. The Janitor therefore implements multiple protection mechanisms.

### Failure Scenario 1 — Stopped Disaster Recovery Instances

#### Risk

An EC2 instance may remain stopped intentionally for:
- disaster recovery
- maintenance standby
- backup environments
- migration rollback plans

A naïve cleanup policy could terminate these systems automatically.

#### Guardrails

- Support `Protected=true` resource overrides
- Require approval workflows before destructive actions
- Add quarantine periods before deletion
- Send Slack/email alerts before remediation
- Require minimum orphan age thresholds

---

### Failure Scenario 2 — Unattached Volumes with Critical Data

#### Risk

An unattached EBS volume may still contain:
- database backups
- migration snapshots
- forensic investigation data
- archived production information

Automatic deletion could result in permanent data loss.

#### Guardrails

- Automatically snapshot volumes before deletion
- Enforce minimum orphan-age thresholds
- Add denylist support for sensitive environments
- Require ownership tags before remediation
- Maintain deletion audit logs

---

### Failure Scenario 3 — Elastic IPs Used for Failover


#### Risk

An unattached Elastic IP may temporarily belong to:

- blue/green deployments
- disaster recovery failover
- DNS migration processes
- standby systems

Automatic release of these IPs may break failover routing or deployment workflows.

#### Guardrails
- Apply cooldown periods before release
- Require ownership validation tags
- Add environment-based exclusion rules
- Maintain approval workflows for production resources

## 4. Observability Strategy

The FinOps team requires visibility into:
- cloud waste trends
- automation effectiveness
- remediation activity
- false positives
- failed scans

Metrics should be exported to:
- CloudWatch
- Prometheus
- Grafana dashboards

These metrics help the FinOps team measure cloud hygiene effectiveness and operational waste trends over time.

### Core Metrics Matrix

| Metric Name | Data Source | Alert Threshold |
|-------------|-------------|----------------|
| orphan_resources_total | Scanner engine | > 20 resources |
| estimated_monthly_waste_usd | Cost engine | > $500 |
| auto_deleted_resources_total | Deletion logs | Spike > 10/day |
| protected_resource_skips_total | Policy engine | Sudden increase |
| scan_duration_seconds | Workflow metrics | > 300 seconds |

### Alert Routing

#### Critical Alerts

- PagerDuty
- Incident response channels

#### Informational Alerts

- Slack
- Microsoft Teams

### Example Alert Conditions

- Rapid increase in orphan resources
- Failed scans for multiple consecutive runs
- Unusually high deletion counts
- Unexpected spikes in cloud waste estimates

---

## 5. Scope Boundaries (Intentionally Left Out)

Several enterprise-grade features were intentionally excluded to keep the implementation achievable within the assignment time constraints while prioritizing:
- infrastructure reproducibility
- Terraform stability
- CI/CD reliability
- safe remediation logic
- schema-compliant reporting

### Out of Scope

- Multi-account AWS aggregation
- Real AWS Pricing API integration
- Historical trend databases
- OPA/Rego policy engine integration
- Kubernetes cost analysis
- Distributed scan workers
- Slack/PagerDuty integrations
- Full unit/integration test coverage
- Asynchronous queue processing
- Advanced RBAC systems

### LocalStack Limitation

Some AWS features were simplified due to LocalStack emulation limitations and API parity differences compared to real AWS environments.

### Future Improvements

Given additional time, the next priorities would be:

1. Full GCP and Azure adapters
2. Policy-as-Code support using OPA
3. Historical cost analytics dashboards
4. Approval-based remediation workflows
5. Multi-account organization scanning
6. Advanced notification integrations

The implementation prioritizes reproducibility and safe automation over production-scale distributed architecture.