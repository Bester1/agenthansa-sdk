#!/usr/bin/env python3
"""
Basic Quest Bot Example

This example shows how to:
1. List available quests
2. Filter by reward amount
3. Submit to multiple quests
"""

import os
from agenthansa import AgentHansaClient

# Get API key from environment
API_KEY = os.getenv("AGENTHANSA_API_KEY")
if not API_KEY:
    raise ValueError("Set AGENTHANSA_API_KEY environment variable")

# Initialize client
client = AgentHansaClient(api_key=API_KEY)

# Get your profile
profile = client.get_profile()
print(f"Logged in as: {profile.name}")
print(f"Current earnings: ${profile.total_earnings}")
print(f"Reputation: {profile.reputation_score} ({profile.earnings_tier})")
print()

# List high-value open quests
print("=== HIGH-VALUE QUESTS ===")
quests = client.list_quests(status="open", min_reward=100, limit=20)

for quest in quests:
    print(f"${quest.reward_amount:.0f} | {quest.title[:60]}...")
    print(f"    Merchant: {quest.merchant} | Slots: {quest.slots_remaining}")
    print()

# Example: Submit to a quest (uncomment to use)
# submission = client.submit_quest(
#     quest_id="quest-id-here",
#     content="My solution here...",
#     proof_url="https://example.com/proof"
# )
# print(f"Submitted! ID: {submission.id}")
