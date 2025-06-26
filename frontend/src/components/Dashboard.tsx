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
  backendMode?: 'standard' | 'enterprise';
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
function normalizeAssetName(assetType: any): string {
  const assetString = String(assetType || '');
  switch (assetString.toLowerCase()) {
    case 'real_estate':
      return 'Real Estate';
    case 'etfs':
      return 'ETFs';
    case 'reits':
      return 'REITs';
    default:
      return assetString.charAt(0).toUpperCase() + assetString.slice(1);
  }
}

// Helper to parse report sections
function parseReportSections(report: any) {
  // Ensure report is a string, handle potential object with raw property
  let reportText = report;
  if (typeof report === 'object' && report !== null) {
    if ('raw' in report) {
      reportText = report.raw;
    } else {
      reportText = JSON.stringify(report);
    }
    console.log('🔍 parseReportSections: Converting object to string:', typeof report, reportText.substring(0, 100));
  }
  
  const summaryMatch = reportText.match(/Summary:\s*([\s\S]*?)(Market Outlook:|Recommendations:|$)/i);
  const outlookMatch = reportText.match(/Market Outlook:\s*([\s\S]*?)(Recommendations:|$)/i);
  const recsMatch = reportText.match(/Recommendations:\s*([\s\S]*)/i);
  return {
    summary: summaryMatch ? summaryMatch[1].trim() : '',
    outlook: outlookMatch ? outlookMatch[1].trim() : '',
    recommendations: recsMatch ? recsMatch[1].trim() : ''
  };
}

