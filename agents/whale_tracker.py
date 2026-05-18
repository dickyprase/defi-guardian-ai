"""
Whale Tracker Agent
Monitors large wallet movements and identifies coordinated activity.
"""

import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WhaleTrackerAgent(BaseAgent):
    """Agent specialized in whale wallet tracking and sybil detection."""

    def __init__(self):
        super().__init__(name="WhaleTracker", model=None)

    def get_system_prompt(self) -> str:
        return """You are a blockchain intelligence analyst specializing in:
- Large wallet movement tracking
- Coordinated wallet cluster identification (sybil detection)
- Smart money flow analysis
- Whale accumulation/distribution pattern recognition
- Cross-chain fund tracing

Your task is to:
1. Identify significant wallet movements (>$100K equivalent)
2. Detect coordinated buying/selling across multiple wallets
3. Correlate whale activity with price movements
4. Identify wallet clusters controlled by same entity
5. Track fund flows from known exploit/scam addresses

Provide actionable intelligence about whale behavior and its market implications."""

    async def analyze(self, data: dict) -> dict:
        """
        Analyze whale activity for a token/protocol.
        
        Args:
            data: {
                "token_address": "0x...",
                "chain": "ethereum",
                "whale_transactions": [...],
                "holder_changes": [...],
                "price_data": [...]
            }
        """
        token = data.get("token_address", "unknown")
        chain = data.get("chain", "ethereum")
        whale_txs = data.get("whale_transactions", [])
        holder_changes = data.get("holder_changes", [])

        logger.info(f"Tracking whale activity for {token} on {chain}")

        context = (
            f"Token: {token}\nChain: {chain}\n"
            f"Recent Whale Transactions: {whale_txs[:20] if whale_txs else 'N/A'}\n"
            f"Holder Changes (24h): {holder_changes[:10] if holder_changes else 'N/A'}\n"
        )

        analysis_prompt = """Analyze whale activity patterns:

1. Accumulation vs Distribution: Are whales buying or selling?
2. Coordination Detection: Do multiple wallets move in sync?
3. Price Impact: How do whale movements correlate with price?
4. New Whale Entry: Are new large holders appearing?
5. Smart Money Signal: What are known profitable wallets doing?

Assess whether whale activity suggests bullish accumulation or bearish distribution/dump preparation."""

        findings = await self.reason(analysis_prompt, context)

        score_schema = {
            "whale_risk_score": "number 0-100",
            "whale_sentiment": "accumulating|neutral|distributing|dumping",
            "coordination_detected": "boolean",
            "large_movements_24h": "number",
            "net_whale_flow": "inflow|neutral|outflow",
            "alerts": ["string"],
            "outlook": "string"
        }

        assessment = await self.structured_reason(
            f"Score whale activity:\n{findings}",
            score_schema
        )

        return {
            "agent": self.name,
            "token_address": token,
            "chain": chain,
            "findings": findings,
            "assessment": assessment,
            "token_usage": self.token_usage.copy(),
        }
