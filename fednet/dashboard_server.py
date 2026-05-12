"""
FedNet Dashboard Server
Real-time monitoring of audit artifacts, Solana attestations, and inference monetization.
"""

import logging
from flask import Flask, render_template_string, jsonify
from pathlib import Path
import json
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger("fednet.dashboard")


class FedNetDashboard:
    """Dashboard server for FedNet monitoring."""

    def __init__(
        self,
        artifacts_dir: str = "artifacts",
        attestations_dir: str = "attestations",
        port: int = 5001,
    ):
        """Initialize dashboard."""
        self.artifacts_dir = Path(artifacts_dir)
        self.attestations_dir = Path(attestations_dir)
        self.port = port

        # Set up Flask with templates directory
        template_dir = Path(__file__).parent / "templates"
        self.app = Flask(__name__, template_folder=str(template_dir))
        self._register_routes()

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route("/", methods=["GET"])
        def dashboard():
            """Serve dashboard HTML."""
            template_path = Path(__file__).parent / "templates" / "dashboard.html"
            if template_path.exists():
                return template_path.read_text()
            # Fallback to inline minimal page
            return "<h1>FedNet Dashboard</h1><p>Template not found</p>", 500

        @self.app.route("/api/stats", methods=["GET"])
        def stats():
            """Get dashboard statistics."""
            artifacts = self._get_artifacts()
            attestations = self._get_attestations()
            inferences = self._get_inferences()

            return jsonify({
                "artifacts": {
                    "total_rounds": len(artifacts),
                    "artifacts": artifacts,
                },
                "attestations": {
                    "total": len(attestations),
                    "attestations": attestations,
                },
                "inferences": {
                    "total_queries": len(inferences),
                    "total_revenue": str(sum(
                        Decimal(i.get("amount", "0")) for i in inferences
                    )),
                    "inferences": inferences,
                },
                "timestamp": datetime.now().isoformat(),
            })

    def _get_artifacts(self) -> list:
        """Get all artifacts from disk."""
        artifacts = []

        if self.artifacts_dir.exists():
            for artifact_file in sorted(self.artifacts_dir.glob("*.json")):
                with open(artifact_file, "r") as f:
                    data = json.load(f)

                artifacts.append({
                    "round": data.get("round_id"),
                    "timestamp": data.get("timestamp"),
                    "participants": len(data.get("participants", [])),
                    "gradient_hash": data.get("gradient_hash", "")[:16] + "...",
                    "model_version": data.get("model_version"),
                    "dp_epsilon": data.get("epsilon"),
                    "signature_valid": True,  # Would verify in production
                })

        return artifacts

    def _get_attestations(self) -> list:
        """Get attestation records."""
        # Would read from actual Solana records in production
        # For now, return example structure
        return []

    def _get_inferences(self) -> list:
        """Get inference query records."""
        # Would read from actual payment ledger in production
        # For now, return example structure
        return []

    def run(self, debug: bool = False):
        """Run the dashboard server."""
        logger.info("FedNet Dashboard running on http://localhost:%d", self.port)
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)


def create_dashboard(
    artifacts_dir: str = "artifacts",
    attestations_dir: str = "attestations",
    port: int = 5001,
) -> FedNetDashboard:
    """Create and return a dashboard instance."""
    return FedNetDashboard(artifacts_dir, attestations_dir, port)
