import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FaArrowUp, FaArrowDown, FaChartLine, FaSpinner, FaClock, FaInfoCircle, FaTrash, FaEye } from 'react-icons/fa';
import RecentAnalyses from './RecentAnalyses';

interface IndexData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

interface HistoricalData {
  date: string;
  price: number;
}

const timePeriods = [
    { label: '1D', value: '1d' },
    { label: '5D', value: '5d' },
    { label: '1M', value: '1mo' },
    { label: '3M', value: '3mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: '2Y', value: '2y' },
]

interface MarketsProps {
  backendMode?: 'standard' | 'enterprise';
}

const Markets: React.FC<MarketsProps> = ({ backendMode = 'standard' }) => {
    const [indices, setIndices] = useState<IndexData[]>([]);
    const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
    const [selectedSymbol, setSelectedSymbol] = useState('SPY');
    const [selectedPeriod, setSelectedPeriod] = useState('6mo');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [marketAnalysis, setMarketAnalysis] = useState<string | null>(null);
    const [analysisLoading, setAnalysisLoading] = useState(false);
    const [savedAnalysis, setSavedAnalysis] = useState<any>(null);
    const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);
    const [showAnalysisModal, setShowAnalysisModal] = useState(false);
    const [userProfile, setUserProfile] = useState<any>(null);

    useEffect(() => {
        const fetchMarketData = async () => {
            try {
                setLoading(true);
                
                if (backendMode === 'enterprise') {
                    console.log('🏢 Markets: Loading data from enterprise cache (zero API calls)...');
                    
                    // Single API call to get all market data from enterprise cache
                    const response = await fetch('/api/v1/market/data');
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    console.log('🏢 Markets: Received data from:', data.cache_info?.data_source);
                    console.log('🏢 Markets: API calls made:', data.cache_info?.api_calls_made);
                    
                    // Load market indices from cached analysis data
                    const cachedIndices = data.analysis?.indices || [];
                    
                    if (cachedIndices.length > 0) {
                        setIndices(cachedIndices);
                        console.log('🏢 Markets: Loaded market indices from cache without external API calls');
                    } else {
                        console.log('🏢 Markets: No cached indices found, but avoiding API calls as requested');
                        setError('No market data available. Please check your data files or update market analysis.');
                    }
                    
                    // Also load user profile for analysis generation
                    try {
                        const profileResponse = await fetch('/api/v1/dashboard/data');
                        if (profileResponse.ok) {
                            const profileData = await profileResponse.json();
                            setUserProfile(profileData.profile);
                            console.log('🏢 Markets: Loaded user profile from cache for analysis generation');
                        }
                    } catch (profileErr) {
                        console.log('🏢 Markets: Could not load user profile, will use defaults for analysis');
                    }
                    
                } else {
                    console.log('📊 Markets: Using standard mode endpoints');
                    
                    // Use standard market indices endpoint
                    const response = await fetch('/api/v1/market/indices');
                    
                    if (response.ok) {
                        const indicesData = await response.json();
                        setIndices(indicesData);
                        console.log('📊 Markets: Loaded market indices from standard endpoint');
                    } else {
                        console.log('📊 Markets: Could not load market indices, using defaults');
                        // Use default market data
                        setIndices([
                            { symbol: 'SPY', name: 'S&P 500 ETF', price: 450.25, change: 2.15, change_percent: 0.48 },
                            { symbol: 'QQQ', name: 'NASDAQ ETF', price: 378.90, change: -1.45, change_percent: -0.38 },
                            { symbol: 'IWM', name: 'Russell 2000 ETF', price: 194.75, change: 0.95, change_percent: 0.49 },
                            { symbol: 'DIA', name: 'Dow Jones ETF', price: 342.10, change: 1.20, change_percent: 0.35 }
                        ]);
                    }
                    
                    // Load user profile for analysis generation
                    try {
                        const profileResponse = await fetch('/api/v1/portfolio/summary');
                        if (profileResponse.ok) {
                            const profileData = await profileResponse.json();
                            if (!profileData.no_profile) {
                                setUserProfile(profileData);
                                console.log('📊 Markets: Loaded user profile for analysis generation');
                            }
                        }
                    } catch (profileErr) {
                        console.log('📊 Markets: Could not load user profile, will use defaults for analysis');
                    }
                }
                
            } catch (err) {
                console.error('Markets: Error loading market data:', err);
                setError(err instanceof Error ? err.message : 'An error occurred loading market data')
            } finally {
                setLoading(false);
            }
        };
        fetchMarketData();
    }, []);

    useEffect(() => {
        const fetchHistoricalData = async () => {
            if (!selectedSymbol) return;
            try {
                const res = await fetch(`/api/v1/market/historical/${selectedSymbol}?period=${selectedPeriod}`);
                if (!res.ok) throw new Error(`Failed to fetch historical data for ${selectedSymbol}`);
                const data = await res.json();
                setHistoricalData(data.history);
            } catch (err) {
                console.error(err);
                // Don't set a main error for this, just log it.
            }
        };
        fetchHistoricalData();
    }, [selectedSymbol, selectedPeriod]);

    // Load saved analysis when symbol or period changes
    useEffect(() => {
        const loadSavedAnalysis = async () => {
            if (!selectedSymbol || !selectedPeriod) return;
            
            try {
                const res = await fetch(`/api/v1/market/analysis/${selectedSymbol}/${selectedPeriod}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.success && data.analysis) {
                        setSavedAnalysis(data.analysis);
                        setMarketAnalysis(data.analysis.analysis_data.ai_response || '');
                        console.log('Loaded saved analysis:', data.analysis);
                    } else {
                        setSavedAnalysis(null);
                        setMarketAnalysis('');
                    }
                } else {
                    setSavedAnalysis(null);
                    setMarketAnalysis('');
                }
            } catch (error) {
                console.error('Error loading saved analysis:', error);
                setSavedAnalysis(null);
                setMarketAnalysis('');
            }
        };
        
        loadSavedAnalysis();
    }, [selectedSymbol, selectedPeriod]);

    const formatXAxis = (tickItem: string) => {
        if(selectedPeriod === '1d') {
            return new Date(tickItem).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit'});
        }
        return new Date(tickItem).toLocaleDateString([], { month: 'short', day: 'numeric'});
    }

    const generateMarketAnalysis = async () => {
        try {
            setAnalysisLoading(true);
            setMarketAnalysis(''); // Clear previous analysis
            const selectedIndex = indices.find(index => index.symbol === selectedSymbol);
            
            // Calculate period-based changes from historical data
            let periodAnalysis = null;
            if (historicalData && historicalData.length > 1) {
                const firstPrice = historicalData[0].price;
                const lastPrice = historicalData[historicalData.length - 1].price;
                const periodChange = lastPrice - firstPrice;
                const periodChangePercent = ((lastPrice - firstPrice) / firstPrice) * 100;
                
                // Calculate additional metrics
                const prices = historicalData.map(d => d.price);
                const highPrice = Math.max(...prices);
                const lowPrice = Math.min(...prices);
                const volatility = calculateVolatility(prices);
                
                periodAnalysis = {
                    period: selectedPeriod,
                    start_price: firstPrice,
                    end_price: lastPrice,
                    period_change: periodChange,
                    period_change_percent: periodChangePercent,
                    high_price: highPrice,
                    low_price: lowPrice,
                    volatility: volatility,
                    data_points: historicalData.length
                };
            }
            
            // Use real user profile data from enterprise cache
            const profileData = userProfile || {
                name: 'User',
                age: 30,
                income: 100000,
                risk_tolerance: 'moderate',
                investment_goal: 'growth',
                investment_horizon: 'long-term'
            };
            
            console.log('🏢 Markets: Generating analysis with user profile:', {
                name: profileData.name,
                age: profileData.age,
                income: profileData.income,
                risk_tolerance: profileData.risk_tolerance
            });
            
            // Create abort controller for timeout handling
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
            
            const response = await fetch('/api/v1/fap/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: profileData.name || 'User',
                    age: profileData.age || 30,
                    income: profileData.income || 100000,
                    risk_tolerance: profileData.risk_tolerance || 'moderate',
                    investment_goal: profileData.investment_goal || 'growth',
                    investment_horizon: profileData.investment_horizon || 'long-term',
                    additional_context: {
                        market_data: {
                            symbol: selectedSymbol,
                            name: selectedIndex?.name,
                            current_price: selectedIndex?.price,
                            daily_change: selectedIndex?.change,
                            daily_change_percent: selectedIndex?.change_percent,
                            period: selectedPeriod,
                            period_analysis: periodAnalysis
                        },
                        analysis_type: 'market_analysis'
                    }
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Market Analysis Response received:', data); // Debug log
                
                // Extract report from different possible locations in the response
                const report = data.fap_context?.analysis_result || data.fap_context?.report || data.fallback_response || data.report;
                
                if (report && report.trim()) {
                    setMarketAnalysis(report);
                    console.log('✅ Markets: Analysis generated successfully using profile:', {
                        name: profileData.name,
                        age: profileData.age,
                        risk_tolerance: profileData.risk_tolerance,
                        analysis_length: report.length
                    });
                } else {
                    console.error('❌ No analysis content found in response:', data);
                    setMarketAnalysis('No market analysis content was generated. Please try again.');
                    return;
                }
                
                // Save analysis to backend (non-blocking)
                try {
                    const analysisData = {
                        symbol: selectedSymbol,
                        period: selectedPeriod,
                        analysis_data: {
                            ai_response: report,
                            market_data: {
                                symbol: selectedSymbol,
                                name: selectedIndex?.name,
                                current_price: selectedIndex?.price,
                                daily_change: selectedIndex?.change,
                                daily_change_percent: selectedIndex?.change_percent,
                                period: selectedPeriod,
                                period_analysis: periodAnalysis
                            },
                            user_profile: {
                                name: profileData.name || 'User',
                                age: profileData.age || 30,
                                income: profileData.income || 100000,
                                risk_tolerance: profileData.risk_tolerance || 'moderate',
                                investment_goal: profileData.investment_goal || 'growth',
                                investment_horizon: profileData.investment_horizon || 'long-term'
                            },
                            generated_at: new Date().toISOString()
                        }
                    };
                    
                    const saveResponse = await fetch('/api/v1/market/analysis/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(analysisData)
                    });
                    
                    if (saveResponse.ok) {
                        const saveData = await saveResponse.json();
                        setSavedAnalysis(saveData.analysis);
                        console.log('✅ Analysis saved successfully');
                    } else {
                        console.warn('⚠️ Failed to save analysis (non-critical):', await saveResponse.text());
                    }
                } catch (saveError) {
                    console.warn('⚠️ Error saving analysis (non-critical):', saveError);
                }
                
            } else {
                const errorText = await response.text();
                console.error('❌ Market Analysis API Error:', response.status, errorText);
                setMarketAnalysis(`Unable to generate market analysis. Server responded with status ${response.status}. Please try again.`);
            }
        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') {
                console.error('❌ Market analysis request timed out');
                setMarketAnalysis('Analysis request timed out. The analysis takes time to generate. Please try again.');
            } else {
                console.error('❌ Error generating market analysis:', error);
                const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
                setMarketAnalysis(`Error generating market analysis: ${errorMessage}. Please check your connection and try again.`);
            }
        } finally {
            setAnalysisLoading(false);
        }
    };

    // Helper function to calculate volatility
    const calculateVolatility = (prices: number[]): number => {
        if (prices.length < 2) return 0;
        
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i-1]) / prices[i-1]);
        }
        
        const mean = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
        const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - mean, 2), 0) / returns.length;
        
        return Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized volatility in percentage
    };

    const handleAnalysisSelect = (analysis: any) => {
        setSelectedAnalysis(analysis);
        setShowAnalysisModal(true);
    };

    const closeAnalysisModal = () => {
        setShowAnalysisModal(false);
        setSelectedAnalysis(null);
    };

    if (loading) return <div>Loading market data...</div>;
    if (error) return <div className="text-red-500">Error: {error}</div>;

    return (
        <div className="p-6 bg-white rounded-lg shadow-md mt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Markets</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-1">
                    <ul className="space-y-2">
                        {indices.map(index => (
                            <li 
                                key={index.symbol} 
                                className={`p-3 rounded-lg cursor-pointer ${selectedSymbol === index.symbol ? 'bg-blue-100' : 'hover:bg-gray-50'}`}
                                onClick={() => setSelectedSymbol(index.symbol)}
                            >
                                <div className="flex justify-between items-center">
                                    <span className="font-bold">{index.name}</span>
                                    <span className={`font-semibold ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {index.price.toFixed(2)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className={`flex items-center ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {index.change >= 0 ? <FaArrowUp /> : <FaArrowDown />}
                                        <span className="ml-1">{index.change.toFixed(2)}</span>
                                    </span>
                                    <span className={`font-semibold ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {index.change_percent.toFixed(2)}%
                                    </span>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="md:col-span-2">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={historicalData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" tickFormatter={formatXAxis} />
                            <YAxis domain={['dataMin', 'dataMax']} tickFormatter={(tick) => tick.toFixed(0)} />
                            <Tooltip
                                formatter={(value: number) => [value.toFixed(2), 'Price']}
                                labelFormatter={(label: string) => new Date(label).toLocaleString()}
                            />
                            <Line type="monotone" dataKey="price" stroke="#3b82f6" dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                    <div className="flex justify-end gap-2 mt-2">
                        {timePeriods.map(period => (
                            <button 
                                key={period.value}
                                onClick={() => setSelectedPeriod(period.value)}
                                className={`px-3 py-1 text-sm rounded-md ${selectedPeriod === period.value ? 'bg-blue-600 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                            >
                                {period.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
            
            {/* AI Market Analysis Section */}
            <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-semibold text-gray-800">🤖 AI Market Analysis</h3>
                    <button
                        onClick={generateMarketAnalysis}
                        disabled={analysisLoading}
                        className={`px-4 py-2 rounded ${
                            analysisLoading
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                    >
                        {analysisLoading ? '🔄 Analyzing...' : '📊 Generate Analysis'}
                    </button>
                </div>
                
                {marketAnalysis && (
                    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                        {/* Enhanced Market Analysis Display */}
                        <div className="space-y-6">
                            {/* Market Data Summary Card */}
                            {(() => {
                                const selectedIndex = indices.find(index => index.symbol === selectedSymbol);
                                let periodAnalysis = null;
                                if (historicalData && historicalData.length > 1) {
                                    const firstPrice = historicalData[0].price;
                                    const lastPrice = historicalData[historicalData.length - 1].price;
                                    const periodChange = lastPrice - firstPrice;
                                    const periodChangePercent = ((lastPrice - firstPrice) / firstPrice) * 100;
                                    const prices = historicalData.map(d => d.price);
                                    const highPrice = Math.max(...prices);
                                    const lowPrice = Math.min(...prices);
                                    
                                    periodAnalysis = {
                                        period: selectedPeriod,
                                        start_price: firstPrice,
                                        end_price: lastPrice,
                                        period_change: periodChange,
                                        period_change_percent: periodChangePercent,
                                        high_price: highPrice,
                                        low_price: lowPrice
                                    };
                                }
                                
                                return (
                                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                                        <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                            📊 Market Data Summary - {selectedIndex?.name}
                                        </h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                            <div className="bg-white p-4 rounded-lg shadow-sm">
                                                <div className="text-sm text-gray-600">Current Price</div>
                                                <div className="text-2xl font-bold text-gray-800">
                                                    ${selectedIndex?.price?.toFixed(2)}
                                                </div>
                                            </div>
                                            <div className="bg-white p-4 rounded-lg shadow-sm">
                                                <div className="text-sm text-gray-600">Daily Change</div>
                                                <div className={`text-2xl font-bold ${(selectedIndex?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {(selectedIndex?.change || 0) >= 0 ? '+' : ''}${(selectedIndex?.change || 0).toFixed(2)}
                                                    <span className="text-sm ml-1">
                                                        ({(selectedIndex?.change_percent || 0).toFixed(2)}%)
                                                    </span>
                                                </div>
                                            </div>
                                            {periodAnalysis && (
                                                <>
                                                    <div className="bg-white p-4 rounded-lg shadow-sm">
                                                        <div className="text-sm text-gray-600">{periodAnalysis.period.toUpperCase()} Change</div>
                                                        <div className={`text-2xl font-bold ${periodAnalysis.period_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                            {periodAnalysis.period_change >= 0 ? '+' : ''}${periodAnalysis.period_change?.toFixed(2)}
                                                            <span className="text-sm ml-1">
                                                                ({periodAnalysis.period_change_percent?.toFixed(2)}%)
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="bg-white p-4 rounded-lg shadow-sm">
                                                        <div className="text-sm text-gray-600">Price Range ({periodAnalysis.period.toUpperCase()})</div>
                                                        <div className="text-lg font-semibold text-gray-800">
                                                            ${periodAnalysis.low_price?.toFixed(2)} - ${periodAnalysis.high_price?.toFixed(2)}
                                                        </div>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                );
                            })()}
                            
                            {/* AI Analysis Content */}
                            <div className="p-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="text-lg font-semibold text-gray-800 flex items-center">
                                        🤖 AI Financial Analysis & Recommendations
                                    </h4>
                                    {savedAnalysis && (
                                        <div className="text-sm text-gray-500 flex items-center">
                                            <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                            Saved: {new Date(savedAnalysis.timestamp).toLocaleString()}
                                        </div>
                                    )}
                                </div>
                                <div className="prose max-w-none">
                                    <div className="bg-gray-50 p-4 rounded-lg">
                                        <pre className="whitespace-pre-wrap text-gray-700 font-sans text-sm leading-relaxed">
                                            {marketAnalysis}
                                        </pre>
                                    </div>
                                </div>
                            </div>
                            
                            {/* Quick Action Recommendations */}
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg">
                                <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                    💡 Quick Action Items
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="bg-white p-4 rounded-lg shadow-sm">
                                        <div className="text-green-600 font-semibold mb-2">📈 Investment Strategy</div>
                                        <div className="text-sm text-gray-600">
                                            Based on current analysis, consider your risk tolerance and investment timeline
                                        </div>
                                    </div>
                                    <div className="bg-white p-4 rounded-lg shadow-sm">
                                        <div className="text-blue-600 font-semibold mb-2">⚖️ Risk Management</div>
                                        <div className="text-sm text-gray-600">
                                            Monitor volatility and set appropriate stop-loss levels
                                        </div>
                                    </div>
                                    <div className="bg-white p-4 rounded-lg shadow-sm">
                                        <div className="text-purple-600 font-semibold mb-2">🎯 Next Steps</div>
                                        <div className="text-sm text-gray-600">
                                            Review portfolio allocation and consider rebalancing
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                {!marketAnalysis && !analysisLoading && (
                    <p className="text-gray-600 italic">
                        Click "Generate Analysis" to get AI-powered insights about the current market conditions and selected index.
                    </p>
                )}
            </div>
            
            {/* Recent Market Analyses Section */}
            <div className="mt-8">
                <RecentAnalyses 
                    limit={10} 
                    showTitle={true} 
                    disableApiCalls={true}
                    analysesData={[]}
                    onAnalysisSelect={handleAnalysisSelect} 
                />
            </div>
            
            {/* Analysis Details Modal */}
            {showAnalysisModal && selectedAnalysis && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                        {/* Modal Header */}
                        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h2 className="text-2xl font-bold">
                                        {selectedAnalysis.analysis_data.market_data.name} Analysis
                                    </h2>
                                    <p className="text-blue-100 mt-1">
                                        {selectedAnalysis.symbol} • {selectedAnalysis.period.toUpperCase()} • {new Date(selectedAnalysis.timestamp).toLocaleString()}
                                    </p>
                                </div>
                                <button
                                    onClick={closeAnalysisModal}
                                    className="text-white hover:text-gray-200 transition-colors p-2"
                                    title="Close"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                        
                        {/* Modal Content */}
                        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                            {/* Market Summary */}
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                    📊 Market Summary
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                                    <div className="bg-gray-50 p-4 rounded-lg">
                                        <div className="text-sm text-gray-600">Current Price</div>
                                        <div className="text-xl font-bold text-gray-800">
                                            ${selectedAnalysis.analysis_data.market_data.current_price?.toFixed(2)}
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 p-4 rounded-lg">
                                        <div className="text-sm text-gray-600">Period Change</div>
                                        <div className={`text-xl font-bold ${
                                            (selectedAnalysis.analysis_data.market_data.period_change || 0) >= 0 
                                                ? 'text-green-600' 
                                                : 'text-red-600'
                                        }`}>
                                            {(selectedAnalysis.analysis_data.market_data.period_change || 0) >= 0 ? '+' : ''}
                                            {selectedAnalysis.analysis_data.market_data.period_change_percent?.toFixed(2)}%
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 p-4 rounded-lg">
                                        <div className="text-sm text-gray-600">Risk Profile</div>
                                        <div className="text-xl font-bold text-gray-800 capitalize">
                                            {selectedAnalysis.analysis_data.user_profile.risk_tolerance}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            {/* AI Analysis */}
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                    🤖 AI Analysis
                                </h3>
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
                                        {selectedAnalysis.analysis_data.ai_response}
                                    </pre>
                                </div>
                            </div>
                            
                            {/* Raw JSON Data */}
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                    📄 Raw JSON Data
                                </h3>
                                <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                                    <pre className="text-sm font-mono">
                                        {JSON.stringify(selectedAnalysis, null, 2)}
                                    </pre>
                                </div>
                            </div>
                        </div>
                        
                        {/* Modal Footer */}
                        <div className="bg-gray-50 px-6 py-4 flex justify-end">
                            <button
                                onClick={closeAnalysisModal}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Markets; 