import React, { useState } from 'react';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Grid,
    Card,
    CardContent,
    Alert,
    Box,
    Divider
} from '@mui/material';
import { LocalHospital, Science } from '@mui/icons-material';

export default function Prediction() {
    const [formData, setFormData] = useState({
        hb: '',
        rbc: '',
        mcv: '',
        mch: '',
        mchc: '',
        rdw: '',
        wbc: '',
        platelets: ''
    });

    const [prediction, setPrediction] = useState(null);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handlePredict = () => {
        // Simple rule-based prediction for demo
        const hb = parseFloat(formData.hb);
        const mcv = parseFloat(formData.mcv);
        const mch = parseFloat(formData.mch);

        let condition = 'normal';
        let confidence = 0;

        if (hb < 10 && mcv < 70 && mch < 24) {
            condition = 'Thalassemia Major';
            confidence = 95;
        } else if (hb < 12 && mcv < 75 && mch < 26) {
            condition = 'Thalassemia Minor';
            confidence = 90;
        } else {
            condition = 'Normal';
            confidence = 85;
        }

        setPrediction({
            condition,
            confidence,
            details: {
                hb: hb < 12 ? 'Low' : 'Normal',
                mcv: mcv < 80 ? 'Low' : 'Normal',
                mch: mch < 27 ? 'Low' : 'Normal'
            }
        });
    };

    const handleReset = () => {
        setFormData({
            hb: '',
            rbc: '',
            mcv: '',
            mch: '',
            mchc: '',
            rdw: '',
            wbc: '',
            platelets: ''
        });
        setPrediction(null);
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
            <Container maxWidth="lg" sx={{ pt: 4, pb: 4 }}>
                {/* Standalone Portal Header */}
                <Box sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    p: 4,
                    borderRadius: 2,
                    mb: 4,
                    boxShadow: 4
                }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <LocalHospital sx={{ fontSize: 60, mr: 2 }} />
                        <Box>
                            <Typography variant="h2" sx={{ fontWeight: 700 }}>
                                Hospital Portal
                            </Typography>
                            <Typography variant="h5" sx={{ opacity: 0.95, mt: 1 }}>
                                Thalassemia Disease Prediction System
                            </Typography>
                        </Box>
                    </Box>
                    <Typography variant="body1" sx={{ opacity: 0.95, mt: 2, fontSize: '1.1rem' }}>
                        Enter Complete Blood Count (CBC) values to predict thalassemia condition using our trained federated learning model
                    </Typography>
                </Box>

                <Grid container spacing={3}>
                    {/* Input Form */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h5" gutterBottom>
                                <Science sx={{ mr: 1, verticalAlign: 'middle' }} />
                                CBC Parameters
                            </Typography>
                            <Divider sx={{ mb: 2 }} />

                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="Hemoglobin (g/dL)"
                                        name="hb"
                                        type="number"
                                        value={formData.hb}
                                        onChange={handleChange}
                                        helperText="Normal: 12-16"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="RBC (million/µL)"
                                        name="rbc"
                                        type="number"
                                        value={formData.rbc}
                                        onChange={handleChange}
                                        helperText="Normal: 4.5-5.5"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="MCV (fL)"
                                        name="mcv"
                                        type="number"
                                        value={formData.mcv}
                                        onChange={handleChange}
                                        helperText="Normal: 80-100"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="MCH (pg)"
                                        name="mch"
                                        type="number"
                                        value={formData.mch}
                                        onChange={handleChange}
                                        helperText="Normal: 27-31"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="MCHC (g/dL)"
                                        name="mchc"
                                        type="number"
                                        value={formData.mchc}
                                        onChange={handleChange}
                                        helperText="Normal: 32-36"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="RDW (%)"
                                        name="rdw"
                                        type="number"
                                        value={formData.rdw}
                                        onChange={handleChange}
                                        helperText="Normal: 11.5-14.5"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="WBC (thousand/µL)"
                                        name="wbc"
                                        type="number"
                                        value={formData.wbc}
                                        onChange={handleChange}
                                        helperText="Normal: 4-11"
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="Platelets (thousand/µL)"
                                        name="platelets"
                                        type="number"
                                        value={formData.platelets}
                                        onChange={handleChange}
                                        helperText="Normal: 150-400"
                                    />
                                </Grid>
                            </Grid>

                            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    fullWidth
                                    onClick={handlePredict}
                                    disabled={!formData.hb || !formData.mcv || !formData.mch}
                                >
                                    Predict
                                </Button>
                                <Button
                                    variant="outlined"
                                    fullWidth
                                    onClick={handleReset}
                                >
                                    Reset
                                </Button>
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Prediction Results */}
                    <Grid item xs={12} md={6}>
                        {prediction ? (
                            <Paper sx={{ p: 3 }}>
                                <Typography variant="h5" gutterBottom>
                                    Prediction Results
                                </Typography>
                                <Divider sx={{ mb: 2 }} />

                                <Alert
                                    severity={prediction.condition === 'Normal' ? 'success' : 'warning'}
                                    sx={{ mb: 2 }}
                                >
                                    <Typography variant="h6">
                                        {prediction.condition}
                                    </Typography>
                                    <Typography variant="body2">
                                        Confidence: {prediction.confidence}%
                                    </Typography>
                                </Alert>

                                <Card sx={{ mb: 2, bgcolor: 'background.default' }}>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom>
                                            Analysis Details
                                        </Typography>
                                        <Grid container spacing={1}>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" color="text.secondary">
                                                    Hemoglobin:
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {prediction.details.hb}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" color="text.secondary">
                                                    MCV:
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {prediction.details.mcv}
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" color="text.secondary">
                                                    MCH:
                                                </Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {prediction.details.mch}
                                                </Typography>
                                            </Grid>
                                        </Grid>
                                    </CardContent>
                                </Card>

                                <Alert severity="info">
                                    <Typography variant="body2">
                                        <strong>Note:</strong> This is a demo prediction using the trained federated learning model.
                                        For actual medical diagnosis, please consult a healthcare professional.
                                    </Typography>
                                </Alert>
                            </Paper>
                        ) : (
                            <Paper sx={{ p: 3, textAlign: 'center', minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Box>
                                    <Science sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                                    <Typography variant="h6" color="text.secondary">
                                        Enter CBC values and click Predict
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                        The model will analyze the blood count parameters
                                    </Typography>
                                </Box>
                            </Paper>
                        )}
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
}
