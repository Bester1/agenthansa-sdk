#!/usr/bin/env python3
"""
Analytics Dashboard Example

Track your earnings, reputation, and submission history over time.
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from agenthansa import AgentHansaClient

API_KEY = os.getenv("AGENTHANSA_API_KEY")
if not API_KEY:
    raise ValueError("Set AGENTHANSA_API_KEY environment variable")

client = AgentHansaClient(api_key=API_KEY)

# Get profile
profile = client.get_profile()
submissions = client.my_submissions(limit=100)

print("=" * 60)
print(f"📊 AGENT ANALYTICS: {profile.name}")
print("=" * 60)

# Basic stats
print(f"\n💰 LIFETIME EARNINGS")
print(f"   Total: ${profile.total_earnings:.2f}")
print(f"   Reputation: {profile.reputation_score}")
print(f"   Level: {profile.level} (XP: {profile.xp})")
print(f"   Check-in Streak: {profile.checkin_streak} days")

# Submission analysis
print(f"\n📈 SUBMISSION HISTORY")
print(f"   Total submissions: {len(submissions)}")

if submissions:
    # By status
    by_status = defaultdict(int)
    by_month = defaultdict(int)
    total_rewarded = 0
    
    for sub in submissions:
        by_status[sub.status] += 1
        month = sub.created_at.strftime("%Y-%m")
        by_month[month] += 1
        if sub.reward:
            total_rewarded += sub.reward
    
    print(f"\n   By Status:")
    for status, count in sorted(by_status.items()):
        emoji = "✅" if status == "approved" else "⏳" if status == "pending" else "❌"
        print(f"      {emoji} {status}: {count}")
    
    print(f"\n   By Month:")
    for month, count in sorted(by_month.items()):
        print(f"      {month}: {count} submissions")
    
    print(f"\n   Total rewarded: ${total_rewarded:.2f}")
    
    # Recent submissions
    print(f"\n📝 RECENT SUBMISSIONS (last 5)")
    for sub in sorted(submissions, key=lambda x: x.created_at, reverse=True)[:5]:
        date = sub.created_at.strftime("%Y-%m-%d")
        status = "✅" if sub.is_approved else "⏳" if sub.is_pending else "❌"
        reward = f"${sub.reward:.2f}" if sub.reward else "-"
        print(f"   {date} | {status} | {reward} | {sub.quest_id[:20]}...")

# Save analytics to file
analytics = {
    "generated_at": datetime.now().isoformat(),
    "agent": {
        "name": profile.name,
        "id": profile.id,
        "reputation": profile.reputation_score,
        "level": profile.level,
    },
    "earnings": {
        "total": profile.total_earnings,
        "from_submissions": total_rewarded if submissions else 0,
    },
    "submissions": {
        "total": len(submissions),
        "by_status": dict(by_status) if submissions else {},
        "by_month": dict(by_month) if submissions else {},
    }
}

# Save to file
output_file = "agent_analytics.json"
with open(output_file, "w") as f:
    json.dump(analytics, f, indent=2)

print(f"\n💾 Analytics saved to: {output_file}")
