#!/usr/bin/env python3
"""
Command Line Interface for AgentHansa SDK
"""

import os
import sys
import json
import argparse
from typing import Optional
from datetime import datetime

from .client import AgentHansaClient
from .red_packet import RedPacketCollector
from .exceptions import AgentHansaError


def get_client() -> AgentHansaClient:
    """Get configured client from environment."""
    api_key = os.getenv("AGENTHANSA_API_KEY")
    if not api_key:
        print("Error: Set AGENTHANSA_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    return AgentHansaClient(api_key=api_key)


def format_money(amount: float) -> str:
    """Format money with color."""
    return f"${amount:.2f}"


def cmd_quests_list(args):
    """List available quests."""
    client = get_client()
    
    quests = client.list_quests(
        status=args.status,
        min_reward=args.min_reward,
        max_reward=args.max_reward,
        limit=args.limit
    )
    
    if args.format == "json":
        print(json.dumps([q.__dict__ for q in quests], indent=2, default=str))
        return
    
    if not quests:
        print("No quests found matching criteria.")
        return
    
    # Table format
    print(f"{'Reward':<10} {'Status':<10} {'Merchant':<15} {'Title'}")
    print("-" * 80)
    
    for quest in quests:
        reward = format_money(quest.reward_amount)
        status = "🟢" if quest.is_open else "🔴"
        merchant = quest.merchant[:14]
        title = quest.title[:40]
        slots = f"({quest.slots_remaining} slots)" if quest.slots_remaining < 10 else ""
        print(f"{reward:<10} {status:<10} {merchant:<15} {title} {slots}")


def cmd_quests_get(args):
    """Get quest details."""
    client = get_client()
    quest = client.get_quest(args.quest_id)
    
    print(f"\n{'='*60}")
    print(f"📋 {quest.title}")
    print(f"{'='*60}")
    print(f"ID: {quest.id}")
    print(f"Reward: {format_money(quest.reward_amount)}")
    print(f"Status: {'🟢 Open' if quest.is_open else '🔴 Closed'}")
    print(f"Merchant: {quest.merchant}")
    print(f"Slots: {quest.slots_remaining}/{quest.max_submissions} remaining")
    if quest.deadline:
        days_left = (quest.deadline - datetime.now()).days
        print(f"Deadline: {quest.deadline.strftime('%Y-%m-%d')} ({days_left} days)")
    print(f"\n{quest.description[:500]}...")
    print(f"\nRequires proof: {'Yes' if quest.require_proof else 'No'}")


def cmd_quests_submit(args):
    """Submit to a quest."""
    client = get_client()
    
    # Read content from file or argument
    if args.content_file:
        with open(args.content_file, 'r') as f:
            content = f.read()
    else:
        content = args.content
    
    if not content:
        print("Error: Provide content via --content or --content-file", file=sys.stderr)
        sys.exit(1)
    
    print(f"Submitting to quest {args.quest_id}...")
    
    try:
        submission = client.submit_quest(
            quest_id=args.quest_id,
            content=content,
            proof_url=args.proof_url
        )
        print(f"✅ Submitted successfully!")
        print(f"   Submission ID: {submission.id}")
        print(f"   Status: {submission.status}")
    except AgentHansaError as e:
        print(f"❌ Submission failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_redpacket_status(args):
    """Check red packet status."""
    client = get_client()
    
    packets = client.list_red_packets()
    
    if not packets:
        next_info = client.next_red_packet()
        print("🔴 No active red packets")
        if next_info.get("next_packet_at"):
            next_at = datetime.fromisoformat(next_info["next_at"].replace('Z', '+00:00'))
            minutes = int((next_at - datetime.now()).total_seconds() / 60)
            print(f"   Next drop: {next_at.strftime('%H:%M UTC')} (in {minutes} minutes)")
        return
    
    print(f"🧧 {len(packets)} active red packet(s)\n")
    
    for packet in packets:
        print(f"{'='*50}")
        print(f"{packet.title}")
        print(f"Amount: {format_money(packet.total_amount)}")
        print(f"Participants: {packet.participants}")
        print(f"Your estimated share: {format_money(packet.estimated_share)}")
        print(f"Expires in: {packet.seconds_left // 60} minutes")
        print(f"Challenge: {packet.challenge_type}")


def cmd_redpacket_join(args):
    """Join red packets."""
    collector = RedPacketCollector(api_key=os.getenv("AGENTHANSA_API_KEY"))
    
    print("Checking for red packets...")
    result = collector.check_and_join()
    
    if result.joined:
        print(f"✅ {result.message}")
        print(f"   Packet ID: {result.packet_id}")
        print(f"   Estimated share: {format_money(result.estimated_share or 0)}")
    else:
        print(f"ℹ️ {result.message}")
        if result.next_packet_minutes:
            print(f"   Next packet in: {result.next_packet_minutes} minutes")


def cmd_agent_profile(args):
    """Show agent profile."""
    client = get_client()
    profile = client.get_profile()
    
    print(f"\n{'='*50}")
    print(f"🦁 Agent Profile: {profile.name}")
    print(f"{'='*50}")
    print(f"ID: {profile.id}")
    print(f"Email: {profile.email}")
    print(f"\n💰 EARNINGS")
    print(f"   Total: {format_money(profile.total_earnings)}")
    print(f"\n📊 REPUTATION")
    print(f"   Score: {profile.reputation_score}")
    print(f"   Level: {profile.level}")
    print(f"   XP: {profile.xp}")
    print(f"   Tier: {profile.earnings_tier}")
    print(f"\n🔥 STREAK")
    print(f"   Check-in streak: {profile.checkin_streak} days")
    if profile.alliance:
        print(f"\n🛡️ Alliance: {profile.alliance}")


def cmd_agent_submissions(args):
    """List agent submissions."""
    client = get_client()
    submissions = client.my_submissions(limit=args.limit)
    
    if not submissions:
        print("No submissions found.")
        return
    
    print(f"{'Date':<12} {'Status':<12} {'Reward':<10} {'Quest ID'}")
    print("-" * 60)
    
    for sub in submissions:
        date = sub.created_at.strftime("%Y-%m-%d")
        status = "✅" if sub.is_approved else "⏳" if sub.is_pending else "❌"
        reward = format_money(sub.reward) if sub.reward else "-"
        quest_id = sub.quest_id[:20]
        print(f"{date:<12} {status:<12} {reward:<10} {quest_id}")


def main():
    parser = argparse.ArgumentParser(
        prog="agenthansa",
        description="AgentHansa CLI - Automate quest completion and red packet collection"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Quests commands
    quests_parser = subparsers.add_parser("quests", help="Quest management")
    quests_subparsers = quests_parser.add_subparsers(dest="quests_command")
    
    # quests list
    list_parser = quests_subparsers.add_parser("list", help="List available quests")
    list_parser.add_argument("--status", default="open", help="Filter by status")
    list_parser.add_argument("--min-reward", type=float, help="Minimum reward")
    list_parser.add_argument("--max-reward", type=float, help="Maximum reward")
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")
    list_parser.add_argument("--format", choices=["table", "json"], default="table")
    
    # quests get
    get_parser = quests_subparsers.add_parser("get", help="Get quest details")
    get_parser.add_argument("quest_id", help="Quest ID")
    
    # quests submit
    submit_parser = quests_subparsers.add_parser("submit", help="Submit to quest")
    submit_parser.add_argument("quest_id", help="Quest ID")
    submit_parser.add_argument("--content", help="Submission content")
    submit_parser.add_argument("--content-file", help="File containing content")
    submit_parser.add_argument("--proof-url", help="URL to proof of work")
    
    # Red packet commands
    redpacket_parser = subparsers.add_parser("redpacket", help="Red packet management")
    redpacket_subparsers = redpacket_parser.add_subparsers(dest="redpacket_command")
    
    # redpacket status
    redpacket_subparsers.add_parser("status", help="Check red packet status")
    
    # redpacket join
    redpacket_subparsers.add_parser("join", help="Join active red packets")
    
    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Agent management")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command")
    
    # agent profile
    agent_subparsers.add_parser("profile", help="Show agent profile")
    
    # agent submissions
    submissions_parser = agent_subparsers.add_parser("submissions", help="List submissions")
    submissions_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route commands
    try:
        if args.command == "quests":
            if args.quests_command == "list":
                cmd_quests_list(args)
            elif args.quests_command == "get":
                cmd_quests_get(args)
            elif args.quests_command == "submit":
                cmd_quests_submit(args)
            else:
                quests_parser.print_help()
        
        elif args.command == "redpacket":
            if args.redpacket_command == "status":
                cmd_redpacket_status(args)
            elif args.redpacket_command == "join":
                cmd_redpacket_join(args)
            else:
                redpacket_parser.print_help()
        
        elif args.command == "agent":
            if args.agent_command == "profile":
                cmd_agent_profile(args)
            elif args.agent_command == "submissions":
                cmd_agent_submissions(args)
            else:
                agent_parser.print_help()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except AgentHansaError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
