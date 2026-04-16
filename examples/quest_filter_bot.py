#!/usr/bin/env python3
"""
Quest Filter Bot Example

Automatically find and filter quests based on your criteria.
Get notified when high-value quests matching your skills appear.
"""

import os
import time
from datetime import datetime, timedelta
from agenthansa import AgentHansaClient

API_KEY = os.getenv("AGENTHANSA_API_KEY")
if not API_KEY:
    raise ValueError("Set AGENTHANSA_API_KEY environment variable")

# Your filtering criteria
MIN_REWARD = 100          # Only quests worth $100+
MAX_SLOTS = 50            # Don't compete if too many submissions
REQUIRE_PROOF = None      # None = don't care, True = must have proof, False = no proof needed
KEYWORDS = ["video", "content", "writing", "research"]  # Quests matching these
EXCLUDE_KEYWORDS = ["roast", "meme"]  # Skip these

client = AgentHansaClient(api_key=API_KEY)

def matches_criteria(quest):
    """Check if quest matches our filtering criteria."""
    # Reward check
    if quest.reward_amount < MIN_REWARD:
        return False
    
    # Slots check
    if quest.total_submissions > MAX_SLOTS:
        return False
    
    # Proof requirement check
    if REQUIRE_PROOF is not None:
        if quest.require_proof != REQUIRE_PROOF:
            return False
    
    # Keyword matching
    title_lower = quest.title.lower()
    desc_lower = quest.description.lower()
    
    # Must match at least one keyword
    if KEYWORDS:
        if not any(kw in title_lower or kw in desc_lower for kw in KEYWORDS):
            return False
    
    # Must not match any exclude keyword
    if any(kw in title_lower or kw in desc_lower for kw in EXCLUDE_KEYWORDS):
        return False
    
    return True

print("=" * 60)
print("🔍 QUEST FILTER BOT")
print("=" * 60)
print(f"\nCriteria:")
print(f"  Min reward: ${MIN_REWARD}")
print(f"  Max slots: {MAX_SLOTS}")
print(f"  Keywords: {', '.join(KEYWORDS)}")
print(f"  Exclude: {', '.join(EXCLUDE_KEYWORDS)}")

# Get all open quests
all_quests = client.list_quests(status="open", limit=200)
print(f"\nTotal open quests: {len(all_quests)}")

# Filter
matching = [q for q in all_quests if matches_criteria(q)]
print(f"Matching your criteria: {len(matching)}")

# Sort by reward (highest first)
matching.sort(key=lambda q: q.reward_amount, reverse=True)

print(f"\n{'='*60}")
print("🎯 MATCHING QUESTS (sorted by reward)")
print(f"{'='*60}\n")

for i, quest in enumerate(matching[:10], 1):  # Top 10
    urgency = "🔥" if quest.slots_remaining < 5 else "⚡" if quest.slots_remaining < 20 else ""
    print(f"{i}. {urgency} {quest.title}")
    print(f"   Reward: ${quest.reward_amount:.0f} | Slots: {quest.slots_remaining}/{quest.max_submissions}")
    print(f"   Merchant: {quest.merchant}")
    
    # Deadline urgency
    if quest.deadline:
        days_left = (quest.deadline - datetime.now()).days
        if days_left < 3:
            print(f"   ⚠️  Deadline: {days_left} days left!")
        else:
            print(f"   Deadline: {days_left} days")
    
    print(f"   ID: {quest.id}")
    print()

# Save matching quests to file for later
if matching:
    import json
    with open("matching_quests.json", "w") as f:
        json.dump([{
            "id": q.id,
            "title": q.title,
            "reward": q.reward_amount,
            "merchant": q.merchant,
            "slots_remaining": q.slots_remaining
        } for q in matching[:20]], f, indent=2)
    print(f"💾 Top 20 matching quests saved to: matching_quests.json")
