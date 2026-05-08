"""API routes and endpoints."""

from flask import Blueprint, request, jsonify
import torch
import numpy as np
from pathlib import Path
import csv
import os
from models.thalassemia_models import get_model
from models.model_utils import load_model
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Global model (loaded on startup)
global_model = None


@api_bp.route('/predict/cbc', methods=['POST'])
def predict_cbc():
    """
    Predict thalassemia from CBC data.
    
    Request body:
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
    """
    try:
        data = request.get_json()
        
        # Extract features
        features = np.array([[
            data['hb'],
            data['rbc'],
            data['mcv'],
            data['mch'],
            data['mchc'],
            data['rdw'],
            data['wbc'],
            data['platelets']
        ]], dtype=np.float32)
        
        # Normalize (you should use the same scaler from training)
        features_tensor = torch.FloatTensor(features)
        
        # Predict (placeholder - load actual model)
        # prediction = model(features_tensor)
        
        # Mock prediction
        prediction = {
            'condition': 'normal',
            'confidence': 0.85,
            'probabilities': {
                'normal': 0.85,
                'minor': 0.10,
                'major': 0.05
            }
        }
        
        return jsonify(prediction)
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400


@api_bp.route('/model/info', methods=['GET'])
def model_info():
    """Get model information."""
    return jsonify({
        'model_type': settings.model_type,
        'num_classes': settings.num_classes,
        'image_size': settings.image_size,
        'status': 'loaded' if global_model else 'not_loaded'
    })


@api_bp.route('/blockchain/status', methods=['GET'])
def blockchain_status():
    """Get blockchain status."""
    # Placeholder - integrate with actual blockchain
    return jsonify({
        'enabled': settings.blockchain_enabled,
        'network': settings.blockchain_network,
        'blocks': 0
    })


@api_bp.route('/federated/status', methods=['GET'])
def federated_status():
    """Get federated learning status."""
    return jsonify({
        'fl_rounds': settings.fl_rounds,
        'min_clients': settings.min_clients,
        'aggregation_method': settings.aggregation_method,
        'current_round': 0
    })


@api_bp.route('/hospital/register', methods=['POST'])
def register_hospital():
    """
    Register a hospital as FL client.
    
    Request body:
    {
        "hospital_id": "hospital_italy",
        "organization": "Hospital Italy",
        "data_size": 1000
    }
    """
    try:
        data = request.get_json()
        
        # Placeholder - integrate with smart contract
        response = {
            'status': 'registered',
            'hospital_id': data['hospital_id'],
            'message': 'Hospital successfully registered for federated learning'
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 400


@api_bp.route('/hospital/upload', methods=['POST'])
def hospital_upload():
    """
    Accept a single patient sample and append to the hospital CSV file.

    Expected JSON body:
    {
        "hospital_id": "italy",
        "sample": {
            "id": "P001",
            "hemoglobin": 12.3,
            "mcv": 85,
            "mch": 28,
            "mchc": 33,
            "rdw": 13.5,
            "wbc": 7.5,
            "platelets": 250,
            "reticulocyte": 1.5,
            "diagnosis": "normal"
        }
    }
    """
    try:
        data = request.get_json()
        hospital_id = data.get('hospital_id')
        sample = data.get('sample')

        if not hospital_id or not sample:
            return jsonify({'error': 'hospital_id and sample required'}), 400

        # Build path to hospital CSV
        # settings.data_dir is a Path
        hospital_dir = settings.data_dir / f"hospital_{hospital_id}"
        hospital_dir.mkdir(parents=True, exist_ok=True)
        csv_path = hospital_dir / 'cbc_data.csv'

        # Determine headers: if CSV exists, reuse its header order to preserve extra columns (age, gender, etc.)
        target_headers = ['hb', 'rbc', 'mcv', 'mch', 'mchc', 'rdw', 'wbc', 'platelets', 'patient_id', 'condition']
        if csv_path.exists():
            with open(csv_path, 'r', newline='', encoding='utf-8') as rf:
                reader = csv.reader(rf)
                try:
                    existing_headers = next(reader)
                except StopIteration:
                    existing_headers = target_headers
            headers = existing_headers
            write_header = False
        else:
            headers = target_headers
            write_header = True

        def _get_val(*keys):
            for k in keys:
                if k in sample and sample.get(k) is not None and sample.get(k) != '':
                    return sample.get(k)
            return ''

        # Candidate sample values
        mapped = {
            'patient_id': _get_val('id', 'patient_id', 'patientId'),
            'hb': _get_val('hb', 'hemoglobin', 'hgb'),
            'rbc': _get_val('rbc', 'rbcCount', 'rbc_count'),
            'mcv': _get_val('mcv'),
            'mch': _get_val('mch'),
            'mchc': _get_val('mchc'),
            'rdw': _get_val('rdw'),
            'wbc': _get_val('wbc', 'wbcCount', 'wbc_count'),
            'platelets': _get_val('platelets', 'plateletCount', 'platelet_count'),
            'reticulocyte': _get_val('reticulocyte', 'reticulocyteCount'),
            'condition': _get_val('condition', 'diagnosis'),
            'age': _get_val('age'),
            'gender': _get_val('gender')
        }

        # Build row following headers order
        row_values = []
        for h in headers:
            key = h
            # normalize common header names
            if h in ('id', 'patient_id', 'patientId', 'patient_id'):
                row_values.append(mapped['patient_id'])
            elif h in ('hb', 'hgb'):
                row_values.append(mapped['hb'])
            elif h == 'rbc':
                row_values.append(mapped['rbc'])
            elif h == 'mcv':
                row_values.append(mapped['mcv'])
            elif h == 'mch':
                row_values.append(mapped['mch'])
            elif h == 'mchc':
                row_values.append(mapped['mchc'])
            elif h == 'rdw':
                row_values.append(mapped['rdw'])
            elif h == 'wbc':
                row_values.append(mapped['wbc'])
            elif h == 'platelets':
                row_values.append(mapped['platelets'])
            elif h == 'reticulocyte':
                row_values.append(mapped['reticulocyte'])
            elif h == 'condition':
                row_values.append(mapped['condition'])
            elif h == 'age':
                row_values.append(mapped['age'])
            elif h == 'gender':
                row_values.append(mapped['gender'])
            else:
                # attempt to pull from sample directly for unknown headers
                row_values.append(sample.get(h, ''))

        # Try to coerce numeric fields where appropriate (hb..platelets, age)
        numeric_fields = set(['hb','rbc','mcv','mch','mchc','rdw','wbc','platelets','reticulocyte','age'])
        for idx, h in enumerate(headers):
            if h in numeric_fields and row_values[idx] not in ('', None):
                try:
                    row_values[idx] = float(row_values[idx])
                except Exception:
                    pass

        # Append row preserving header order
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(headers)
            writer.writerow(row_values)

        logger.info(f"Appended sample to {csv_path}")
        return jsonify({'status': 'ok', 'sample': sample}), 200

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500
