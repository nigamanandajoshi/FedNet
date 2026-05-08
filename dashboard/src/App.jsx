import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ModelTraining from './components/ModelTraining';
import Prediction from './components/Prediction';
import Blockchain from './components/Blockchain';
import HospitalUpload from './components/HospitalUpload';
import FederatedModelUpdatePage from './components/FederatedModelUpdatePage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0d9488',
    },
    secondary: {
      main: '#065f46',
    },
    success: {
      main: '#059669',
    },
    info: {
      main: '#0f766e',
    },
    warning: {
      main: '#f59e0b'
    }
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        {/* No shared navigation - each portal is completely isolated */}
        <Routes>
          {/* Direct URL access only - no navigation between portals */}
          <Route path="/" element={<Prediction />} />
          <Route path="/hospital-portal" element={<Prediction />} />
          <Route path="/admin-portal" element={<ModelTraining />} />
          <Route path="/data-upload-portal" element={<HospitalUpload />} />
          <Route path="/blockchain" element={<Blockchain />} />
          <Route path="/federated-success" element={<FederatedModelUpdatePage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
