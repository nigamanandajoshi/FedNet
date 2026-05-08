"""Ledger for tracking federated-learning updates.

This repo supports two modes:
- `local` (default): an append-only hash-chained JSON ledger (hackathon-friendly, zero infra).
- `ethereum`: records to the MedChainLedger smart contract via `EthereumClient`.
"""

from __future__ import annotations

import json
import hashlib
import time
from typing import List, Dict, Optional, Any
from config.logging_config import get_logger
from blockchain.ethereum_client import EthereumClient

logger = get_logger(__name__)


class BlockchainLedger:
    """A minimal ledger for FL auditability (local or Ethereum)."""
    
    def __init__(
        self,
        backend: str = "local",
        eth_client: Optional[EthereumClient] = None,
        contract_address: Optional[str] = None,
        abi_path: Optional[str] = None,
        admin_private_key: Optional[str] = None,
    ):
        self.backend = backend

        # Local ledger state
        self.chain: List[Dict[str, Any]] = []

        # Ethereum state (optional)
        self.eth = eth_client
        self.contract = None
        self.admin_pk = admin_private_key

        if backend == "ethereum":
            if eth_client is None or contract_address is None or abi_path is None or admin_private_key is None:
                raise ValueError("Ethereum backend requires eth_client, contract_address, abi_path, admin_private_key")
            self.contract = self.eth.load_contract(contract_address, abi_path)
            logger.info(f"Initialized Ethereum smart-contract ledger at {contract_address}")
        else:
            self._init_genesis()
            logger.info("Initialized local hash-chained ledger")

    def _init_genesis(self) -> None:
        if self.chain:
            return
        genesis = {
            "index": 0,
            "type": "genesis",
            "ts": int(time.time()),
            "payload": {},
            "prev_hash": "0" * 64,
        }
        genesis["hash"] = self._hash_block(genesis)
        self.chain.append(genesis)

    @staticmethod
    def _hash_block(block: Dict[str, Any]) -> str:
        material = json.dumps(
            {k: v for k, v in block.items() if k != "hash"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(material).hexdigest()

    def _append_local(self, block_type: str, payload: Dict[str, Any]) -> str:
        self._init_genesis()
        prev_hash = self.chain[-1]["hash"]
        block = {
            "index": len(self.chain),
            "type": block_type,
            "ts": int(time.time()),
            "payload": payload,
            "prev_hash": prev_hash,
        }
        block["hash"] = self._hash_block(block)
        self.chain.append(block)
        return block["hash"]
    
    def record_fl_round(
        self,
        round_number: int,
        num_clients: int,
        global_metrics: Dict,
        model_hash: Optional[str] = None
    ) -> bool:
        """
        Record a federated learning round on the blockchain.
        
        Args:
            round_number: FL round number
            num_clients: Number of participating clients
            global_metrics: Aggregated metrics
            model_hash: Hash of global model weights
            
        Returns:
            True if recorded successfully
        """
        if self.backend == "ethereum":
            metrics_json = json.dumps(global_metrics)
            model_hash_str = model_hash if model_hash else ""
            try:
                receipt = self.eth.send_transaction(
                    self.contract,
                    "recordFLRound",
                    self.admin_pk,
                    round_number,
                    num_clients,
                    metrics_json,
                    model_hash_str,
                )
                logger.info(f"Recorded FL round {round_number} on-chain in tx {receipt['transactionHash'].hex()}")
                return True
            except Exception as e:
                logger.error(f"Failed to record FL round {round_number}: {str(e)}")
                return False

        # Local
        block_hash = self._append_local(
            "fl_round",
            {
                "round_number": round_number,
                "num_clients": num_clients,
                "global_metrics": global_metrics,
                "model_hash": model_hash or "",
            },
        )
        logger.info(f"Recorded FL round {round_number} in local ledger: {block_hash[:12]}…")
        return True
    
    def record_client_update(
        self,
        round_number: int,
        client_private_key: str,
        data_size: int,
        metrics: Dict
    ) -> bool:
        """
        Record a client update. Client signs this transaction themselves.
        
        Args:
            round_number: FL round number
            client_private_key: The Ethereum private key of the client sending the update
            data_size: Client dataset size
            metrics: Client metrics
            
        Returns:
            True if successful
        """
        if self.backend == "ethereum":
            metrics_json = json.dumps(metrics)
            try:
                receipt = self.eth.send_transaction(
                    self.contract,
                    "recordClientUpdate",
                    client_private_key,
                    round_number,
                    data_size,
                    metrics_json,
                )
                logger.info(f"Client recorded update for round {round_number} in tx {receipt['transactionHash'].hex()}")
                return True
            except Exception as e:
                logger.error(f"Client failed to record update: {str(e)}")
                return False

        # Local: treat `client_private_key` as an opaque client identifier.
        block_hash = self._append_local(
            "client_update",
            {
                "round_number": round_number,
                "client_id": client_private_key,
                "data_size": data_size,
                "metrics": metrics,
            },
        )
        logger.info(f"Recorded client update for round {round_number} in local ledger: {block_hash[:12]}…")
        return True
            
    def get_fl_rounds(self) -> List[Dict]:
        """Get all FL round records from blockchain.
        This iterates from 1 to latestRound property on the contract.
        """
        if self.backend != "ethereum":
            rounds: List[Dict[str, Any]] = []
            for b in self.chain:
                if b["type"] != "fl_round":
                    continue
                p = b["payload"]
                rounds.append(
                    {
                        "round": p["round_number"],
                        "num_clients": p["num_clients"],
                        "metrics": p["global_metrics"],
                        "model_hash": p.get("model_hash", ""),
                        "timestamp": b["ts"],
                        "hash": b["hash"],
                    }
                )
            return rounds

        rounds = []
        try:
            latest_round = self.eth.call_view_function(self.contract, 'latestRound')
            for i in range(1, latest_round + 1):
                round_data = self.eth.call_view_function(self.contract, 'flRounds', i)
                # Ensure the round exists (struct uninitialized value check)
                if round_data[0] != 0: 
                    rounds.append({
                        "round": round_data[0],
                        "num_clients": round_data[1],
                        "metrics": json.loads(round_data[2]) if round_data[2] else {},
                        "model_hash": round_data[3],
                        "timestamp": round_data[4]
                    })
        except Exception as e:
            logger.error(f"Failed to fetch FL rounds: {str(e)}")
            
        return rounds

    def get_client_updates(self, round_number: int) -> List[Dict]:
        """Get client updates for a specific round."""
        if self.backend != "ethereum":
            updates: List[Dict[str, Any]] = []
            for b in self.chain:
                if b["type"] != "client_update":
                    continue
                p = b["payload"]
                if p.get("round_number") != round_number:
                    continue
                updates.append(
                    {
                        "client_id": p.get("client_id"),
                        "round": p.get("round_number"),
                        "data_size": p.get("data_size"),
                        "metrics": p.get("metrics") or {},
                        "timestamp": b["ts"],
                        "hash": b["hash"],
                    }
                )
            return updates

        updates = []
        try:
            updates_data = self.eth.call_view_function(self.contract, 'getClientUpdates', round_number)
            for update in updates_data:
                updates.append({
                    "client_address": update[0],
                    "round": update[1],
                    "data_size": update[2],
                    "metrics": json.loads(update[3]) if update[3] else {},
                    "timestamp": update[4]
                })
        except Exception as e:
            logger.error(f"Failed to fetch client updates for round {round_number}: {str(e)}")
            
        return updates

    def is_valid(self) -> bool:
        """Validate local hash chain integrity (always True for Ethereum backend)."""
        if self.backend == "ethereum":
            return True
        if not self.chain:
            return True
        for i, b in enumerate(self.chain):
            expected = self._hash_block(b)
            if b.get("hash") != expected:
                return False
            if i == 0:
                if b.get("prev_hash") != "0" * 64:
                    return False
            else:
                if b.get("prev_hash") != self.chain[i - 1].get("hash"):
                    return False
        return True

    def save_to_file(self, path: str) -> None:
        """Save local ledger as JSON (no-op for Ethereum backend)."""
        if self.backend == "ethereum":
            logger.warning("save_to_file is a no-op for Ethereum backend (data already on-chain)")
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"backend": "local", "chain": self.chain}, f, indent=2)
