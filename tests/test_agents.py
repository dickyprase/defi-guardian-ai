"""
Unit tests for DeFi Guardian AI agents.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from agents.base_agent import BaseAgent
from agents.contract_auditor import ContractAuditorAgent
from agents.token_economics import TokenEconomicsAgent


class TestBaseAgent:
    """Test base agent functionality."""

    def test_agent_initialization(self):
        """Test that agents initialize correctly."""
        agent = ContractAuditorAgent()
        assert agent.name == "ContractAuditor"
        assert agent.model is not None
        assert agent.token_usage == {"input": 0, "output": 0}

    def test_get_stats(self):
        """Test stats reporting."""
        agent = ContractAuditorAgent()
        stats = agent.get_stats()
        assert "name" in stats
        assert "model" in stats
        assert "token_usage" in stats
        assert stats["total_tokens"] == 0


class TestContractAuditor:
    """Test Contract Auditor Agent."""

    def test_system_prompt(self):
        """Test system prompt contains key terms."""
        agent = ContractAuditorAgent()
        prompt = agent.get_system_prompt()
        assert "vulnerability" in prompt.lower()
        assert "rug pull" in prompt.lower()
        assert "severity" in prompt.lower()


class TestTokenEconomics:
    """Test Token Economics Agent."""

    def test_system_prompt(self):
        """Test system prompt contains key terms."""
        agent = TokenEconomicsAgent()
        prompt = agent.get_system_prompt()
        assert "honeypot" in prompt.lower()
        assert "tokenomics" in prompt.lower()
        assert "mint" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
