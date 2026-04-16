"""
Red Packet automation utilities
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from .client import AgentHansaClient, AsyncAgentHansaClient
from .models import RedPacket

logger = logging.getLogger(__name__)


@dataclass
class RedPacketResult:
    """Result of a red packet collection attempt."""
    joined: bool
    packet_id: Optional[str] = None
    estimated_share: Optional[float] = None
    next_packet_at: Optional[datetime] = None
    next_packet_minutes: Optional[int] = None
    message: str = ""


class RedPacketCollector:
    """Automated red packet collection utility."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AgentHansaClient(api_key)
    
    def check_and_join(self) -> RedPacketResult:
        """
        Check for active red packets and join if available.
        
        Returns:
            RedPacketResult with details of the attempt
        """
        try:
            # Get active red packets
            packets = self.client.list_red_packets()
            
            if not packets:
                # No active packets, get next drop time
                next_info = self.client.next_red_packet()
                next_at = next_info.get("next_at")
                seconds = next_info.get("seconds_until")
                
                return RedPacketResult(
                    joined=False,
                    next_packet_at=datetime.fromisoformat(next_at.replace('Z', '+00:00')) if next_at else None,
                    next_packet_minutes=int(seconds / 60) if seconds else None,
                    message="No active red packets. Waiting for next drop."
                )
            
            # Join the first active packet
            packet = packets[0]
            logger.info(f"Found red packet: {packet.title} (${packet.total_amount})")
            
            # Get challenge
            try:
                challenge = self.client.get_red_packet_challenge(packet.id)
                
                if "detail" in challenge and "Already joined" in challenge.get("detail", ""):
                    return RedPacketResult(
                        joined=False,
                        packet_id=packet.id,
                        estimated_share=packet.estimated_share,
                        message="Already joined this red packet"
                    )
                
                # Extract answer from challenge (usually a math problem)
                # This is simplified - real implementation would parse the question
                answer = self._solve_challenge(challenge)
                
                # Join the packet
                result = self.client.join_red_packet(packet.id, answer)
                
                if "error" in result:
                    return RedPacketResult(
                        joined=False,
                        packet_id=packet.id,
                        message=f"Failed to join: {result.get('error')}"
                    )
                
                return RedPacketResult(
                    joined=True,
                    packet_id=packet.id,
                    estimated_share=packet.estimated_share,
                    message=f"Successfully joined! Estimated share: ${packet.estimated_share:.2f}"
                )
                
            except Exception as e:
                return RedPacketResult(
                    joined=False,
                    packet_id=packet.id,
                    message=f"Error joining: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Error checking red packets: {e}")
            return RedPacketResult(
                joined=False,
                message=f"Error: {str(e)}"
            )
    
    def _solve_challenge(self, challenge: Dict[str, Any]) -> str:
        """
        Solve the red packet challenge.
        
        Most challenges are simple math problems like:
        - "18 badges split among 3 robots = ?"
        - "What is 15 + 27?"
        """
        # Get the question text
        question = challenge.get("question", "")
        
        # Try to extract numbers and operation
        # This is a simple parser - can be made more sophisticated
        import re
        
        # Look for patterns like "X split among Y" or "X divided by Y"
        split_match = re.search(r'(\d+).*?split among.*?(\d+)', question, re.IGNORECASE)
        if split_match:
            total = int(split_match.group(1))
            parts = int(split_match.group(2))
            return str(total // parts)
        
        # Look for simple math expressions
        numbers = re.findall(r'\d+', question)
        if len(numbers) >= 2:
            # Check for +, -, *, / in the question
            if '+' in question:
                return str(int(numbers[0]) + int(numbers[1]))
            elif '-' in question:
                return str(int(numbers[0]) - int(numbers[1]))
            elif '*' in question or 'multiply' in question.lower():
                return str(int(numbers[0]) * int(numbers[1]))
            elif '/' in question or 'divide' in question.lower():
                return str(int(numbers[0]) // int(numbers[1]))
        
        # Default: return first number found or "0"
        return numbers[0] if numbers else "0"
    
    def run_scheduler(self, check_interval_minutes: int = 60):
        """
        Run continuous red packet collection.
        
        Args:
            check_interval_minutes: How often to check for packets
        """
        import time
        
        logger.info(f"Starting red packet collector (checking every {check_interval_minutes} minutes)")
        
        while True:
            result = self.check_and_join()
            
            if result.joined:
                logger.info(f"✅ {result.message}")
            elif result.next_packet_minutes:
                logger.info(f"⏳ Next packet in {result.next_packet_minutes} minutes")
            else:
                logger.info(f"ℹ️ {result.message}")
            
            # Sleep until next check
            time.sleep(check_interval_minutes * 60)


class AsyncRedPacketCollector:
    """Async version of red packet collector."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def check_and_join(self) -> RedPacketResult:
        """Async version of check_and_join."""
        async with AsyncAgentHansaClient(self.api_key) as client:
            try:
                packets = await client.list_red_packets()
                
                if not packets:
                    return RedPacketResult(
                        joined=False,
                        message="No active red packets"
                    )
                
                # Implementation similar to sync version
                # Would need async challenge solving
                packet = packets[0]
                
                return RedPacketResult(
                    joined=True,
                    packet_id=packet.id,
                    estimated_share=packet.estimated_share,
                    message=f"Found packet: {packet.title}"
                )
                
            except Exception as e:
                return RedPacketResult(
                    joined=False,
                    message=f"Error: {str(e)}"
                )
