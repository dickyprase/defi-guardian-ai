"""
Contract Auditor Agent
Analyzes smart contracts for vulnerabilities, backdoors, and rug pull patterns.
"""

import logging
from typing import Any

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

VULNERABILITY_PATTERNS = [
    "reentrancy",
    "integer_overflow",
    "unchecked_external_call",
    "tx_origin_auth",
    "delegatecall_injection",
    "selfdestruct_exposure",
    "hidden_mint_function",
    "ownership_manipulation",
    "fee_manipulation",
    "blacklist_function",
    "proxy_upgrade_backdoor",
    "flash_loan_vulnerability",
]


class ContractAuditorAgent(BaseAgent):
    """Agent specialized in smart contract security analysis."""

    def __init__(self):
        super().__init__(name="ContractAuditor", model=None)

    def get_system_prompt(self) -> str:
        return """You are an expert smart contract security auditor with deep knowledge of:
- Solidity/Vyper vulnerability patterns
- EVM bytecode analysis
- DeFi protocol attack vectors
- Rug pull detection techniques
- Proxy pattern security implications

Your task is to analyze smart contracts and identify:
1. Critical vulnerabilities (can lead to fund loss)
2. High-risk patterns (potential for exploitation)
3. Suspicious functions (hidden backdoors, owner privileges)
4. Rug pull indicators (mint functions, fee manipulation, blacklists)

For each finding, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO
- Category: vulnerability type
- Location: function or code section
- Description: clear explanation
- Impact: potential consequences
- Recommendation: how to mitigate

Use long-chain reasoning to trace execution paths and identify complex multi-step attack vectors."""

    async def analyze(self, data: dict) -> dict:
        """
        Analyze a smart contract.
        
        Args:
            data: {
                "address": "0x...",
                "chain": "ethereum",
                "source_code": "...",  # optional
                "bytecode": "...",     # optional
                "abi": [...]           # optional
            }
        """
        address = data.get("address", "unknown")
        chain = data.get("chain", "ethereum")
        source_code = data.get("source_code", "")
        abi = data.get("abi", [])

        logger.info(f"Auditing contract {address} on {chain}")

        # Phase 1: Initial scan
        context = f"Contract Address: {address}\nChain: {chain}\n"
        if source_code:
            context += f"\nSource Code:\n```solidity\n{source_code[:8000]}\n```"
        if abi:
            context += f"\nABI Functions: {[f.get('name') for f in abi if f.get('type') == 'function']}"

        # Phase 2: Deep analysis with MiMo reasoning
        analysis_prompt = f"""Perform a comprehensive security audit of this smart contract.

Analyze for ALL of these vulnerability categories:
{', '.join(VULNERABILITY_PATTERNS)}

For each issue found, assess:
1. Can this be exploited to drain funds?
2. Does the owner have excessive privileges?
3. Are there hidden functions that could rug users?
4. Is the contract upgradeable in a dangerous way?

Provide your findings as a structured security report."""

        findings_raw = await self.reason(analysis_prompt, context)

        # Phase 3: Risk scoring
        score_schema = {
            "risk_score": "number 0-100",
            "severity_breakdown": {
                "critical": "count",
                "high": "count",
                "medium": "count",
                "low": "count"
            },
            "rug_pull_probability": "number 0-100",
            "top_risks": ["string"],
            "recommendation": "string",
            "safe_to_interact": "boolean"
        }

        risk_assessment = await self.structured_reason(
            f"Based on this audit, provide a risk score:\n\n{findings_raw}",
            score_schema
        )

        return {
            "agent": self.name,
            "address": address,
            "chain": chain,
            "findings": findings_raw,
            "risk_assessment": risk_assessment,
            "token_usage": self.token_usage.copy(),
        }
