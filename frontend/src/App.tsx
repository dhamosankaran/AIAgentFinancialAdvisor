import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import UserProfileForm from './components/UserProfileForm'
import Portfolio from './components/Portfolio'
import Journal from './components/Journal'
import Markets from './components/Markets'
import ChatBubble from './components/ChatBubble'
import ChatWindow from './components/ChatWindow'
import EnterpriseChatWindow from './components/EnterpriseChatWindow'
import PluginManager from './components/PluginManager'
import FAPResultsDisplay from './components/FAPResultsDisplay'

interface UserProfileData {
  name: string
  age: number
  income: number
  risk_tolerance: string
  investment_goal: string
  investment_horizon: string
}

interface InvestmentProposalSectionProps {
  proposal: string;
}

// Helper function to parse investment proposal content
function parseInvestmentProposal(proposal: string) {
  // Split the proposal into sections
  const sections: { title: string; content: string }[] = [];
  
  // Look for Portfolio Allocation section
  const allocationMatch = proposal.match(/Portfolio Allocation:\s*([\s\S]*?)(?=---|\n\n|Report:|$)/i);
  if (allocationMatch) {
    sections.push({
      title: "📊 Portfolio Allocation",
      content: allocationMatch[1].trim()
    });
  }
  
  // Look for Report section with subsections
  const reportMatch = proposal.match(/Report:\s*([\s\S]*?)(?=---|\n\n|$)/i);
  if (reportMatch) {
    const reportContent = reportMatch[1].trim();
    
    // Parse Summary
    const summaryMatch = reportContent.match(/Summary:\s*([\s\S]*?)(?=Market Outlook:|Recommendations:|$)/i);
    if (summaryMatch) {
      sections.push({
        title: "📋 Summary",
        content: summaryMatch[1].trim()
      });
    }
    
    // Parse Market Outlook
    const outlookMatch = reportContent.match(/Market Outlook:\s*([\s\S]*?)(?=Recommendations:|$)/i);
    if (outlookMatch) {
      sections.push({
        title: "📈 Market Outlook",
        content: outlookMatch[1].trim()
      });
    }
    
    // Parse Recommendations
    const recsMatch = reportContent.match(/Recommendations:\s*([\s\S]*)/i);
    if (recsMatch) {
      sections.push({
        title: "💡 Recommendations",
        content: recsMatch[1].trim()
      });
    }
  }
  
  // If no structured sections found, treat as general content
  if (sections.length === 0) {
    sections.push({
      title: "📄 Investment Proposal",
      content: proposal
    });
  }
  
  return sections;
}

// Helper function to parse allocation lines
function parseAllocationLines(content: string) {
  const lines = content.split('\n').filter(line => line.trim());
  const allocations: { asset: string; percentage: string }[] = [];
  
  lines.forEach(line => {
    const match = line.match(/[-•*]?\s*([^:]+):\s*(\d+(?:\.\d+)?%)/);
    if (match) {
      allocations.push({
        asset: match[1].trim(),
        percentage: match[2]
      });
    }
  });
  
  return allocations;
}

