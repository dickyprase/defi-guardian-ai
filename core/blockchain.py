"""
Blockchain Data Fetcher
Multi-chain data retrieval for DeFi analysis.
"""

import os
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

CHAIN_CONFIG = {
    "ethereum": {
        "rpc": os.getenv("ETH_RPC_URL", "https://eth-mainnet.g.alchemy.com/v2/demo"),
        "explorer_api": "https://api.etherscan.io/api",
        "explorer_key": os.getenv("ETHERSCAN_API_KEY", ""),
        "chain_id": 1,
    },
    "bsc": {
        "rpc": os.getenv("BSC_RPC_URL", "https://bsc-dataseed1.binance.org"),
        "explorer_api": "https://api.bscscan.com/api",
        "explorer_key": os.getenv("BSCSCAN_API_KEY", ""),
        "chain_id": 56,
    },
    "polygon": {
        "rpc": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        "explorer_api": "https://api.polygonscan.com/api",
        "explorer_key": os.getenv("POLYGONSCAN_API_KEY", ""),
        "chain_id": 137,
    },
    "arbitrum": {
        "rpc": os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
        "explorer_api": "https://api.arbiscan.io/api",
        "explorer_key": os.getenv("ARBISCAN_API_KEY", ""),
        "chain_id": 42161,
    },
}


class BlockchainDataFetcher:
    """Fetches on-chain data from multiple blockchains."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self.session

    async def get_token_info(self, address: str, chain: str = "ethereum") -> dict:
        """Get token information including contract details."""
        config = CHAIN_CONFIG.get(chain, CHAIN_CONFIG["ethereum"])
        session = await self._get_session()

        try:
            # Get contract source code
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": config["explorer_key"],
            }
            async with session.get(config["explorer_api"], params=params) as resp:
                data = await resp.json()
                contract_info = data.get("result", [{}])[0] if data.get("status") == "1" else {}

            # Get token info
            params = {
                "module": "token",
                "action": "tokeninfo",
                "contractaddress": address,
                "apikey": config["explorer_key"],
            }
            async with session.get(config["explorer_api"], params=params) as resp:
                data = await resp.json()
                token_info = data.get("result", [{}])[0] if data.get("status") == "1" else {}

            return {
                "name": token_info.get("tokenName", contract_info.get("ContractName", "")),
                "symbol": token_info.get("symbol", ""),
                "total_supply": int(token_info.get("totalSupply", "0")) if token_info.get("totalSupply") else 0,
                "contract": {
                    "source_code": contract_info.get("SourceCode", ""),
                    "abi": contract_info.get("ABI", ""),
                    "compiler": contract_info.get("CompilerVersion", ""),
                    "verified": contract_info.get("ABI") != "Contract source code not verified",
                },
            }
        except Exception as e:
            logger.error(f"Failed to fetch token info for {address}: {e}")
            return {"name": "", "symbol": "", "total_supply": 0, "contract": {}}

    async def get_liquidity_pools(self, token_address: str, chain: str = "ethereum") -> dict:
        """Get liquidity pool data from DeFiLlama."""
        session = await self._get_session()

        try:
            url = f"https://api.llama.fi/protocol/{token_address}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "tvl_history": data.get("tvl", [])[-30:],
                        "chain_tvls": data.get("chainTvls", {}),
                    }
        except Exception as e:
            logger.warning(f"DeFiLlama fetch failed: {e}")

        return {}

    async def get_whale_activity(self, token_address: str, chain: str = "ethereum") -> dict:
        """Get large holder transactions."""
        config = CHAIN_CONFIG.get(chain, CHAIN_CONFIG["ethereum"])
        session = await self._get_session()

        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": token_address,
                "sort": "desc",
                "page": "1",
                "offset": "100",
                "apikey": config["explorer_key"],
            }
            async with session.get(config["explorer_api"], params=params) as resp:
                data = await resp.json()
                transactions = data.get("result", []) if data.get("status") == "1" else []

            # Filter whale transactions (top 10% by value)
            if transactions:
                values = [int(tx.get("value", "0")) for tx in transactions if tx.get("value")]
                if values:
                    threshold = sorted(values, reverse=True)[len(values) // 10] if len(values) > 10 else 0
                    whale_txs = [tx for tx in transactions if int(tx.get("value", "0")) >= threshold]
                    return {"whale_transactions": whale_txs[:20]}

        except Exception as e:
            logger.error(f"Whale activity fetch failed: {e}")

        return {"whale_transactions": []}

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
