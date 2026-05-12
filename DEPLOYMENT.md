# FedNet Deployment Guide — Free Hackathon Deployment

Deploy FedNet to production for **free** using Render.com's free tier. This guide gets you live in 5 minutes.

---

## Quick Start: Deploy to Render (Free)

### Step 1: Create a Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (authenticate your account)
3. Accept the connections request to your repository

### Step 2: Deploy Dashboard Service
1. Click **"New"** → **"Web Service"**
2. Select your `FedNet` repository
3. Fill in the details:
   - **Name:** `fednet-dashboard`
   - **Runtime:** Python 3.11
   - **Build Command:** `pip install -r requirements-deploy.txt`
   - **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. **Environment Variables:**
   ```
   PYTHON_VERSION=3.11.0
   SOLANA_NETWORK=devnet
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```
5. Click **"Create Web Service"**
6. Wait 3-5 minutes for deployment
7. ✅ Your dashboard is live at: `https://fednet-dashboard-[random].onrender.com`

### Step 3: Deploy Inference Server (Optional, Recommended)
1. Click **"New"** → **"Web Service"**
2. Select your `FedNet` repository (same repo)
3. Fill in the details:
   - **Name:** `fednet-inference`
   - **Runtime:** Python 3.11
   - **Build Command:** `pip install -r requirements-deploy.txt`
   - **Start Command:** `LOAD_INFERENCE_APP=true gunicorn wsgi:inference_app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. **Environment Variables:**
   ```
   PYTHON_VERSION=3.11.0
   SOLANA_NETWORK=devnet
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   QUERY_PRICE_USDC=0.05
   ```
5. Click **"Create Web Service"**
6. ✅ Your inference API is live at: `https://fednet-inference-[random].onrender.com`

---

## Testing Your Deployment

### Test Dashboard
```bash
curl https://fednet-dashboard-[random].onrender.com
# Returns: Dashboard HTML with real-time artifact, attestation, and payment data
```

### Test Inference API
```bash
# Check health
curl https://fednet-inference-[random].onrender.com/health

# Get model info
curl https://fednet-inference-[random].onrender.com/model/info

# Request inference (without payment — should return 402)
curl -X POST https://fednet-inference-[random].onrender.com/inference \
  -H "Content-Type: application/json" \
  -d '{"input": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]}'

# Response: HTTP 402 Payment Required
```

---

## Understanding the Deployment

### Dashboard Service (`fednet-dashboard`)
- **What it does:** Real-time monitoring of audit artifacts, Solana attestations, and inference payments
- **Endpoint:** `https://fednet-dashboard-[random].onrender.com`
- **Routes:**
  - `/` — Dashboard UI
  - `/api/stats` — JSON stats (artifacts, attestations, inferences)
  - `ws://` — WebSocket for live updates (if configured)

### Inference Service (`fednet-inference`)
- **What it does:** x402-gated model inference endpoint with payment verification
- **Endpoint:** `https://fednet-inference-[random].onrender.com`
- **Routes:**
  - `/health` — Health check
  - `/model/info` — Model metadata and pricing
  - `/inference` — Gated inference (requires payment)
  - `/payments/history` — Payment ledger
  - `/stats` — Server statistics

### Solana Integration
- **Network:** Devnet (testing, free SOL faucet)
- **Attestations:** Free (~$0.000005 per hash anchor)
- **Payments:** USDC on Solana devnet
- **RPC:** Free public RPC endpoint

---

## Production Upgrades (After Hackathon)

### Upgrade from Free to Paid Tier
1. Click your service → **"Settings"**
2. Change **Plan** from **"Free"** to **"Starter"** ($7/month)
   - Benefits: No auto-sleep, persistent storage, better performance
3. Or upgrade to **"Standard"** for production scale

### Use Real Solana Mainnet (After Hackathon)
Update environment variable:
```
SOLANA_NETWORK=mainnet
```

### Add Database (After Hackathon)
For persistent payment ledger:
1. Go to **"Data Services"** → **"PostgreSQL"**
2. Create free tier database
3. Add connection string to environment:
```
DATABASE_URL=postgres://...
```

### Custom Domain
1. Click service → **"Settings"** → **"Custom Domain"**
2. Add your domain (e.g., `fednet.yourdomain.com`)
3. Update DNS records as instructed

