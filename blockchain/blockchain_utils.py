"""Blockchain utilities."""

import hashlib
import json
from typing import Any, Dict


def hash_dict(data: Dict) -> str:
    """
    Create SHA256 hash of dictionary.
    
    Args:
        data: Dictionary to hash
        
    Returns:
        Hex digest of hash
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def hash_model_weights(weights: Dict) -> str:
    """
    Create hash of model weights.
    
    Args:
        weights: Model state dict
        
    Returns:
        Hash digest
    """
    # Convert tensors to lists for hashing
    weights_list = {}
    for key, value in weights.items():
        if hasattr(value, 'cpu'):
            weights_list[key] = value.cpu().numpy().tobytes().hex()
        else:
            weights_list[key] = str(value)
    
    return hash_dict(weights_list)


def verify_hash(data: Any, expected_hash: str) -> bool:
    """
    Verify data against expected hash.
    
    Args:
        data: Data to verify
        expected_hash: Expected hash
        
    Returns:
        True if hash matches
    """
    if isinstance(data, dict):
        actual_hash = hash_dict(data)
    else:
        actual_hash = hashlib.sha256(str(data).encode()).hexdigest()
    
    return actual_hash == expected_hash
