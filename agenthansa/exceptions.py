"""
Custom exceptions for AgentHansa SDK
"""


class AgentHansaError(Exception):
    """Base exception for AgentHansa SDK."""
    pass


class AuthenticationError(AgentHansaError):
    """Raised when API authentication fails."""
    pass


class RateLimitError(AgentHansaError):
    """Raised when API rate limit is exceeded."""
    pass


class QuestNotFoundError(AgentHansaError):
    """Raised when a quest is not found."""
    pass


class SubmissionError(AgentHansaError):
    """Raised when quest submission fails."""
    pass


class RedPacketError(AgentHansaError):
    """Raised when red packet operation fails."""
    pass
