/**
 * Conductor Dashboard - Main overview page
 * 
 * TODO: Implement Conductor dashboard:
 * - [ ] Show active GPU jobs (real-time, high, medium, batch)
 * - [ ] Display GPU cluster status (A100, RTX 4090, T4 availability)
 * - [ ] Show job queue with ETAs
 * - [ ] Display today's usage metrics
 * - [ ] Cost tracking (WTF spent today)
 * - [ ] Recent job history
 * - [ ] Quick actions (cancel job, change priority)
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface ConductorDashboardProps {
  apiUrl: string;
}

export default function ConductorDashboard({ apiUrl }: ConductorDashboardProps) {
  
  // TODO: Fetch Conductor status
  const { data: status } = useQuery({
    queryKey: ['conductor-status'],
    queryFn: async () => {
      const response = await fetch(`${apiUrl}/api/v1/conductor/status`);
      return response.json();
    },
    refetchInterval: 5000  // Refresh every 5 seconds
  });
  
  return (
    <div className="conductor-dashboard">
      <h1>🎵 Apollo Conductor</h1>
      <p className="subtitle">The Maestro of Compute</p>
      
      {/* TODO: GPU Cluster Status Card */}
      <div className="gpu-cluster-status">
        <h2>GPU Cluster Status</h2>
        {/* TODO: Show A100, RTX 4090, T4 availability */}
        <p>TODO: Implement GPU status visualization</p>
      </div>
      
      {/* TODO: Active Jobs Card */}
      <div className="active-jobs">
        <h2>Active Jobs</h2>
        {/* TODO: List real-time, high, medium priority jobs */}
        <p>TODO: Implement active jobs list</p>
      </div>
      
      {/* TODO: Job Queue Card */}
      <div className="job-queue">
        <h2>Queue ({status?.queued_jobs || 0} jobs)</h2>
        {/* TODO: Show queued jobs with ETAs */}
        <p>TODO: Implement job queue visualization</p>
      </div>
      
      {/* TODO: Usage Metrics */}
      <div className="usage-metrics">
        <h2>Today's Usage</h2>
        {/* TODO: Show AI inference, training, rendering, RAG stats */}
        <p>TODO: Implement usage metrics</p>
      </div>
      
      {/* TODO: Cost Tracking */}
      <div className="cost-tracking">
        <h2>Cost: {status?.total_cost_today || 0} WTF</h2>
        {/* TODO: Breakdown by job type */}
        <p>TODO: Implement cost breakdown chart</p>
      </div>
    </div>
  );
}

