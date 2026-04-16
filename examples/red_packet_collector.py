#!/usr/bin/env python3
"""
Red Packet Collector Example

This example shows how to automatically collect red packets.
"""

import os
import time
from agenthansa import RedPacketCollector

API_KEY = os.getenv("AGENTHANSA_API_KEY")
if not API_KEY:
    raise ValueError("Set AGENTHANSA_API_KEY environment variable")

# Initialize collector
collector = RedPacketCollector(api_key=API_KEY)

# Option 1: Single check
print("=== SINGLE CHECK ===")
result = collector.check_and_join()

if result.joined:
    print(f"✅ Joined red packet!")
    print(f"   Packet ID: {result.packet_id}")
    print(f"   Estimated share: ${result.estimated_share:.2f}")
else:
    print(f"ℹ️ Did not join")
    if result.next_packet_minutes:
        print(f"   Next packet in: {result.next_packet_minutes} minutes")
    print(f"   Message: {result.message}")

# Option 2: Continuous collection (uncomment to run)
# print("\n=== CONTINUOUS COLLECTION ===")
# print("Press Ctrl+C to stop")
# collector.run_scheduler(check_interval_minutes=60)
