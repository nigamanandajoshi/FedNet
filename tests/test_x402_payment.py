"""Tests for x402 payment processing."""

import pytest
from decimal import Decimal
from fednet.x402_payment import (
    create_payment_processor,
    X402PaymentProcessor,
    MockX402PaymentProcessor,
    PaymentRequest,
    PaymentProof,
)


class TestPaymentRequest:
    """Test PaymentRequest dataclass."""

    def test_create_payment_request(self):
        """Test creating a payment request."""
        processor = MockX402PaymentProcessor("test_model")
        request = processor.create_payment_request("0xuser123")

        assert request.model_id == "test_model"
        assert request.requester == "0xuser123"
        assert request.amount == Decimal("0.05")
        assert request.request_hash != ""


class TestPaymentProof:
    """Test PaymentProof dataclass."""

    def test_create_payment_proof(self):
        """Test creating a payment proof."""
        proof = PaymentProof(
            tx_id="mock_tx_123",
            amount=Decimal("0.05"),
            payer="0xpayer",
            receiver="0xreceiver",
            model_id="model_v1",
            timestamp="2026-05-08T00:00:00Z",
            slot=12345,
        )

        assert proof.tx_id == "mock_tx_123"
        assert proof.amount == Decimal("0.05")
        assert proof.confirmed is True


class TestMockX402PaymentProcessor:
    """Test mock payment processor."""

    @pytest.fixture
    def processor(self):
        return MockX402PaymentProcessor(
            "test_model",
            price_per_inference=Decimal("0.05"),
        )

    def test_create_payment_request(self, processor):
        """Test creating a payment request."""
        request = processor.create_payment_request("0xuser123")

        assert request.model_id == "test_model"
        assert request.requester == "0xuser123"
        assert request.amount == Decimal("0.05")

    def test_verify_sufficient_payment(self, processor):
        """Test verifying a sufficient payment."""
        result = processor.verify_payment(
            "tx_123",
            "0xpayer",
            Decimal("0.05"),
        )
        assert result is True

    def test_reject_insufficient_payment(self, processor):
        """Test rejecting insufficient payment."""
        result = processor.verify_payment(
            "tx_123",
            "0xpayer",
            Decimal("0.01"),
        )
        assert result is False

    def test_record_payment(self, processor):
        """Test recording a payment."""
        proof = processor.record_payment(
            tx_id="tx_123",
            payer_wallet="0xpayer",
            amount=Decimal("0.05"),
            slot=12345,
        )

        assert proof.tx_id == "tx_123"
        assert proof.amount == Decimal("0.05")
        assert proof.confirmed is True

    def test_get_payment_proof(self, processor):
        """Test retrieving a payment proof."""
        processor.record_payment(
            tx_id="tx_123",
            payer_wallet="0xpayer",
            amount=Decimal("0.05"),
            slot=12345,
        )

        proof = processor.get_payment_proof("tx_123")

        assert proof is not None
        assert proof.tx_id == "tx_123"

    def test_get_payment_history(self, processor):
        """Test getting payment history."""
        for i in range(3):
            processor.record_payment(
                tx_id=f"tx_{i}",
                payer_wallet=f"0xpayer{i}",
                amount=Decimal("0.05"),
                slot=12345 + i,
            )

        history = processor.get_payment_history()

        assert len(history) == 3

    def test_get_total_revenue(self, processor):
        """Test calculating total revenue."""
        for i in range(3):
            processor.record_payment(
                tx_id=f"tx_{i}",
                payer_wallet=f"0xpayer{i}",
                amount=Decimal("0.05"),
                slot=12345,
            )

        total = processor.get_total_revenue()

        assert total == Decimal("0.15")

    def test_calculate_node_payout(self, processor):
        """Test calculating node payout."""
        # Record some revenue
        processor.record_payment(
            tx_id="tx_1",
            payer_wallet="0xpayer",
            amount=Decimal("1.00"),
            slot=12345,
        )

        # Calculate 50% payout
        payout = processor.calculate_node_payout(Decimal("0.5"))

        assert payout == Decimal("0.50")

    def test_custom_price_per_inference(self):
        """Test custom pricing."""
        processor = MockX402PaymentProcessor(
            "test_model",
            price_per_inference=Decimal("0.10"),
        )

        request = processor.create_payment_request("0xuser")

        assert request.amount == Decimal("0.10")

    def test_factory_creates_mock(self):
        """Test factory creates mock processor."""
        processor = create_payment_processor(
            "test_model",
            use_mock=True,
        )

        assert isinstance(processor, MockX402PaymentProcessor)

    def test_factory_creates_real_processor(self):
        """Test factory creates real processor."""
        processor = create_payment_processor(
            "test_model",
            use_mock=False,
        )

        assert isinstance(processor, X402PaymentProcessor)

    def test_multiple_payments_same_payer(self, processor):
        """Test multiple payments from same payer."""
        for i in range(3):
            processor.record_payment(
                tx_id=f"tx_{i}",
                payer_wallet="0xpayer",
                amount=Decimal("0.05"),
                slot=12345 + i,
            )

        history = processor.get_payment_history()

        assert len(history) == 3
        assert all(p.payer == "0xpayer" for p in history)

    def test_receiver_wallet(self):
        """Test custom receiver wallet."""
        receiver = "0xcustom_receiver"
        processor = MockX402PaymentProcessor(
            "test_model",
            receiver_wallet=receiver,
        )

        proof = processor.record_payment(
            tx_id="tx_1",
            payer_wallet="0xpayer",
            amount=Decimal("0.05"),
            slot=12345,
        )

        assert proof.receiver == receiver
