# FedNet Deployment Guide

## Deployment Options

1. **Local Development**: Run on local machine
2. **Docker**: Containerized deployment
3. **Azure ML**: Cloud-based FL
4. **Kubernetes**: Production-scale deployment

## Docker Deployment

### Build Images

```bash
docker-compose build
```

### Run Services

```bash
docker-compose up -d
```

This will start:
- API server on `localhost:5000`
- Dashboard on `localhost:3000`
- MongoDB for data storage
- Redis for caching

### Stop Services

```bash
docker-compose down
```

## Azure ML Deployment

### Prerequisites

1. Azure subscription
2. Azure CLI installed
3. Configured `.env` with Azure credentials

### Steps

1. **Create Workspace**
```bash
python azure_ml/setup_compute.py
```

2. **Upload Data**
```bash
python azure_ml/upload_data.py
```

3. **Deploy Pipeline**
```bash
python azure_ml/pipeline.py
```

4. **Deploy Model**
```bash
python azure_ml/deploy.py
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- kubectl configured
- Docker images pushed to registry

### Deploy

```bash
kubectl apply -f deployment/kubernetes/
```

### Services Deployed

- `fednet-api`: API service
- `fednet-dashboard`: Frontend
- `mongodb`: Database
- `redis`: Cache

### Check Status

```bash
kubectl get pods
kubectl get services
```

## Production Checklist

- [ ] Change all default secrets and keys
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable backup and disaster recovery
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline
- [ ] Perform security audit
- [ ] Set up rate limiting
- [ ] Configure CORS properly

## Monitoring

### Logs

```bash
# API logs
tail -f logs/fednet*.log

# Docker logs
docker-compose logs -f api

# Kubernetes logs
kubectl logs -f deployment/fednet-api
```

### Metrics

- Training metrics: TensorBoard or W&B
- API metrics: Prometheus + Grafana
- Blockchain: Custom dashboard

## Scaling

### Horizontal Scaling

Add more hospital clients:
```python
# In smart contract
contract.register_client("hospital_new", "Hospital New", 1500)
```

### Vertical Scaling

Increase Azure ML compute:
```bash
# Update azure_config.py
MAX_NODES = 10
VM_SIZE = "Standard_NC12"
```

## Troubleshooting

### Port Conflicts
Change ports in `docker-compose.yml` or `.env`

### Out of Memory
Increase Docker memory limits

### Network Issues
Check firewall and network policies

## Security Best Practices

1. Use environment variables for secrets
2. Enable encryption at rest and in transit
3. Implement authentication and authorization
4. Regular security updates
5. Audit logging enabled
6. Network segmentation
7. Rate limiting on API