const InvestmentProposalSection: React.FC<InvestmentProposalSectionProps> = ({ proposal }) => {
  const sections = parseInvestmentProposal(proposal);
  
  return (
    <div className="mt-8 max-w-4xl mx-auto">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
        <div className="flex items-center">
          <span className="text-3xl mr-4">💼</span>
          <div>
            <h2 className="text-2xl font-bold">Personalized Investment Proposal</h2>
            <p className="text-blue-100 mt-1">Based on your updated profile and risk assessment</p>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-b-2xl shadow-xl border border-gray-200">
        {sections.map((section, index) => (
          <div key={index} className={`p-6 ${index !== sections.length - 1 ? 'border-b border-gray-100' : ''}`}>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              {section.title}
            </h3>
            
            {section.title.includes('Portfolio Allocation') ? (
              <div className="space-y-3">
                {parseAllocationLines(section.content).length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {parseAllocationLines(section.content).map((allocation, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                        <span className="font-medium text-gray-700">{allocation.asset}</span>
                        <span className="font-bold text-blue-600 text-lg">{allocation.percentage}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <pre className="text-gray-700 whitespace-pre-wrap font-mono text-sm">{section.content}</pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="prose prose-lg max-w-none">
                <div className="p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{section.content}</p>
                </div>
              </div>
            )}
          </div>
        ))}
        
        <div className="p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-b-2xl">
          <div className="flex items-center text-green-700">
            <span className="text-2xl mr-3">✅</span>
            <div>
              <p className="font-semibold">Proposal Generated Successfully</p>
              <p className="text-sm text-green-600">This recommendation is tailored to your current profile and market conditions.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasProfile, setHasProfile] = useState(false)
  const [userId, setUserId] = useState<string | null>(null)
  const [showEdit, setShowEdit] = useState(false)
  const [profileData, setProfileData] = useState<UserProfileData | null>(null)
  const [investmentProposal, setInvestmentProposal] = useState<string | null>(null)
  const [fapContext, setFapContext] = useState<any>(null);
  const [fapHistory, setFapHistory] = useState<any[]>([]);
  const [fapLoading, setFapLoading] = useState(false);
  const [fapError, setFapError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [useEnterpriseChat, setUseEnterpriseChat] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [backendMode, setBackendMode] = useState<'standard' | 'enterprise' | 'detecting'>('detecting');
  const [enterpriseFeatures, setEnterpriseFeatures] = useState<any>({});

  useEffect(() => {
    // Detect backend mode first
    const detectBackendMode = async () => {
      try {
        const res = await fetch('/api/v1/backend/mode')
        if (res.ok) {
          const modeData = await res.json()
          setBackendMode(modeData.mode)
          setEnterpriseFeatures(modeData.features)
          
          // Only enable enterprise features if backend supports them
          if (modeData.mode === 'standard') {
            setUseEnterpriseChat(false)
            setIsAdmin(false)
          }
        } else {
          // Fallback: assume standard mode if endpoint doesn't exist
          setBackendMode('standard')
          setEnterpriseFeatures({})
          setUseEnterpriseChat(false)
          setIsAdmin(false)
        }
      } catch (error) {
        console.log('Backend mode detection failed, assuming standard mode')
        setBackendMode('standard')
        setEnterpriseFeatures({})
        setUseEnterpriseChat(false)
        setIsAdmin(false)
      }
    }

    // Check if user profile exists
    const checkProfile = async () => {
      try {
        console.log('🔧 App: Checking profile...')
        const res = await fetch('/api/v1/portfolio/summary')
        if (res.ok) {
          const data = await res.json()
          console.log('🔧 App: Profile response:', data)
          console.log('🔧 App: data.no_profile value:', data.no_profile)
          
          if (data.no_profile) {
            console.log('🔧 App: No profile found, setting hasProfile = false')
            setHasProfile(false)
            setUserId(null)
            setProfileData(null)
          } else {
            console.log('🔧 App: Profile found, setting hasProfile = true')
            setHasProfile(true)
            setUserId(data.user_id)
            setProfileData({
              name: data.name,
              age: data.age || 0,
              income: data.income || 0,
              risk_tolerance: data.risk_tolerance,
              investment_goal: data.investment_goal,
              investment_horizon: data.investment_horizon,
            })
            console.log('🔧 App: Profile data set:', {
              name: data.name,
              age: data.age,
              risk_tolerance: data.risk_tolerance
            })
          }
        } else {
          console.log('🔧 App: Profile check failed with status:', res.status)
        }
      } catch (err) {
        console.error('🔧 App: Error checking profile:', err)
      }
    }

    // Load existing FAP results if available
    const loadExistingFapResults = async () => {
      try {
        const res = await fetch('/api/v1/fap/results')
        if (res.ok) {
          const data = await res.json()
          // Handle both direct fap_context and nested results.fap_context structure
          const fapContext = data.fap_context || data.results?.fap_context
          if (fapContext) {
            console.log('🏢 App: Loading existing FAP results from backend')
            setFapContext(fapContext)
            setFapHistory(fapContext?.history || [])
          }
        }
      } catch (err) {
        console.log('🏢 App: No existing FAP results found or error loading:', err)
      }
    }

    // Run backend detection first, then check profile and load FAP results
    const initializeApp = async () => {
      await detectBackendMode()
      await checkProfile()
      await loadExistingFapResults()
    }

    initializeApp()
  }, [])

  const reloadDashboard = async () => {
    try {
      const res = await fetch('/api/v1/portfolio/summary')
      if (res.ok) {
        const data = await res.json()
        if (data.no_profile) {
          setHasProfile(false)
          setUserId(null)
          setProfileData(null)
        } else {
          setHasProfile(true)
          setUserId(data.user_id)
          setProfileData({
            name: data.name,
            age: data.age || 0,
            income: data.income || 0,
            risk_tolerance: data.risk_tolerance,
            investment_goal: data.investment_goal,
            investment_horizon: data.investment_horizon,
          })
        }
      }
      
      // Also reload FAP results
      try {
        const fapRes = await fetch('/api/v1/fap/results')
        if (fapRes.ok) {
          const fapData = await fapRes.json()
          // Handle both direct fap_context and nested results.fap_context structure
          const fapContext = fapData.fap_context || fapData.results?.fap_context
          if (fapContext) {
            setFapContext(fapContext)
            setFapHistory(fapContext?.history || [])
          }
        }
      } catch (fapErr) {
        console.log('Error reloading FAP results:', fapErr)
      }
    } catch (err) {
      console.error('Error reloading dashboard:', err)
    }
  }

  const handleProfileSubmit = async (data: UserProfileData) => {
    try {
      const res = await fetch('/api/v1/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      if (!res.ok) {
        throw new Error('Failed to create profile')
      }
      await reloadDashboard()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, user_id: userId }),
      })

      if (!res.ok) {
        throw new Error('Failed to get response')
      }

      const data = await res.json()
      setResponse(data.response)
      setMessage('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const runFapAnalysis = async () => {
    setFapLoading(true);
    setFapError(null);
    try {
      // First, get the most up-to-date profile data from the server
      const profileRes = await fetch('/api/v1/portfolio/summary');
      if (!profileRes.ok) throw new Error('Failed to get current profile data');
      const currentProfile = await profileRes.json();
      
      if (currentProfile.no_profile) {
        throw new Error('No profile found. Please create a profile first.');
      }

      // Now run FAP analysis with the current profile data
      const res = await fetch('/api/v1/fap/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: currentProfile.name,
          age: currentProfile.age,
          income: currentProfile.income,
          risk_tolerance: currentProfile.risk_tolerance,
          investment_goal: currentProfile.investment_goal,
          investment_horizon: currentProfile.investment_horizon,
        }),
      });
      if (!res.ok) throw new Error('Failed to run Financial Analysis Pipeline');
      const data = await res.json();
      setFapContext(data.fap_context);
      setFapHistory(data.fap_context?.history || []);
      
              // Generate Investment Proposal from the FAP analysis result
        if (data.fap_context && data.fap_context.report) {
          // Create a formatted proposal from FAP analysis
          const proposal = `---
Portfolio Allocation:
${data.fap_context.portfolio_allocation ? Object.entries(data.fap_context.portfolio_allocation.raw)
  .map(([key, value]) => `- ${key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}: ${((value as number) * 100).toFixed(0)}%`)
  .join('\n') : ''}
---
Report:
${data.fap_context.report}
---`;
                  setInvestmentProposal(proposal);
      }
      
      // Trigger refresh of portfolio data to sync with FAP results
      if ((window as any).refreshPortfolio) {
        (window as any).refreshPortfolio();
      }
      
      // Also update the local profile data to stay in sync
      setProfileData({
        name: currentProfile.name,
        age: currentProfile.age || 0,
        income: currentProfile.income || 0,
        risk_tolerance: currentProfile.risk_tolerance,
        investment_goal: currentProfile.investment_goal,
        investment_horizon: currentProfile.investment_horizon,
      });
    } catch (err) {
      setFapError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setFapLoading(false);
    }
  };

  const runFapAnalysisFromProfile = async () => {
    setFapLoading(true);
    setFapError(null);
    try {
      // First, get the most up-to-date profile data from the server
      const profileRes = await fetch('/api/v1/portfolio/summary');
      if (!profileRes.ok) throw new Error('Failed to get current profile data');
      const currentProfile = await profileRes.json();
      
      if (currentProfile.no_profile) {
        throw new Error('No profile found. Please create a profile first.');
      }

      // Now run FAP analysis with the current profile data
      const res = await fetch('/api/v1/fap/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: currentProfile.name,
          age: currentProfile.age,
          income: currentProfile.income,
          risk_tolerance: currentProfile.risk_tolerance,
          investment_goal: currentProfile.investment_goal,
          investment_horizon: currentProfile.investment_horizon,
        }),
      });
      if (!res.ok) throw new Error('Failed to run Financial Analysis Pipeline');
      const data = await res.json();
      setFapContext(data.fap_context);
      setFapHistory(data.fap_context?.history || []);
      
      // Generate Investment Proposal from the FAP analysis result
      if (data.fap_context && data.fap_context.report) {
        const proposal = `---
Portfolio Allocation:
${data.fap_context.portfolio_allocation ? Object.entries(data.fap_context.portfolio_allocation.raw)
  .map(([key, value]) => `- ${key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}: ${((value as number) * 100).toFixed(0)}%`)
  .join('\n') : ''}
---
Report:
${data.fap_context.report}
---`;
        setInvestmentProposal(proposal);
      }
      
      // Update profile portfolio storage with new allocation to sync across all tabs
      if (data.fap_context?.portfolio_allocation?.raw) {
        const allocation = Object.entries(data.fap_context.portfolio_allocation.raw).map(([asset_type, percentage]) => ({
          asset_type,
          allocation_percentage: Math.round((percentage as number) * 100)
        }));
        
        // Generate portfolio summary
        const portfolioSummary = `Summary:
Based on your profile (Age: ${currentProfile.age}, Risk Tolerance: ${currentProfile.risk_tolerance}, Investment Goal: ${currentProfile.investment_goal}, Time Horizon: ${currentProfile.investment_horizon}), we recommend a ${currentProfile.risk_tolerance} investment approach.

Market Outlook:
Current market conditions suggest a balanced approach to asset allocation. Diversification across multiple asset classes helps manage risk while maintaining growth potential.

Recommendations:
Your recommended portfolio allocation: ${Object.entries(data.fap_context.portfolio_allocation.raw)
  .map(([asset, percentage]) => `**${asset.charAt(0).toUpperCase() + asset.slice(1).replace('_', ' ')} (${Math.round((percentage as number) * 100)}%)**`)
  .join(', ')}. This allocation balances risk and return potential based on your ${currentProfile.risk_tolerance} risk profile and ${currentProfile.investment_horizon} investment horizon.`;
        
        await fetch('/api/v1/profile/portfolio/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_profile: currentProfile,
            portfolio_allocation: allocation,
            portfolio_summary: portfolioSummary
          })
        });
      }
      
      // Trigger refresh of portfolio data to sync with FAP results across all tabs
      if ((window as any).refreshPortfolio) {
        (window as any).refreshPortfolio();
      }
      
      // Reload dashboard to reflect new allocation
      await reloadDashboard();
      
      // Update the local profile data to stay in sync
      setProfileData({
        name: currentProfile.name,
        age: currentProfile.age || 0,
        income: currentProfile.income || 0,
        risk_tolerance: currentProfile.risk_tolerance,
        investment_goal: currentProfile.investment_goal,
        investment_horizon: currentProfile.investment_horizon,
      });
    } catch (err) {
      setFapError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setFapLoading(false);
    }
  };

  const renderContent = () => {
    console.log('🔧 App: renderContent called - hasProfile:', hasProfile, 'backendMode:', backendMode, 'activeTab:', activeTab)
    
    if (!hasProfile) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Create Your Profile</h2>
            <UserProfileForm onSubmit={async (data) => { await handleProfileSubmit(data); }} />
          </div>
        </div>
      );
    }
    
    if (showEdit && profileData) {
      return (
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Edit Your Profile</h2>
          <UserProfileForm
            onSubmit={async () => { await reloadDashboard(); }}
            initialValues={profileData}
            mode="edit"
            userId={userId || ''}
            onProposal={async (proposal) => {
              setInvestmentProposal(proposal)
              setShowEdit(false)
              await reloadDashboard()
            }}
          />
        </div>
      )
    }

    switch (activeTab) {
      case 'dashboard':
        return (
          <>
            <div className="mb-8">
              <Dashboard 
                fapContext={fapContext} 
                fapHistory={fapHistory} 
                backendMode={backendMode === 'detecting' ? 'standard' : backendMode}
              />
            </div>
          </>
        );
      case 'portfolio':
        return <Portfolio backendMode={backendMode === 'detecting' ? 'standard' : backendMode} />;
      case 'markets':
        return <Markets backendMode={backendMode === 'detecting' ? 'standard' : backendMode} />;
      case 'journal':
        return <Journal backendMode={backendMode === 'detecting' ? 'standard' : backendMode} />;
      case 'profile':
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Profile Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">My Profile</h2>
              {profileData && (
                <UserProfileForm
                  onSubmit={async () => { await reloadDashboard(); }}
                  initialValues={profileData}
                  mode="edit"
                  userId={userId || ''}
                  onProposal={async (proposal) => {
                    setInvestmentProposal(proposal)
                    await reloadDashboard()
                  }}
                />
              )}
            </div>
            
            {/* FAP Section */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800 flex items-center">
                <span className="mr-3">🤖</span>
                Generate Portfolio Allocation
              </h2>
              <p className="text-gray-600 mb-6">
                Run a comprehensive analysis to generate personalized investment recommendations based on your current profile and market conditions. 
                This will update your portfolio allocation across all tabs.
              </p>
              <button
                className={`px-6 py-3 rounded-lg font-semibold text-white ${fapLoading ? 'bg-blue-300' : 'bg-blue-700 hover:bg-blue-800'}`}
                onClick={runFapAnalysisFromProfile}
                disabled={fapLoading}
              >
                {fapLoading ? 'Analyzing...' : 'Generate New Portfolio Allocation'}
              </button>
              {fapError && (
                <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                  <strong>Error:</strong> {fapError}
                </div>
              )}
              
              {/* FAP Results Display */}
              <FAPResultsDisplay 
                fapContext={fapContext} 
                fapHistory={fapHistory}
                onClear={() => {
                  setFapContext(null);
                  setFapHistory([]);
                }}
              />
            </div>
          </div>
        );
      case 'plugins':
        return isAdmin ? <PluginManager /> : (
          <div className="text-center py-12">
            <p className="text-gray-600">Access denied. Admin privileges required.</p>
          </div>
        );
      default:
        return null;
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Financial Investment Advisor</h1>
        
        {hasProfile && (
          <div className="mb-8 border-b border-gray-200">
            <nav className="-mb-px flex gap-6">
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('dashboard')}
              >
                Dashboard
              </button>

              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'markets'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('markets')}
              >
                Markets
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'portfolio'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('portfolio')}
              >
                My Portfolio
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profile'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('profile')}
              >
                My Profile
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'journal'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('journal')}
              >
                My Journal
              </button>
              
              {/* Enterprise Features - Only show if backend supports them */}
              {backendMode === 'enterprise' && (
                <>
                  {/* Enterprise Plugin Manager (Admin Only) */}
                  {isAdmin && enterpriseFeatures.plugin_manager && (
                    <button
                      className={`py-4 px-1 border-b-2 font-medium text-sm ${
                        activeTab === 'plugins'
                          ? 'border-purple-500 text-purple-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                      onClick={() => setActiveTab('plugins')}
                    >
                      🏢 Plugin Manager
                    </button>
                  )}
                  
                  {/* Enterprise Mode Toggle */}
                  {enterpriseFeatures.enterprise_chat && (
                    <div className="flex items-center ml-4">
                      <label className="flex items-center gap-2 text-sm text-gray-600">
                        <input
                          type="checkbox"
                          checked={useEnterpriseChat}
                          onChange={(e) => setUseEnterpriseChat(e.target.checked)}
                          className="rounded"
                        />
                        Enterprise Mode
                      </label>
                    </div>
                  )}
                  
                  {/* Admin Mode Toggle */}
                  {enterpriseFeatures.plugin_manager && (
                    <div className="flex items-center ml-2">
                      <label className="flex items-center gap-2 text-sm text-gray-600">
                        <input
                          type="checkbox"
                          checked={isAdmin}
                          onChange={(e) => setIsAdmin(e.target.checked)}
                          className="rounded"
                        />
                        Admin Access
                      </label>
                    </div>
                  )}
                </>
              )}
              
              {/* Backend Mode Indicator */}
              <div className="flex items-center ml-4">
                <span className={`text-xs px-2 py-1 rounded ${
                  backendMode === 'enterprise' 
                    ? 'bg-purple-100 text-purple-800' 
                    : backendMode === 'standard'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {backendMode === 'detecting' ? 'Detecting...' : `${backendMode.charAt(0).toUpperCase() + backendMode.slice(1)} Mode`}
                </span>
              </div>
            </nav>
          </div>
        )}

        {renderContent()}

        {investmentProposal && <InvestmentProposalSection proposal={investmentProposal} />}
        
        {hasProfile && (
          <>
            <ChatBubble onClick={() => setIsChatOpen(true)} />
            {useEnterpriseChat ? (
              <EnterpriseChatWindow 
                isOpen={isChatOpen} 
                onClose={() => setIsChatOpen(false)}
                userId={userId}
              />
            ) : (
              <ChatWindow 
                isOpen={isChatOpen} 
                onClose={() => setIsChatOpen(false)}
                userId={userId}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App