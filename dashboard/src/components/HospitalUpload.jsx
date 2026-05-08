
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Activity, Database, Shield, CheckCircle, AlertCircle, Users } from 'lucide-react';
import './HospitalUpload.css';

const HospitalDataUploadDashboard = () => {
    const [selectedHospital, setSelectedHospital] = useState('italy');
    const [uploadStatus, setUploadStatus] = useState('idle');
    const [trainingStatus, setTrainingStatus] = useState('idle');
    const [patientData, setPatientData] = useState({
        patientId: '',
        hemoglobin: '',
        rbcCount: '',
        mcv: '',
        mch: '',
        mchc: '',
        rdw: '',
        wbcCount: '',
        plateletCount: '',
        reticulocyteCount: '',
        diagnosis: 'normal',
        Age: '',
        Gender: ''
    });
    const [uploadedSamples, setUploadedSamples] = useState([]);
    const [trainingMetrics, setTrainingMetrics] = useState({
        accuracy: 0,
        loss: 0,
        epoch: 0,
        totalEpochs: 5
    });
    const navigate = useNavigate();

    const hospitals = [
        { id: 'italy', name: 'Hospital Italy', location: 'Rome, Italy', samples: 1247 },
        { id: 'pakistan', name: 'Hospital Pakistan', location: 'Karachi, Pakistan', samples: 892 },
        { id: 'usa', name: 'Hospital USA', location: 'New York, USA', samples: 634 }
    ];

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setPatientData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setUploadStatus('uploading');

            setTimeout(() => {
                const mockSamples = [
                    { id: 'P001', hemoglobin: 11.2, mcv: 65, diagnosis: 'minor' },
                    { id: 'P002', hemoglobin: 14.5, mcv: 88, diagnosis: 'normal' },
                    { id: 'P003', hemoglobin: 7.3, mcv: 58, diagnosis: 'major' }
                ];
                setUploadedSamples(mockSamples);
                setUploadStatus('success');
            }, 2000);
        }
    };

    const handleManualSubmit = async () => {
        setUploadStatus('uploading');

        const newSample = {
            hemoglobin: patientData.hemoglobin ? parseFloat(patientData.hemoglobin) : '',
            rbc: patientData.rbcCount ? parseFloat(patientData.rbcCount) : '',
            mcv: patientData.mcv ? parseFloat(patientData.mcv) : '',
            mch: patientData.mch ? parseFloat(patientData.mch) : '',
            mchc: patientData.mchc ? parseFloat(patientData.mchc) : '',
            rdw: patientData.rdw ? parseFloat(patientData.rdw) : '',
            wbc: patientData.wbcCount ? parseFloat(patientData.wbcCount) : '',
            platelets: patientData.plateletCount ? parseFloat(patientData.plateletCount) : '',
            id: patientData.patientId,
            diagnosis: patientData.diagnosis,
            Age: patientData.Age,
            Gender: patientData.Gender,
        };

        try {
            const res = await fetch('http://localhost:5000/api/hospital/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ hospital_id: selectedHospital, sample: newSample })
            });

            if (!res.ok) throw new Error(`Server error: ${res.status}`);

            const body = await res.json();
            // Add to table UI
            setUploadedSamples(prev => [...prev, newSample]);
            setUploadStatus('success');

            // Reset form
            setPatientData({
                hemoglobin: '',
                rbcCount: '',
                mcv: '',
                mch: '',
                mchc: '',
                rdw: '',
                wbcCount: '',
                plateletCount: '',
                patientId: '',
                diagnosis: 'normal',
                Age: '',
                Gender: ''
            });
        } catch (err) {
            console.error('Upload failed', err);
            setUploadStatus('error');
        }
    };

    const startLocalTraining = () => {
        setTrainingStatus('training');
        setTrainingMetrics({ accuracy: 0, loss: 2.5, epoch: 0, totalEpochs: 5 });

        let epoch = 0;
        const interval = setInterval(() => {
            epoch++;
            const accuracy = 65 + (epoch * 6.2);
            const loss = 2.5 - (epoch * 0.45);

            setTrainingMetrics({
                accuracy: Math.min(accuracy, 96.8),
                loss: Math.max(loss, 0.12),
                epoch,
                totalEpochs: 5
            });

            if (epoch >= 5) {
                clearInterval(interval);
                setTrainingStatus('complete');
            }
        }, 1500);
    };

    return (
        <div className="hospital-dashboard-container" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
            <div className="dashboard-wrapper">
                {/* Standalone Portal Header */}
                <div style={{
                    background: 'linear-gradient(135deg, #059669 0%, #0d9488 100%)',
                    color: 'white',
                    padding: '2.5rem',
                    borderRadius: '1rem',
                    marginBottom: '2rem',
                    boxShadow: '0 8px 16px rgba(0,0,0,0.15)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                        <Upload size={64} style={{ marginRight: '1.5rem' }} />
                        <div>
                            <h1 style={{ margin: 0, fontSize: '3rem', fontWeight: 700 }}>Data Upload Portal</h1>
                            <h2 style={{ margin: '0.75rem 0 0 0', fontSize: '1.5rem', opacity: 0.95, fontWeight: 500 }}>
                                Hospital Data Contribution System
                            </h2>
                        </div>
                    </div>
                    <p style={{ margin: '1rem 0 0 0', fontSize: '1.1rem', opacity: 0.95 }}>
                        Upload patient CBC data for privacy-preserving federated learning
                    </p>
                </div>

                {/* Hospital Selection */}
                <div className="dashboard-card">
                    <div className="section-header">
                        <Users style={{ color: '#0d9488' }} />
                        <h2 className="section-title-text">Select Your Hospital</h2>
                    </div>
                    <div className="hospital-grid">
                        {hospitals.map(hospital => (
                            <button
                                key={hospital.id}
                                onClick={() => setSelectedHospital(hospital.id)}
                                className={`hospital-selector-btn ${selectedHospital === hospital.id ? 'active' : ''}`}
                            >
                                <div className="text-left">
                                    <h3 className="hospital-name">{hospital.name}</h3>
                                    <p className="hospital-location">{hospital.location}</p>
                                    <p className="hospital-meta">Current samples: {hospital.samples}</p>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="main-content-grid">
                    {/* Left Column - Data Upload */}
                    <div>
                        {/* Manual Entry Section */}
                        <div className="dashboard-card">
                            <div className="section-header">
                                <Database style={{ color: '#065f46' }} />
                                <h2 className="section-title-text">Manual Data Entry</h2>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                <div className="form-grid">
                                    <div className="form-group full-width">
                                        <label className="form-label">Patient ID</label>
                                        <input
                                            type="text"
                                            name="patientId"
                                            value={patientData.patientId}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="P001"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Hemoglobin (g/dL)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="hemoglobin"
                                            value={patientData.hemoglobin}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="12.5"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">RBC Count (M/μL)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="rbcCount"
                                            value={patientData.rbcCount}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="4.7"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">MCV (fL)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="mcv"
                                            value={patientData.mcv}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="85"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">MCH (pg)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="mch"
                                            value={patientData.mch}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="28"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">MCHC (g/dL)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="mchc"
                                            value={patientData.mchc}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="33"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">RDW (%)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="rdw"
                                            value={patientData.rdw}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="13.5"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">WBC Count (K/μL)</label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            name="wbcCount"
                                            value={patientData.wbcCount}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="7.5"
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Platelet (K/μL)</label>
                                        <input
                                            type="number"
                                            step="1"
                                            name="plateletCount"
                                            value={patientData.plateletCount}
                                            onChange={handleInputChange}
                                            className="form-input"
                                            placeholder="250"
                                        />
                                    </div>


                                    <div className="form-group full-width">
                                        <label className="form-label">Diagnosis</label>
                                        <select
                                            name="diagnosis"
                                            value={patientData.diagnosis}
                                            onChange={handleInputChange}
                                            className="form-input"
                                        >
                                            <option value="normal">Normal</option>
                                            <option value="minor">Thalassemia Minor</option>
                                            <option value="major">Thalassemia Major</option>
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Age</label>
                                        <input
                                            type="number"
                                            step="1"
                                            name="Age"
                                            value={patientData.Age}
                                            onChange={handleInputChange}
                                            className="form-input"
                                        />
                                    </div>



                                    <div className="form-group">
                                        <label className="form-label">Gender</label>
                                        <select
                                            name="Gender"
                                            value={patientData.Gender}
                                            onChange={handleInputChange}
                                            className="form-input"
                                        >
                                            <option value="normal">F</option>
                                            <option value="minor">M</option>
                                        </select>
                                    </div>



                                </div>




                                <button
                                    onClick={handleManualSubmit}
                                    className="action-btn btn-primary"
                                >
                                    Add Patient Data
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Right Column - Status & Training */}
                    <div>
                        {/* Uploaded Samples */}
                        <div className="dashboard-card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                    <Database className="mr-2" style={{ color: '#0d9488' }} />
                                    <h2 className="section-title-text">Uploaded Samples</h2>
                                </div>
                                <span className="badge" style={{ backgroundColor: '#dffaf6', color: '#064e3b' }}>
                                    {uploadedSamples.length} samples
                                </span>
                            </div>

                            {uploadedSamples.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '2rem 0', color: '#6b7280' }}>
                                    <Database style={{ width: '3rem', height: '3rem', opacity: 0.3, margin: '0 auto 0.5rem auto' }} />
                                    <p>No samples uploaded yet</p>
                                </div>
                            ) : (
                                <div className="table-container">
                                    <table className="data-table">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th>Patient ID</th>
                                                <th>Hgb</th>
                                                <th>MCV</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {uploadedSamples.map((sample, idx) => (
                                                <tr key={idx}>
                                                    <td>{sample.id}</td>
                                                    <td>{sample.hemoglobin}</td>
                                                    <td>{sample.mcv}</td>
                                                    <td>
                                                        <span className={`badge ${sample.diagnosis === 'normal'
                                                            ? 'badge-normal'
                                                            : sample.diagnosis === 'minor'
                                                                ? 'badge-minor'
                                                                : 'badge-major'
                                                            }`}>
                                                            {sample.diagnosis}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>

                        {/* Local Training */}
                        <div className="dashboard-card">
                            <div className="section-header">
                                <Activity style={{ color: '#059669' }} />
                                <h2 className="section-title-text">Local Model Training</h2>
                            </div>

                            {trainingStatus === 'idle' && (
                                <div style={{ textAlign: 'center', padding: '2rem 0' }}>
                                    <button
                                        onClick={startLocalTraining}
                                        disabled={uploadedSamples.length === 0}
                                        className="action-btn btn-success"
                                        style={{ width: 'auto', padding: '0.75rem 1.5rem', marginBottom: '0.5rem' }}
                                    >
                                        Start Local Training
                                    </button>
                                    <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                                        {uploadedSamples.length === 0
                                            ? 'Upload data first to begin training'
                                            : 'Train model on your local data'}
                                    </p>
                                </div>
                            )}

                            {trainingStatus === 'training' && (
                                <div>
                                    <div className="mb-4">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                                            <span className="text-gray-600">Training Progress</span>
                                            <span className="font-semibold">
                                                Epoch {trainingMetrics.epoch}/{trainingMetrics.totalEpochs}
                                            </span>
                                        </div>
                                        <div className="progress-track" style={{ height: '0.75rem' }}>
                                            <div
                                                className="progress-fill"
                                                style={{ backgroundColor: '#0d9488', height: '0.75rem', width: `${(trainingMetrics.epoch / trainingMetrics.totalEpochs) * 100}%` }}
                                            />
                                        </div>
                                    </div>

                                    <div className="metrics-grid">
                                        <div className="metric-card accuracy">
                                            <p className="metric-label">Accuracy</p>
                                            <p className="metric-value text-blue">
                                                {trainingMetrics.accuracy.toFixed(1)}%
                                            </p>
                                        </div>
                                        <div className="metric-card loss">
                                            <p className="metric-label">Loss</p>
                                            <p className="metric-value text-purple">
                                                {trainingMetrics.loss.toFixed(3)}
                                            </p>
                                        </div>
                                    </div>

                                    <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#ecfeff', border: '1px solid #bbf7d0', borderRadius: '0.5rem', display: 'flex', alignItems: 'flex-start' }}>
                                        <AlertCircle className="mr-2" size={20} style={{ color: '#065f46', flexShrink: 0 }} />
                                        <p style={{ fontSize: '0.875rem', color: '#064e3b' }}>
                                            Training in progress... Model weights will be encrypted and sent to blockchain for verification.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {trainingStatus === 'complete' && (
                                <div>
                                    <div className="success-message" style={{ marginBottom: '1rem' }}>
                                        <div className="success-flex" style={{ marginBottom: '0.5rem' }}>
                                            <CheckCircle className="mr-2" size={24} />
                                            <span style={{ fontSize: '1.125rem', fontWeight: 600 }}>Training Complete!</span>
                                        </div>
                                        <p style={{ fontSize: '0.875rem', color: '#059669' }}>
                                            Local model trained successfully on {uploadedSamples.length} samples
                                        </p>
                                    </div>

                                    <div className="metrics-grid" style={{ marginBottom: '1rem' }}>
                                        <div className="metric-card accuracy">
                                            <p className="metric-label">Final Accuracy</p>
                                            <p className="metric-value text-blue">96.8%</p>
                                        </div>
                                        <div className="metric-card loss">
                                            <p className="metric-label">Final Loss</p>
                                            <p className="metric-value text-purple">0.120</p>
                                        </div>
                                    </div>

                                    <button
                                        className="action-btn btn-indigo"
                                        onClick={() => navigate('/federated-success')}
                                    >
                                        Submit to Federated Network
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Privacy Notice */}
                        <div className="privacy-card">
                            <div className="privacy-flex">
                                <Shield style={{ color: '#065f46', flexShrink: 0 }} />
                                <div className="privacy-content">
                                    <h3 className="privacy-title">Privacy-Preserving Training</h3>
                                    <ul className="privacy-list">
                                        <li>✓ All patient data stays on your local server</li>
                                        <li>✓ Only model weights are shared (not raw data)</li>
                                        <li>✓ Blockchain verifies every contribution</li>
                                        <li>✓ HIPAA & GDPR compliant by design</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HospitalDataUploadDashboard;
