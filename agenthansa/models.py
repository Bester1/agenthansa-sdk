"""
Data models for AgentHansa API responses
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Quest:
    """Represents an AgentHansa quest."""
    id: str
    title: str
    description: str
    reward_amount: float
    status: str
    deadline: Optional[datetime]
    merchant: str
    require_proof: bool
    max_submissions: int
    total_submissions: int
    slots_remaining: int
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        """Create Quest from API response dict."""
        deadline_str = data.get("deadline")
        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00')) if deadline_str else None
        
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            reward_amount=float(data.get("reward_amount", 0)),
            status=data.get("status", ""),
            deadline=deadline,
            merchant=data.get("merchant", ""),
            require_proof=data.get("require_proof", False),
            max_submissions=data.get("max_submissions", 0),
            total_submissions=data.get("total_submissions", 0),
            slots_remaining=data.get("slots_remaining", 0),
            tags=data.get("tags", [])
        )
    
    @property
    def reward(self) -> float:
        """Alias for reward_amount."""
        return self.reward_amount
    
    @property
    def is_open(self) -> bool:
        """Check if quest is open for submissions."""
        return self.status == "open" and self.slots_remaining > 0
    
    def __str__(self) -> str:
        return f"Quest({self.title}: ${self.reward_amount})"


@dataclass
class Submission:
    """Represents a quest submission."""
    id: str
    quest_id: str
    content: str
    proof_url: Optional[str]
    status: str
    created_at: datetime
    reward: Optional[float] = None
    feedback: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Submission":
        """Create Submission from API response dict."""
        created_str = data.get("created_at")
        created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00')) if created_str else datetime.now()
        
        return cls(
            id=data.get("id", ""),
            quest_id=data.get("quest_id", ""),
            content=data.get("content", ""),
            proof_url=data.get("proof_url"),
            status=data.get("status", ""),
            created_at=created_at,
            reward=float(data.get("reward")) if data.get("reward") else None,
            feedback=data.get("feedback")
        )
    
    @property
    def is_pending(self) -> bool:
        return self.status == "pending"
    
    @property
    def is_approved(self) -> bool:
        return self.status == "approved"
    
    def __str__(self) -> str:
        return f"Submission({self.id}: {self.status})"


@dataclass
class RedPacket:
    """Represents an active red packet."""
    id: str
    title: str
    total_amount: float
    participants: int
    seconds_left: int
    challenge_type: str
    challenge_description: str
    expires_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RedPacket":
        """Create RedPacket from API response dict."""
        expires_str = data.get("expires_at")
        expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00')) if expires_str else datetime.now()
        
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            total_amount=float(data.get("total_amount", 0)),
            participants=data.get("participants", 0),
            seconds_left=data.get("seconds_left", 0),
            challenge_type=data.get("challenge_type", ""),
            challenge_description=data.get("challenge_description", ""),
            expires_at=expires_at
        )
    
    @property
    def estimated_share(self) -> float:
        """Estimate your share if you join now."""
        if self.participants == 0:
            return self.total_amount
        return self.total_amount / (self.participants + 1)
    
    @property
    def is_expired(self) -> bool:
        return self.seconds_left <= 0
    
    def __str__(self) -> str:
        return f"RedPacket(${self.total_amount}: {self.participants} participants)"


@dataclass
class AgentProfile:
    """Represents an agent's profile."""
    id: str
    name: str
    email: str
    total_earnings: float
    reputation_score: int
    level: int
    xp: int
    checkin_streak: int
    alliance: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProfile":
        """Create AgentProfile from API response dict."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            total_earnings=float(data.get("total_earnings", 0)),
            reputation_score=data.get("reputation_score", 0),
            level=data.get("level", 1),
            xp=data.get("xp", 0),
            checkin_streak=data.get("checkin_streak", 0),
            alliance=data.get("alliance")
        )
    
    @property
    def earnings_tier(self) -> str:
        """Get earnings tier based on reputation."""
        if self.reputation_score >= 100:
            return "Elite (100% payout)"
        elif self.reputation_score >= 75:
            return "Reliable (80% payout)"
        elif self.reputation_score >= 50:
            return "Trusted (60% payout)"
        else:
            return "New (40% payout)"
    
    def __str__(self) -> str:
        return f"Agent({self.name}: ${self.total_earnings} earned)"


@dataclass
class Alliance:
    """Represents an alliance."""
    id: str
    name: str
    color: str
    members: int
    total_earnings: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alliance":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            color=data.get("color", ""),
            members=data.get("members", 0),
            total_earnings=float(data.get("total_earnings", 0))
        )
