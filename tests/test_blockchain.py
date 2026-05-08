"""Unit tests for blockchain."""

from blockchain.ledger import BlockchainLedger


def test_blockchain_creation():
    """Test blockchain initialization."""
    blockchain = BlockchainLedger()
    
    assert len(blockchain.chain) == 1  # Genesis block
    assert blockchain.is_valid()


def test_fl_round_recording():
    """Test recording FL round."""
    blockchain = BlockchainLedger()
    
    metrics = {"accuracy": 0.85, "loss": 0.3}
    ok = blockchain.record_fl_round(1, 3, metrics)
    
    assert ok is True
    rounds = blockchain.get_fl_rounds()
    assert rounds[0]["round"] == 1
    assert blockchain.is_valid()


def test_client_update_recording():
    """Test recording a client update."""
    blockchain = BlockchainLedger()
    ok = blockchain.record_client_update(1, "hospital_a", 123, {"loss": 0.42, "accuracy": 0.77})
    assert ok is True
    updates = blockchain.get_client_updates(1)
    assert len(updates) == 1
    assert updates[0]["client_id"] == "hospital_a"
    assert blockchain.is_valid()
