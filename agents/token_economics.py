"""
Token Economics Agent
Analyzes tokenomics for manipulation patterns and sustainability.
"""

import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TokenEconomicsAgent(BaseAgent):
    """Agent specialized in token economics analysis."""

    def __init__(self):
        super().__init__(name="TokenEconomics", model=None)

    def get_system_prompt(self) -> str:
        return """You are a tokenomics expert specializing in:
- Token supply distribution analysis
- Vesting schedule evaluation
- Inflation/deflation mechanism assessment
- Honeypot token detection
- Tax/fee mechanism analysis
- Mint/burn function risk assessment

Your task is to analyze token economics and identify:
1. Unfair distribution (team/insider allocation >30%)
2. Hidden inflation mechanisms (unlimited mint)
3. Honeypot patterns (can buy but cannot sell)
4. Excessive transaction taxes (>10%)
5. Manipulative fee structures
6. Centralized control over token parameters

Provide quantitative analysis with specific numbers and percentages."""

    async def analyze(self, data: dict) -> dict:
        """
        Analyze token economics.
        
        Args:
            data: {
                "token_address": "0x...",
                "chain": "ethereum",
                "name": "TokenName",
                "symbol": "TKN",
                "total_supply": 1000000000,
                "holders": [...],
                "transfer_tax": {...},
                "contract_features": [...]
            }
        """
        token = data.get("token_address", "unknown")
        chain = data.get("chain", "ethereum")
        name = data.get("name", "Unknown")
        symbol = data.get("symbol", "???")
        total_supply = data.get("total_supply", 0)
        holders = data.get("holders", [])
        tax = data.get("transfer_tax", {})

        logger.info(f"Analyzing tokenomics for {name} ({symbol}) on {chain}")

        context = (
            f"Token: {name} ({symbol})\nAddress: {token}\nChain: {chain}\n"
            f"Total Supply: {total_supply:,}\n"
            f"Top Holders: {holders[:10] if holders else 'N/A'}\n"
            f"Transfer Tax: Buy {tax.get('buy', '?')}% / Sell {tax.get('sell', '?')}%\n"
            f"Contract Features: {data.get('contract_features', [])}\n"
        )

        analysis_prompt = """Perform comprehensive tokenomics analysis:

1. Supply Distribution: How concentrated is token ownership?
2. Tax Analysis: Are buy/sell taxes reasonable? Can they be changed?
3. Mint Function: Can new tokens be minted? By whom?
4. Honeypot Check: Can holders freely sell their tokens?
5. Vesting/Lock: Are team tokens locked? For how long?
6. Sustainability: Is the token model economically viable?

Identify any red flags that suggest this token is designed to extract value from buyers."""

        findings = await self.reason(analysis_prompt, context)

        score_schema = {
            "tokenomics_score": "number 0-100 (100=safe)",
            "honeypot_probability": "number 0-100",
            "distribution_fairness": "number 0-100",
            "tax_risk": "low|medium|high|critical",
            "mint_risk": "none|low|medium|high|critical",
            "red_flags": ["string"],
            "verdict": "safe|caution|warning|danger|scam"
        }

        assessment = await self.structured_reason(
            f"Score this token based on analysis:\n{findings}",
            score_schema
        )

        return {
            "agent": self.name,
            "token_address": token,
            "chain": chain,
            "name": name,
            "symbol": symbol,
            "findings": findings,
            "assessment": assessment,
            "token_usage": self.token_usage.copy(),
        }
