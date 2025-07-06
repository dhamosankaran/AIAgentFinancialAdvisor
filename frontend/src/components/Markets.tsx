import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';

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

const Markets: React.FC = () => {
    const [indices, setIndices] = useState<IndexData[]>([]);
    const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
    const [selectedSymbol, setSelectedSymbol] = useState('^GSPC'); // Default to S&P 500
    const [selectedPeriod, setSelectedPeriod] = useState('1d');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMarketData = async () => {
            try {
                setLoading(true);
                const res = await fetch('/api/v1/market/indices');
                if (!res.ok) throw new Error('Failed to fetch market indices');
                const data = await res.json();
                setIndices(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
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

    const formatXAxis = (tickItem: string) => {
        if(selectedPeriod === '1d') {
            return new Date(tickItem).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit'});
        }
        return new Date(tickItem).toLocaleDateString([], { month: 'short', day: 'numeric'});
    }

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
        </div>
    );
};

export default Markets; 