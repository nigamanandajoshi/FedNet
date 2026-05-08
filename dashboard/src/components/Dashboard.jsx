import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Grid, Card, CardContent, CardActionArea, Divider } from '@mui/material';
import { LocalHospital, AdminPanelSettings, CloudUpload, Assessment } from '@mui/icons-material';

export default function Dashboard() {
    const navigate = useNavigate();

    const portals = [
        {
            title: 'Hospital Portal',
            subtitle: 'Disease Checking Interface',
            description: 'Check patient CBC values and predict thalassemia conditions using the trained federated model',
            icon: <LocalHospital sx={{ fontSize: 60, color: '#0d9488' }} />,
            path: '/hospital-portal',
            color: '#0d9488'
        },
        {
            title: 'Admin Portal',
            subtitle: 'Model Training Monitor',
            description: 'Monitor federated learning progress from local models to global model aggregation',
            icon: <AdminPanelSettings sx={{ fontSize: 60, color: '#065f46' }} />,
            path: '/admin-portal',
            color: '#065f46'
        },
        {
            title: 'Data Upload Portal',
            subtitle: 'Hospital Data Contribution',
            description: 'Upload patient data and train local models for privacy-preserving federated learning',
            icon: <CloudUpload sx={{ fontSize: 60, color: '#059669' }} />,
            path: '/data-upload-portal',
            color: '#059669'
        }
    ];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 6 }}>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: 600 }}>
                    MedChain-FL Portal
                </Typography>
                <Typography variant="h6" color="text.secondary" paragraph>
                    Privacy-Preserving Federated Learning for Thalassemia Detection
                </Typography>
            </Box>

            <Grid container spacing={4} sx={{ mb: 4 }}>
                {portals.map((portal, index) => (
                    <Grid item xs={12} md={4} key={index}>
                        <Card
                            sx={{
                                height: '100%',
                                transition: 'transform 0.2s, box-shadow 0.2s',
                                '&:hover': {
                                    transform: 'translateY(-8px)',
                                    boxShadow: 6
                                }
                            }}
                        >
                            <CardActionArea
                                onClick={() => navigate(portal.path)}
                                sx={{ height: '100%', p: 3 }}
                            >
                                <CardContent sx={{ textAlign: 'center' }}>
                                    <Box sx={{ mb: 2 }}>
                                        {portal.icon}
                                    </Box>
                                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                                        {portal.title}
                                    </Typography>
                                    <Typography variant="subtitle1" color="primary" gutterBottom>
                                        {portal.subtitle}
                                    </Typography>
                                    <Divider sx={{ my: 2 }} />
                                    <Typography variant="body2" color="text.secondary" sx={{ minHeight: 60 }}>
                                        {portal.description}
                                    </Typography>
                                </CardContent>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                    <Card sx={{ bgcolor: 'primary.light' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Assessment sx={{ fontSize: 40, color: 'white', mb: 1 }} />
                            <Typography variant="h4" sx={{ color: 'white' }}>3</Typography>
                            <Typography variant="body2" sx={{ color: 'white' }}>
                                FL Rounds Completed
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card sx={{ bgcolor: 'success.main' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <LocalHospital sx={{ fontSize: 40, color: 'white', mb: 1 }} />
                            <Typography variant="h4" sx={{ color: 'white' }}>3</Typography>
                            <Typography variant="body2" sx={{ color: 'white' }}>
                                Active Hospitals
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card sx={{ bgcolor: 'info.main' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <CloudUpload sx={{ fontSize: 40, color: 'white', mb: 1 }} />
                            <Typography variant="h4" sx={{ color: 'white' }}>3,300</Typography>
                            <Typography variant="body2" sx={{ color: 'white' }}>
                                Total Samples
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card sx={{ bgcolor: 'warning.main' }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <AdminPanelSettings sx={{ fontSize: 40, color: 'white', mb: 1 }} />
                            <Typography variant="h4" sx={{ color: 'white' }}>100%</Typography>
                            <Typography variant="body2" sx={{ color: 'white' }}>
                                Model Accuracy
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
}
