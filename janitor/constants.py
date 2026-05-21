"""
CloudCost Janitor Pricing Constants

Pricing references:
https://aws.amazon.com/ebs/pricing/
https://aws.amazon.com/ec2/pricing/on-demand/
https://aws.amazon.com/vpc/pricing/

Values are simplified static estimates
for local simulation purposes only.
"""

# ==========================================
# EBS Pricing
# ==========================================

# gp3 storage pricing per GB-month
EBS_GP3_COST_PER_GB = 0.08

# ==========================================
# Elastic IP Pricing
# ==========================================

# Approximate unused Elastic IP monthly cost
ELASTIC_IP_MONTHLY_COST = 3.65

# ==========================================
# Stopped EC2 Estimate
# ==========================================

# Estimated attached storage / infra waste
# for stopped instances
STOPPED_INSTANCE_MONTHLY_COST = 5.00

# ==========================================
# Required Governance Tags
# ==========================================

REQUIRED_TAGS = [
    "Project",
    "Environment",
    "Owner"
]

# ==========================================
# Default Settings
# ==========================================

DEFAULT_REGION = "us-east-1"

DEFAULT_STOPPED_DAYS = 14

PROTECTED_TAG_KEY = "Protected"

PROTECTED_TAG_VALUE = "true"

DEFAULT_ACCOUNT_ID = "000000000000"