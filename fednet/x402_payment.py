"""
Layer 3: HTTP 402-Gated Inference Monetization

Implements x402 payment protocol for model inference access.
Researchers and AI agents query the model by paying in USDC on Solana.
Payments are split proportionally to contributing nodes.
"""

import json
import hashlib
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


@dataclass
class PaymentRequest:
    """x402 payment request for model inference."""
    amount: Decimal  # In USDC
    model_id: str
    requester: str  # Wallet address requesting inference
    timestamp: str
    request_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": str(self.amount),
            "model_id": self.model_id,
            "requester": self.requester,
            "timestamp": self.timestamp,
            "request_hash": self.request_hash,
        }


@dataclass
class PaymentProof:
    """Proof of successful payment on Solana."""
    tx_id: str  # Solana transaction ID
    amount: Decimal
    payer: str  # Wallet that paid
    receiver: str  # Model owner / aggregator wallet
    model_id: str
    timestamp: str
    slot: int  # Solana slot number
    confirmed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "amount": str(self.amount),
            "payer": self.payer,
            "receiver": self.receiver,
            "model_id": self.model_id,
            "timestamp": self.timestamp,
            "slot": self.slot,
            "confirmed": self.confirmed,
        }


class X402PaymentProcessor:
    """
    Processes x402 payments for model inference access.
    Verifies USDC transfers on Solana and gates inference accordingly.
    """

    def __init__(
        self,
        model_id: str,
        price_per_inference: Decimal = Decimal("0.05"),  # $0.05 per inference
        receiver_wallet: Optional[str] = None,
    ):
        """
        Initialize payment processor.

        Args:
            model_id: Unique identifier for the model
            price_per_inference: USDC cost per inference
            receiver_wallet: Wallet address to receive payments
        """
        self.model_id = model_id
        self.price_per_inference = price_per_inference
        self.receiver_wallet = receiver_wallet or "FedNetAggregator111111111111111111111111111"
        self.payment_ledger: Dict[str, PaymentProof] = {}

    def create_payment_request(
        self,
        requester_wallet: str,
        amount: Optional[Decimal] = None,
    ) -> PaymentRequest:
        """
        Create a payment request for model inference.

        Args:
            requester_wallet: Wallet address of the requester
            amount: Amount in USDC (defaults to price_per_inference)

        Returns:
            PaymentRequest instance
        """
        if amount is None:
            amount = self.price_per_inference

        request = PaymentRequest(
            amount=amount,
            model_id=self.model_id,
            requester=requester_wallet,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_hash="",
        )

        # Create deterministic hash of request
        request_json = json.dumps(
            {
                "amount": str(amount),
                "model_id": self.model_id,
                "requester": requester_wallet,
                "timestamp": request.timestamp,
            },
            sort_keys=True,
        )
        request.request_hash = hashlib.sha256(request_json.encode()).hexdigest()

        return request

    def verify_payment(
        self,
        tx_id: str,
        payer_wallet: str,
        amount: Decimal,
    ) -> bool:
        """
        Verify a payment on Solana.

        Args:
            tx_id: Solana transaction ID
            payer_wallet: Wallet that initiated the payment
            amount: Amount transferred (in USDC)

        Returns:
            True if payment is valid and sufficient
        """
        # In production: Query Solana RPC to verify transaction
        # For MVP: Accept payment if amount >= price_per_inference
        return amount >= self.price_per_inference

    def record_payment(
        self,
        tx_id: str,
        payer_wallet: str,
        amount: Decimal,
        slot: int,
    ) -> PaymentProof:
        """
        Record a verified payment.

        Args:
            tx_id: Solana transaction ID
            payer_wallet: Wallet that paid
            amount: Amount in USDC
            slot: Solana slot number

        Returns:
            PaymentProof instance
        """
        proof = PaymentProof(
            tx_id=tx_id,
            amount=amount,
            payer=payer_wallet,
            receiver=self.receiver_wallet,
            model_id=self.model_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            slot=slot,
            confirmed=True,
        )

        self.payment_ledger[tx_id] = proof
        return proof

    def get_payment_proof(self, tx_id: str) -> Optional[PaymentProof]:
        """Get recorded payment proof."""
        return self.payment_ledger.get(tx_id)

    def get_payment_history(self) -> List[PaymentProof]:
        """Get all recorded payments."""
        return list(self.payment_ledger.values())

    def get_total_revenue(self) -> Decimal:
        """Calculate total revenue from inference payments."""
        return sum(
            proof.amount for proof in self.payment_ledger.values()
        )

    def calculate_node_payout(
        self,
        node_contribution_score: Decimal,  # 0.0 to 1.0
        total_amount: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Calculate payout for a node based on contribution.

        Args:
            node_contribution_score: Node's relative contribution (0.0 to 1.0)
            total_amount: Total amount to distribute (defaults to total revenue)

        Returns:
            Amount to distribute to this node
        """
        if total_amount is None:
            total_amount = self.get_total_revenue()

        # Split proportionally to contribution
        # Contribution score should be based on:
        # - Being online during training round
        # - Completing the training job
        # - Passing gradient schema validation
        # - Submitting accepted encrypted update

        return total_amount * node_contribution_score


class MockX402PaymentProcessor(X402PaymentProcessor):
    """
    Mock payment processor for testing without Solana RPC.
    Simulates payment verification and recording.
    """

    def __init__(
        self,
        model_id: str,
        price_per_inference: Decimal = Decimal("0.05"),
        receiver_wallet: Optional[str] = None,
    ):
        super().__init__(model_id, price_per_inference, receiver_wallet)
        self.verified_payments: Dict[str, bool] = {}

    def verify_payment(
        self,
        tx_id: str,
        payer_wallet: str,
        amount: Decimal,
    ) -> bool:
        """Simulate payment verification."""
        # For mock: accept any payment >= price_per_inference
        is_valid = amount >= self.price_per_inference
        self.verified_payments[tx_id] = is_valid
        return is_valid

    def record_payment(
        self,
        tx_id: str,
        payer_wallet: str,
        amount: Decimal,
        slot: int = 12345,
    ) -> PaymentProof:
        """Record mock payment."""
        return super().record_payment(tx_id, payer_wallet, amount, slot)


def create_payment_processor(
    model_id: str,
    use_mock: bool = False,
    price_per_inference: Decimal = Decimal("0.05"),
    receiver_wallet: Optional[str] = None,
) -> X402PaymentProcessor:
    """
    Factory function to create a payment processor.

    Args:
        model_id: Model identifier
        use_mock: Use mock processor for testing
        price_per_inference: Cost per inference in USDC
        receiver_wallet: Receiver wallet address

    Returns:
        X402PaymentProcessor or MockX402PaymentProcessor instance
    """
    if use_mock:
        return MockX402PaymentProcessor(
            model_id,
            price_per_inference,
            receiver_wallet,
        )

    return X402PaymentProcessor(
        model_id,
        price_per_inference,
        receiver_wallet,
    )
