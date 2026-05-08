#!/usr/bin/env bash
set -euo pipefail

MEMO="${1:-}"

if [ -z "$MEMO" ]; then
  echo "Usage: scripts/solana_anchor_memo.sh \"<memo string>\""
  exit 1
fi

if ! command -v solana >/dev/null 2>&1; then
  echo "solana CLI not found. Install from https://docs.solana.com/cli/install-solana-cli-tools"
  exit 1
fi

SOLANA_URL="${SOLANA_URL:-https://api.devnet.solana.com}"
solana config set --url "$SOLANA_URL" >/dev/null

ADDR="$(solana address)"

# Best-effort airdrop (devnet only). Ignore failures to avoid breaking flows.
solana airdrop 0.2 >/dev/null 2>&1 || true

# Anchor memo by making a tiny self-transfer with memo.
SIG="$(solana transfer "$ADDR" 0.000001 --with-memo "$MEMO" --allow-unfunded-recipient --no-wait | rg -o 'Signature: .*' | sed 's/Signature: //')"

echo "Anchored memo on Solana devnet:"
echo "  Address: $ADDR"
echo "  Signature: $SIG"
echo "  Explorer: https://explorer.solana.com/tx/$SIG?cluster=devnet"

