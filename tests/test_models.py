"""
Tests for data models
"""

import pytest
from datetime import datetime
from agenthansa.models import Quest, Submission, RedPacket, AgentProfile


class TestQuest:
    """Test Quest model."""
    
    def test_quest_from_dict(self):
        """Test creating Quest from API response."""
        data = {
            "id": "quest-123",
            "title": "Test Quest",
            "description": "A test quest description",
            "reward_amount": "100.00",
            "status": "open",
            "deadline": "2026-12-31T23:59:59+00:00",
            "merchant": "TestMerchant",
            "require_proof": True,
            "max_submissions": 50,
            "total_submissions": 10,
            "slots_remaining": 40,
            "tags": ["writing", "content"]
        }
        
        quest = Quest.from_dict(data)
        
        assert quest.id == "quest-123"
        assert quest.title == "Test Quest"
        assert quest.reward_amount == 100.00
        assert quest.status == "open"
        assert quest.merchant == "TestMerchant"
        assert quest.require_proof is True
        assert quest.slots_remaining == 40
        assert quest.is_open is True
    
    def test_quest_no_deadline(self):
        """Test Quest with no deadline."""
        data = {
            "id": "quest-456",
            "title": "No Deadline Quest",
            "description": "Test",
            "reward_amount": 50,
            "status": "open",
            "merchant": "Test",
            "require_proof": False,
            "max_submissions": 100,
            "total_submissions": 100,
            "slots_remaining": 0
        }
        
        quest = Quest.from_dict(data)
        assert quest.deadline is None
        assert quest.is_open is False  # No slots remaining
    
    def test_quest_str(self):
        """Test Quest string representation."""
        quest = Quest(
            id="q1",
            title="Test",
            description="Desc",
            reward_amount=100,
            status="open",
            deadline=None,
            merchant="M",
            require_proof=False,
            max_submissions=10,
            total_submissions=5,
            slots_remaining=5
        )
        assert "Test" in str(quest)
        assert "$100" in str(quest)


class TestSubmission:
    """Test Submission model."""
    
    def test_submission_from_dict(self):
        """Test creating Submission from API response."""
        data = {
            "id": "sub-123",
            "quest_id": "quest-456",
            "content": "My submission content",
            "proof_url": "https://example.com/proof",
            "status": "pending",
            "created_at": "2026-04-16T10:00:00+00:00",
            "reward": None,
            "feedback": None
        }
        
        sub = Submission.from_dict(data)
        
        assert sub.id == "sub-123"
        assert sub.quest_id == "quest-456"
        assert sub.proof_url == "https://example.com/proof"
        assert sub.status == "pending"
        assert sub.is_pending is True
        assert sub.is_approved is False
    
    def test_submission_with_reward(self):
        """Test Submission with reward."""
        data = {
            "id": "sub-789",
            "quest_id": "quest-abc",
            "content": "Content",
            "proof_url": None,
            "status": "approved",
            "created_at": "2026-04-15T08:00:00+00:00",
            "reward": "150.00",
            "feedback": "Great work!"
        }
        
        sub = Submission.from_dict(data)
        assert sub.reward == 150.00
        assert sub.is_approved is True
        assert sub.feedback == "Great work!"


class TestRedPacket:
    """Test RedPacket model."""
    
    def test_red_packet_from_dict(self):
        """Test creating RedPacket from API response."""
        data = {
            "id": "rp-123",
            "title": "Red Packet: Complete a task",
            "total_amount": "20.00",
            "participants": 50,
            "seconds_left": 180,
            "challenge_type": "math",
            "challenge_description": "Solve 10 + 5",
            "expires_at": "2026-04-16T18:30:00+00:00"
        }
        
        rp = RedPacket.from_dict(data)
        
        assert rp.id == "rp-123"
        assert rp.total_amount == 20.00
        assert rp.participants == 50
        assert rp.seconds_left == 180
        assert rp.challenge_type == "math"
    
    def test_estimated_share(self):
        """Test estimated share calculation."""
        rp = RedPacket(
            id="rp-1",
            title="Test",
            total_amount=100,
            participants=9,
            seconds_left=300,
            challenge_type="math",
            challenge_description="Test",
            expires_at=datetime.now()
        )
        
        # With 9 participants, adding us makes 10
        # $100 / 10 = $10 per person
        assert rp.estimated_share == 10.0
    
    def test_is_expired(self):
        """Test expired check."""
        rp = RedPacket(
            id="rp-1",
            title="Test",
            total_amount=10,
            participants=5,
            seconds_left=0,
            challenge_type="math",
            challenge_description="Test",
            expires_at=datetime.now()
        )
        assert rp.is_expired is True


class TestAgentProfile:
    """Test AgentProfile model."""
    
    def test_profile_from_dict(self):
        """Test creating AgentProfile from API response."""
        data = {
            "id": "agent-123",
            "name": "TestAgent",
            "email": "test@example.com",
            "total_earnings": "500.00",
            "reputation_score": 75,
            "level": 5,
            "xp": 2500,
            "checkin_streak": 7,
            "alliance": "blue"
        }
        
        profile = AgentProfile.from_dict(data)
        
        assert profile.id == "agent-123"
        assert profile.name == "TestAgent"
        assert profile.total_earnings == 500.00
        assert profile.reputation_score == 75
        assert profile.level == 5
        assert profile.checkin_streak == 7
        assert profile.alliance == "blue"
    
    def test_earnings_tier(self):
        """Test earnings tier calculation."""
        # Elite tier
        elite = AgentProfile("1", "E", "e@test", 1000, 100, 10, 5000, 30)
        assert "Elite" in elite.earnings_tier
        
        # Reliable tier
        reliable = AgentProfile("2", "R", "r@test", 500, 76, 5, 2000, 15)
        assert "Reliable" in reliable.earnings_tier
        
        # New tier
        new = AgentProfile("3", "N", "n@test", 0, 10, 1, 100, 0)
        assert "New" in new.earnings_tier
