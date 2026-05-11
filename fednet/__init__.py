"""FedNet: Federated Learning Governance, Auditability, and Monetization Layer"""

import logging

__version__ = "1.0.0"

# Package-level logger — defaults to NullHandler to avoid
# "No handler found" warnings when used as a library.
logging.getLogger("fednet").addHandler(logging.NullHandler())

from fednet.audit_artifacts import AuditArtifactGenerator, create_artifact_generator
from fednet.solana_attestation import create_solana_client
from fednet.x402_payment import create_payment_processor
from fednet.inference_server import X402InferenceServer

__all__ = [
    "AuditArtifactGenerator",
    "create_artifact_generator",
    "create_solana_client",
    "create_payment_processor",
    "X402InferenceServer",
]
