import React, { useState, useEffect } from 'react';
import { CheckCircle, TrendingUp, Award, Lock, Network, Database, Activity, ArrowRight, Download, Globe } from 'lucide-react';
import './FederatedModelUpdatePage.css';

const FederatedModelUpdatePage = () => {
  const [animationStep, setAnimationStep] = useState(0);
  const [contributionReward, setContributionReward] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Animate steps sequentially
    const steps = [0, 1, 2, 3, 4];
    steps.forEach((step, index) => {
      setTimeout(() => {
        setAnimationStep(step);
        if (step === 4) {
          setShowConfetti(true);
        }
      }, index * 1500);
    });

    // Animate reward counter
    let current = 0;
    const target = 1250;
    const increment = target / 50;
    const interval = setInterval(() => {
      current += increment;
      if (current >= target) {
        setContributionReward(target);
        clearInterval(interval);
      } else {
        setContributionReward(Math.floor(current));
      }
    }, 30);

    return () => clearInterval(interval);
  }, []);

  const hospitals = [
    { name: 'Hospital Italy', contribution: 'Model Weights Verified', samples: 1247, accuracy: 94.2, color: 'blue' },
    { name: 'Hospital Pakistan', contribution: 'Model Weights Verified', samples: 892, accuracy: 92.8, color: 'green' },
    { name: 'Hospital USA', contribution: 'Model Weights Verified ✓', samples: 634, accuracy: 96.8, color: 'purple', isYou: true }
  ];

  const beforeAfterMetrics = {
    before: {
      accuracy: 89.4,
      sensitivity: 87.2,
      specificity: 90.1,
      samples: 2139
    },
    after: {
      accuracy: 94.7,
      sensitivity: 93.5,
      specificity: 95.2,
      samples: 2773
    }
  };

  const blockchainBlocks = [
    { id: 'block_031', hash: 'a3f592b1...', hospital: 'Italy', verified: true, time: '3 min ago' },
    { id: 'block_032', hash: 'b7e243d9...', hospital: 'Pakistan', verified: true, time: '2 min ago' },
    { id: 'block_033', hash: 'c9a184f2...', hospital: 'USA', verified: true, time: 'Just now', highlight: true }
  ];

  return (
    <div className="federated-page-container">
      {/* Animated Background */}
      <div className="bg-bubbles">
        <div className="bubble" style={{ width: '200px', height: '200px', background: '#bfdbfe', top: '10%', left: '10%' }}></div>
        <div className="bubble" style={{ width: '150px', height: '150px', background: '#bbf7d0', top: '20%', right: '10%', animationDelay: '1s' }}></div>
        <div className="bubble" style={{ width: '180px', height: '180px', background: '#e9d5ff', bottom: '10%', left: '20%', animationDelay: '2s' }}></div>
      </div>

      {/* Confetti Effect */}
      {showConfetti && (
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="fed-confetti-dot"
              style={{
                left: `${Math.random() * 100}%`,
                backgroundColor: ['#0d9488', '#059669', '#f59e0b', '#ef4444', '#8b5cf6'][Math.floor(Math.random() * 5)],
                animationDuration: `${2 + Math.random() * 2}s`,
                animationDelay: `${Math.random() * 0.5}s`
              }}
            />
          ))}
        </div>
      )}

      <div className="federated-wrapper">
        {/* Success Header */}
        <div className="success-header-container" style={{ opacity: animationStep >= 0 ? 1 : 0, transition: 'opacity 1s' }}>
          <div className={`success-icon-wrapper ${animationStep >= 0 ? 'animate-scale-in' : ''}`}>
            <CheckCircle style={{ width: '4rem', height: '4rem', color: '#059669' }} />
          </div>
          <h1 className="page-title">
            Federated Model Successfully Updated! 🎉
          </h1>
          <p className="page-subtitle">
            Your contribution has been verified on the blockchain and integrated into the global model.
          </p>
        </div>

        {/* Process Flow Visualization */}
        <div className="federated-card animate-fade-in" style={{ opacity: animationStep >= 1 ? 1 : 0 }}>
          <h2 className="section-title">
            <Activity className="section-icon blue" size={28} />
            Federated Learning Process Completed
          </h2>

          <div className="grid-5-col">
            {/* Step 1: Local Training */}
            <div className="process-step" style={{ opacity: animationStep >= 1 ? 1 : 0.3 }}>
              <div className="step-icon-circle blue">
                <Database size={32} />
              </div>
              <h3 className="step-title">Local Training</h3>
              <p className="step-desc">Your hospital trained the model locally</p>
              <CheckCircle size={20} className="text-green-600 mt-2" />
            </div>

            <div className="step-nav-arrow">
              <ArrowRight size={24} />
            </div>

            {/* Step 2: Blockchain Verification */}
            <div className="process-step" style={{ opacity: animationStep >= 2 ? 1 : 0.3 }}>
              <div className="step-icon-circle indigo">
                <Lock size={32} />
              </div>
              <h3 className="step-title">Blockchain Verified</h3>
              <p className="step-desc">Weights cryptographically secured</p>
              <CheckCircle size={20} className="text-green-600 mt-2" />
            </div>

            <div className="step-nav-arrow">
              <ArrowRight size={24} />
            </div>

            {/* Step 3: Global Aggregation */}
            <div className="process-step" style={{ opacity: animationStep >= 3 ? 1 : 0.3 }}>
              <div className="step-icon-circle green">
                <Network size={32} />
              </div>
              <h3 className="step-title">Global Update</h3>
              <p className="step-desc">Model aggregated across all hospitals</p>
              <CheckCircle size={20} className="text-green-600 mt-2" />
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="master-progress-container">
            <div className="master-progress-track">
              <div
                className="master-progress-fill"
                style={{ width: animationStep >= 3 ? '100%' : `${(animationStep / 3) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Before/After Comparison */}
        <div className="federated-card animate-fade-in" style={{ opacity: animationStep >= 2 ? 1 : 0 }}>
          <h2 className="section-title">
            <TrendingUp className="section-icon green" size={28} />
            Global Model Performance Improvement
          </h2>

          <div className="grid-2-col">
            {/* Before */}
            <div>
              <h3 className="step-title text-center mb-4">Before Your Contribution</h3>
              <div className="comparison-card before">
                <div className="metric-row">
                  <span className="metric-name">Accuracy</span>
                  <span className="metric-val">{beforeAfterMetrics.before.accuracy}%</span>
                </div>
              </div>
              <div className="comparison-card before">
                <div className="metric-row">
                  <span className="metric-name">Sensitivity</span>
                  <span className="metric-val">{beforeAfterMetrics.before.sensitivity}%</span>
                </div>
              </div>
              <div className="comparison-card before">
                <div className="metric-row">
                  <span className="metric-name">Specificity</span>
                  <span className="metric-val">{beforeAfterMetrics.before.specificity}%</span>
                </div>
              </div>
              <div className="comparison-card before">
                <div className="metric-row">
                  <span className="metric-name">Total Samples</span>
                  <span className="metric-val">{beforeAfterMetrics.before.samples.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* After */}
            <div>
              <h3 className="step-title text-center mb-4" style={{ color: '#059669' }}>After Your Contribution ✓</h3>
              <div className="comparison-card after">
                <div className="metric-row">
                  <span className="metric-name">Accuracy</span>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="metric-val improved">{beforeAfterMetrics.after.accuracy}%</span>
                    <span className="metric-delta">
                      +{(beforeAfterMetrics.after.accuracy - beforeAfterMetrics.before.accuracy).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="comparison-card after">
                <div className="metric-row">
                  <span className="metric-name">Sensitivity</span>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="metric-val improved">{beforeAfterMetrics.after.sensitivity}%</span>
                    <span className="metric-delta">
                      +{(beforeAfterMetrics.after.sensitivity - beforeAfterMetrics.before.sensitivity).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="comparison-card after">
                <div className="metric-row">
                  <span className="metric-name">Specificity</span>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="metric-val improved">{beforeAfterMetrics.after.specificity}%</span>
                    <span className="metric-delta">
                      +{(beforeAfterMetrics.after.specificity - beforeAfterMetrics.before.specificity).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="comparison-card after">
                <div className="metric-row">
                  <span className="metric-name">Total Samples</span>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="metric-val improved">{beforeAfterMetrics.after.samples.toLocaleString()}</span>
                    <span className="metric-delta">
                      +{(beforeAfterMetrics.after.samples - beforeAfterMetrics.before.samples).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Impact Statement */}
          <div className="impact-box">
            <p className="impact-text">
              🎯 Your contribution improved the global model by <span className="highlight-green">+5.3%</span>,
              potentially helping diagnose thalassemia in <span className="highlight-blue">thousands</span> of patients worldwide!
            </p>
          </div>
        </div>

        <div className="grid-2-col">
          {/* Blockchain Verification */}
          <div className="federated-card animate-fade-in" style={{ opacity: animationStep >= 3 ? 1 : 0 }}>
            <h2 className="section-title">
              <Lock className="section-icon indigo" size={28} />
              Blockchain Verification
            </h2>
            <p className="text-gray-600 mb-4 text-sm">
              All contributions are cryptographically verified and recorded on an immutable ledger
            </p>

            <div className="blockchain-list">
              {blockchainBlocks.map((block) => (
                <div
                  key={block.id}
                  className={`block-entry ${block.highlight ? 'highlight' : ''}`}
                >
                  <div className="block-header">
                    <span className="block-id">{block.id}</span>
                    <span className="block-time">{block.time}</span>
                  </div>
                  <div className="block-details">
                    <span className="text-gray-600">Hospital: {block.hospital}</span>
                    <div style={{ display: 'flex', alignItems: 'center', color: '#059669' }}>
                      <CheckCircle size={16} className="mr-2" />
                      <span className="font-bold text-xs">Verified</span>
                    </div>
                  </div>
                  <div className="block-hash">
                    Hash: {block.hash}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-3 bg-indigo-50 rounded-lg text-sm text-indigo-800 flex items-center">
              <Lock size={16} className="mr-2" />
              Chain integrity: <span className="font-bold ml-1">100% Verified</span>
            </div>
          </div>

          {/* Reward & Network Status */}
          <div className="animate-fade-in" style={{ opacity: animationStep >= 4 ? 1 : 0 }}>
            {/* Contribution Reward */}
            <div className="reward-section">
              <div className="section-title" style={{ marginBottom: '1rem' }}>
                <Award size={32} className="mr-2 text-yellow-600" />
                <h2 className="font-bold text-gray-800 text-2xl">Contribution Reward</h2>
              </div>
              <div className="text-center py-4">
                <div className="reward-amount">
                  {contributionReward}
                </div>
                <p className="text-xl text-gray-700 font-semibold">MED Tokens Earned</p>
                <p className="text-sm text-gray-600 mt-2">
                  Based on data quality and model improvement
                </p>
              </div>
              <div className="reward-stats-grid">
                <div className="stat-box">
                  <p className="text-xs text-gray-600">Quality Score</p>
                  <p className="text-lg font-bold text-green-600">A+</p>
                </div>
                <div className="stat-box">
                  <p className="text-xs text-gray-600">Samples</p>
                  <p className="text-lg font-bold text-blue-600">634</p>
                </div>
                <div className="stat-box">
                  <p className="text-xs text-gray-600">Rank</p>
                  <p className="text-lg font-bold text-purple-600">#1</p>
                </div>
              </div>
            </div>

            {/* Network Status */}
            <div className="federated-card">
              <h2 className="section-title">
                <Globe className="section-icon blue" size={28} />
                Network Status
              </h2>

              <div className="network-list">
                {hospitals.map((hospital) => (
                  <div
                    key={hospital.name}
                    className={`network-item ${hospital.isYou ? 'is-you' : ''}`}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="font-semibold text-gray-800">
                        {hospital.name} {hospital.isYou && '(You)'}
                      </span>
                      <CheckCircle size={20} className="text-green-600" />
                    </div>
                    <div className="text-sm text-gray-600">
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Samples:</span>
                        <span className="font-semibold">{hospital.samples}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Local Accuracy:</span>
                        <span className="font-semibold">{hospital.accuracy}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {/* <div className="action-buttons-container" style={{ opacity: animationStep >= 4 ? 1 : 0, transition: 'opacity 1s' }}>
          <button className="btn-action primary">
            <Download size={20} className="mr-2" />
            Download Updated Model
          </button>
          <button className="btn-action secondary">
            View Detailed Report
          </button>
          <button className="btn-action green">
            Contribute More Data
          </button>
        </div> */}

        {/* Footer Message */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 text-lg">
            Thank you for contributing to <span className="font-bold text-blue-600">global medical intelligence</span>
            {' '}while preserving <span className="font-bold text-green-600">patient privacy</span>! 🌍
          </p>
        </div>
      </div>
    </div>
  );
};

export default FederatedModelUpdatePage;
