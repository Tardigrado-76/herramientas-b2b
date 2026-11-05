"""Forensic verifier for SOC incident alerts and leak auditing."""

import json
from pathlib import Path
import re
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOG_PATH = Path("data/logs/soc_incidents.jsonl")


def verify_soc_log() -> bool:
    print(f"Auditing SOC Incident Log: {LOG_PATH.resolve()}")
    if not LOG_PATH.exists():
        print("[INFO] No incident log file found yet (empty).")
        return True

    required_keys = [
        "event_id",
        "timestamp",
        "severity",
        "incident_type",
        "mitre_technique_id",
        "capec_id",
        "agent_id",
        "command",
    ]

    leak_patterns = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ]

    total_records = 0
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            total_records += 1
            try:
                rec = json.loads(line)
            except Exception as e:
                print(f"[FAIL] Line {idx} is not valid JSON: {e}")
                return False

            for k in required_keys:
                if k not in rec:
                    print(f"[FAIL] Line {idx} missing required key: {k}")
                    return False

            # Secret leak verification
            line_str = line
            for pattern in leak_patterns:
                if pattern.search(line_str) and "[REDACTED]" not in line_str:
                    print(f"[CRITICAL] Line {idx} contains unredacted API key or token!")
                    return False

    print(f"[SUCCESS] All {total_records} incident records are valid, well-formed, and leak-free.")
    return True


if __name__ == "__main__":
    success = verify_soc_log()
    sys.exit(0 if success else 1)