const Dashboard: React.FC<DashboardProps> = ({ onCreateProfile, fapContext, fapHistory, backendMode = 'standard' }) => {
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
      
      console.log('🔧 Dashboard: fetchAnalysis called with backendMode:', backendMode);
      
      if (backendMode === 'enterprise') {
        console.log('🏢 Dashboard: Loading data from enterprise cache (zero API calls)...');
        
        // Single API call to get all dashboard data from enterprise cache
        const response = await fetch('/api/v1/dashboard/data');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('🏢 Dashboard: Received data from:', data.cache_info?.data_source);
        console.log('🏢 Dashboard: API calls made:', data.cache_info?.api_calls_made);
        
        // Check if profile exists - fix the check logic
        const hasProfile = data.profile && data.profile.name && data.profile.name !== "Enterprise User";
        const noProfileFlag = data.profile?.no_profile === true;
        console.log('🏢 Dashboard: Profile check - hasProfile:', hasProfile, 'no_profile flag:', noProfileFlag, 'name:', data.profile?.name);
        
        if (!hasProfile || noProfileFlag) {
          console.log('🏢 Dashboard: No profile detected, showing create profile screen');
          setNoProfile(true);
          setLoading(false);
          return;
        }
        
        // Load portfolio allocation
        const portfolioAllocation = data.portfolio?.allocation || [];
        console.log('🏢 Dashboard: Portfolio allocation loaded:', portfolioAllocation);
        setAllocation(portfolioAllocation);
        
        // Load portfolio summary/report
        const portfolioSummary = data.portfolio?.summary || '';
        console.log('🏢 Dashboard: Portfolio summary loaded:', portfolioSummary.length, 'characters');
        setReport(portfolioSummary);
        
        setNoProfile(false);
        console.log('🏢 Dashboard: Enterprise dashboard data loaded successfully');
        
      } else {
        console.log('📊 Dashboard: Using standard mode endpoints');
        
        // Check profile first
        const profileResponse = await fetch('/api/v1/portfolio/summary');
        if (!profileResponse.ok) {
          throw new Error(`Profile check failed: ${profileResponse.status}`);
        }
        
        const profileData = await profileResponse.json();
        console.log('📊 Dashboard: Profile data:', profileData);
        console.log('📊 Dashboard: profileData.no_profile value:', profileData.no_profile);
        console.log('📊 Dashboard: profileData has name:', !!profileData.name);
        
        if (profileData.no_profile) {
          console.log('📊 Dashboard: No profile detected, showing create profile screen');
          setNoProfile(true);
          setLoading(false);
          return;
        }
        
        console.log('📊 Dashboard: Profile exists, continuing to load analysis...');
        
        // Get portfolio analysis
        const analysisResponse = await fetch('/api/v1/portfolio/analysis');
        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json();
          console.log('📊 Dashboard: Portfolio analysis loaded:', analysisData);
          
          // Extract allocation and report from analysis data
          const portfolioAllocation = analysisData.allocation || [];
          const portfolioSummary = analysisData.summary || analysisData.report || '';
          
          setAllocation(portfolioAllocation);
          setReport(portfolioSummary);
        } else {
          console.log('📊 Dashboard: Portfolio analysis not available, using defaults');
          setAllocation([]);
          setReport('Portfolio analysis will be available after creating your profile.');
        }
        
        setNoProfile(false);
        console.log('📊 Dashboard: Standard dashboard data loaded successfully');
      }
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
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
    labels: allocation.map(a => normalizeAssetName(String(a.asset_type || ''))),
    datasets: [
      {
        data: allocation.map(a => Number(a.allocation_percentage) || 0),
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
  
  // Ensure sections contain only strings
  const safeSections = {
    summary: typeof sections.summary === 'string' ? sections.summary : '',
    outlook: typeof sections.outlook === 'string' ? sections.outlook : '',
    recommendations: typeof sections.recommendations === 'string' ? sections.recommendations : ''
  };
  
  // Debug logging
  console.log('🏢 Dashboard render - allocation length:', allocation.length);
  console.log('🏢 Dashboard render - report length:', typeof report === 'string' ? report.length : 'not string');
  console.log('🏢 Dashboard render - noProfile:', noProfile);
  console.log('🏢 Dashboard render - loading:', loading);
  console.log('🏢 Dashboard render - error:', error);
  console.log('🔍 Dashboard render - sections:', sections);
  console.log('🔍 Dashboard render - safeSections:', safeSections);
  console.log('🔍 Dashboard render - report type:', typeof report);
  if (typeof report === 'string') {
    console.log('🔍 Dashboard render - report sample:', report.substring(0, 100));
  } else {
    console.log('🔍 Dashboard render - report is object:', report);
  }



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

  try {
    return (
      <div className="bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen py-8 px-2 md:px-8">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-extrabold text-blue-900 mb-6 text-center drop-shadow-sm">Comprehensive Investment Report</h2>
          {fapContext && (
            <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="mr-3">🤖</span>
                Financial Analysis Pipeline Results
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* User Profile */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border-l-4 border-blue-500">
                  <div className="flex items-center mb-3">
                    <span className="text-2xl mr-2">👤</span>
                    <h3 className="font-bold text-blue-800">User Profile</h3>
                  </div>
                  {fapContext.user_profile && (
                    <div className="space-y-2 text-sm">
                      <div className="bg-white p-2 rounded shadow-sm">
                        <p><strong>Name:</strong> {String(fapContext.user_profile.name || 'N/A')}</p>
                        <p><strong>Age:</strong> {String(fapContext.user_profile.age || 'N/A')}</p>
                        <p><strong>Income:</strong> ${typeof fapContext.user_profile.income === 'number' ? fapContext.user_profile.income.toLocaleString() : String(fapContext.user_profile.income || 'N/A')}</p>
                      </div>
                      <div className="bg-white p-2 rounded shadow-sm">
                        <p><strong>Risk Tolerance:</strong> {String(fapContext.user_profile.risk_tolerance || 'N/A')}</p>
                        <p><strong>Investment Goal:</strong> {String(fapContext.user_profile.investment_goal || 'N/A')}</p>
                        <p><strong>Time Horizon:</strong> {String(fapContext.user_profile.investment_horizon || 'N/A')}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Risk Assessment */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border-l-4 border-purple-500">
                  <div className="flex items-center mb-3">
                    <span className="text-2xl mr-2">🎯</span>
                    <h3 className="font-bold text-purple-800">Risk Assessment</h3>
                  </div>
                                  <div className="space-y-2 text-sm">
                  <div className="bg-white p-2 rounded shadow-sm">
                    {fapContext.risk_assessment?.raw ? (
                      <>
                        <p><strong>Risk Level:</strong> {String(fapContext.risk_assessment.raw.risk_level)}</p>
                        <p><strong>Risk Score:</strong> {(Number(fapContext.risk_assessment.raw.risk_score) * 10).toFixed(1)}/10</p>
                      </>
                    ) : (
                      <p><strong>Assessment:</strong> {String(fapContext.risk_assessment || 'Conservative approach recommended')}</p>
                    )}
                  </div>
                </div>
                </div>

                {/* Portfolio Allocation */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border-l-4 border-green-500">
                  <div className="flex items-center mb-3">
                    <span className="text-2xl mr-2">💼</span>
                    <h3 className="font-bold text-green-800">Portfolio Allocation</h3>
                  </div>
                                  {(() => {
                  console.log('🔍 FAP Context allocation debug:', fapContext.allocation);
                  console.log('🔍 FAP Context allocation raw:', fapContext.allocation?.raw);
                  console.log('🔍 FAP Context portfolio_allocation:', fapContext.portfolio_allocation);
                  console.log('🔍 FAP Context portfolio_allocation raw:', fapContext.portfolio_allocation?.raw);
                  return null;
                })()}
                {(fapContext.allocation?.raw || fapContext.allocation || fapContext.portfolio_allocation?.raw || fapContext.portfolio_allocation) && (
                  <div className="space-y-2 text-sm">
                    <div className="bg-white p-2 rounded shadow-sm">
                      <p><strong>Asset Allocation:</strong></p>
                      <ul className="text-xs mt-1 space-y-1">
                        {(() => {
                          // Try different data sources
                          const allocationData = fapContext.allocation?.raw || 
                                               fapContext.portfolio_allocation?.raw || 
                                               fapContext.allocation || 
                                               fapContext.portfolio_allocation;
                          
                          console.log('🔍 Using allocation data:', allocationData);
                          
                          if (allocationData && typeof allocationData === 'object' && !Array.isArray(allocationData)) {
                            return Object.entries(allocationData).map(([assetType, percentage]: [string, any], index: number) => (
                              <li key={index}>• {String(assetType).replace(/_/g, ' ')}: {Math.round(Number(percentage) * 100)}%</li>
                            ));
                          } else if (Array.isArray(allocationData)) {
                            return allocationData.map((asset: any, index: number) => (
                              <li key={index}>• {String(asset.asset_type)}: {String(asset.allocation_percentage)}%</li>
                            ));
                          } else {
                            return <li>No allocation data available</li>;
                          }
                        })()}
                      </ul>
                    </div>
                  </div>
                )}
                </div>
              </div>

              {/* Analysis Metadata */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-green-500">✅</span>
                      <span className="text-sm font-medium text-gray-700">Analysis Complete</span>
                    </div>
                    {fapContext.timestamp && (
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-400">📅</span>
                        <span className="text-sm text-gray-600">
                          {new Date(String(fapContext.timestamp)).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                  {fapContext.session_id && (
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400">🔑</span>
                      <span className="text-xs text-gray-500 font-mono">
                        {String(fapContext.session_id).slice(0, 8)}...
                      </span>
                    </div>
                  )}
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
                  <p className="font-semibold text-gray-700">Total Allocation: {allocation.reduce((sum, a) => sum + (Number(a.allocation_percentage) || 0), 0)}%</p>
                  <div className="mt-2 space-y-1 divide-y divide-gray-200">
                    {allocation.map(a => (
                      <div key={String(a.asset_type)} className="flex justify-between py-1">
                        <span className="capitalize text-gray-700">{normalizeAssetName(String(a.asset_type))}</span>
                        <span className="font-medium text-gray-900">{String(a.allocation_percentage)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            {/* Comprehensive Report Section */}
            <div className="flex flex-col justify-start">
              <div className="bg-gradient-to-br from-blue-100 to-blue-50 border border-blue-200 p-8 rounded-2xl shadow-xl">
                {safeSections.summary && (
                  <div className="mb-6">
                    <h4 className="font-bold text-blue-900 mb-2 text-lg">Summary</h4>
                    <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{safeSections.summary}</p>
                  </div>
                )}
                {safeSections.outlook && (
                  <div className="mb-6">
                    <h4 className="font-bold text-blue-900 mb-2 text-lg">Market Outlook</h4>
                    <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{safeSections.outlook}</p>
                  </div>
                )}
                {safeSections.recommendations && (
                  <div>
                    <h4 className="font-bold text-blue-900 mb-2 text-lg">Recommendations</h4>
                    <p className="text-gray-800 text-base whitespace-pre-line leading-relaxed">{safeSections.recommendations}</p>
                  </div>
                )}
                {!safeSections.summary && !safeSections.outlook && !safeSections.recommendations && (
                  <pre className="whitespace-pre-wrap text-gray-800 text-base">{typeof report === 'string' ? report : JSON.stringify(report, null, 2)}</pre>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  } catch (error) {
    console.error('Dashboard render error:', error);
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Dashboard Error!</strong>
        <span className="block sm:inline"> Failed to render dashboard. Please check console for details.</span>
      </div>
    );
  }
};

export default Dashboard; 