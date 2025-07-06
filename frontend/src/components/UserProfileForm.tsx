import React, { useState } from 'react';

interface UserProfileFormProps {
  onSubmit: (data: UserProfileData) => void;
  initialValues?: UserProfileData;
  mode?: 'create' | 'edit';
  userId?: string;
  onProposal?: (proposal: string) => void;
}

interface UserProfileData {
  name: string;
  age: number;
  income: number;
  risk_tolerance: string;
  investment_goal: string;
  investment_horizon: string;
}

const UserProfileForm: React.FC<UserProfileFormProps> = ({ onSubmit, initialValues, mode = 'create', userId, onProposal }) => {
  const [formData, setFormData] = useState<UserProfileData>(
    initialValues || {
      name: '',
      age: 0,
      income: 0,
      risk_tolerance: 'moderate',
      investment_goal: 'balanced_growth',
      investment_horizon: 'long-term',
    }
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'age' || name === 'income' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === 'edit' && userId) {
        // Update profile and get investment proposal
        const res = await fetch(`/api/v1/profile/${userId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
        if (!res.ok) throw new Error('Failed to update profile');
        const data = await res.json();
        if (onProposal) onProposal(data.proposal);
        
        // Trigger dashboard refresh to show updated portfolio allocation
        if ((window as any).refreshDashboard) {
          (window as any).refreshDashboard();
        }
        
        // Also refresh the portfolio component to show updated recommendations
        if ((window as any).refreshPortfolio) {
          (window as any).refreshPortfolio();
        }
      } else {
        onSubmit(formData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow-xl rounded-2xl p-8 max-w-lg mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-center text-blue-700 mb-4">Edit Your Profile</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-1">Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
            placeholder="Enter your name"
          />
        </div>
        <div>
          <label htmlFor="age" className="block text-sm font-semibold text-gray-700 mb-1">Age</label>
          <input
            type="number"
            id="age"
            name="age"
            value={formData.age}
            onChange={handleChange}
            required
            min="18"
            max="100"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
            placeholder="e.g. 35"
          />
        </div>
        <div>
          <label htmlFor="income" className="block text-sm font-semibold text-gray-700 mb-1">Annual Income ($)</label>
          <input
            type="number"
            id="income"
            name="income"
            value={formData.income}
            onChange={handleChange}
            required
            min="0"
            step="1000"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
            placeholder="e.g. 80000"
          />
        </div>
        <div>
          <label htmlFor="risk_tolerance" className="block text-sm font-semibold text-gray-700 mb-1">Risk Tolerance</label>
          <select
            id="risk_tolerance"
            name="risk_tolerance"
            value={formData.risk_tolerance}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
          >
            <option value="conservative">Conservative</option>
            <option value="moderate">Moderate</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </div>
        <div>
          <label htmlFor="investment_goal" className="block text-sm font-semibold text-gray-700 mb-1">Investment Goal</label>
          <select
            id="investment_goal"
            name="investment_goal"
            value={formData.investment_goal}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
          >
            <option value="preservation">Capital Preservation</option>
            <option value="balanced_growth">Balanced Growth</option>
            <option value="aggressive_growth">Aggressive Growth</option>
          </select>
        </div>
        <div>
          <label htmlFor="investment_horizon" className="block text-sm font-semibold text-gray-700 mb-1">Investment Horizon</label>
          <select
            id="investment_horizon"
            name="investment_horizon"
            value={formData.investment_horizon}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-400"
          >
            <option value="short-term">Short-term (1-3 years)</option>
            <option value="medium-term">Medium-term (3-7 years)</option>
            <option value="long-term">Long-term (7+ years)</option>
          </select>
        </div>
      </div>
      <button
        type="submit"
        className="w-full flex justify-center items-center py-3 px-4 rounded-lg shadow text-lg font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 transition"
        disabled={loading}
      >
        {loading ? (
          <span className="animate-spin mr-2 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
        ) : (
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
        {loading ? (mode === 'edit' ? 'Updating...' : 'Creating...') : (mode === 'edit' ? 'Update Profile' : 'Create Profile')}
      </button>
      {error && (
        <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-center">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}
    </form>
  );
};

export default UserProfileForm; 