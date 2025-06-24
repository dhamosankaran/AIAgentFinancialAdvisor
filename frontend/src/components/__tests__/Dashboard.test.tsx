import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';

// Mock fetch
global.fetch = jest.fn();

describe('Dashboard Component', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders error state when API call fails', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Failed to fetch'));
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('renders no profile message when no data is available', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ error: 'No user profile found' })
    });
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/no portfolio data available/i)).toBeInTheDocument();
    });
  });

  it('renders portfolio data when available', async () => {
    const mockData = {
      user_id: 'test123',
      name: 'Test User',
      risk_tolerance: 'moderate',
      investment_goal: 'balanced_growth',
      investment_horizon: 'long-term',
      total_allocation: 100,
      asset_allocation: {
        stocks: 60,
        bonds: 30,
        crypto: 10
      },
      last_updated: '2024-01-01T00:00:00Z'
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(mockData.name)).toBeInTheDocument();
      expect(screen.getByText(/risk tolerance/i)).toBeInTheDocument();
      expect(screen.getByText(/investment goal/i)).toBeInTheDocument();
      expect(screen.getByText(/investment horizon/i)).toBeInTheDocument();
      expect(screen.getByText(/total allocation/i)).toBeInTheDocument();
    });
  });
}); 