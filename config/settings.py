"""Application settings and configuration."""

import os
from pathlib import Path
from typing import List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class Settings:
    """Application settings."""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")  # development, production
    
    # Project paths
    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    models_dir: Path = PROJECT_ROOT / "saved_models"
    logs_dir: Path = PROJECT_ROOT / "logs"
    checkpoints_dir: Path = PROJECT_ROOT / "checkpoints"
    
    # Hospital configurations
    hospitals: List[str] = field(default_factory=lambda: ["italy", "pakistan", "usa"])
    
    # Model settings
    model_type: str = os.getenv("MODEL_TYPE", "hybrid")  # cbc, image, or hybrid
    image_size: int = int(os.getenv("IMAGE_SIZE", "224"))
    num_classes: int = int(os.getenv("NUM_CLASSES", "3"))  # normal, minor, major
    
    # Training settings
    batch_size: int = int(os.getenv("BATCH_SIZE", "32"))
    learning_rate: float = float(os.getenv("LEARNING_RATE", "0.001"))
    epochs: int = int(os.getenv("EPOCHS", "50"))
    num_workers: int = int(os.getenv("NUM_WORKERS", "4"))
    
    # Federated learning settings
    fl_rounds: int = int(os.getenv("FL_ROUNDS", "10"))
    local_epochs: int = int(os.getenv("LOCAL_EPOCHS", "5"))
    aggregation_method: str = os.getenv("AGGREGATION_METHOD", "fedavg")  # fedavg, fedprox
    min_clients: int = int(os.getenv("MIN_CLIENTS", "2"))
    
    # Solana settings
    solana_network: str = os.getenv("SOLANA_NETWORK", "devnet")  # devnet, mainnet-beta
    solana_rpc_url: str = os.getenv("SOLANA_RPC_URL", "")  # auto-derived from network if empty
    solana_wallet_path: str = os.getenv("SOLANA_WALLET_PATH", "")
    usdc_mint_address: str = os.getenv("USDC_MINT_ADDRESS", "")
    receiver_wallet: str = os.getenv("RECEIVER_WALLET", "")
    query_price_usdc: str = os.getenv("QUERY_PRICE_USDC", "0.05")
    
    @property
    def solana_rpc_endpoint(self) -> str:
        """Get Solana RPC endpoint, auto-derived from network if not explicitly set."""
        if self.solana_rpc_url:
            return self.solana_rpc_url
        rpc_urls = {
            "devnet": "https://api.devnet.solana.com",
            "mainnet-beta": "https://api.mainnet-beta.solana.com",
            "testnet": "https://api.testnet.solana.com",
        }
        return rpc_urls.get(self.solana_network, rpc_urls["devnet"])
    
    @property
    def solana_explorer_cluster(self) -> str:
        """Get explorer cluster param. mainnet-beta uses no cluster param."""
        if self.solana_network == "mainnet-beta":
            return ""  # mainnet has no ?cluster= param
        return f"?cluster={self.solana_network}"
    
    @property
    def usdc_mint(self) -> str:
        """Get USDC mint address for the current network."""
        if self.usdc_mint_address:
            return self.usdc_mint_address
        # Well-known USDC mint addresses
        mints = {
            "mainnet-beta": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "devnet": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",  # devnet USDC
        }
        return mints.get(self.solana_network, mints["devnet"])
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "5000"))
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Database settings
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "fednet")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    use_wandb: bool = os.getenv("USE_WANDB", "false").lower() == "true"
    wandb_project: str = os.getenv("WANDB_PROJECT", "fednet")
    use_tensorboard: bool = os.getenv("USE_TENSORBOARD", "true").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    def __post_init__(self):
        """Create necessary directories and validate production config."""
        self.models_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.checkpoints_dir.mkdir(exist_ok=True, parents=True)
        
        # Fail loudly if dev secrets are used in production
        if self.is_production:
            _insecure = {"dev-secret-key-change-in-production", "jwt-secret-key-change-in-production"}
            if self.secret_key in _insecure or self.jwt_secret_key in _insecure:
                raise RuntimeError(
                    "FATAL: Default development secrets detected in production. "
                    "Set SECRET_KEY and JWT_SECRET_KEY environment variables."
                )


# Global settings instance
settings = Settings()
