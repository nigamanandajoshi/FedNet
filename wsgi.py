"""
WSGI entry point for production deployment.

Dashboard:
    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

Inference server:
    LOAD_INFERENCE_APP=true gunicorn wsgi:inference_app --bind 0.0.0.0:5002 --workers 2 --timeout 120
"""

import logging
import os

# Configure basic logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("fednet.wsgi")

# --- Dashboard application (primary) ---
from fednet.dashboard_server import create_dashboard  # noqa: E402

port = int(os.environ.get("PORT", 5001))
dashboard = create_dashboard(port=port)
app = dashboard.app

logger.info("FedNet Dashboard loaded (WSGI mode)")


# --- Inference server application (optional, separate process) ---
def _create_inference_app():
    """Lazy-create inference app only when explicitly imported."""
    try:
        import torch
        import torch.nn as nn
        torch_available = True
    except ImportError:
        torch_available = False
        logger.warning("PyTorch not available; using mock inference server")

    from decimal import Decimal
    from fednet.inference_server import X402InferenceServer

    if torch_available:
        class DefaultModel(nn.Module):
            """Placeholder model — replace with trained model in production."""
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(8, 32)
                self.fc2 = nn.Linear(32, 3)

            def forward(self, x):
                return self.fc2(torch.relu(self.fc1(x)))

        model = DefaultModel()
    else:
        # Fallback: mock model for testing without torch
        class MockModel:
            def __call__(self, x):
                return [0.1, 0.2, 0.3]
        model = MockModel()

    price = Decimal(os.getenv("QUERY_PRICE_USDC", "0.05"))

    server = X402InferenceServer(
        model=model,
        model_id="fednet_healthcare_v1",
        price_per_inference=price,
        use_mock=True,
    )

    return server.get_app()


inference_app = None

if os.getenv("LOAD_INFERENCE_APP", "false").lower() == "true":
    inference_app = _create_inference_app()
    logger.info("FedNet Inference app loaded (WSGI mode)")
