import React, { useState, useRef, useEffect } from 'react';
import { FaTimes, FaPaperPlane, FaShieldAlt, FaExclamationTriangle, FaTools, FaChartLine } from 'react-icons/fa';

interface Message {
  sender: 'user' | 'bot';
  text: string;
  metadata?: {
    moderation_passed?: boolean;
    risk_level?: string;
    compliance_issues?: string[];
    used_tools?: string[];
    confidence_score?: number;
    disclaimer_added?: boolean;
  };
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  userId: string | null;
}

const EnterpriseChatWindow: React.FC<Props> = ({ isOpen, onClose, userId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [enableCompliance, setEnableCompliance] = useState(true);
  const [riskTolerance, setRiskTolerance] = useState('medium');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !userId) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Use enterprise chat endpoint
      const res = await fetch('/api/v2/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input, 
          user_id: userId,
          enable_compliance_check: enableCompliance,
          risk_tolerance: riskTolerance
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to get response from the server.');
      }

      const data = await res.json();
      
      // Check if moderation blocked the request
      if (!data.moderation_passed && data.error) {
        const errorMessage: Message = { 
          sender: 'bot', 
          text: data.response || 'Your message was blocked due to safety guidelines. Please rephrase your question.',
          metadata: {
            moderation_passed: false,
            risk_level: data.risk_level,
            compliance_issues: data.compliance_issues || []
          }
        };
        setMessages((prev) => [...prev, errorMessage]);
      } else {
        const botMessage: Message = { 
          sender: 'bot', 
          text: data.response,
          metadata: {
            moderation_passed: data.moderation_passed,
            risk_level: data.risk_level,
            compliance_issues: data.compliance_issues || [],
            used_tools: data.used_tools || [],
            confidence_score: data.confidence_score,
            disclaimer_added: data.disclaimer_added
          }
        };
        setMessages((prev) => [...prev, botMessage]);
      }

    } catch (error) {
      const errorMessage: Message = { 
        sender: 'bot', 
        text: 'Sorry, I encountered a technical difficulty. Please try again.',
        metadata: {
          moderation_passed: false,
          risk_level: 'high'
        }
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      case 'critical': return 'text-red-800';
      default: return 'text-gray-600';
    }
  };

  const getRiskLevelBg = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'bg-green-100';
      case 'medium': return 'bg-yellow-100';
      case 'high': return 'bg-red-100';
      case 'critical': return 'bg-red-200';
      default: return 'bg-gray-100';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-28 right-8 w-[500px] h-[70vh] bg-white rounded-lg shadow-2xl flex flex-col transition-all">
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex justify-between items-center rounded-t-lg">
        <div>
          <h2 className="text-lg font-semibold">🏢 Enterprise AI Advisor</h2>
          <div className="text-xs opacity-90 flex items-center gap-2 mt-1">
            <FaShieldAlt className="text-green-300" />
            <span>Responsible AI Enabled</span>
          </div>
        </div>
        <button onClick={onClose} className="hover:text-gray-200">
          <FaTimes size={20} />
        </button>
      </header>

      {/* Enterprise Controls */}
      <div className="p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={enableCompliance}
                onChange={(e) => setEnableCompliance(e.target.checked)}
                className="rounded"
              />
              <span className="text-gray-700">Compliance Check</span>
            </label>
            <select
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value)}
              className="px-2 py-1 border border-gray-300 rounded text-xs"
            >
              <option value="low">Conservative</option>
              <option value="medium">Moderate</option>
              <option value="high">Aggressive</option>
            </select>
          </div>
          <div className="text-xs text-gray-500">Enterprise Mode</div>
        </div>
      </div>

      <main className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div key={index} className="space-y-2">
              <div className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-md px-4 py-2 rounded-2xl ${
                  msg.sender === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-800'
                }`}>
                  {msg.text}
                </div>
              </div>
              
              {/* Enterprise Metadata for Bot Messages */}
              {msg.sender === 'bot' && msg.metadata && (
                <div className="ml-4 space-y-1">
                  {/* Moderation Status */}
                  <div className="flex items-center gap-2 text-xs">
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${
                      msg.metadata.moderation_passed 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'
                    }`}>
                      <FaShieldAlt size={10} />
                      <span>{msg.metadata.moderation_passed ? 'Safe' : 'Blocked'}</span>
                    </div>
                    
                    {msg.metadata.risk_level && (
                      <div className={`px-2 py-1 rounded-full text-xs ${getRiskLevelBg(msg.metadata.risk_level)} ${getRiskLevelColor(msg.metadata.risk_level)}`}>
                        Risk: {msg.metadata.risk_level?.toUpperCase()}
                      </div>
                    )}
                    
                    {msg.metadata.confidence_score && (
                      <div className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                        <FaChartLine size={10} className="inline mr-1" />
                        {Math.round(msg.metadata.confidence_score * 100)}% confidence
                      </div>
                    )}
                  </div>

                  {/* Tools Used */}
                  {msg.metadata.used_tools && msg.metadata.used_tools.length > 0 && (
                    <div className="flex items-center gap-1 text-xs text-gray-600">
                      <FaTools size={10} />
                      <span>Tools: {msg.metadata.used_tools.slice(0, 3).join(', ')}</span>
                      {msg.metadata.used_tools.length > 3 && (
                        <span>+{msg.metadata.used_tools.length - 3} more</span>
                      )}
                    </div>
                  )}

                  {/* Compliance Issues */}
                  {msg.metadata.compliance_issues && msg.metadata.compliance_issues.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-2 text-xs">
                      <div className="flex items-center gap-1 text-yellow-700 font-medium">
                        <FaExclamationTriangle size={10} />
                        <span>Compliance Issues:</span>
                      </div>
                      <ul className="mt-1 text-yellow-600 list-disc list-inside">
                        {msg.metadata.compliance_issues.map((issue, i) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Disclaimer Added */}
                  {msg.metadata.disclaimer_added && (
                    <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      ℹ️ Disclaimer automatically added for compliance
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-xs px-4 py-2 rounded-2xl bg-gray-200 text-gray-800">
                <span className="animate-pulse">🤖 Processing with enterprise safeguards...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="p-4 border-t border-gray-200">
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about investments, portfolio, or market analysis..."
            className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-r-lg hover:from-blue-700 hover:to-purple-700 disabled:from-blue-300 disabled:to-purple-300"
            disabled={isLoading || !input.trim()}
          >
            <FaPaperPlane />
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-1 text-center">
          🛡️ Protected by Enterprise AI • 🔧 {enableCompliance ? 'Compliance Enabled' : 'Compliance Disabled'}
        </div>
      </footer>
    </div>
  );
};

export default EnterpriseChatWindow; 