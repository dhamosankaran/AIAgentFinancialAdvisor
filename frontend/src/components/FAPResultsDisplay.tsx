import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaSpinner, FaClock, FaUser, FaTimes, FaRedo } from 'react-icons/fa';

interface FAPStep {
    id: number;
    title: string;
    description: string;
    icon: string;
    status: 'completed' | 'pending' | 'loading';
    result?: any;
}

interface FAPResultsDisplayProps {
    fapContext?: any;
    fapHistory?: any[];
    onClear?: () => void;
}

const FAPResultsDisplay: React.FC<FAPResultsDisplayProps> = ({ 
    fapContext, 
    fapHistory, 
    onClear 
}) => {
    const [savedResults, setSavedResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [sessionRestored, setSessionRestored] = useState(false);

    // Load saved results on component mount
    useEffect(() => {
        loadSavedResults();
        
        // Update session status on mount
        updateSessionStatus(true);
        
        // Update session status on unmount
        return () => {
            updateSessionStatus(false);
        };
    }, []);

    // Update display when new FAP context is provided
    useEffect(() => {
        if (fapContext) {
            setSavedResults({
                fap_context: fapContext,
                timestamp: new Date().toISOString(),
                session_active: true,
                session_restored: false
            });
        }
    }, [fapContext]);

    const loadSavedResults = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/fap/results');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.results) {
                    setSavedResults(data.results);
                    setSessionRestored(data.results.session_restored || false);
                }
            }
        } catch (error) {
            console.error('Error loading saved FAP results:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateSessionStatus = async (active: boolean) => {
        try {
            await fetch('/api/v1/fap/results/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active })
            });
        } catch (error) {
            console.error('Error updating session status:', error);
        }
    };

    const clearResults = async () => {
        try {
            const response = await fetch('/api/v1/fap/results', {
                method: 'DELETE'
            });
            if (response.ok) {
                setSavedResults(null);
                setSessionRestored(false);
                if (onClear) onClear();
            }
        } catch (error) {
            console.error('Error clearing FAP results:', error);
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const parseSteps = (fapContext: any): FAPStep[] => {
        const steps: FAPStep[] = [
            {
                id: 1,
                title: 'Risk Assessment',
                description: 'Analyzing user risk tolerance and investment capacity',
                icon: '🎯',
                status: fapContext?.risk_assessment ? 'completed' : 'pending',
                result: fapContext?.risk_assessment
            },
            {
                id: 2,
                title: 'Market Analysis',
                description: 'Evaluating current market conditions and trends',
                icon: '📊',
                status: fapContext?.market_analysis ? 'completed' : 'pending',
                result: fapContext?.market_analysis
            },
            {
                id: 3,
                title: 'Portfolio Generation',
                description: 'Creating personalized allocation recommendations',
                icon: '💼',
                status: fapContext?.portfolio_allocation ? 'completed' : 'pending',
                result: fapContext?.portfolio_allocation
            },
            {
                id: 4,
                title: 'Report Generation',
                description: 'Compiling comprehensive investment report',
                icon: '📋',
                status: fapContext?.report ? 'completed' : 'pending',
                result: fapContext?.report
            }
        ];
        
        return steps;
    };

    if (loading) {
        return (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-center">
                    <FaSpinner className="animate-spin mr-2" />
                    <span>Loading saved results...</span>
                </div>
            </div>
        );
    }

    if (!savedResults) {
        return (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg text-center text-gray-500">
                <p>No FAP analysis results yet. Run the Financial Analysis Pipeline to see results here.</p>
            </div>
        );
    }

    const steps = parseSteps(savedResults.fap_context);
    const userProfile = savedResults.user_profile || {};

    return (
        <div className="mt-6 bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4">
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-semibold flex items-center">
                            🤖 Financial Analysis Pipeline Results
                        </h3>
                        <div className="flex items-center mt-1 text-sm opacity-90">
                            <FaClock className="mr-1" />
                            {formatTimestamp(savedResults.timestamp)}
                            {sessionRestored && (
                                <span className="ml-3 bg-green-500 px-2 py-1 rounded text-xs">
                                    Session Restored
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={loadSavedResults}
                            className="text-white hover:text-gray-200 transition-colors"
                            title="Refresh results"
                        >
                            <FaRedo />
                        </button>
                        <button
                            onClick={clearResults}
                            className="text-white hover:text-gray-200 transition-colors"
                            title="Clear results"
                        >
                            <FaTimes />
                        </button>
                    </div>
                </div>
            </div>

            {/* User Profile Summary */}
            {userProfile.name && (
                <div className="bg-blue-50 p-4 border-b">
                    <div className="flex items-center mb-2">
                        <FaUser className="mr-2 text-blue-600" />
                        <span className="font-semibold text-gray-800">Analysis Profile</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <span className="text-gray-600">Name:</span>
                            <div className="font-semibold">{userProfile.name}</div>
                        </div>
                        <div>
                            <span className="text-gray-600">Risk Tolerance:</span>
                            <div className="font-semibold capitalize">{userProfile.risk_tolerance}</div>
                        </div>
                        <div>
                            <span className="text-gray-600">Investment Goal:</span>
                            <div className="font-semibold capitalize">{userProfile.investment_goal}</div>
                        </div>
                        <div>
                            <span className="text-gray-600">Time Horizon:</span>
                            <div className="font-semibold capitalize">{userProfile.investment_horizon}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Pipeline Steps */}
            <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {steps.map((step, index) => (
                        <div
                            key={step.id}
                            className={`p-4 rounded-lg border-2 transition-all ${
                                step.status === 'completed'
                                    ? 'border-green-200 bg-green-50'
                                    : step.status === 'loading'
                                    ? 'border-blue-200 bg-blue-50'
                                    : 'border-gray-200 bg-gray-50'
                            }`}
                        >
                            <div className="flex items-center mb-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3 ${
                                    step.status === 'completed'
                                        ? 'bg-green-500 text-white'
                                        : step.status === 'loading'
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-300 text-gray-600'
                                }`}>
                                    {step.status === 'completed' ? (
                                        <FaCheckCircle />
                                    ) : step.status === 'loading' ? (
                                        <FaSpinner className="animate-spin" />
                                    ) : (
                                        step.id
                                    )}
                                </div>
                                <span className="text-2xl">{step.icon}</span>
                            </div>
                            <h4 className="font-semibold text-gray-800 mb-1">{step.title}</h4>
                            <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                            {step.status === 'completed' && (
                                <div className="text-xs text-green-600 font-medium">
                                    ✅ Completed
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Final Report Display */}
                {savedResults.fap_context?.report && (
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                            📋 Final Investment Report
                        </h4>
                        <div className="bg-white p-4 rounded border max-h-96 overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                                {savedResults.fap_context.report}
                            </pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FAPResultsDisplay; 