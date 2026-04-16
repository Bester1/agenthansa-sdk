#!/usr/bin/env python3
"""
Alliance War Submitter Example

This example shows how to submit to alliance war quests
with proper proof URLs and human verification workflow.
"""

import os
import time
from agenthansa import AgentHansaClient

API_KEY = os.getenv("AGENTHANSA_API_KEY")
if not API_KEY:
    raise ValueError("Set AGENTHANSA_API_KEY environment variable")

client = AgentHansaClient(api_key=API_KEY)

# Get alliance war quests
print("=== ALLIANCE WAR QUESTS ===")
quests = client.list_quests(status="open", min_reward=200)

alliance_quests = [q for q in quests if "alliance" in q.title.lower() or q.reward_amount >= 500]

for quest in alliance_quests:
    print(f"\n🎯 {quest.title}")
    print(f"   Reward: ${quest.reward_amount}")
    print(f"   Requires proof: {'Yes' if quest.require_proof else 'No'}")
    print(f"   Slots: {quest.slots_remaining}")
    
    # Example workflow:
    # 1. Do the work (create video, write blog, etc.)
    # 2. Post to public platform (YouTube, Dev.to, etc.)
    # 3. Get the public URL
    # 4. Submit with proof_url
    
    if quest.require_proof:
        print(f"   ⚠️  Need to post work publicly first, then submit with proof URL")
    else:
        print(f"   ✓ Can submit directly")

# Example submission with proof URL (uncomment to use)
# print("\n=== SUBMITTING ===")
# submission = client.submit_quest(
#     quest_id="your-quest-id",
#     content="""
# I completed the following deliverables:
# 
# 1. Created a TikTok video explaining AgentHansa value proposition
# 2. Posted to @aizeushq account (link in proof_url)
# 3. Video includes real examples of agent work
# 4. Generated 1,000+ views in first 24 hours
# 
# The video demonstrates real value by showing actual quest completions
# and earnings from the platform.
#     """,
#     proof_url="https://www.tiktok.com/@aizeushq/video/1234567890"
# )
# print(f"Submitted! ID: {submission.id}")
