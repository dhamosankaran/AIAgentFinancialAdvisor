import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import UserProfileForm from './components/UserProfileForm'
import Portfolio from './components/Portfolio'
import Journal from './components/Journal'
import ChatBubble from './components/ChatBubble'
import ChatWindow from './components/ChatWindow'
import Ticker from './components/Ticker'
import SystemFlowDiagram from './components/SystemFlowDiagram'

interface UserProfileData {
  name: string
  age: number
  income: number
  risk_tolerance: string
  investment_goal: string
  investment_horizon: string
}

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

  // Optionally, detect backend mode (for now, default to 'standard')
  const backendMode: 'standard' | 'enterprise' = 'standard';

  useEffect(() => {
    // Check if user profile exists
    const checkProfile = async () => {
      try {
        const res = await fetch('/api/v1/profile')
        if (res.ok) {
          const data = await res.json()
          setHasProfile(true)
          setUserId(data.user_id)
          setProfileData({
            name: data.name,
            age: data.age,
            income: data.income,
            risk_tolerance: data.risk_tolerance,
            investment_goal: data.investment_goal,
            investment_horizon: data.investment_horizon,
          })
        } else if (res.status === 404) {
          setHasProfile(false)
          setUserId(null)
          setProfileData(null)
        }
      } catch (err) {
        console.error('Error checking profile:', err)
        setHasProfile(false)
        setUserId(null)
        setProfileData(null)
      }
    }
    checkProfile()
  }, [])

  const reloadDashboard = async () => {
    try {
      const res = await fetch('/api/v1/profile')
      if (res.ok) {
        const data = await res.json()
        setHasProfile(true)
        setUserId(data.user_id)
        setProfileData({
          name: data.name,
          age: data.age,
          income: data.income,
          risk_tolerance: data.risk_tolerance,
          investment_goal: data.investment_goal,
          investment_horizon: data.investment_horizon,
        })
      } else if (res.status === 404) {
        setHasProfile(false)
        setUserId(null)
        setProfileData(null)
      }
    } catch (err) {
      console.error('Error reloading dashboard:', err)
      setHasProfile(false)
      setUserId(null)
      setProfileData(null)
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
    if (!profileData) return;
    setFapLoading(true);
    setFapError(null);
    try {
      const res = await fetch('/api/v1/fap/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...profileData }),
      });
      if (!res.ok) throw new Error('Failed to run Financial Analysis Pipeline');
      const data = await res.json();
      setFapContext(data.fap_context);
      setFapHistory(data.fap_context?.history || []);
    } catch (err) {
      setFapError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setFapLoading(false);
    }
  };

  const renderContent = () => {
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
              <Dashboard fapContext={fapContext} fapHistory={fapHistory} />
              <div className="flex gap-4 mt-4">
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => setShowEdit(true)}
                  title="Edit your investment profile"
                >
                  Edit Profile
                </button>
                <button
                  className={`px-4 py-2 rounded text-white ${fapLoading ? 'bg-blue-300' : 'bg-blue-700 hover:bg-blue-800'}`}
                  onClick={runFapAnalysis}
                  disabled={fapLoading}
                  title="Run a comprehensive financial analysis"
                >
                  {fapLoading ? 'Analyzing...' : 'Run Financial Analysis Pipeline'}
                </button>
              </div>
              {fapError && (
                <div className="mt-4 text-red-500">Error: {fapError}</div>
              )}
            </div>
          </>
        );
      case 'portfolio':
        return <Portfolio />;
      case 'journal':
        return <Journal />;
      case 'ticker':
        return <Ticker backendMode={backendMode} />;
      case 'flows':
        return <SystemFlowDiagram backendMode={backendMode} />;
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
            <nav className="-mb-px flex gap-6" aria-label="Main Navigation">
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('dashboard')}
                title="View your dashboard overview"
                aria-current={activeTab === 'dashboard' ? 'page' : undefined}
              >
                Dashboard
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  activeTab === 'portfolio'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('portfolio')}
                title="Manage your investment portfolio"
                aria-current={activeTab === 'portfolio' ? 'page' : undefined}
              >
                My Portfolio
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  activeTab === 'journal'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('journal')}
                title="View and log your investment decisions"
                aria-current={activeTab === 'journal' ? 'page' : undefined}
              >
                Journal
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  activeTab === 'ticker'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('ticker')}
                title="Check real-time stock prices and manage your watchlist"
                aria-current={activeTab === 'ticker' ? 'page' : undefined}
              >
                Stock Ticker
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  activeTab === 'flows'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('flows')}
                title="Visualize system and financial analysis flows"
                aria-current={activeTab === 'flows' ? 'page' : undefined}
              >
                System Flows
              </button>
            </nav>
          </div>
        )}

        {renderContent()}

        {investmentProposal && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow">
            <h2 className="text-lg font-medium text-gray-900">Investment Proposal:</h2>
            <div className="mt-2 p-4 bg-gray-50 rounded-md">
              <p className="text-gray-700 whitespace-pre-wrap">{investmentProposal}</p>
            </div>
          </div>
        )}
        
        {hasProfile && (
          <>
            <ChatBubble onClick={() => setIsChatOpen(true)} />
            <ChatWindow 
              isOpen={isChatOpen} 
              onClose={() => setIsChatOpen(false)}
              userId={userId}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default App 