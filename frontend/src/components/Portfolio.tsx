import React, { useState, useEffect } from 'react';
import { FaSync } from 'react-icons/fa';

interface Holding {
  symbol: string;
  shares: number;
  purchase_price: number;
  purchase_date: string;
  notes?: string;
}

interface Quote {
    price: number;
    change: number;
    change_percent: number;
    timestamp: string;
}

interface Transaction {
  id: string;
  date: string;
  type: string;
  symbol: string;
  shares: number;
  price: number;
  total: number;
}

interface RecommendedAllocation {
  asset_type: string;
  allocation_percentage: number;
}

// Helper function to normalize asset names for display
const normalizeAssetName = (assetType: string): string => {
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
};

const Portfolio: React.FC = () => {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [quotes, setQuotes] = useState<Record<string, Quote>>({});
  const [recommendedAllocations, setRecommendedAllocations] = useState<RecommendedAllocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Form state
  const [symbol, setSymbol] = useState('');
  const [shares, setShares] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [notes, setNotes] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [holdingsRes, transactionsRes, allocationsRes] = await Promise.all([
        fetch('/api/v1/portfolio/holdings'),
        fetch('/api/v1/portfolio/transactions'),
        fetch('/api/v1/portfolio/analysis'),
      ]);

      if (!holdingsRes.ok || !transactionsRes.ok) {
        throw new Error('Failed to fetch portfolio data');
      }

      const holdingsData = await holdingsRes.json();
      const transactionsData = await transactionsRes.json();

      setHoldings(holdingsData);
      setTransactions(transactionsData);

      // Fetch recommended allocations if available
      if (allocationsRes.ok) {
        const allocationsData = await allocationsRes.json();
        if (allocationsData.allocation) {
          setRecommendedAllocations(allocationsData.allocation);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshKey]);

  // Expose refresh function globally for other components
  useEffect(() => {
    (window as any).refreshPortfolio = () => setRefreshKey(prev => prev + 1);
    return () => {
      delete (window as any).refreshPortfolio;
    };
  }, []);

  const handleRefreshQuote = async (symbol: string) => {
    try {
        const res = await fetch(`/api/v1/market/quote/${symbol}`);
        if(!res.ok) {
            throw new Error(`Failed to fetch quote for ${symbol}`);
        }
        const data = await res.json();
        setQuotes(prev => ({...prev, [symbol]: data}));
    } catch (err) {
        // For now, just log the error to the console. A more robust solution could show a toast notification.
        console.error(err);
    }
  };

  const handleAddHolding = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newHolding = {
        symbol,
        shares: parseFloat(shares),
        purchase_price: parseFloat(purchasePrice),
        purchase_date: new Date().toISOString(),
        notes,
      };
      
      const res = await fetch('/api/v1/portfolio/holdings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newHolding),
      });

      if (!res.ok) {
        throw new Error('Failed to add holding');
      }

      // Reset form and refetch data
      setSymbol('');
      setShares('');
      setPurchasePrice('');
      setNotes('');
      fetchData();

    } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  if (loading) {
    return <div>Loading portfolio...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">My Portfolio</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Recommended Allocations Section */}
        <div>
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Recommended Allocations</h3>
          <div className="space-y-3">
            {recommendedAllocations.length > 0 ? (
              recommendedAllocations.map((allocation) => (
                <div key={allocation.asset_type} className="p-3 border rounded-lg bg-blue-50">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-800 capitalize">
                      {normalizeAssetName(allocation.asset_type)}
                    </span>
                    <span className="font-bold text-blue-600">
                      {allocation.allocation_percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${allocation.allocation_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No recommendations available. Create or update your profile to see recommendations.</p>
            )}
          </div>
        </div>

        {/* Current Holdings Section */}
        <div>
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Current Holdings</h3>
          <div className="space-y-4">
            {holdings.length > 0 ? (
              holdings.map((h) => (
                <div key={h.symbol} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-center">
                    <p className="font-bold text-lg">{h.symbol}</p>
                    <button 
                        onClick={() => handleRefreshQuote(h.symbol)}
                        className="p-2 text-gray-500 hover:text-blue-600"
                        aria-label={`Refresh quote for ${h.symbol}`}
                    >
                        <FaSync />
                    </button>
                  </div>
                  <p className="text-sm">{h.shares} shares @ ${h.purchase_price.toFixed(2)}</p>
                  {quotes[h.symbol] ? (
                    <div className="mt-2 text-sm">
                        <p>Current Price: <span className="font-semibold">${quotes[h.symbol].price.toFixed(2)}</span></p>
                        <p>Market Value: <span className="font-semibold">${(h.shares * quotes[h.symbol].price).toFixed(2)}</span></p>
                        <p>Day's Change: <span className={quotes[h.symbol].change > 0 ? 'text-green-600' : 'text-red-600'}>
                            {quotes[h.symbol].change.toFixed(2)} ({quotes[h.symbol].change_percent.toFixed(2)}%)
                        </span></p>
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500 mt-2">Click refresh for the latest price.</p>
                  )}
                </div>
              ))
            ) : (
              <p>No holdings yet.</p>
            )}
          </div>
        </div>

        {/* Recent Transactions Section */}
        <div>
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Recent Transactions</h3>
          <div className="space-y-2">
            {transactions.length > 0 ? (
              transactions.slice(0, 5).map((t) => (
                <div key={t.id} className="text-sm">
                  <span>{new Date(t.date).toLocaleDateString()}</span>
                  <span className={`ml-2 font-semibold ${t.type === 'buy' ? 'text-green-600' : 'text-red-600'}`}>{t.type.toUpperCase()}</span>
                  <span className="ml-2">{t.symbol}</span>
                </div>
              ))
            ) : (
              <p>No transactions yet.</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">Add New Holding</h3>
        <form onSubmit={handleAddHolding} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Symbol (e.g., AAPL)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="p-2 border rounded"
              required
            />
            <input
              type="number"
              placeholder="Shares"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              className="p-2 border rounded"
              required
            />
            <input
              type="number"
              placeholder="Purchase Price"
              value={purchasePrice}
              onChange={(e) => setPurchasePrice(e.target.value)}
              className="p-2 border rounded"
              required
            />
          </div>
          <textarea
            placeholder="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full p-2 border rounded"
            rows={2}
          ></textarea>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Add Holding
          </button>
        </form>
      </div>
    </div>
  );
};

export default Portfolio; 