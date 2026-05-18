"""
Liquidity Monitor Agent
Real-time monitoring of DEX liquidity pools for rug pull detection.
"""

import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LiquidityMonitorAgent(BaseAgent):
    """Agent specialized in liquidity pool monitoring and rug pull detection."""

    def __init__(self):
        super().__init__(name="LiquidityMonitor", model=None)

    def get_system_prompt(self) -> str:
        return """You are a DeFi liquidity analysis expert specializing in:
- DEX liquidity pool mechanics (Uniswap V2/V3, PancakeSwap, etc.)
- Liquidity removal pattern detection
- LP token concentration analysis
- TVL anomaly detection
- Impermanent loss calculation

Your task is to monitor liquidity pools and detect:
1. Sudden large liquidity removals (>10% in single tx)
2. LP token holder concentration (whale dominance)
3. Abnormal TVL fluctuations without corresponding volume
4. Locked vs unlocked liquidity ratios
5. Time-locked liquidity approaching unlock dates

Flag any pattern that suggests imminent rug pull or liquidity manipulation.
Use reasoning to correlate multiple signals into a confidence score."""

    async def analyze(self, data: dict) -> dict:
        """
        Analyze liquidity pool health.
        
        Args:
            data: {
                "pool_address": "0x...",
                "chain": "ethereum",
                "token_pair": ["TOKEN", "WETH"],
                "tvl_history": [...],
                "lp_holders": [...],
                "recent_events": [...]
            }
        """
        pool = data.get("pool_address", "unknown")
        chain = data.get("chain", "ethereum")
        token_pair = data.get("token_pair", [])
        tvl_history = data.get("tvl_history", [])
        lp_holders = data.get("lp_holders", [])

        logger.info(f"Monitoring pool {pool} ({'/'.join(token_pair)}) on {chain}")

        context = (
            f"Pool: {pool}\nChain: {chain}\nPair: {'/'.join(token_pair)}\n"
            f"TVL History (last 7d): {tvl_history[-7:] if tvl_history else 'N/A'}\n"
            f"Top LP Holders: {lp_holders[:10] if lp_holders else 'N/A'}\n"
        )

        analysis_prompt = """Analyze this liquidity pool for risk indicators:

1. TVL Stability: Is the TVL declining abnormally?
2. LP Concentration: Do top holders control >50% of LP tokens?
3. Liquidity Lock Status: Is liquidity locked? When does it unlock?
4. Recent Large Removals: Any suspicious withdrawal patterns?
5. Volume/TVL Ratio: Is trading volume consistent with TVL?

Provide a rug pull risk assessment with confidence level."""

        findings = await self.reason(analysis_prompt, context)

        score_schema = {
            "liquidity_risk_score": "number 0-100",
            "rug_pull_probability": "number 0-100",
            "tvl_trend": "increasing|stable|declining|critical",
            "lp_concentration": "low|medium|high|critical",
            "liquidity_locked_pct": "number 0-100",
            "alerts": ["string"],
            "recommendation": "string"
        }

        assessment = await self.structured_reason(
            f"Score this pool based on analysis:\n{findings}",
            score_schema
        )

        return {
            "agent": self.name,
            "pool_address": pool,
            "chain": chain,
            "token_pair": token_pair,
            "findings": findings,
            "assessment": assessment,
            "token_usage": self.token_usage.copy(),
        }