---

## Monitoring & Logs

### View Real-Time Logs
1. Click your service in Render dashboard
2. Click **"Logs"** tab
3. Watch deployment and runtime logs

### Monitor Metrics
1. Click your service → **"Metrics"** tab
2. View CPU, memory, bandwidth usage
3. Free tier shows: CPU%, Memory%, Request count

### Set Up Alerts
1. Click your service → **"Settings"** → **"Notifications"**
2. Enable email alerts for:
   - Deployment failures
   - Service crashes
   - High resource usage

---

## Troubleshooting

### Service keeps restarting or crashing
**Check logs:** Click service → **"Logs"** → Look for error messages
**Common causes:**
- Memory overflow: Reduce batch size or model size
- Missing dependencies: Ensure `requirements-deploy.txt` is complete
- Port binding issue: Verify environment variables

**Fix:**
```bash
# Locally test the exact command that Render runs
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
```

### Dashboard shows "No artifacts yet"
- Artifacts are generated by the FL training process
- Run locally first: `python test_fednet_complete.py`
- This generates artifacts to `./artifacts/` directory
- Commit artifacts to git, and Render will load them

### Inference API returns 500 errors
1. Check logs for stack trace
2. Verify model dimensions match test input
3. Ensure torch is installed in deployment environment

### Build fails with "module not found"
- Verify `requirements-deploy.txt` is complete
- Test locally: `pip install -r requirements-deploy.txt`
- Add missing dependencies if needed

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      RENDER.COM (FREE TIER)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────┐   ┌──────────────────────────┐
│  │  Dashboard Service       │   │  Inference Service       │
│  │  (fednet-dashboard)      │   │  (fednet-inference)      │
│  │                          │   │                          │
│  │  Port: $PORT             │   │  Port: $PORT             │
│  │  /                       │   │  /inference              │
│  │  /api/stats              │   │  /health                 │
│  │                          │   │  /model/info             │
│  │                          │   │  /payments/history       │
│  └──────────────────────────┘   └──────────────────────────┘
│           │                             │                   │
│           └─────────────┬───────────────┘                   │
│                         ↓                                   │
│                  [Solana Devnet]                           │
│                  RPC: free endpoint                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Sharing Your Deployment

### For Hackathon Judges
Share these links:

```
📊 Dashboard: https://fednet-dashboard-[random].onrender.com
🔧 API Docs: https://fednet-inference-[random].onrender.com/model/info
📚 Source: https://github.com/yourusername/FedNet
📖 Docs: https://github.com/yourusername/FedNet/blob/main/FEDNET.md
```

### Include in Hackathon Submission
- **Link to live demo:** Dashboard URL
- **API endpoint:** Inference API URL
- **GitHub repo:** GitHub URL
- **Documentation:** FEDNET.md for technical details
- **Quick start:** QUICKSTART.md for judges to run locally

---

## Cost Breakdown (Hackathon)

| Component | Cost | Notes |
|-----------|------|-------|
| Render Dashboard | **FREE** | Free tier, shared resources |
| Render Inference | **FREE** | Free tier, shared resources |
| Solana Devnet | **FREE** | Testnet with free SOL faucet |
| USDC on Devnet | **FREE** | No real money involved |
| **Total** | **$0/month** | Perfect for hackathon! |

### After Hackathon (If Scaling)
- Dashboard: $7/month (Starter tier)
- Inference: $7/month (Starter tier)
- PostgreSQL: $15/month (if using persistent DB)
- **Total: $29/month** (still free tier available)

---

## Next Steps

1. ✅ **Deploy to Render** (this guide)
2. 📊 **Share dashboard URL** with hackathon judges
3. 🧪 **Test inference endpoint** with sample queries
4. 📝 **Document your submission** with links and screenshots
5. 🚀 **Submit to hackathon!**

---

## Support & Questions

- **Render Docs:** https://render.com/docs
- **FedNet Docs:** See FEDNET.md
- **Solana Devnet Faucet:** https://faucet.solana.com
- **GitHub Issues:** https://github.com/nigamanandajoshi/FedNet/issues

---

**Deployment Complete! 🎉**

Your FedNet system is now live and ready for hackathon judges to explore.
