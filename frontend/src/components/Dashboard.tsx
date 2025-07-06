import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
} from 'chart.js';
import Markets from './Markets';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

interface Allocation {
  asset_type: string;
  allocation_percentage: number;
}

interface DashboardProps {
  onCreateProfile?: () => void;
  fapContext?: any;
  fapHistory?: any[];
}

// Helper to parse allocation from report
function parseAllocationsFromReport(report: string): Allocation[] {
  // Updated regex to handle all 8 asset classes including ETFs and REITs
  const allocationRegex = /\*\*(.*?)\s*\((\d+)%\)\*\*/g;
  const allocations: Allocation[] = [];
  let match;
  while ((match = allocationRegex.exec(report)) !== null) {
    // Normalize asset type names
    let assetType = match[1].trim().toLowerCase();
    if (assetType === 'real estate') assetType = 'real_estate';
    
    allocations.push({
      asset_type: assetType,
      allocation_percentage: parseInt(match[2], 10),
    });
  }
  return allocations;
}

// Helper to normalize asset names for display
function normalizeAssetName(assetType: string): string {
  switch (assetType.toLowerCase()) {
    case 'real_estate':
      return 'Real Estate';
    case 'etfs':
      return 'ETFs';
    case 'reits':
      return 'REITs';
    default:
      return assetType.charAt(0).toUpperCase() + assetType.slice(1);
  }
}

// Helper to parse report sections
function parseReportSections(report: string) {
  const summaryMatch = report.match(/Summary:\s*([\s\S]*?)(Market Outlook:|Recommendations:|$)/i);
  const outlookMatch = report.match(/Market Outlook:\s*([\s\S]*?)(Recommendations:|$)/i);
  const recsMatch = report.match(/Recommendations:\s*([\s\S]*)/i);
  return {
    summary: summaryMatch ? summaryMatch[1].trim() : '',
    outlook: outlookMatch ? outlookMatch[1].trim() : '',
    recommendations: recsMatch ? recsMatch[1].trim() : ''
  };
}

const Dashboard: React.FC<DashboardProps> = ({ onCreateProfile, fapContext, fapHistory }) => {
  const [allocation, setAllocation] = useState<Allocation[]>([]);
  const [report, setReport] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noProfile, setNoProfile] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/v1/portfolio/analysis');
      if (response.status === 404) {
        setNoProfile(true);
        setLoading(false);
        return;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.error && data.error.includes('No user profile')) {
        setNoProfile(true);
        setLoading(false);
        return;
      }

      const reportText = data.report || '';
      setReport(reportText);

      // Try to parse allocations from report first, then fall back to data.allocation
      const allocationsFromReport = parseAllocationsFromReport(reportText);
      if (allocationsFromReport.length > 0) {
        setAllocation(allocationsFromReport);
      } else if (data.allocation && data.allocation.length > 0) {
        setAllocation(data.allocation);
      } else {
        // Fallback to empty allocation if no data
        setAllocation([]);
      }

      setNoProfile(false);
    } catch (err) {
      console.error('Error fetching analysis:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [refreshKey]);

  // Function to refresh the dashboard data
  const refreshDashboard = () => {
    setRefreshKey(prev => prev + 1);
  };

  // Expose refresh function globally for other components
  useEffect(() => {
    (window as any).refreshDashboard = refreshDashboard;
    return () => {
      delete (window as any).refreshDashboard;
    };
  }, []);

  // Enhanced color palette for 8 asset classes
  const chartData = allocation.length > 0 ? {
    labels: allocation.map(a => normalizeAssetName(a.asset_type)),
    datasets: [
      {
        data: allocation.map(a => a.allocation_percentage),
        backgroundColor: [
          '#2563eb', // blue - stocks
          '#f59e42', // orange - bonds
          '#10b981', // green - cash
          '#f43f5e', // red - real estate
          '#a21caf', // purple - commodities
          '#fbbf24', // yellow - cryptocurrency
          '#0ea5e9', // sky - etfs
          '#6366f1', // indigo - reits
        ],
        borderWidth: 1,
      },
    ],
  } : null;

  const sections = parseReportSections(report);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (noProfile) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="bg-white shadow rounded-lg p-8 text-center max-w-md">
          <h2 className="text-xl font-bold mb-4 text-gray-800">No Investment Profile Found</h2>
          <p className="mb-6 text-gray-600">Please create your profile to get personalized portfolio recommendations and reports.</p>
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
            onClick={onCreateProfile}
          >
            Create Profile
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen py-8 px-2 md:px-8">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-extrabold text-blue-900 mb-6 text-center drop-shadow-sm">Comprehensive Investment Report</h2>
        <Markets />
        {fapContext && fapHistory && fapHistory.length > 0 && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Financial Analysis Pipeline Details</h2>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
              {JSON.stringify(fapContext, null, 2)}
            </pre>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Portfolio Allocation Section */}
          <div className="space-y-4 bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-800 mb-2">Portfolio Allocation</h3>
            <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
              {chartData && (
                <div className="h-64">
                  <Pie data={{
                    ...chartData,
                    datasets: [
                      {
                        ...chartData.datasets[0],
                        backgroundColor: [
                          '#2563eb', // blue
                          '#f59e42', // orange
                          '#10b981', // green
                          '#f43f5e', // red
                          '#a21caf', // purple
                          '#fbbf24', // yellow
                          '#0ea5e9', // sky
                          '#6366f1', // indigo
                        ],
                      },
                    ],
                  }} options={{ maintainAspectRatio: false, plugins: { legend: { display: true, position: 'bottom', labels: { font: { size: 14, weight: 'bold' } } } } }} />
                </div>
              )}
              <div className="mt-4">
                <p className="font-semibold text-gray-700">Total Allocation: {allocation.reduce((sum, a) => sum + a.allocation_percentage, 0)}%</p>
                <div className="mt-2 space-y-1 divide-y divide-gray-200">
                  {allocation.map(a => (
                    <div key={a.asset_type} className="flex justify-between py-1">
                      <span className="capitalize text-gray-700">{normalizeAssetName(a.asset_type)}</span>
                      <span className="font-medium text-gray-900">{a.allocation_percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          {/* Comprehensive Report Section */}
          <div className="flex flex-col justify-start">
            <div className="bg-gradient-to-br from-blue-100 to-blue-50 border border-blue-200 p-8 rounded-2xl shadow-xl">
              {sections.summary && (
                <div className="mb-6">
                  <h4 className="font-bold text-blue-900 mb-2 text-lg">Summary</h4>
                  <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{sections.summary}</p>
                </div>
              )}
              {sections.outlook && (
                <div className="mb-6">
                  <h4 className="font-bold text-blue-900 mb-2 text-lg">Market Outlook</h4>
                  <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{sections.outlook}</p>
                </div>
              )}
              {sections.recommendations && (
                <div>
                  <h4 className="font-bold text-blue-900 mb-2 text-lg">Recommendations</h4>
                  <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{sections.recommendations}</p>
                </div>
              )}
              {!sections.summary && !sections.outlook && !sections.recommendations && (
                <pre className="whitespace-pre-wrap text-gray-800 text-base">{report}</pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 