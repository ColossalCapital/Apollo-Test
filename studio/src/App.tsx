/**
 * Apollo Studio - AI Management Interface
 * 
 * The visual conductor's podium - see and control everything
 * Embedded in Atlas as a module for power users
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages
import ConductorDashboard from './pages/conductor/Dashboard';
import TrainingDashboard from './pages/training/TrainingDashboard';
import RAGManager from './pages/rag/RAGManager';
import RenderQueue from './pages/rendering/RenderQueue';
import AgentBuilder from './pages/agents/AgentBuilder';
import PerformanceMonitor from './pages/monitoring/PerformanceMonitor';
import DataGovernance from './pages/governance/DataGovernance';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// Styles
import './App.css';

const queryClient = new QueryClient();

interface ApolloStudioProps {
  apiUrl: string;
  authToken: string;
  userId: string;
  theme?: 'light' | 'dark';
}

export function ApolloStudio({
  apiUrl,
  authToken,
  userId,
  theme = 'dark'
}: ApolloStudioProps) {
  
  return (
    <QueryClientProvider client={queryClient}>
      <div className={`apollo-studio theme-${theme}`}>
        <BrowserRouter basename="/apollo">
          <div className="studio-layout">
            <Sidebar />
            <div className="main-content">
              <Header userId={userId} />
              <Routes>
                <Route path="/" element={<Navigate to="/conductor" replace />} />
                <Route path="/conductor" element={<ConductorDashboard apiUrl={apiUrl} />} />
                <Route path="/training" element={<TrainingDashboard apiUrl={apiUrl} />} />
                <Route path="/rag" element={<RAGManager apiUrl={apiUrl} />} />
                <Route path="/rendering" element={<RenderQueue apiUrl={apiUrl} />} />
                <Route path="/agents" element={<AgentBuilder apiUrl={apiUrl} />} />
                <Route path="/monitoring" element={<PerformanceMonitor apiUrl={apiUrl} />} />
                <Route path="/governance" element={<DataGovernance apiUrl={apiUrl} userId={userId} />} />
              </Routes>
            </div>
          </div>
        </BrowserRouter>
      </div>
    </QueryClientProvider>
  );
}

export default ApolloStudio;

