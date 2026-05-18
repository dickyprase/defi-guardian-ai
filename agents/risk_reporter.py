"""
Risk Reporter Agent
Aggregates findings from all agents and generates comprehensive risk reports.
"""

import logging
from datetime import datetime
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RiskReporterAgent(BaseAgent):
    """Agent that aggregates multi-agent findings into actionable risk reports."""

    def __init__(self):
        super().__init__(name="RiskReporter", model=None)

    def get_system_prompt(self) -> str:
        return """You are a DeFi risk assessment specialist who synthesizes findings from multiple 
security agents into comprehensive, actionable reports.

Your role:
1. Aggregate findings from Contract Auditor, Liquidity Monitor, Token Economics, and Whale Tracker
2. Identify correlations between different risk signals
3. Calculate an overall risk score (0-100, where 100 = maximum risk)
4. Prioritize findings by severity and immediacy
5. Generate clear, actionable recommendations

Your reports should be:
- Concise but comprehensive
- Prioritized by risk severity
- Actionable (specific steps users should take)
- Calibrated (avoid false alarms, but never miss critical risks)

Risk Score Guidelines:
0-20: Low risk - Generally safe to interact
21-40: Moderate risk - Proceed with caution
41-60: Elevated risk - Significant concerns identified
61-80: High risk - Strong indicators of potential loss
81-100: Critical risk - Likely scam/exploit, avoid interaction"""

    async def analyze(self, data: dict) -> dict:
        """
        Generate comprehensive risk report from multi-agent findings.
        
        Args:
            data: {
                "target": "0x... or protocol name",
                "chain": "ethereum",
                "agent_results": {
                    "contract_auditor": {...},
                    "liquidity_monitor": {...},
                    "token_economics": {...},
                    "whale_tracker": {...}
                }
            }
        """
        target = data.get("target", "unknown")
        chain = data.get("chain", "ethereum")
        agent_results = data.get("agent_results", {})

        logger.info(f"Generating risk report for {target} on {chain}")

        # Compile all findings
        context_parts = [f"Target: {target}\nChain: {chain}\nTimestamp: {datetime.utcnow().isoformat()}\n"]

        for agent_name, result in agent_results.items():
            if result:
                findings = result.get("findings", "No findings")
                assessment = result.get("assessment", {})
                context_parts.append(
                    f"\n--- {agent_name.upper()} FINDINGS ---\n"
                    f"Assessment: {assessment}\n"
                    f"Details: {findings[:2000]}\n"
                )

        context = "\n".join(context_parts)

        report_prompt = """Generate a comprehensive risk report by:

1. Synthesizing all agent findings into a unified risk assessment
2. Identifying correlations (e.g., high contract risk + whale dumping = imminent rug)
3. Calculating overall risk score considering all factors
4. Listing top 5 risks in priority order
5. Providing specific actionable recommendations

Format as a professional security report suitable for DeFi investors."""

        report = await self.reason(report_prompt, context)

        score_schema = {
            "overall_risk_score": "number 0-100",
            "risk_level": "LOW|MODERATE|ELEVATED|HIGH|CRITICAL",
            "confidence": "number 0-100",
            "top_risks": [
                {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "description": "string"}
            ],
            "recommendations": ["string"],
            "safe_to_interact": "boolean",
            "summary": "string (one paragraph)"
        }

        final_assessment = await self.structured_reason(
            f"Provide final structured assessment:\n{report}",
            score_schema
        )

        return {
            "agent": self.name,
            "target": target,
            "chain": chain,
            "report": report,
            "final_assessment": final_assessment,
            "generated_at": datetime.utcnow().isoformat(),
            "token_usage": self.token_usage.copy(),
        }
