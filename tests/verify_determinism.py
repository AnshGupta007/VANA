#!/usr/bin/env python3
"""
VANA Determinism Verification Audit Script
==========================================
Task ID: T-GOV-F01
Assignee: Ansh Gupta

Audits Strict Quality Gate:
'Deterministic execution: 50 consecutive runs must produce identical SHA-256 state hashes'
"""

import sys
import os
import time
import hashlib

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation_engine.rule_engine import VanaRuleEngine, VanaEvaluationRequest


def run_determinism_audit(runs: int = 50) -> bool:
    print(f"[*] Starting VANA Deterministic Execution Audit ({runs} consecutive cycles)...")
    engine = VanaRuleEngine()

    start_time = time.time()
    audit_result = engine.compute_deterministic_state_hash(runs=runs)
    elapsed = time.time() - start_time

    print(f"[+] Total runs executed: {audit_result['runs']}")
    print(f"[+] Unique hashes observed: {audit_result['unique_hashes_count']}")
    print(f"[+] Deterministic state hash: {audit_result['sample_hash']}")
    print(f"[+] Execution time: {elapsed * 1000:.2f} ms ({elapsed / runs * 1000:.3f} ms/run)")

    if audit_result["all_hashes_identical"] and audit_result["unique_hashes_count"] == 1:
        print("\n" + "=" * 65)
        print(">>> SUCCESS: 50/50 CONSECUTIVE RUNS PRODUCED IDENTICAL SHA-256 HASHES <<<")
        print(">>> QUALITY GATE SATISFIED: ZERO STATE DRIFT VERIFIED                 <<<")
        print("=" * 65 + "\n")
        return True
    else:
        print("\n" + "!" * 65)
        print(">>> FAILURE: STATE DRIFT DETECTED IN CONSECUTIVE RUNS <<<")
        print("!" * 65 + "\n")
        return False


if __name__ == "__main__":
    success = run_determinism_audit(50)
    sys.exit(0 if success else 1)
