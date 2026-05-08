# FedNet API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "fednet-api",
  "version": "0.1.0"
}
```

---

### Predict Thalassemia (CBC)

**POST** `/api/predict/cbc`

Predict thalassemia condition from CBC data.

**Request Body:**
```json
{
  "hb": 12.5,
  "rbc": 5.0,
  "mcv": 75.0,
  "mch": 25.0,
  "mchc": 32.0,
  "rdw": 14.5,
  "wbc": 7.0,
  "platelets": 250.0
}
```

**Response:**
```json
{
  "condition": "normal",
  "confidence": 0.85,
  "probabilities": {
    "normal": 0.85,
    "minor": 0.10,
    "major": 0.05
  }
}
```

---

### Model Information

**GET** `/api/model/info`

Get information about the loaded model.

**Response:**
```json
{
  "model_type": "hybrid",
  "num_classes": 3,
  "image_size": 224,
  "status": "loaded"
}
```

---

### Blockchain Status

**GET** `/api/blockchain/status`

Get blockchain status.

**Response:**
```json
{
  "enabled": true,
  "network": "ganache",
  "blocks": 15
}
```

---

### Federated Learning Status

**GET** `/api/federated/status`

Get FL training status.

**Response:**
```json
{
  "fl_rounds": 10,
  "min_clients": 2,
  "aggregation_method": "fedavg",
  "current_round": 5
}
```

---

### Register Hospital

**POST** `/api/hospital/register`

Register a hospital as FL client.

**Request Body:**
```json
{
  "hospital_id": "hospital_italy",
  "organization": "Hospital Italy",
  "data_size": 1000
}
```

**Response:**
```json
{
  "status": "registered",
  "hospital_id": "hospital_italy",
  "message": "Hospital successfully registered for federated learning"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `402`: Payment Required (x402 inference)
- `404`: Not Found
- `500`: Internal Server Error

---

## FedNet Layer 3: x402 Inference Endpoint

### Query Model (Payment-Gated)

**POST** `/inference`

Run inference on the trained federated model. Requires x402 USDC payment.

**Request Body:**
```json
{
  "input": [0.1, 0.2, 0.3, 0.5, 0.8, 0.2, 0.1, 0.4],
  "payment_tx_id": "solana_tx_signature_here",
  "payer_wallet": "0xresearcher_wallet",
  "payment_amount": "0.05"
}
```

**Response (Success):**
```json
{
  "prediction": [-1.12, -2.97, 1.23],
  "inference_id": "000001",
  "model_version": "v1.2.3",
  "payment_verified": true
}
```

**Response (Payment Required):**
```
HTTP 402 Payment Required
{
  "error": "Payment required",
  "amount": "0.05 USDC",
  "payment_address": "solana_wallet_address"
}
```

## Example Usage

### Python

```python
import requests

# Predict thalassemia
data = {
    "hb": 12.5,
    "rbc": 5.0,
    "mcv": 75.0,
    "mch": 25.0,
    "mchc": 32.0,
    "rdw": 14.5,
    "wbc": 7.0,
    "platelets": 250.0
}

response = requests.post("http://localhost:5000/api/predict/cbc", json=data)
print(response.json())
```

### cURL

```bash
curl -X POST http://localhost:5000/api/predict/cbc \
  -H "Content-Type: application/json" \
  -d '{
    "hb": 12.5,
    "rbc": 5.0,
    "mcv": 75.0,
    "mch": 25.0,
    "mchc": 32.0,
    "rdw": 14.5,
    "wbc": 7.0,
    "platelets": 250.0
  }'
```

### JavaScript

```javascript
const data = {
  hb: 12.5,
  rbc: 5.0,
  mcv: 75.0,
  mch: 25.0,
  mchc: 32.0,
  rdw: 14.5,
  wbc: 7.0,
  platelets: 250.0
};

fetch('http://localhost:5000/api/predict/cbc', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(res => res.json())
.then(console.log);
```
