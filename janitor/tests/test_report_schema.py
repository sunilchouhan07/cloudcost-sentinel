def test_report_structure():
    report = {
        "scan_timestamp": "2026-05-22T10:00:00Z",
        "account_id": "000000000000",
        "region": "us-east-1",
        "summary": {},
        "findings": []
    }

    required_fields = [
        "scan_timestamp",
        "account_id",
        "region",
        "summary",
        "findings"
    ]

    for field in required_fields:
        assert field in report