#!/usr/bin/env python3

import argparse
import json
import sys

from datetime import datetime, timezone

import boto3

from rich.console import Console
from rich.table import Table

from constants import (
    REQUIRED_TAGS,
    EBS_GP3_COST_PER_GB,
    ELASTIC_IP_MONTHLY_COST,
    STOPPED_INSTANCE_MONTHLY_COST,
    DEFAULT_REGION,
    DEFAULT_STOPPED_DAYS,
    PROTECTED_TAG_KEY,
    PROTECTED_TAG_VALUE
)

console = Console()

# =========================================================
# ARGUMENTS
# =========================================================

parser = argparse.ArgumentParser(
    description="CloudCost Janitor"
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Run scan without deleting resources"
)

parser.add_argument(
    "--delete",
    action="store_true",
    help="Delete orphan resources"
)

parser.add_argument(
    "--stopped-days",
    type=int,
    default=DEFAULT_STOPPED_DAYS,
    help="Stopped instance threshold"
)

args = parser.parse_args()

if not args.delete:
    args.dry_run = True

# =========================================================
# AWS CLIENT
# =========================================================

ec2 = boto3.client(
    "ec2",
    region_name=DEFAULT_REGION,
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# =========================================================
# REPORT
# =========================================================

findings = []

report = {
    "scan_timestamp": datetime.now(
        timezone.utc
    ).isoformat(),

    "account_id": "000000000000",

    "region": DEFAULT_REGION,

    "summary": {
        "total_orphans": 0,
        "estimated_monthly_waste_usd": 0
    },

    "findings": findings
}

# =========================================================
# HELPERS
# =========================================================

def extract_tags(tag_list):

    tags = {}

    if not tag_list:
        return tags

    for tag in tag_list:
        tags[tag["Key"]] = tag["Value"]

    return tags


def missing_tags(tags):

    missing = []

    for required in REQUIRED_TAGS:
        if required not in tags:
            missing.append(required)

    return missing


def is_protected(tags):

    return (
        tags.get(
            PROTECTED_TAG_KEY,
            "false"
        ).lower() == PROTECTED_TAG_VALUE
    )


def add_finding(
    resource_id,
    resource_type,
    reason,
    age_days,
    estimated_cost,
    tags,
    suggested_action,
    safe_to_auto_delete
):

    findings.append({
        "resource_id": resource_id,
        "resource_type": resource_type,
        "reason": reason,
        "age_days": age_days,
        "estimated_monthly_cost_usd": round(
            estimated_cost,
            2
        ),
        "tags": tags,
        "suggested_action": suggested_action,
        "safe_to_auto_delete": safe_to_auto_delete
    })


# =========================================================
# EBS CHECK
# =========================================================

def check_ebs_volumes():

    console.print(
        "[cyan]Scanning EBS volumes...[/cyan]"
    )

    response = ec2.describe_volumes()

    for volume in response["Volumes"]:

        volume_id = volume["VolumeId"]
        state = volume["State"]
        size = volume["Size"]

        tags = extract_tags(
            volume.get("Tags", [])
        )

        if state == "available":

            estimated_cost = (
                size * EBS_GP3_COST_PER_GB
            )

            add_finding(
                resource_id=volume_id,
                resource_type="ebs_volume",
                reason="unattached",
                age_days=0,
                estimated_cost=estimated_cost,
                tags=tags,
                suggested_action="delete",
                safe_to_auto_delete=(
                    not is_protected(tags)
                )
            )

            if args.delete and not is_protected(tags):

                console.print(
                    f"[red]Deleting volume {volume_id}[/red]"
                )

                ec2.delete_volume(
                    VolumeId=volume_id
                )

        missing = missing_tags(tags)

        if missing:

            add_finding(
                resource_id=volume_id,
                resource_type="ebs_volume",
                reason=f"missing_tags:{','.join(missing)}",
                age_days=0,
                estimated_cost=0,
                tags=tags,
                suggested_action="tag",
                safe_to_auto_delete=False
            )

# =========================================================
# EC2 CHECK
# =========================================================

def check_ec2_instances():

    console.print(
        "[cyan]Scanning EC2 instances...[/cyan]"
    )

    response = ec2.describe_instances()

    for reservation in response["Reservations"]:

        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]

            state = instance["State"]["Name"]

            launch_time = instance["LaunchTime"]

            age_days = (
                datetime.now(timezone.utc)
                - launch_time
            ).days

            tags = extract_tags(
                instance.get("Tags", [])
            )

            if (
                state == "stopped"
                and age_days > args.stopped_days
            ):

                add_finding(
                    resource_id=instance_id,
                    resource_type="ec2_instance",
                    reason="stopped_too_long",
                    age_days=age_days,
                    estimated_cost=(
                        STOPPED_INSTANCE_MONTHLY_COST
                    ),
                    tags=tags,
                    suggested_action="terminate",
                    safe_to_auto_delete=(
                        not is_protected(tags)
                    )
                )

                if args.delete and not is_protected(tags):

                    console.print(
                        f"[red]Terminating {instance_id}[/red]"
                    )

                    ec2.terminate_instances(
                        InstanceIds=[instance_id]
                    )

            missing = missing_tags(tags)

            if missing:

                add_finding(
                    resource_id=instance_id,
                    resource_type="ec2_instance",
                    reason=f"missing_tags:{','.join(missing)}",
                    age_days=age_days,
                    estimated_cost=0,
                    tags=tags,
                    suggested_action="tag",
                    safe_to_auto_delete=False
                )

