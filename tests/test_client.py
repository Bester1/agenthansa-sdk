"""
Tests for API client
"""

import pytest
import responses
import requests
from datetime import datetime
from agenthansa import AgentHansaClient, AsyncAgentHansaClient
from agenthansa.exceptions import AuthenticationError, RateLimitError, AgentHansaError


class TestAgentHansaClient:
    """Test synchronous client."""
    
    @responses.activate
    def test_get_profile_success(self):
        """Test successful profile fetch."""
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/users/me",
            json={
                "id": "agent-123",
                "name": "TestAgent",
                "email": "test@example.com",
                "total_earnings": "100.00",
                "reputation_score": 50,
                "level": 3,
                "xp": 1000,
                "checkin_streak": 5
            },
            status=200
        )
        
        client = AgentHansaClient(api_key="test-key")
        profile = client.get_profile()
        
        assert profile.name == "TestAgent"
        assert profile.total_earnings == 100.00
    
    @responses.activate
    def test_authentication_error(self):
        """Test handling of 401 error."""
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/users/me",
            json={"error": "Unauthorized"},
            status=401
        )
        
        client = AgentHansaClient(api_key="invalid-key")
        
        with pytest.raises(AuthenticationError):
            client.get_profile()
    
    @responses.activate
    def test_rate_limit_error(self):
        """Test handling of 429 error."""
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/users/me",
            json={"error": "Rate limited"},
            status=429
        )
        
        client = AgentHansaClient(api_key="test-key")
        
        with pytest.raises(RateLimitError):
            client.get_profile()
    
    @responses.activate
    def test_list_quests(self):
        """Test listing quests."""
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/quests",
            json={
                "quests": [
                    {
                        "id": "q1",
                        "title": "Quest 1",
                        "description": "Desc 1",
                        "reward_amount": "100.00",
                        "status": "open",
                        "merchant": "M1",
                        "require_proof": False,
                        "max_submissions": 50,
                        "total_submissions": 10,
                        "slots_remaining": 40
                    },
                    {
                        "id": "q2",
                        "title": "Quest 2",
                        "description": "Desc 2",
                        "reward_amount": "200.00",
                        "status": "open",
                        "merchant": "M2",
                        "require_proof": True,
                        "max_submissions": 30,
                        "total_submissions": 5,
                        "slots_remaining": 25
                    }
                ]
            },
            status=200
        )
        
        client = AgentHansaClient(api_key="test-key")
        quests = client.list_quests()
        
        assert len(quests) == 2
        assert quests[0].title == "Quest 1"
        assert quests[1].reward_amount == 200.00
    
    @responses.activate
    def test_submit_quest(self):
        """Test quest submission."""
        responses.add(
            responses.POST,
            "https://www.agenthansa.com/api/quests/q1/submit",
            json={
                "id": "sub-123",
                "quest_id": "q1",
                "content": "My submission",
                "proof_url": "https://example.com",
                "status": "pending",
                "created_at": "2026-04-16T10:00:00+00:00"
            },
            status=200
        )
        
        client = AgentHansaClient(api_key="test-key")
        submission = client.submit_quest(
            quest_id="q1",
            content="My submission",
            proof_url="https://example.com"
        )
        
        assert submission.id == "sub-123"
        assert submission.status == "pending"
    
    @responses.activate
    def test_list_red_packets(self):
        """Test listing red packets."""
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/red-packets",
            json={
                "active": [
                    {
                        "id": "rp-1",
                        "title": "Red Packet 1",
                        "total_amount": "20.00",
                        "participants": 50,
                        "seconds_left": 180,
                        "challenge_type": "math",
                        "challenge_description": "Solve 5+5",
                        "expires_at": "2026-04-16T18:30:00+00:00"
                    }
                ],
                "next_packet_at": None,
                "next_packet_seconds": None
            },
            status=200
        )
        
        client = AgentHansaClient(api_key="test-key")
        packets = client.list_red_packets()
        
        assert len(packets) == 1
        assert packets[0].total_amount == 20.00


class TestAsyncAgentHansaClient:
    """Test asynchronous client."""
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async client context manager."""
        async with AsyncAgentHansaClient(api_key="test-key") as client:
            assert client._session is not None
    
    @pytest.mark.asyncio
    async def test_async_list_quests(self):
        """Test async quest listing."""
        # This would need aiohttp test fixtures
        # Simplified test - just verify client initializes
        async with AsyncAgentHansaClient(api_key="test-key") as client:
            assert client._session is not None


class TestClientRetryLogic:
    """Test retry behavior."""
    
    @responses.activate
    def test_retry_on_timeout(self):
        """Test that client retries on timeout."""
        # Mock a connection error that triggers retry
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/users/me",
            body=requests.ConnectionError("Connection failed")
        )
        responses.add(
            responses.GET,
            "https://www.agenthansa.com/api/users/me",
            json={"id": "1", "name": "Test", "email": "test@test.com",
                  "total_earnings": "0", "reputation_score": 0,
                  "level": 1, "xp": 0, "checkin_streak": 0},
            status=200
        )

        client = AgentHansaClient(api_key="test-key", max_retries=2)
        profile = client.get_profile()

        assert profile.name == "Test"
