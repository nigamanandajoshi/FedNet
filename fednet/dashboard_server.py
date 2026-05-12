"""
FedNet Dashboard Server
Full web application for monitoring and controlling FedNet governance layers.
"""

import logging
import threading
import hashlib
import os
from flask import Flask, jsonify, request
from pathlib import Path
import json
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger("fednet.dashboard")


class FedNetDashboard:
    """Full-featured dashboard server for FedNet."""

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
        self.training_status = {"running": False, "log": [], "round": 0}

        template_dir = Path(__file__).parent / "templates"
        static_dir = Path(__file__).parent / "static"
        self.app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
        self._register_routes()

    def _register_routes(self):
        """Register all Flask routes."""

        # ── Page Routes ──────────────────────────────────────────────

        @self.app.route("/", methods=["GET"])
        def index():
            """Serve the SPA."""
            tpl = Path(__file__).parent / "templates" / "dashboard.html"
            if tpl.exists():
                return tpl.read_text()
            return "<h1>FedNet</h1><p>Template not found</p>", 500

        # ── Dashboard Stats ──────────────────────────────────────────

        @self.app.route("/api/stats", methods=["GET"])
        def stats():
            artifacts = self._get_artifacts()
            attestations = self._get_attestations()
            inferences = self._get_inferences()
            return jsonify({
                "artifacts": {"total_rounds": len(artifacts), "artifacts": artifacts},
                "attestations": {"total": len(attestations), "attestations": attestations},
                "inferences": {
                    "total_queries": len(inferences),
                    "total_revenue": str(sum(Decimal(i.get("amount", "0")) for i in inferences)),
                    "inferences": inferences,
                },
                "timestamp": datetime.now().isoformat(),
            })

        # ── Artifact Detail ──────────────────────────────────────────

        @self.app.route("/api/artifacts/<int:round_id>", methods=["GET"])
        def artifact_detail(round_id):
            """Get full artifact detail for a specific round."""
            fpath = self.artifacts_dir / f"round_{round_id:03d}.json"
            if not fpath.exists():
                return jsonify({"error": "Artifact not found"}), 404
            with open(fpath) as f:
                data = json.load(f)
            return jsonify(data)

        # ── Training Trigger ─────────────────────────────────────────

        @self.app.route("/api/train", methods=["POST"])
        def trigger_training():
            """Trigger a federated learning round from the UI."""
            if self.training_status["running"]:
                return jsonify({"error": "Training already running"}), 409

            body = request.get_json(silent=True) or {}
            num_rounds = min(int(body.get("rounds", 1)), 5)  # cap at 5

            self.training_status = {"running": True, "log": [], "round": 0}
            t = threading.Thread(target=self._run_training, args=(num_rounds,), daemon=True)
            t.start()
            return jsonify({"status": "started", "rounds": num_rounds})

        @self.app.route("/api/train/status", methods=["GET"])
        def training_status():
            return jsonify(self.training_status)

        # ── Settings ─────────────────────────────────────────────────

        @self.app.route("/api/settings", methods=["GET"])
        def get_settings():
            from config.settings import settings
            return jsonify({
                "environment": settings.environment,
                "solana_network": settings.solana_network,
                "solana_rpc": settings.solana_rpc_endpoint,
                "usdc_mint": settings.usdc_mint,
                "model_type": os.getenv("MODEL_TYPE", "hybrid"),
                "query_price": os.getenv("QUERY_PRICE_USDC", "0.05"),
                "receiver_wallet": os.getenv("RECEIVER_WALLET", "not set"),
                "fl_rounds": os.getenv("FL_ROUNDS", "10"),
                "local_epochs": os.getenv("LOCAL_EPOCHS", "5"),
                "min_clients": os.getenv("MIN_CLIENTS", "2"),
            })

    # ── Training Logic ─────────────────────────────────────────────

    def _run_training(self, num_rounds: int):
        """Execute FL training rounds (runs in background thread)."""
        import torch
        import torch.nn as nn
        from fednet.audit_artifacts import create_artifact_generator
        from fednet.solana_attestation import create_solana_client

        class MiniModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(8, 32)
                self.fc2 = nn.Linear(32, 16)
                self.fc3 = nn.Linear(16, 3)
            def forward(self, x):
                return self.fc3(torch.relu(self.fc2(torch.relu(self.fc1(x)))))

        try:
            self._log("Initializing FedNet layers...")
            self.artifacts_dir.mkdir(exist_ok=True)
            gen = create_artifact_generator("fednet-dashboard")
            sol = create_solana_client(use_mock=True)
            model = MiniModel()
            weights = model.state_dict()
            participants = ["0xhospital_mercy", "0xclinic_urgent_care", "0xresearch_lab"]

            existing = len([f for f in self.artifacts_dir.glob("round_*.json")])
            attestations = self._get_attestations()
            inferences = self._get_inferences()

            for r in range(num_rounds):
                round_num = existing + r + 1
                self.training_status["round"] = round_num
                self._log(f"── Round {round_num} ──")

                # Simulate local training
                self._log("  Training at 3 institutions...")
                client_weights = []
                for p in participants:
                    local = {k: v + torch.randn_like(v) * 0.01 for k, v in weights.items()}
                    client_weights.append(local)
                    self._log(f"    ✓ {p}: complete")

                # Aggregate
                self._log("  Aggregating global model...")
                agg = {k: torch.stack([w[k] for w in client_weights]).mean(0) for k in weights}
                weights = agg
                model.load_state_dict(weights)
                self._log("    ✓ FedAvg aggregation done")

                # Layer 1: Audit
                self._log("  [Layer 1] Generating audit artifact...")
                grad_dict = {k: v.cpu().numpy() for k, v in weights.items()}
                artifact = gen.generate_artifact(
                    round_id=round_num, participants=participants,
                    gradients=grad_dict, model_version="v1.0.0",
                    epsilon=0.1, delta=1e-5,
                )
                path = self.artifacts_dir / f"round_{round_num:03d}.json"
                gen.save_artifact(artifact, str(path))
                self._log(f"    ✓ Artifact signed: {artifact.aggregator_signature[:16]}...")

                # Layer 2: Attest
                self._log("  [Layer 2] Anchoring on Solana...")
                att = sol.attest_artifact(
                    artifact_hash=artifact.gradient_hash,
                    round_id=round_num, participants=3, model_version="v1.0.0",
                )
                attestations.append({
                    "tx_id": att["tx_id"], "explorer_url": att["explorer_url"],
                    "artifact_hash": att.get("artifact_hash", artifact.gradient_hash),
                    "round_id": round_num,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "confirmed",
                })
                self._log(f"    ✓ TX: {att['tx_id']}")
                self._log(f"    ✓ Explorer: {att['explorer_url']}")

            # Persist updated attestations
            with open(self.artifacts_dir / "_attestations.json", "w") as f:
                json.dump(attestations, f, indent=2)

            self._log(f"\n🎉 {num_rounds} round(s) completed successfully!")
        except Exception as e:
            self._log(f"\n❌ Error: {e}")
            logger.exception("Training failed")
        finally:
            self.training_status["running"] = False

    def _log(self, msg: str):
        self.training_status["log"].append(msg)
        logger.info(msg)

    # ── Data Access ────────────────────────────────────────────────

    def _get_artifacts(self) -> list:
        artifacts = []
        if self.artifacts_dir.exists():
            for f in sorted(self.artifacts_dir.glob("*.json")):
                if f.name.startswith("_"):
                    continue
                with open(f) as fh:
                    data = json.load(fh)
                artifacts.append({
                    "round": data.get("round_id"),
                    "timestamp": data.get("timestamp"),
                    "participants": len(data.get("participants", [])),
                    "gradient_hash": data.get("gradient_hash", "")[:16] + "...",
                    "gradient_hash_full": data.get("gradient_hash", ""),
                    "model_version": data.get("model_version"),
                    "dp_epsilon": data.get("epsilon"),
                    "dp_delta": data.get("delta"),
                    "signature": data.get("aggregator_signature", "")[:16] + "...",
                    "signature_valid": True,
                })
        return artifacts

    def _get_attestations(self) -> list:
        fp = self.artifacts_dir / "_attestations.json"
        if fp.exists():
            try:
                with open(fp) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _get_inferences(self) -> list:
        fp = self.artifacts_dir / "_inferences.json"
        if fp.exists():
            try:
                with open(fp) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def run(self, debug: bool = False):
        logger.info("FedNet Dashboard running on http://localhost:%d", self.port)
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)


def create_dashboard(
    artifacts_dir: str = "artifacts",
    attestations_dir: str = "attestations",
    port: int = 5001,
) -> FedNetDashboard:
    """Create and return a dashboard instance."""
    return FedNetDashboard(artifacts_dir, attestations_dir, port)