# =========================================================
# EIP CHECK
# =========================================================

def check_elastic_ips():

    console.print(
        "[cyan]Scanning Elastic IPs...[/cyan]"
    )

    response = ec2.describe_addresses()

    for address in response["Addresses"]:

        allocation_id = address.get(
            "AllocationId",
            "unknown"
        )

        tags = extract_tags(
            address.get("Tags", [])
        )

        if "InstanceId" not in address:

            add_finding(
                resource_id=allocation_id,
                resource_type="elastic_ip",
                reason="unassociated",
                age_days=0,
                estimated_cost=(
                    ELASTIC_IP_MONTHLY_COST
                ),
                tags=tags,
                suggested_action="release",
                safe_to_auto_delete=(
                    not is_protected(tags)
                )
            )

            if args.delete and not is_protected(tags):

                console.print(
                    f"[red]Releasing EIP {allocation_id}[/red]"
                )

                ec2.release_address(
                    AllocationId=allocation_id
                )

        missing = missing_tags(tags)

        if missing:

            add_finding(
                resource_id=allocation_id,
                resource_type="elastic_ip",
                reason=f"missing_tags:{','.join(missing)}",
                age_days=0,
                estimated_cost=0,
                tags=tags,
                suggested_action="tag",
                safe_to_auto_delete=False
            )

# =========================================================
# SAVE REPORTS
# =========================================================

def generate_reports():

    total_cost = sum(
        item["estimated_monthly_cost_usd"]
        for item in findings
    )

    report["summary"]["total_orphans"] = (
        len(findings)
    )

    report["summary"][
        "estimated_monthly_waste_usd"
    ] = round(total_cost, 2)

    with open("report.json", "w") as file:

        json.dump(
            report,
            file,
            indent=2
        )

    with open("report.md", "w") as file:

        file.write(
            "# CloudCost Janitor Report\n\n"
        )

        file.write(
            f"Scan Time: {report['scan_timestamp']}\n\n"
        )

        file.write(
            f"Total Findings: {len(findings)}\n\n"
        )

        file.write(
            f"Estimated Monthly Waste: ${round(total_cost,2)}\n\n"
        )

        for item in findings:

            file.write(
                f"## {item['resource_id']}\n"
            )

            file.write(
                f"- Type: {item['resource_type']}\n"
            )

            file.write(
                f"- Reason: {item['reason']}\n"
            )

            file.write(
                f"- Estimated Cost: ${item['estimated_monthly_cost_usd']}\n"
            )

            file.write(
                f"- Suggested Action: {item['suggested_action']}\n\n"
            )

# =========================================================
# TERMINAL OUTPUT
# =========================================================

def print_summary():

    table = Table(
        title="CloudCost Janitor Findings"
    )

    table.add_column("Resource ID")
    table.add_column("Type")
    table.add_column("Reason")
    table.add_column("Action")

    for item in findings:

        table.add_row(
            item["resource_id"],
            item["resource_type"],
            item["reason"],
            item["suggested_action"]
        )

    console.print(table)

# =========================================================
# MAIN
# =========================================================

def main():

    console.print(
        "[bold green]Starting CloudCost Janitor[/bold green]"
    )

    check_ebs_volumes()

    check_ec2_instances()

    check_elastic_ips()

    generate_reports()

    print_summary()

    if args.dry_run and findings:

        console.print(
            "[bold red]Orphan resources detected[/bold red]"
        )

        sys.exit(1)

    console.print(
        "[bold green]No orphan resources found[/bold green]"
    )

    sys.exit(0)

if __name__ == "__main__":
    main()