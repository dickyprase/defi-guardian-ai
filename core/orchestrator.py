"""
Agent Orchestrator
Coordinates multi-agent analysis pipeline for DeFi risk assessment.
"""

import os
import asyncio
import logging
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv

from agents import (
    ContractAuditorAgent,
    LiquidityMonitorAgent,
    TokenEconomicsAgent,
    WhaleTrackerAgent,
    RiskReporterAgent,
)
from core.blockchain import BlockchainDataFetcher

load_dotenv()
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates multi-agent DeFi risk analysis.
    Determines which agents to activate based on the analysis target.
    """

    def __init__(self):
        self.contract_auditor = ContractAuditorAgent()
        self.liquidity_monitor = LiquidityMonitorAgent()
        self.token_economics = TokenEconomicsAgent()
        self.whale_tracker = WhaleTrackerAgent()
        self.risk_reporter = RiskReporterAgent()
        self.blockchain = BlockchainDataFetcher()

        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
        self.timeout = int(os.getenv("AGENT_TIMEOUT", "120"))

        logger.info("Agent Orchestrator initialized with all agents")

    async def analyze_token(self, address: str, chain: str = "ethereum") -> dict:
        """
        Full token analysis — activates all relevant agents.
        """
        logger.info(f"Starting full analysis for {address} on {chain}")
        start_time = datetime.utcnow()

        # Fetch blockchain data
        token_data = await self.blockchain.get_token_info(address, chain)
        pool_data = await self.blockchain.get_liquidity_pools(address, chain)
        whale_data = await self.blockchain.get_whale_activity(address, chain)

        # Run agents concurrently
        agent_tasks = []

        # Contract audit
        agent_tasks.append(self._run_agent(
            self.contract_auditor,
            {"address": address, "chain": chain, **token_data.get("contract", {})}
        ))

        # Liquidity monitoring
        if pool_data:
            agent_tasks.append(self._run_agent(
                self.liquidity_monitor,
                {"pool_address": pool_data.get("main_pool", ""), "chain": chain, **pool_data}
            ))

        # Token economics
        agent_tasks.append(self._run_agent(
            self.token_economics,
            {"token_address": address, "chain": chain, **token_data}
        ))

        # Whale tracking
        agent_tasks.append(self._run_agent(
            self.whale_tracker,
            {"token_address": address, "chain": chain, **whale_data}
        ))

        # Execute all agents with timeout
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Collect results
        agent_results = {}
        agent_names = ["contract_auditor", "liquidity_monitor", "token_economics", "whale_tracker"]

        for i, result in enumerate(results):
            name = agent_names[i] if i < len(agent_names) else f"agent_{i}"
            if isinstance(result, Exception):
                logger.error(f"Agent {name} failed: {result}")
                agent_results[name] = None
            else:
                agent_results[name] = result

        # Generate final report
        report = await self._run_agent(
            self.risk_reporter,
            {"target": address, "chain": chain, "agent_results": agent_results}
        )

        elapsed = (datetime.utcnow() - start_time).total_seconds()

        return {
            "target": address,
            "chain": chain,
            "agent_results": agent_results,
            "final_report": report,
            "metadata": {
                "analysis_time_seconds": elapsed,
                "agents_activated": len(agent_tasks),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

    async def analyze_contract(self, address: str, chain: str = "ethereum") -> dict:
        """Quick contract-only audit."""
        token_data = await self.blockchain.get_token_info(address, chain)
        return await self._run_agent(
            self.contract_auditor,
            {"address": address, "chain": chain, **token_data.get("contract", {})}
        )

    async def _run_agent(self, agent, data: dict) -> dict:
        """Run a single agent with timeout."""
        try:
            return await asyncio.wait_for(
                agent.analyze(data),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Agent {agent.name} timed out after {self.timeout}s")
            return {"error": f"Agent {agent.name} timed out", "agent": agent.name}
        except Exception as e:
            logger.error(f"Agent {agent.name} error: {e}")
            return {"error": str(e), "agent": agent.name}

    def get_all_stats(self) -> dict:
        """Get stats from all agents."""
        return {
            "contract_auditor": self.contract_auditor.get_stats(),
            "liquidity_monitor": self.liquidity_monitor.get_stats(),
            "token_economics": self.token_economics.get_stats(),
            "whale_tracker": self.whale_tracker.get_stats(),
            "risk_reporter": self.risk_reporter.get_stats(),
        }


async def main():
    """CLI entry point for running analysis."""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m core.orchestrator <token_address> [chain]")
        print("Example: python -m core.orchestrator 0x1234... ethereum")
        sys.exit(1)

    address = sys.argv[1]
    chain = sys.argv[2] if len(sys.argv) > 2 else "ethereum"

    orchestrator = AgentOrchestrator()
    result = await orchestrator.analyze_token(address, chain)

    # Print summary
    report = result.get("final_report", {})
    assessment = report.get("final_assessment", {})

    print("\n" + "=" * 60)
    print(f"  DeFi Guardian AI - Risk Report")
    print(f"  Target: {address}")
    print(f"  Chain: {chain}")
    print("=" * 60)
    print(f"\n  Risk Score: {assessment.get('overall_risk_score', 'N/A')}/100")
    print(f"  Risk Level: {assessment.get('risk_level', 'N/A')}")
    print(f"  Safe to Interact: {assessment.get('safe_to_interact', 'N/A')}")
    print(f"\n  Summary: {assessment.get('summary', 'N/A')}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
