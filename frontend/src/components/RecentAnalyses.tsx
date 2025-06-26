import React, { useState, useEffect } from 'react';
import { FaChartLine, FaClock, FaTrash } from 'react-icons/fa';

interface AnalysisData {
    id: string;
    symbol: string;
    period: string;
    timestamp: string;
    analysis_data: {
        ai_response: string;
        market_data: {
            name: string;
            current_price: number;
            period_change: number;
            period_change_percent: number;
        };
        user_profile: {
            risk_tolerance: string;
            investment_goal: string;
        };
    };
}

interface RecentAnalysesProps {
    limit?: number;
    showTitle?: boolean;
    onAnalysisSelect?: (analysis: AnalysisData) => void;
    analysesData?: AnalysisData[]; // Add prop to receive cached data
    disableApiCalls?: boolean; // Add flag to disable API calls for enterprise mode
}

const RecentAnalyses: React.FC<RecentAnalysesProps> = ({ 
    limit = 5, 
    showTitle = true, 
    onAnalysisSelect,
    analysesData,
    disableApiCalls = false
}) => {
    const [analyses, setAnalyses] = useState<AnalysisData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (disableApiCalls && analysesData) {
            // Use provided cached data instead of making API calls
            console.log('🏢 RecentAnalyses: Using cached data (zero API calls)...');
            setAnalyses(analysesData.slice(0, limit));
            setLoading(false);
            setError(null);
        } else {
            // Fallback to API calls for standard mode
            fetchRecentAnalyses();
        }
    }, [limit, analysesData, disableApiCalls]);

    const fetchRecentAnalyses = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/v1/market/analysis/recent?limit=${limit}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    setAnalyses(data.analyses);
                } else {
                    setError('Failed to load analyses');
                }
            } else {
                setError('Failed to fetch analyses');
            }
        } catch (err) {
            setError('Error loading analyses');
            console.error('Error fetching recent analyses:', err);
        } finally {
            setLoading(false);
        }
    };

    const deleteAnalysis = async (symbol: string, period: string) => {
        try {
            const response = await fetch(`/api/v1/market/analysis/${symbol}/${period}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Refresh the list
                fetchRecentAnalyses();
            } else {
                console.error('Failed to delete analysis');
            }
        } catch (err) {
            console.error('Error deleting analysis:', err);
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    };

    if (loading) {
        return (
            <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="space-y-3">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-16 bg-gray-200 rounded"></div>
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-sm">
                {error}
            </div>
        );
    }

    if (analyses.length === 0) {
        return (
            <div className="text-gray-500 text-sm text-center py-4">
                No recent analyses found. Generate your first analysis in the Markets tab!
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm p-4">
            {showTitle && (
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <FaChartLine className="mr-2" />
                    Recent Market Analyses
                </h3>
            )}
            
            <div className="space-y-3">
                {analyses.map((analysis) => (
                    <div 
                        key={analysis.id}
                        className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors cursor-pointer"
                        onClick={() => onAnalysisSelect && onAnalysisSelect(analysis)}
                    >
                        <div className="flex justify-between items-start">
                            <div className="flex-1">
                                <div className="flex items-center mb-1">
                                    <span className="font-semibold text-gray-800">
                                        {analysis.analysis_data.market_data.name}
                                    </span>
                                    <span className="text-sm text-gray-500 ml-2">
                                        ({analysis.symbol})
                                    </span>
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded ml-2">
                                        {analysis.period.toUpperCase()}
                                    </span>
                                </div>
                                
                                <div className="flex items-center text-sm text-gray-600 mb-2">
                                    <span className="mr-4">
                                        ${analysis.analysis_data.market_data.current_price?.toFixed(2)}
                                    </span>
                                    <span className={`font-semibold ${
                                        (analysis.analysis_data.market_data.period_change || 0) >= 0 
                                            ? 'text-green-600' 
                                            : 'text-red-600'
                                    }`}>
                                        {(analysis.analysis_data.market_data.period_change || 0) >= 0 ? '+' : ''}
                                        {analysis.analysis_data.market_data.period_change_percent?.toFixed(2)}%
                                    </span>
                                </div>
                                
                                <div className="flex items-center text-xs text-gray-500">
                                    <FaClock className="mr-1" />
                                    {formatTimestamp(analysis.timestamp)}
                                    <span className="ml-3">
                                        {analysis.analysis_data.user_profile.risk_tolerance} risk
                                    </span>
                                </div>
                            </div>
                            
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deleteAnalysis(analysis.symbol, analysis.period);
                                }}
                                className="text-gray-400 hover:text-red-500 transition-colors p-1"
                                title="Delete analysis"
                            >
                                <FaTrash size={12} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            
            {analyses.length >= limit && (
                <div className="text-center mt-4">
                    <button 
                        onClick={fetchRecentAnalyses}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                        Refresh
                    </button>
                </div>
            )}
        </div>
    );
};

export default RecentAnalyses; 