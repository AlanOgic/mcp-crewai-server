import React from 'react';
import { useDashboard } from '../contexts/DashboardContext';
import SystemStatus from './SystemStatus';
import ModelHub from './ModelHub';
import ProviderStatus from './ProviderStatus';
import CrewMetrics from './CrewMetrics';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import ConnectionStatus from './ConnectionStatus';

const Dashboard = () => {
  const { dashboardData, loading, error, isConnected } = useDashboard();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  if (!dashboardData) {
    return <ErrorMessage error="No dashboard data available" />;
  }

  const { system, ollama, providers, metrics, summary } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🔥 MCP CrewAI Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                Real-time monitoring and crew management
              </p>
            </div>
            <ConnectionStatus isConnected={isConnected} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Models</p>
                <p className="text-2xl font-bold text-gray-900">{summary.total_models}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-2xl">⚡</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Providers</p>
                <p className="text-2xl font-bold text-gray-900">{summary.active_providers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-2xl">🦙</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Local Models</p>
                <p className="text-2xl font-bold text-gray-900">{summary.local_models}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <span className="text-2xl">☁️</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Cloud Ready</p>
                <p className="text-2xl font-bold text-gray-900">{summary.cloud_providers_configured}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            <ModelHub ollama={ollama} />
            <ProviderStatus providers={providers} />
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <SystemStatus system={system} />
            <CrewMetrics metrics={metrics} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;