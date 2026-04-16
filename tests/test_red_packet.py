"""
Tests for red packet utilities
"""

import pytest
from datetime import datetime
from agenthansa.red_packet import RedPacketCollector, RedPacketResult
from agenthansa.models import RedPacket


class TestRedPacketCollector:
    """Test RedPacketCollector."""
    
    def test_solve_challenge_split(self):
        """Test solving 'split among' challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "18 badges split among 3 robots = ?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "6"
    
    def test_solve_challenge_addition(self):
        """Test solving addition challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "What is 15 + 27?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "42"
    
    def test_solve_challenge_subtraction(self):
        """Test solving subtraction challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "What is 100 - 35?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "65"
    
    def test_solve_challenge_multiplication(self):
        """Test solving multiplication challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "What is 8 * 7?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "56"
    
    def test_solve_challenge_division(self):
        """Test solving division challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "What is 100 / 4?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "25"
    
    def test_solve_challenge_divided_by(self):
        """Test solving 'divided by' challenge."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "50 divided by 5 equals?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "10"
    
    def test_solve_challenge_no_numbers(self):
        """Test handling challenge with no numbers."""
        collector = RedPacketCollector(api_key="test")
        
        challenge = {"question": "What is the answer?"}
        answer = collector._solve_challenge(challenge)
        assert answer == "0"


class TestRedPacketResult:
    """Test RedPacketResult dataclass."""
    
    def test_result_joined(self):
        """Test successful join result."""
        result = RedPacketResult(
            joined=True,
            packet_id="rp-123",
            estimated_share=0.35,
            message="Successfully joined!"
        )
        
        assert result.joined is True
        assert result.packet_id == "rp-123"
        assert result.estimated_share == 0.35
    
    def test_result_not_joined(self):
        """Test failed join result."""
        result = RedPacketResult(
            joined=False,
            next_packet_minutes=120,
            message="No active packets"
        )
        
        assert result.joined is False
        assert result.next_packet_minutes == 120
        assert result.packet_id is None


class TestRedPacketModel:
    """Test RedPacket model calculations."""
    
    def test_estimated_share_calculation(self):
        """Test share calculation with different participant counts."""
        # $100 with 9 participants, adding us makes 10
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
        assert rp.estimated_share == 10.0
        
        # $20 with 4 participants, adding us makes 5
        rp2 = RedPacket(
            id="rp-2",
            title="Test",
            total_amount=20,
            participants=4,
            seconds_left=300,
            challenge_type="math",
            challenge_description="Test",
            expires_at=datetime.now()
        )
        assert rp2.estimated_share == 4.0
    
    def test_estimated_share_zero_participants(self):
        """Test share calculation with no participants."""
        rp = RedPacket(
            id="rp-1",
            title="Test",
            total_amount=50,
            participants=0,
            seconds_left=300,
            challenge_type="math",
            challenge_description="Test",
            expires_at=datetime.now()
        )
        # If we're first, we get it all (but realistically split happens)
        assert rp.estimated_share == 50.0
    
    def test_is_expired_true(self):
        """Test expired detection."""
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
    
    def test_is_expired_false(self):
        """Test non-expired detection."""
        rp = RedPacket(
            id="rp-1",
            title="Test",
            total_amount=10,
            participants=5,
            seconds_left=300,
            challenge_type="math",
            challenge_description="Test",
            expires_at=datetime.now()
        )
        assert rp.is_expired is False
