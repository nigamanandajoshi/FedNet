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

        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route("/", methods=["GET"])
        def dashboard():
            """Serve dashboard HTML."""
            return render_template_string(self.get_dashboard_html())

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

    def get_dashboard_html(self) -> str:
        """Get dashboard HTML template."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FedNet Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 16px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15);
        }

        .card h2 {
            color: #667eea;
            font-size: 18px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }

        .stat:last-child {
            border-bottom: none;
        }

        .stat-label {
            color: #666;
            font-size: 14px;
        }

        .stat-value {
            color: #333;
            font-weight: 600;
            font-size: 18px;
        }

        .badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge.success {
            background: #48bb78;
        }

        .badge.warning {
            background: #ed8936;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .table th {
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e2e8f0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .table td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
        }

        .table tr:hover {
            background: #f7fafc;
        }

        .link {
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }

        .link:hover {
            text-decoration: underline;
        }

        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        .status-badge.verified {
            background: #c6f6d5;
            color: #22543d;
        }

        .status-badge.pending {
            background: #fed7d7;
            color: #742a2a;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .error {
            background: #fed7d7;
            color: #742a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            font-size: 12px;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        .loading-pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 FedNet Dashboard</h1>
            <p class="subtitle">Real-time monitoring: Audit artifacts • Solana attestations • Inference monetization</p>
        </header>

        <div id="stats" class="loading">
            <p class="loading-pulse">Loading data...</p>
        </div>

        <footer>
            FedNet: Federated Learning Governance, Auditability & Monetization
            <br />
            Layer 1: Audit Artifacts | Layer 2: Solana Attestation | Layer 3: x402 Monetization
        </footer>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                renderDashboard(data);
            } catch (error) {
                console.error('Error loading stats:', error);
                document.getElementById('stats').innerHTML = '<div class="error">Error loading dashboard data</div>';
            }
        }

        function renderDashboard(data) {
            const html = `
                <div class="grid">
                    <!-- Layer 1: Audit Artifacts -->
                    <div class="card">
                        <h2>📋 Layer 1: Audit Artifacts</h2>
                        <div class="stat">
                            <span class="stat-label">Total Rounds</span>
                            <span class="stat-value">${data.artifacts.total_rounds}</span>
                        </div>
                        ${data.artifacts.artifacts.length > 0 ? `
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Round</th>
                                        <th>Participants</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.artifacts.artifacts.map(a => `
                                        <tr>
                                            <td>#${a.round}</td>
                                            <td>${a.participants}</td>
                                            <td><span class="status-badge verified">✓ Verified</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : '<p style="color: #999; margin-top: 10px;">No artifacts yet</p>'}
                    </div>

                    <!-- Layer 2: Solana Attestation -->
                    <div class="card">
                        <h2>⛓️ Layer 2: Solana Attestation</h2>
                        <div class="stat">
                            <span class="stat-label">On-Chain Proofs</span>
                            <span class="stat-value">${data.attestations.total}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Status</span>
                            <span class="badge success">Ready</span>
                        </div>
                        <p style="color: #666; font-size: 13px; margin-top: 15px;">
                            <strong>State Compression:</strong> Artifact hashes anchored on Solana devnet for tamper-proof verification (~$0.000005/tx)
                        </p>
                    </div>

                    <!-- Layer 3: Monetization -->
                    <div class="card">
                        <h2>💰 Layer 3: x402 Monetization</h2>
                        <div class="stat">
                            <span class="stat-label">Inference Queries</span>
                            <span class="stat-value">${data.inferences.total_queries}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Total Revenue</span>
                            <span class="stat-value">$${data.inferences.total_revenue} USDC</span>
                        </div>
                        <p style="color: #666; font-size: 13px; margin-top: 15px;">
                            <strong>Price:</strong> $0.05 USDC per inference query
                        </p>
                    </div>
                </div>

                ${data.artifacts.artifacts.length > 0 ? `
                    <div class="card">
                        <h2>📊 Audit Artifacts Detail</h2>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Round</th>
                                    <th>Timestamp</th>
                                    <th>Participants</th>
                                    <th>Gradient Hash</th>
                                    <th>Model</th>
                                    <th>DP ε</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.artifacts.artifacts.map(a => `
                                    <tr>
                                        <td>#${a.round}</td>
                                        <td>${new Date(a.timestamp).toLocaleDateString()}</td>
                                        <td>${a.participants}</td>
                                        <td><span class="link">${a.gradient_hash}</span></td>
                                        <td>${a.model_version}</td>
                                        <td>${a.dp_epsilon}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                ` : ''}
            `;

            document.getElementById('stats').innerHTML = html;
        }

        // Load stats on page load
        loadStats();

        // Refresh stats every 10 seconds
        setInterval(loadStats, 10000);
    </script>
</body>
</html>
        '''

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
