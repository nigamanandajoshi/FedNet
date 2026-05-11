"""
WSGI entry point for production deployment.

Usage with gunicorn:
    gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4 --timeout 120

For the inference server:
    gunicorn wsgi:inference_app --bind 0.0.0.0:5001 --workers 2 --timeout 120
"""

import logging
import os
from config.logging_config import setup_logging
from config.settings import settings

# Configure logging for production
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level, log_dir=settings.logs_dir)

logger = logging.getLogger("fednet.wsgi")

# --- Main API application ---
from api.app import app  # noqa: E402

logger.info("FedNet API loaded (WSGI mode)")


# --- Inference server application (optional, separate process) ---
def _create_inference_app():
    """Lazy-create inference app only when explicitly imported."""
    import torch
    import torch.nn as nn
    from decimal import Decimal
    from fednet.inference_server import X402InferenceServer

    class DefaultModel(nn.Module):
        """Placeholder model — replace with trained model in production."""
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(8, 32)
            self.fc2 = nn.Linear(32, 3)

        def forward(self, x):
            return self.fc2(torch.relu(self.fc1(x)))

    # Load trained model if available
    model_path = settings.models_dir / "final_global_model.pth"
    model = DefaultModel()

    if model_path.exists():
        try:
            model.load_state_dict(torch.load(model_path, map_location="cpu"))
            logger.info("Loaded trained model from %s", model_path)
        except Exception as e:
            logger.warning("Could not load model from %s: %s", model_path, e)
    else:
        logger.warning("No trained model found at %s — using default", model_path)

    use_mock = not settings.is_production
    price = Decimal(os.getenv("QUERY_PRICE_USDC", "0.05"))

    server = X402InferenceServer(
        model=model,
        model_id="fednet_healthcare_v1",
        price_per_inference=price,
        use_mock=use_mock,
    )

    return server.get_app()


# Only create inference app when this attribute is accessed
inference_app = None

if os.getenv("LOAD_INFERENCE_APP", "false").lower() == "true":
    inference_app = _create_inference_app()
    logger.info("FedNet Inference app loaded (WSGI mode)")
