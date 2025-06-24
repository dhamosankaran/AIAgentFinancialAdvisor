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
import { FaUser, FaDollarSign, FaCog, FaChartPie } from 'react-icons/fa';

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
      
      // First try to load from profile portfolio storage
      const profilePortfolioResponse = await fetch('/api/v1/profile/portfolio');
      if (profilePortfolioResponse.ok) {
        const profileData = await profilePortfolioResponse.json();
        if (profileData.success && profileData.portfolio) {
          // Use stored profile portfolio data
          const storedPortfolio = profileData.portfolio;
          setAllocation(storedPortfolio.portfolio_allocation || []);
          setReport(storedPortfolio.portfolio_summary || '');
          setNoProfile(false);
          setLoading(false);
          return;
        }
      }
      
      // Fallback to regular portfolio analysis if no stored data
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
        {fapContext && fapHistory && fapHistory.length > 0 && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
              <span className="mr-3">🔄</span>
              Financial Analysis Pipeline Journey
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Step 1: Risk Assessment */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border-l-4 border-purple-500">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-2">🎯</span>
                  <h3 className="font-bold text-purple-800">Step 1: Risk Assessment</h3>
                </div>
                {fapContext.risk_assessment && (
                  <div className="space-y-2 text-sm">
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Risk Score:</strong> {(fapContext.risk_assessment.raw.risk_score * 100).toFixed(0)}%</p>
                      <p><strong>Risk Level:</strong> {fapContext.risk_assessment.raw.risk_level}</p>
                    </div>
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Profile:</strong></p>
                      <ul className="text-xs mt-1 space-y-1">
                        <li>• Age: {fapContext.risk_assessment.raw.profile_analysis.age}</li>
                        <li>• Income: {fapContext.risk_assessment.raw.profile_analysis.income}</li>
                        <li>• Risk Tolerance: {fapContext.risk_assessment.raw.profile_analysis.risk_tolerance}</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 2: Market Analysis */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border-l-4 border-green-500">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-2">📈</span>
                  <h3 className="font-bold text-green-800">Step 2: Market Analysis</h3>
                </div>
                {fapContext.market_analysis && (
                  <div className="space-y-2 text-sm">
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Current Price:</strong> ${fapContext.market_analysis.raw.current_price}</p>
                      <p><strong>Daily Change:</strong> {fapContext.market_analysis.raw.daily_change_percent?.toFixed(2)}%</p>
                    </div>
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Volume:</strong> {(fapContext.market_analysis.raw.volume / 1000000).toFixed(1)}M</p>
                      <p><strong>Sentiment:</strong> {fapContext.market_analysis.raw.market_sentiment}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 3: Portfolio Generation */}
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border-l-4 border-orange-500">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-2">💼</span>
                  <h3 className="font-bold text-orange-800">Step 3: Portfolio</h3>
                </div>
                {fapContext.portfolio_allocation && (
                  <div className="space-y-2 text-sm">
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Top Allocations:</strong></p>
                      <ul className="text-xs mt-1 space-y-1">
                        <li>• Stocks: {(fapContext.portfolio_allocation.raw.stocks * 100).toFixed(0)}%</li>
                        <li>• Bonds: {(fapContext.portfolio_allocation.raw.bonds * 100).toFixed(0)}%</li>
                        <li>• Cash: {(fapContext.portfolio_allocation.raw.cash * 100).toFixed(0)}%</li>
                      </ul>
                    </div>
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p className="text-xs"><strong>Alternative Assets:</strong></p>
                      <ul className="text-xs mt-1 space-y-1">
                        <li>• Real Estate: {(fapContext.portfolio_allocation.raw.real_estate * 100).toFixed(0)}%</li>
                        <li>• Crypto: {(fapContext.portfolio_allocation.raw.cryptocurrency * 100).toFixed(0)}%</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 4: Report Generation */}
              <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-4 rounded-lg border-l-4 border-pink-500">
                <div className="flex items-center mb-3">
                  <span className="text-2xl mr-2">📋</span>
                  <h3 className="font-bold text-pink-800">Step 4: Final Report</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="bg-white p-2 rounded shadow-sm">
                    <p><strong>Report Generated:</strong> ✅</p>
                    <p><strong>Sections:</strong></p>
                    <ul className="text-xs mt-1 space-y-1">
                      <li>• Risk Assessment Summary</li>
                      <li>• Market Outlook</li>
                      <li>• Portfolio Recommendations</li>
                    </ul>
                  </div>
                  <div className="bg-white p-2 rounded shadow-sm">
                    <p className="text-xs"><strong>Total Steps:</strong> {fapHistory.length}</p>
                    <p className="text-xs"><strong>Session ID:</strong> {fapContext.session_id?.slice(0, 8)}...</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Pipeline Flow Visualization */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-700 mb-3">Pipeline Flow:</h4>
              <div className="flex items-center justify-center space-x-2 overflow-x-auto">
                <div className="flex items-center space-x-2 min-w-max">
                  <div className="flex items-center justify-center w-8 h-8 bg-purple-500 text-white rounded-full text-sm font-bold">1</div>
                  <span className="text-xs font-medium">Risk</span>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full text-sm font-bold">2</div>
                  <span className="text-xs font-medium">Market</span>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center justify-center w-8 h-8 bg-orange-500 text-white rounded-full text-sm font-bold">3</div>
                  <span className="text-xs font-medium">Portfolio</span>
                  <span className="text-gray-400">→</span>
                  <div className="flex items-center justify-center w-8 h-8 bg-pink-500 text-white rounded-full text-sm font-bold">4</div>
                  <span className="text-xs font-medium">Report</span>
                </div>
              </div>
            </div>
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