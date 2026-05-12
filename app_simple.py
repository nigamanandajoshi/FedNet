#!/usr/bin/env python3
"""
Ultra-minimal FedNet Dashboard for Render deployment.
Zero external dependencies except Flask.
"""

from flask import Flask, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Serve simple dashboard HTML."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>FedNet Dashboard</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #667eea; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .badge { background: #667eea; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 FedNet Dashboard</h1>
        <p>Federated Learning Governance, Auditability & Monetization</p>

        <div class="card">
            <h2>📋 Layer 1: Audit Artifacts</h2>
            <div class="stat">
                <span>Total Rounds</span>
                <span id="rounds">Loading...</span>
            </div>
        </div>

        <div class="card">
            <h2>⛓️ Layer 2: Solana Attestation</h2>
            <div class="stat">
                <span>On-Chain Proofs</span>
                <span id="attestations">Loading...</span>
            </div>
        </div>

        <div class="card">
            <h2>💰 Layer 3: x402 Monetization</h2>
            <div class="stat">
                <span>Inference Queries</span>
                <span id="inferences">Loading...</span>
            </div>
        </div>

        <div class="card">
            <h2>📊 System Status</h2>
            <p>✅ Dashboard: Online</p>
            <p>✅ API: Ready</p>
            <p>📚 <a href="https://github.com/nigamanandajoshi/FedNet" target="_blank">View Source Code</a></p>
        </div>
    </div>

    <script>
        // Load stats from API
        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('rounds').textContent = data.artifacts.total_rounds || '0';
                document.getElementById('attestations').textContent = data.attestations.total || '0';
                document.getElementById('inferences').textContent = data.inferences.total_queries || '0';
            } catch (err) {
                console.log('Artifacts directory empty - run test_fednet_complete.py to generate data');
            }
        }
        loadStats();
        setInterval(loadStats, 10000);
    </script>
</body>
</html>
    '''

@app.route('/api/stats')
def stats():
    """Get system statistics."""
    artifacts_dir = Path("artifacts")
    attestations_dir = Path("attestations")

    artifacts = len(list(artifacts_dir.glob("*.json"))) if artifacts_dir.exists() else 0
    attestations = len(list(attestations_dir.glob("*.json"))) if attestations_dir.exists() else 0

    return jsonify({
        "artifacts": {"total_rounds": artifacts},
        "attestations": {"total": attestations},
        "inferences": {"total_queries": 0},
    })

@app.route('/health')
def health():
    """Health check."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
