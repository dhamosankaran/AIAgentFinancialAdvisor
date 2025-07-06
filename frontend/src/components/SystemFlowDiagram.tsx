import React, { useState } from 'react';

interface SystemFlowDiagramProps {
  backendMode: 'standard' | 'enterprise';
}

const SystemFlowDiagram: React.FC<SystemFlowDiagramProps> = ({ backendMode }) => {
  const [selectedFlow, setSelectedFlow] = useState<'overview' | 'fap' | 'chat' | 'mcp'>('overview');
  const [hoveredComponent, setHoveredComponent] = useState<string | null>(null);

  const FlowCard = ({ 
    title, 
    description, 
    icon, 
    color, 
    isActive, 
    onClick 
  }: {
    title: string;
    description: string;
    icon: string;
    color: string;
    isActive: boolean;
    onClick: () => void;
  }) => (
    <div
      className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
        isActive 
          ? `${color} text-white shadow-lg transform scale-105` 
          : 'bg-white border-2 border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center mb-2">
        <span className="text-2xl mr-3">{icon}</span>
        <h3 className="font-bold text-lg">{title}</h3>
      </div>
      <p className={`text-sm ${isActive ? 'text-white' : 'text-gray-600'}`}>
        {description}
      </p>
    </div>
  );

  const ComponentBox = ({ 
    name, 
    description, 
    type, 
    onHover, 
    isHovered 
  }: {
    name: string;
    description: string;
    type: 'frontend' | 'api' | 'agent' | 'service' | 'external';
    onHover: (name: string | null) => void;
    isHovered: boolean;
  }) => {
    const colors = {
      frontend: 'bg-blue-100 border-blue-300 text-blue-800',
      api: 'bg-green-100 border-green-300 text-green-800',
      agent: 'bg-purple-100 border-purple-300 text-purple-800',
      service: 'bg-orange-100 border-orange-300 text-orange-800',
      external: 'bg-gray-100 border-gray-300 text-gray-800'
    };

    return (
      <div
        className={`p-3 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
          isHovered 
            ? `${colors[type]} shadow-lg transform scale-105` 
            : `${colors[type]} hover:shadow-md`
        }`}
        onMouseEnter={() => onHover(name)}
        onMouseLeave={() => onHover(null)}
      >
        <div className="font-semibold text-sm mb-1">{name}</div>
        <div className="text-xs opacity-80">{description}</div>
      </div>
    );
  };

  const Arrow = ({ direction = 'right', color = 'gray' }: { direction?: string; color?: string }) => (
    <div className={`flex items-center justify-center text-${color}-500`}>
      {direction === 'right' && <span className="text-2xl">→</span>}
      {direction === 'down' && <span className="text-2xl">↓</span>}
      {direction === 'up' && <span className="text-2xl">↑</span>}
      {direction === 'left' && <span className="text-2xl">←</span>}
    </div>
  );

  const renderOverviewFlow = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          🔄 Complete System Architecture Overview
        </h3>
        <p className="text-gray-600 mb-8">
          End-to-end flow showing all major components and their interactions
        </p>
      </div>

      {/* Layer 1: Frontend */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-blue-800 mb-4">🖥️ Frontend Layer (React + TypeScript)</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <ComponentBox
            name="User Interface"
            description="React components, forms, dashboards"
            type="frontend"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'User Interface'}
          />
          <ComponentBox
            name="State Management"
            description="User profile, FAP results, chat history"
            type="frontend"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'State Management'}
          />
          <ComponentBox
            name="API Client"
            description="HTTP requests to backend APIs"
            type="frontend"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'API Client'}
          />
          <ComponentBox
            name="Real-time Updates"
            description="WebSocket connections, live data"
            type="frontend"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Real-time Updates'}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <Arrow direction="down" color="blue" />
      </div>

      {/* Layer 2: API Gateway */}
      <div className="bg-green-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-green-800 mb-4">🚀 API Layer (FastAPI)</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ComponentBox
            name="REST Endpoints"
            description="/api/v1/* routes, request validation"
            type="api"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'REST Endpoints'}
          />
          <ComponentBox
            name="Authentication"
            description="User session management, security"
            type="api"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Authentication'}
          />
          <ComponentBox
            name="Request Routing"
            description="Route to appropriate services/agents"
            type="api"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Request Routing'}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <Arrow direction="down" color="green" />
      </div>

      {/* Layer 3: Agent Orchestration */}
      <div className="bg-purple-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-purple-800 mb-4">🤖 Agent Layer (LangChain + LangGraph)</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <ComponentBox
            name="FAP Pipeline"
            description="4-stage financial advisory pipeline"
            type="agent"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'FAP Pipeline'}
          />
          <ComponentBox
            name="Portfolio Agent"
            description="Portfolio analysis and allocation"
            type="agent"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Portfolio Agent'}
          />
          <ComponentBox
            name="Risk Agent"
            description="Risk assessment and scoring"
            type="agent"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Risk Agent'}
          />
          <ComponentBox
            name="Chat Agent"
            description="Conversational financial advice"
            type="agent"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Chat Agent'}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <Arrow direction="down" color="purple" />
      </div>

      {/* Layer 4: Services & MCP */}
      <div className="bg-orange-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-orange-800 mb-4">⚙️ Service Layer (MCP Integration)</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ComponentBox
            name="MCP Client"
            description="Model Context Protocol client"
            type="service"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'MCP Client'}
          />
          <ComponentBox
            name="Market Data Server"
            description="Real-time market data via MCP"
            type="service"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Market Data Server'}
          />
          <ComponentBox
            name="AI Analysis Server"
            description="AI-powered analysis via MCP"
            type="service"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'AI Analysis Server'}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <Arrow direction="down" color="orange" />
      </div>

      {/* Layer 5: External Services */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-gray-800 mb-4">🌐 External Services</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <ComponentBox
            name="OpenAI API"
            description="GPT-4 for financial analysis"
            type="external"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'OpenAI API'}
          />
          <ComponentBox
            name="Alpha Vantage"
            description="Market data and stock prices"
            type="external"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Alpha Vantage'}
          />
          <ComponentBox
            name="LangSmith"
            description="Observability and evaluation"
            type="external"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'LangSmith'}
          />
          <ComponentBox
            name="Data Storage"
            description="User profiles, FAP results"
            type="external"
            onHover={setHoveredComponent}
            isHovered={hoveredComponent === 'Data Storage'}
          />
        </div>
      </div>

      {/* LangSmith Observability Overlay */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border-2 border-indigo-200">
        <h4 className="text-lg font-bold text-indigo-800 mb-4">📊 LangSmith Observability (Cross-Layer)</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border border-indigo-200">
            <div className="font-semibold text-indigo-800 mb-2">🔍 Tracing</div>
            <div className="text-sm text-indigo-600">
              Complete request flow tracking from frontend to external APIs
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-indigo-200">
            <div className="font-semibold text-indigo-800 mb-2">📈 Evaluation</div>
            <div className="text-sm text-indigo-600">
              Quality assessment with custom financial evaluators
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-indigo-200">
            <div className="font-semibold text-indigo-800 mb-2">⚡ Performance</div>
            <div className="text-sm text-indigo-600">
              Real-time metrics, latency tracking, error monitoring
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFAPFlow = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          🤖 Financial Advisory Pipeline (FAP) Flow
        </h3>
        <p className="text-gray-600 mb-8">
          4-stage pipeline with comprehensive LangSmith tracing
        </p>
      </div>

      {/* FAP Request Flow */}
      <div className="space-y-6">
        {/* Stage 1: Profile Analysis */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">1</div>
            <h4 className="text-lg font-bold text-blue-800">Profile Analysis Stage</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">📊 Input Processing</div>
              <div className="text-sm text-blue-600">
                User profile data (age, income, risk tolerance, goals)
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">🔍 MCP Analysis</div>
              <div className="text-sm text-blue-600">
                AI Analysis Server via MCP for profile evaluation
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">📈 LangSmith Trace</div>
              <div className="text-sm text-blue-600">
                Profile analysis performance and quality metrics
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Arrow direction="down" color="blue" />
        </div>

        {/* Stage 2: Risk Assessment */}
        <div className="bg-orange-50 p-6 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="bg-orange-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">2</div>
            <h4 className="text-lg font-bold text-orange-800">Risk Assessment Stage</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-orange-200">
              <div className="font-semibold text-orange-800 mb-2">⚖️ Risk Calculation</div>
              <div className="text-sm text-orange-600">
                Multi-factor risk scoring algorithm
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-orange-200">
              <div className="font-semibold text-orange-800 mb-2">🎯 Risk Categorization</div>
              <div className="text-sm text-orange-600">
                Conservative, Moderate, or Aggressive classification
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-orange-200">
              <div className="font-semibold text-orange-800 mb-2">📊 LangSmith Evaluation</div>
              <div className="text-sm text-orange-600">
                Risk assessment accuracy and alignment evaluation
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Arrow direction="down" color="orange" />
        </div>

        {/* Stage 3: Strategy Generation */}
        <div className="bg-green-50 p-6 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">3</div>
            <h4 className="text-lg font-bold text-green-800">Strategy Generation Stage</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">📈 Market Data</div>
              <div className="text-sm text-green-600">
                Real-time market data via MCP Market Data Server
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">🎯 Allocation Logic</div>
              <div className="text-sm text-green-600">
                Risk-based portfolio allocation (stocks, bonds, cash)
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">🔍 LangSmith Trace</div>
              <div className="text-sm text-green-600">
                Strategy generation performance and diversification metrics
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Arrow direction="down" color="green" />
        </div>

        {/* Stage 4: Recommendation Explanation */}
        <div className="bg-purple-50 p-6 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="bg-purple-500 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-4">4</div>
            <h4 className="text-lg font-bold text-purple-800">Recommendation Explanation Stage</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 mb-2">📝 Analysis Generation</div>
              <div className="text-sm text-purple-600">
                Comprehensive financial analysis with OpenAI GPT-4
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 mb-2">🎯 Personalization</div>
              <div className="text-sm text-purple-600">
                Tailored explanations based on user profile and goals
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 mb-2">✅ Quality Evaluation</div>
              <div className="text-sm text-purple-600">
                LangSmith financial advice quality assessment
              </div>
            </div>
          </div>
        </div>

        {/* Final Results */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg border-2 border-indigo-200">
          <h4 className="text-lg font-bold text-indigo-800 mb-4">🎯 FAP Results Output</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-indigo-200">
              <div className="font-semibold text-indigo-800 mb-2">📊 Portfolio Allocation</div>
              <div className="text-sm text-indigo-600 mb-2">
                Risk-aligned asset allocation percentages
              </div>
              <div className="text-xs text-indigo-500">
                • Conservative: 70% bonds, 20% stocks, 10% cash<br/>
                • Moderate: 50% stocks, 30% bonds, 20% cash<br/>
                • Aggressive: 70% stocks, 15% bonds, 15% cash
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-indigo-200">
              <div className="font-semibold text-indigo-800 mb-2">📈 Comprehensive Analysis</div>
              <div className="text-sm text-indigo-600 mb-2">
                Detailed financial analysis and recommendations
              </div>
              <div className="text-xs text-indigo-500">
                • Profile analysis and risk factors<br/>
                • Market outlook and strategy rationale<br/>
                • Personalized investment recommendations
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderChatFlow = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          💬 Chat System Flow
        </h3>
        <p className="text-gray-600 mb-8">
          Real-time conversational financial advice with enterprise features
        </p>
      </div>

      {/* Chat Flow Diagram */}
      <div className="space-y-6">
        {/* User Input */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <h4 className="text-lg font-bold text-blue-800 mb-4">💭 User Input Processing</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">⌨️ Message Input</div>
              <div className="text-sm text-blue-600">
                User types financial question or request
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">🔍 Context Analysis</div>
              <div className="text-sm text-blue-600">
                Extract intent and financial context
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="font-semibold text-blue-800 mb-2">📊 Profile Integration</div>
              <div className="text-sm text-blue-600">
                Load user profile and FAP results for context
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Arrow direction="down" color="blue" />
        </div>

        {/* Chat Agent Processing */}
        <div className="bg-purple-50 p-6 rounded-lg">
          <h4 className="text-lg font-bold text-purple-800 mb-4">🤖 Chat Agent Processing</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 mb-2">🧠 LangChain Processing</div>
              <div className="text-sm text-purple-600 mb-2">
                Agent-based conversation handling
              </div>
              <div className="text-xs text-purple-500">
                • Message understanding<br/>
                • Context maintenance<br/>
                • Response planning
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <div className="font-semibold text-purple-800 mb-2">🔧 MCP Tool Usage</div>
              <div className="text-sm text-purple-600 mb-2">
                Dynamic tool selection and execution
              </div>
              <div className="text-xs text-purple-500">
                • Market data retrieval<br/>
                • Portfolio analysis<br/>
                • Risk assessment
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Arrow direction="down" color="purple" />
        </div>

        {/* Response Generation */}
        <div className="bg-green-50 p-6 rounded-lg">
          <h4 className="text-lg font-bold text-green-800 mb-4">💡 Response Generation</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">🎯 OpenAI Integration</div>
              <div className="text-sm text-green-600">
                GPT-4 generates personalized financial advice
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">🛡️ Safety Filtering</div>
              <div className="text-sm text-green-600">
                Compliance checks and safety validation
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="font-semibold text-green-800 mb-2">📊 LangSmith Trace</div>
              <div className="text-sm text-green-600">
                Response quality and performance tracking
              </div>
            </div>
          </div>
        </div>

        {/* Enterprise vs Standard Mode */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-lg border-2 border-purple-200">
            <h4 className="text-lg font-bold text-purple-800 mb-4">🏢 Enterprise Mode Features</h4>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm">Advanced Analytics</div>
                <div className="text-xs text-purple-600">
                  Enhanced financial analysis with compliance tracking
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm">Plugin System</div>
                <div className="text-xs text-purple-600">
                  Extensible plugin architecture for custom features
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm">Audit Trail</div>
                <div className="text-xs text-purple-600">
                  Complete conversation logging for compliance
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-lg border-2 border-blue-200">
            <h4 className="text-lg font-bold text-blue-800 mb-4">🎯 Standard Mode Features</h4>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <div className="font-semibold text-blue-800 text-sm">Core Chat</div>
                <div className="text-xs text-blue-600">
                  Essential conversational financial advice
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <div className="font-semibold text-blue-800 text-sm">Basic Analytics</div>
                <div className="text-xs text-blue-600">
                  Standard financial analysis and recommendations
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-blue-200">
                <div className="font-semibold text-blue-800 text-sm">Simple Logging</div>
                <div className="text-xs text-blue-600">
                  Basic conversation history and user preferences
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMCPFlow = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          🔌 Model Context Protocol (MCP) Integration
        </h3>
        <p className="text-gray-600 mb-8">
          Secure, standardized communication between AI agents and external services
        </p>
      </div>

      {/* MCP Architecture */}
      <div className="space-y-6">
        {/* MCP Client */}
        <div className="bg-indigo-50 p-6 rounded-lg">
          <h4 className="text-lg font-bold text-indigo-800 mb-4">🔧 MCP Client (Central Hub)</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-indigo-200">
              <div className="font-semibold text-indigo-800 mb-2">🎯 Connection Management</div>
              <div className="text-sm text-indigo-600">
                Manages connections to multiple MCP servers
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-indigo-200">
              <div className="font-semibold text-indigo-800 mb-2">🔄 Request Routing</div>
              <div className="text-sm text-indigo-600">
                Routes tool calls to appropriate MCP servers
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-indigo-200">
              <div className="font-semibold text-indigo-800 mb-2">🛡️ Error Handling</div>
              <div className="text-sm text-indigo-600">
                Fallback mechanisms and graceful degradation
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center space-x-8">
          <Arrow direction="down" color="indigo" />
          <Arrow direction="down" color="indigo" />
        </div>

        {/* MCP Servers */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Market Data Server */}
          <div className="bg-green-50 p-6 rounded-lg">
            <h4 className="text-lg font-bold text-green-800 mb-4">📈 Market Data Server</h4>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg border border-green-200">
                <div className="font-semibold text-green-800 text-sm mb-1">🔧 Available Tools</div>
                <div className="text-xs text-green-600">
                  • get_stock_quote<br/>
                  • get_market_summary<br/>
                  • get_market_trends<br/>
                  • get_sector_performance
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-green-200">
                <div className="font-semibold text-green-800 text-sm mb-1">🌐 Data Sources</div>
                <div className="text-xs text-green-600">
                  Alpha Vantage API for real-time market data
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-green-200">
                <div className="font-semibold text-green-800 text-sm mb-1">⚡ Caching</div>
                <div className="text-xs text-green-600">
                  Intelligent caching to optimize API usage
                </div>
              </div>
            </div>
          </div>

          {/* AI Analysis Server */}
          <div className="bg-purple-50 p-6 rounded-lg">
            <h4 className="text-lg font-bold text-purple-800 mb-4">🤖 AI Analysis Server</h4>
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm mb-1">🔧 Available Tools</div>
                <div className="text-xs text-purple-600">
                  • analyze_portfolio<br/>
                  • assess_risk<br/>
                  • generate_recommendations<br/>
                  • evaluate_strategy
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm mb-1">🧠 AI Integration</div>
                <div className="text-xs text-purple-600">
                  OpenAI GPT-4 for financial analysis
                </div>
              </div>
              <div className="bg-white p-3 rounded-lg border border-purple-200">
                <div className="font-semibold text-purple-800 text-sm mb-1">📊 Quality Control</div>
                <div className="text-xs text-purple-600">
                  Built-in validation and safety checks
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* MCP Communication Flow */}
        <div className="bg-orange-50 p-6 rounded-lg">
          <h4 className="text-lg font-bold text-orange-800 mb-4">🔄 MCP Communication Flow</h4>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">1. Request</div>
              <div className="text-xs text-orange-600">
                Agent calls MCP tool
              </div>
            </div>
            <div className="flex items-center justify-center">
              <Arrow direction="right" color="orange" />
            </div>
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">2. Route</div>
              <div className="text-xs text-orange-600">
                Client routes to server
              </div>
            </div>
            <div className="flex items-center justify-center">
              <Arrow direction="right" color="orange" />
            </div>
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">3. Execute</div>
              <div className="text-xs text-orange-600">
                Server processes request
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4">
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">4. Response</div>
              <div className="text-xs text-orange-600">
                Server returns results
              </div>
            </div>
            <div className="flex items-center justify-center">
              <Arrow direction="left" color="orange" />
            </div>
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">5. Deliver</div>
              <div className="text-xs text-orange-600">
                Client delivers to agent
              </div>
            </div>
            <div className="flex items-center justify-center">
              <Arrow direction="left" color="orange" />
            </div>
            <div className="bg-white p-3 rounded-lg border border-orange-200 text-center">
              <div className="font-semibold text-orange-800 text-sm mb-1">6. Continue</div>
              <div className="text-xs text-orange-600">
                Agent continues processing
              </div>
            </div>
          </div>
        </div>

        {/* MCP Benefits */}
        <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-6 rounded-lg border-2 border-cyan-200">
          <h4 className="text-lg font-bold text-cyan-800 mb-4">✅ MCP Integration Benefits</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-cyan-200">
              <div className="font-semibold text-cyan-800 mb-2">🔒 Security</div>
              <div className="text-sm text-cyan-600">
                Controlled access to external services with proper authentication
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-cyan-200">
              <div className="font-semibold text-cyan-800 mb-2">🔧 Modularity</div>
              <div className="text-sm text-cyan-600">
                Easy to add new tools and services without core changes
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-cyan-200">
              <div className="font-semibold text-cyan-800 mb-2">📊 Observability</div>
              <div className="text-sm text-cyan-600">
                Complete tracing of tool usage through LangSmith integration
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          🏗️ System Architecture & Flow Diagrams
        </h2>
        <p className="text-gray-600 mb-6">
          Comprehensive visualization of the Financial Investment Advisor Agent system
        </p>
        <div className="flex justify-center mb-2">
          <span className={`text-xs px-3 py-1 rounded ${
            backendMode === 'enterprise' 
              ? 'bg-purple-100 text-purple-800' 
              : 'bg-blue-100 text-blue-800'
          }`}>
            Running in {backendMode.charAt(0).toUpperCase() + backendMode.slice(1)} Mode
          </span>
        </div>
      </div>

      {/* Flow Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <FlowCard
          title="System Overview"
          description="Complete architecture with all layers and components"
          icon="🔄"
          color="bg-blue-500"
          isActive={selectedFlow === 'overview'}
          onClick={() => setSelectedFlow('overview')}
        />
        <FlowCard
          title="FAP Pipeline"
          description="4-stage Financial Advisory Pipeline with tracing"
          icon="🤖"
          color="bg-purple-500"
          isActive={selectedFlow === 'fap'}
          onClick={() => setSelectedFlow('fap')}
        />
        <FlowCard
          title="Chat System"
          description="Real-time conversational AI with enterprise features"
          icon="💬"
          color="bg-green-500"
          isActive={selectedFlow === 'chat'}
          onClick={() => setSelectedFlow('chat')}
        />
        <FlowCard
          title="MCP Integration"
          description="Model Context Protocol for secure tool access"
          icon="🔌"
          color="bg-orange-500"
          isActive={selectedFlow === 'mcp'}
          onClick={() => setSelectedFlow('mcp')}
        />
      </div>

      {/* Flow Diagram Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {selectedFlow === 'overview' && renderOverviewFlow()}
        {selectedFlow === 'fap' && renderFAPFlow()}
        {selectedFlow === 'chat' && renderChatFlow()}
        {selectedFlow === 'mcp' && renderMCPFlow()}
      </div>

      {/* Legend */}
      <div className="mt-8 bg-gray-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-gray-800 mb-4">🔍 Component Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-100 border border-blue-300 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Frontend</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-100 border border-green-300 rounded mr-2"></div>
            <span className="text-sm text-gray-700">API Layer</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-purple-100 border border-purple-300 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Agents</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-orange-100 border border-orange-300 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Services</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded mr-2"></div>
            <span className="text-sm text-gray-700">External</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemFlowDiagram; 