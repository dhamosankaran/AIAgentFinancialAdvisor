import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FaSearch, FaPlus, FaTrash, FaChartLine, FaSpinner, FaStar, FaRegStar, FaArrowUp, FaArrowDown, FaSync } from 'react-icons/fa';

interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previous_close: number;
  timestamp: string;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

interface HistoricalData {
  date: string;
  price: number;
}

interface WatchlistItem {
  symbol: string;
  added_at: string;
}

const timePeriods = [
  { label: '1D', value: '1d' },
  { label: '5D', value: '5d' },
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: '6M', value: '6mo' },
  { label: '1Y', value: '1y' },
  { label: '2Y', value: '2y' },
];

interface TickerProps {
  backendMode?: 'standard' | 'enterprise';
}

const Ticker: React.FC<TickerProps> = ({ backendMode = 'standard' }) => {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [currentSymbol, setCurrentSymbol] = useState('AAPL'); // Default to Apple
  const [stockData, setStockData] = useState<StockQuote | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('1mo');
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInWatchlist, setIsInWatchlist] = useState(false);

  // Load initial data
  useEffect(() => {
    if (currentSymbol) {
      fetchStockData(currentSymbol);
      fetchHistoricalData(currentSymbol, selectedPeriod);
    }
  }, [currentSymbol, selectedPeriod]);

  // Load watchlist
  useEffect(() => {
    loadWatchlist();
  }, []);

  // Check if current symbol is in watchlist
  useEffect(() => {
    setIsInWatchlist(watchlist.some(item => item.symbol === currentSymbol));
  }, [watchlist, currentSymbol]);

  const fetchStockData = async (symbol: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/v1/market/quote/${symbol.toUpperCase()}`);
      
      if (!response.ok) {
        throw new Error(`Unable to fetch data for symbol: ${symbol}`);
      }
      
      const data = await response.json();
      
      // Check for API errors
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Validate essential fields
      if (!data.symbol || typeof data.price !== 'number') {
        throw new Error('Invalid stock data received from API');
      }
      
      setStockData(data);
      console.log('Stock data fetched:', data);
      
    } catch (err) {
      console.error('Error fetching stock data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch stock data');
      setStockData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async (symbol: string, period: string) => {
    try {
      const response = await fetch(`/api/v1/market/historical/${symbol.toUpperCase()}?period=${period}`);
      
      if (response.ok) {
        const data = await response.json();
        setHistoricalData(data.history || []);
      } else {
        console.warn('Historical data not available for', symbol);
        setHistoricalData([]);
      }
    } catch (err) {
      console.error('Error fetching historical data:', err);
      setHistoricalData([]);
    }
  };

  const loadWatchlist = () => {
    try {
      const saved = localStorage.getItem('stock_watchlist');
      if (saved) {
        setWatchlist(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Error loading watchlist:', err);
    }
  };

  const saveWatchlist = (newWatchlist: WatchlistItem[]) => {
    try {
      localStorage.setItem('stock_watchlist', JSON.stringify(newWatchlist));
      setWatchlist(newWatchlist);
    } catch (err) {
      console.error('Error saving watchlist:', err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchSymbol.trim()) {
      setCurrentSymbol(searchSymbol.toUpperCase().trim());
      setSearchSymbol('');
    }
  };

  const handleWatchlistToggle = () => {
    if (isInWatchlist) {
      // Remove from watchlist
      const newWatchlist = watchlist.filter(item => item.symbol !== currentSymbol);
      saveWatchlist(newWatchlist);
    } else {
      // Add to watchlist
      const newWatchlist = [...watchlist, {
        symbol: currentSymbol,
        added_at: new Date().toISOString()
      }];
      saveWatchlist(newWatchlist);
    }
  };

  const selectWatchlistSymbol = (symbol: string) => {
    setCurrentSymbol(symbol);
  };

  const removeFromWatchlist = (symbol: string) => {
    const newWatchlist = watchlist.filter(item => item.symbol !== symbol);
    saveWatchlist(newWatchlist);
  };

  const formatXAxis = (tickItem: string) => {
    if (selectedPeriod === '1d') {
      return new Date(tickItem).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return new Date(tickItem).toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const refreshData = () => {
    if (currentSymbol) {
      fetchStockData(currentSymbol);
      fetchHistoricalData(currentSymbol, selectedPeriod);
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen py-8 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-blue-900 mb-2">Stock Ticker</h1>
          <p className="text-gray-600 text-lg">Real-time stock prices, charts, and analysis</p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <form onSubmit={handleSearch} className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchSymbol}
                onChange={(e) => setSearchSymbol(e.target.value)}
                placeholder="Enter stock symbol (e.g., AAPL, TSLA, MSFT)..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <FaSpinner className="animate-spin" /> : <FaSearch />}
              <span>Search</span>
            </button>
          </form>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Watchlist Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                <FaStar className="mr-2 text-yellow-500" />
                Watchlist
              </h3>
              
              {watchlist.length > 0 ? (
                <div className="space-y-2">
                  {watchlist.map((item) => (
                    <div
                      key={item.symbol}
                      className={`p-3 rounded-lg cursor-pointer transition-colors flex items-center justify-between ${
                        currentSymbol === item.symbol ? 'bg-blue-100 border border-blue-300' : 'hover:bg-gray-50'
                      }`}
                    >
                      <span
                        onClick={() => selectWatchlistSymbol(item.symbol)}
                        className="font-semibold text-gray-800 flex-1"
                      >
                        {item.symbol}
                      </span>
                      <button
                        onClick={() => removeFromWatchlist(item.symbol)}
                        className="text-red-500 hover:text-red-700 p-1"
                      >
                        <FaTrash size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No stocks in watchlist. Search for a stock and add it to your watchlist.</p>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                <div className="flex items-center">
                  <span className="mr-2">⚠️</span>
                  <span>{error}</span>
                </div>
              </div>
            )}

            {/* Stock Information Card */}
            {stockData && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-800">{stockData.symbol}</h2>
                    <p className="text-gray-600">Last updated: {new Date(stockData.timestamp).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={handleWatchlistToggle}
                      className={`p-2 rounded-lg transition-colors ${
                        isInWatchlist 
                          ? 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200' 
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {isInWatchlist ? <FaStar /> : <FaRegStar />}
                    </button>
                    <button
                      onClick={refreshData}
                      disabled={loading}
                      className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors disabled:opacity-50"
                    >
                      <FaSync className={loading ? 'animate-spin' : ''} />
                    </button>
                  </div>
                </div>

                {/* Price Information Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Current Price</div>
                    <div className="text-2xl font-bold text-gray-800">
                      ${(stockData.price || 0).toFixed(2)}
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Change</div>
                    <div className={`text-xl font-bold flex items-center ${
                      (stockData.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {(stockData.change || 0) >= 0 ? <FaArrowUp className="mr-1" /> : <FaArrowDown className="mr-1" />}
                      ${Math.abs(stockData.change || 0).toFixed(2)}
                      <span className="text-sm ml-1">
                        ({(stockData.change_percent || 0).toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Volume</div>
                    <div className="text-xl font-bold text-gray-800">
                      {(stockData.volume || 0).toLocaleString()}
                    </div>
                  </div>
                  
                  {stockData.high && stockData.low ? (
                    <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Day Range</div>
                      <div className="text-lg font-semibold text-gray-800">
                        ${stockData.low.toFixed(2)} - ${stockData.high.toFixed(2)}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">Last Updated</div>
                      <div className="text-sm font-semibold text-gray-800">
                        {stockData.timestamp ? new Date(stockData.timestamp).toLocaleTimeString() : 'N/A'}
                      </div>
                    </div>
                  )}
                </div>

                {/* Additional Metrics - Only show if data is available */}
                {(stockData.open || stockData.previous_close || stockData.market_cap) && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {stockData.open && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 mb-1">Open</div>
                        <div className="text-lg font-semibold">${stockData.open.toFixed(2)}</div>
                      </div>
                    )}
                    {stockData.previous_close && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 mb-1">Previous Close</div>
                        <div className="text-lg font-semibold">${stockData.previous_close.toFixed(2)}</div>
                      </div>
                    )}
                    {stockData.market_cap && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="text-sm text-gray-600 mb-1">Market Cap</div>
                        <div className="text-lg font-semibold">
                          ${(stockData.market_cap / 1e9).toFixed(2)}B
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Historical Chart */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800 flex items-center">
                  <FaChartLine className="mr-2" />
                  Price Chart - {currentSymbol}
                </h3>
                <div className="flex space-x-2">
                  {timePeriods.map(period => (
                    <button 
                      key={period.value}
                      onClick={() => setSelectedPeriod(period.value)}
                      className={`px-3 py-1 text-sm rounded-md transition-colors ${
                        selectedPeriod === period.value 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                      }`}
                    >
                      {period.label}
                    </button>
                  ))}
                </div>
              </div>
              
              {historicalData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={formatXAxis}
                      stroke="#6b7280"
                    />
                    <YAxis 
                      domain={['dataMin', 'dataMax']} 
                      tickFormatter={(tick) => `$${tick.toFixed(0)}`}
                      stroke="#6b7280"
                    />
                    <Tooltip
                      formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                      labelFormatter={(label: string) => new Date(label).toLocaleString()}
                      contentStyle={{
                        backgroundColor: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, fill: '#3b82f6' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12">
                  <FaChartLine className="mx-auto text-4xl text-gray-400 mb-4" />
                  <p className="text-gray-500">No historical data available for this period</p>
                </div>
              )}
            </div>

            {/* Popular Stocks Quick Access */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Popular Stocks</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'SPY', 'QQQ', 'VTI'].map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => setCurrentSymbol(symbol)}
                    className={`p-3 rounded-lg font-semibold transition-colors ${
                      currentSymbol === symbol
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Ticker; 