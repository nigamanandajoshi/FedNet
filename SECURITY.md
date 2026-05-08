# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in FedNet, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. **Email**: Send a detailed report to [nigamanandajoshi@gmail.com](mailto:nigamanandajoshi@gmail.com)
2. **Subject**: Use the prefix `[SECURITY]` in the subject line
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Assessment**: Initial severity assessment within 5 business days
- **Resolution**: We aim to address critical vulnerabilities within 30 days

### Scope

The following are in scope for security reports:

- **FedNet governance layer** (`fednet/` package)
- **Audit artifact generation** — integrity of compliance records
- **Solana attestation** — hash anchoring and verification
- **x402 payment processing** — payment verification logic
- **Inference server** — access control and data exposure
- **API endpoints** — authentication and authorization

### Out of Scope

- Vulnerabilities in third-party dependencies (report these upstream)
- Issues in the demo/test infrastructure (`test_fednet_*.py`)
- Social engineering attacks

## Security Best Practices for Deployers

When deploying FedNet in production:

1. **Never commit secrets** — Use `.env` files and environment variables
2. **Use HTTPS** — Deploy the Flask inference server behind a TLS reverse proxy
3. **Rotate signing keys** — Regularly rotate HMAC keys used for artifact signing
4. **Restrict Solana wallet access** — Use separate wallets for attestation vs. payments
5. **Enable audit logging** — Monitor all inference and payment transactions
6. **Network segmentation** — Isolate FL training nodes from public inference endpoints
