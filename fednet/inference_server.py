"""
Layer 3: x402-Gated Inference Server

Flask server that gates model inference behind x402 payments.
Researchers and AI agents pay per query via Solana USDC transfers.
"""

import torch
import json
import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

from fednet.x402_payment import create_payment_processor, PaymentProof

logger = logging.getLogger("fednet.inference_server")

# Maximum input size to prevent abuse (number of elements)
MAX_INPUT_SIZE = 10_000


class X402InferenceServer:
    """
    Flask-based inference server with x402 payment gating.
    Routes requests through payment verification before running inference.
    """

    def __init__(
        self,
        model: torch.nn.Module,
        model_id: str = "fednet_model_v1",
        price_per_inference: Decimal = Decimal("0.05"),
        use_mock: bool = True,
        debug: bool = False,
    ):
        """
        Initialize inference server.

        Args:
            model: Trained PyTorch model
            model_id: Model identifier
            price_per_inference: Price in USDC per inference
            use_mock: Use mock payment processor (set False for production)
            debug: Enable Flask debug mode
        """
        self.model = model
        self.model_id = model_id
        self.model.eval()

        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config["DEBUG"] = debug
        self.app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB max payload

        # Initialize payment processor
        self.payment_processor = create_payment_processor(
            model_id=model_id,
            use_mock=use_mock,
            price_per_inference=price_per_inference,
        )

        if use_mock:
            logger.warning("Using mock payment processor — not suitable for production")

        # Track inference statistics
        self.inference_count = 0
        self.total_revenue = Decimal("0.0")

        # Register routes
        self._register_routes()

        logger.info(
            "Inference server initialized: model=%s price=%s mock=%s",
            model_id, price_per_inference, use_mock,
        )

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "model_id": self.model_id,
                "price_per_inference": str(self.payment_processor.price_per_inference),
            }), 200

        @self.app.route("/model/info", methods=["GET"])
        def model_info():
            """Get model metadata."""
            return jsonify({
                "model_id": self.model_id,
                "price_per_inference_usdc": str(self.payment_processor.price_per_inference),
                "total_inferences": self.inference_count,
                "total_revenue_usdc": str(self.total_revenue),
                "payment_required": True,
            }), 200

        @self.app.route("/inference", methods=["POST"])
        def inference():
            """
            Gated inference endpoint.

            Requires x402 payment proof.
            Request body:
            {
                "input": [...],
                "payment_tx_id": "...",
                "payer_wallet": "...",
                "payment_amount": "0.05"
            }
            """
            try:
                data = request.get_json()

                if not data:
                    return self._x402_payment_required()

                # Extract payment info
                payment_tx_id = data.get("payment_tx_id")
                payer_wallet = data.get("payer_wallet")
                payment_amount_str = data.get("payment_amount")

                if not all([payment_tx_id, payer_wallet, payment_amount_str]):
                    return self._x402_payment_required()

                # Verify payment
                try:
                    amount = Decimal(str(payment_amount_str))
                except (InvalidOperation, ValueError, TypeError):
                    logger.warning(
                        "Invalid payment amount from %s: %s",
                        payer_wallet, payment_amount_str,
                    )
                    return self._x402_payment_required()

                if not self.payment_processor.verify_payment(
                    payment_tx_id,
                    payer_wallet,
                    amount,
                ):
                    logger.info(
                        "Payment verification failed: tx=%s payer=%s amount=%s",
                        payment_tx_id, payer_wallet, amount,
                    )
                    return self._x402_payment_required()

                # Record payment
                payment_proof = self.payment_processor.record_payment(
                    tx_id=payment_tx_id,
                    payer_wallet=payer_wallet,
                    amount=amount,
                    slot=12345,
                )

                # Run inference
                input_data = data.get("input")
                if input_data is None:
                    return jsonify({"error": "Missing 'input' field"}), 400

                # Validate input size
                if isinstance(input_data, list) and len(input_data) > MAX_INPUT_SIZE:
                    return jsonify({"error": f"Input exceeds maximum size of {MAX_INPUT_SIZE}"}), 400

                try:
                    result = self._run_inference(input_data)

                    # Update statistics
                    self.inference_count += 1
                    self.total_revenue += amount

                    logger.info(
                        "Inference #%d completed: tx=%s payer=%s amount=%s",
                        self.inference_count, payment_tx_id, payer_wallet, amount,
                    )

                    return jsonify({
                        "result": result,
                        "model_id": self.model_id,
                        "payment_verified": True,
                        "payment_tx_id": payment_tx_id,
                        "inference_id": f"{self.inference_count:06d}",
                    }), 200

                except Exception as e:
                    logger.error("Inference failed: %s", e, exc_info=True)
                    return jsonify({"error": f"Inference failed: {str(e)}"}), 500

            except Exception as e:
                logger.error("Request processing error: %s", e, exc_info=True)
                return jsonify({"error": str(e)}), 400

        @self.app.route("/payments/history", methods=["GET"])
        def payment_history():
            """Get payment history."""
            history = self.payment_processor.get_payment_history()

            return jsonify({
                "total_payments": len(history),
                "total_revenue": str(self.payment_processor.get_total_revenue()),
                "payments": [p.to_dict() for p in history],
            }), 200

        @self.app.route("/stats", methods=["GET"])
        def stats():
            """Get server statistics."""
            return jsonify({
                "model_id": self.model_id,
                "total_inferences": self.inference_count,
                "total_revenue_usdc": str(self.total_revenue),
                "total_payments": len(self.payment_processor.get_payment_history()),
                "avg_revenue_per_inference": str(
                    self.total_revenue / max(self.inference_count, 1)
                ),
            }), 200

    def _x402_payment_required(self) -> Tuple[Dict[str, Any], int]:
        """Return HTTP 402 Payment Required response."""
        return jsonify({
            "error": "Payment required",
            "price_usdc": str(self.payment_processor.price_per_inference),
            "instructions": [
                "1. Send USDC payment to Solana with model_id in memo",
                "2. Include payment transaction ID in next request",
                "3. Provide payment details in request body",
            ],
            "example_request": {
                "payment_tx_id": "solana_tx_signature",
                "payer_wallet": "your_solana_wallet",
                "payment_amount": str(self.payment_processor.price_per_inference),
                "input": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            },
        }), 402

    def _run_inference(self, input_data) -> list:
        """
        Run model inference on input data.

        Args:
            input_data: Input list or array

        Returns:
            Model output
        """
        # Convert to tensor
        if isinstance(input_data, list):
            input_tensor = torch.FloatTensor([input_data])
        else:
            input_tensor = torch.FloatTensor(input_data)

        # Run inference
        with torch.no_grad():
            output = self.model(input_tensor)

        # Convert to list
        return output.squeeze().tolist()

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """Run the Flask server."""
        logger.info(
            "Starting inference server: model=%s price=$%s host=%s:%d",
            self.model_id, self.payment_processor.price_per_inference, host, port,
        )
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """Get the Flask app for testing."""
        return self.app
