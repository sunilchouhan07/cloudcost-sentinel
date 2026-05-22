# Submission — DevOps Engineer Assignment

**Candidate name:** Sunil Chouhan  
**Email:** sunilchouhanw@gmail.com  
**Date submitted:** 2026-05-22  
**Hours spent (approximate):** Approximately 13–15 hours

## Deliverables checklist

- [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in --dry-run mode and produces report.json
- [x] Part B: GitHub Actions workflow executes successfully end-to-end on a fresh PR
- [x] Part B: --delete mode respects Protected=true tag
- [x] Part C: DESIGN.md is present and within 2 pages
- [x] Walkthrough video link below is accessible (unlisted is fine)

---

## Walkthrough video

Link (Loom / YouTube unlisted / Google Drive):  
https://drive.google.com/file/d/10xjH1xk4cPyjpGVI3gw9WnY5fkXhSF8S/view?usp=sharing

Length: max 5 minutes

---

## Sample report

Path to a sample report.json produced by your script:

```text
samples/report.example.json
```

---

## Known limitations

- LocalStack was used for local AWS emulation; some advanced AWS APIs and billing-specific behaviors are not fully supported by the emulator.
- Cost estimation currently uses static pricing constants for predictable offline testing instead of live AWS Pricing API integration.
- The GitHub Actions workflow has been validated primarily against LocalStack-based infrastructure for reproducible local testing.
- Multi-cloud provider adapters (GCP/Azure) are discussed in DESIGN.md but not implemented as part of the assignment scope.
- Test coverage focuses on core orphan-detection flows and CI validation paths due to the limited assignment timeframe.
- Historical trend analysis and persistent reporting storage were intentionally excluded to keep the solution lightweight and assignment-focused.
- Real-time notification integrations (Slack, PagerDuty, Teams) were intentionally left out to prioritize core FinOps automation functionality.

---

## AI usage disclosure

AI tools such as ChatGPT were used during development for:
- Terraform troubleshooting
- GitHub Actions debugging
- documentation refinement
- reviewing architecture decisions
- understanding LocalStack compatibility limitations
- improving Terraform patterns such as `for_each`, S3 lifecycle configuration, and versioning logic

The project was implemented through a combination of manual development, iterative debugging, and AI-assisted research. Infrastructure provisioning, tagging strategy, LocalStack integration, CI/CD wiring, and orphan-detection behavior were manually tested and validated throughout development.

One incorrect AI suggestion involved overly permissive IAM delete permissions for EC2-related resources. This was identified during review because unrestricted termination access violated least-privilege principles and increased operational risk.

AI assistance was intentionally treated as a productivity and learning aid rather than a replacement for implementation validation, debugging, or operational understanding.