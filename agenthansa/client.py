"""
AgentHansa API Client
"""

import requests
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .models import Quest, Submission, RedPacket, AgentProfile
from .exceptions import AgentHansaError, AuthenticationError, RateLimitError


class AgentHansaClient:
    """Synchronous AgentHansa API client."""
    
    BASE_URL = "https://www.agenthansa.com/api"
    
    # Known working endpoints (as of 2026-04-16):
    # ✅ GET /api/red-packets - List active red packets
    # ✅ GET /api/red-packets/{id}/challenge - Get challenge question
    # ✅ POST /api/red-packets/{id}/join - Join red packet
    # ❌ GET /api/users/me - Returns HTML (not JSON)
    # ❌ GET /api/quests - Returns HTML (not JSON)
    # ❌ GET /api/quests/{id} - Endpoint unknown
    # ❌ POST /api/quests/{id}/submit - Endpoint unknown
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 400:
                    raise AgentHansaError(
                        f"API error: {response.status_code} - {response.text}"
                    )
                
                return response.json() if response.content else {}
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise AgentHansaError(f"Request timeout after {self.max_retries} retries")
                continue
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise AgentHansaError(f"Request failed: {e}")
                continue
    
    # Quests API
    def list_quests(
        self,
        status: Optional[str] = "open",
        min_reward: Optional[float] = None,
        max_reward: Optional[float] = None,
        alliance: Optional[str] = None,
        limit: int = 100
    ) -> List[Quest]:
        """List available quests with optional filters."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        if min_reward:
            params["min_reward"] = min_reward
        if max_reward:
            params["max_reward"] = max_reward
        if alliance:
            params["alliance"] = alliance
        
        data = self._request("GET", "/quests", params=params)
        return [Quest.from_dict(q) for q in data.get("quests", [])]
    
    def get_quest(self, quest_id: str) -> Quest:
        """Get detailed information about a quest."""
        data = self._request("GET", f"/quests/{quest_id}")
        return Quest.from_dict(data)
    
    def submit_quest(
        self,
        quest_id: str,
        content: str,
        proof_url: Optional[str] = None
    ) -> Submission:
        """Submit a solution to a quest."""
        payload = {"content": content}
        if proof_url:
            payload["proof_url"] = proof_url
        
        data = self._request(
            "POST",
            f"/quests/{quest_id}/submit",
            json=payload
        )
        return Submission.from_dict(data)
    
    def my_submissions(self, limit: int = 100) -> List[Submission]:
        """List your submissions."""
        data = self._request("GET", "/submissions", params={"limit": limit})
        return [Submission.from_dict(s) for s in data.get("submissions", [])]
    
    # Red Packets API
    def list_red_packets(self) -> List[RedPacket]:
        """List active red packets."""
        data = self._request("GET", "/red-packets")
        return [RedPacket.from_dict(rp) for rp in data.get("active", [])]
    
    def get_red_packet_challenge(self, packet_id: str) -> Dict[str, Any]:
        """Get the challenge question for a red packet."""
        return self._request("GET", f"/red-packets/{packet_id}/challenge")
    
    def join_red_packet(self, packet_id: str, answer: str) -> Dict[str, Any]:
        """Join a red packet with the answer."""
        return self._request(
            "POST",
            f"/red-packets/{packet_id}/join",
            json={"answer": answer}
        )
    
    def next_red_packet(self) -> Optional[Dict[str, Any]]:
        """Get information about the next red packet drop."""
        data = self._request("GET", "/red-packets")
        return {
            "next_at": data.get("next_packet_at"),
            "seconds_until": data.get("next_packet_seconds"),
            "schedule": data.get("schedule")
        }
    
    # Agent API
    def get_profile(self) -> AgentProfile:
        """Get your agent profile."""
        data = self._request("GET", "/users/me")
        return AgentProfile.from_dict(data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get earnings and reputation statistics."""
        profile = self.get_profile()
        return {
            "total_earnings": profile.total_earnings,
            "reputation": profile.reputation_score,
            "level": profile.level,
            "xp": profile.xp,
            "checkin_streak": profile.checkin_streak
        }


class AsyncAgentHansaClient:
    """Asynchronous AgentHansa API client."""
    
    BASE_URL = "https://www.agenthansa.com/api"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make async authenticated request."""
        if not self._session:
            raise AgentHansaError("Client not initialized. Use async with context.")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with self._session.request(method=method, url=url, **kwargs) as response:
            if response.status == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status >= 400:
                text = await response.text()
                raise AgentHansaError(f"API error: {response.status} - {text}")
            
            if response.content_type == "application/json":
                return await response.json()
            return {}
    
    async def list_quests(
        self,
        status: Optional[str] = "open",
        min_reward: Optional[float] = None,
        max_reward: Optional[float] = None,
        limit: int = 100
    ) -> List[Quest]:
        """List available quests (async)."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        if min_reward:
            params["min_reward"] = min_reward
        if max_reward:
            params["max_reward"] = max_reward
        
        data = await self._request("GET", "/quests", params=params)
        return [Quest.from_dict(q) for q in data.get("quests", [])]
    
    async def submit_quest(
        self,
        quest_id: str,
        content: str,
        proof_url: Optional[str] = None
    ) -> Submission:
        """Submit to a quest (async)."""
        payload = {"content": content}
        if proof_url:
            payload["proof_url"] = proof_url
        
        data = await self._request(
            "POST",
            f"/quests/{quest_id}/submit",
            json=payload
        )
        return Submission.from_dict(data)
    
    async def list_red_packets(self) -> List[RedPacket]:
        """List active red packets (async)."""
        data = await self._request("GET", "/red-packets")
        return [RedPacket.from_dict(rp) for rp in data.get("active", [])]
