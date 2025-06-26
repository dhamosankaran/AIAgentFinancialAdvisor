import React, { useState, useEffect } from 'react';
import { 
  FaPlug, 
  FaPlay, 
  FaStop, 
  FaSync, 
  FaCog, 
  FaTools, 
  FaExclamationTriangle, 
  FaCheckCircle,
  FaTimesCircle,
  FaInfo,
  FaChartBar
} from 'react-icons/fa';

interface Plugin {
  name: string;
  status: string;
  category: string;
  version: string;
  description: string;
  tools_count: number;
  load_time: string;
  error_message?: string;
}

interface PluginStats {
  total_plugins: number;
  active_plugins: number;
}

interface SystemStatus {
  status: string;
  version: string;
  features: {
    responsible_ai: boolean;
    plugin_architecture: boolean;
    dynamic_tools: boolean;
    compliance_checking: boolean;
  };
  plugins: PluginStats;
  timestamp: string;
}

const PluginManager: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [config, setConfig] = useState('{}');

  useEffect(() => {
    loadPlugins();
    loadSystemStatus();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadPlugins();
      loadSystemStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/v2/plugins/available');
      if (response.ok) {
        const data = await response.json();
        setPlugins(data.plugins || []);
      }
    } catch (error) {
      console.error('Failed to load plugins:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/api/v2/enterprise/status');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data);
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const handlePluginAction = async (pluginName: string, action: string, pluginConfig?: any) => {
    setActionLoading(pluginName);
    
    try {
      const response = await fetch('/api/v2/plugins/manage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plugin_name: pluginName,
          action: action,
          config: pluginConfig
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`Plugin ${pluginName} ${action}:`, result);
        
        // Refresh plugins and system status
        await loadPlugins();
        await loadSystemStatus();
        
        // Show success message
        alert(`Plugin ${pluginName} ${action} successful!`);
      } else {
        const error = await response.json();
        alert(`Failed to ${action} plugin ${pluginName}: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error(`Plugin ${action} error:`, error);
      alert(`Error ${action} plugin ${pluginName}: ${error}`);
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <FaCheckCircle className="text-green-500" />;
      case 'error': return <FaTimesCircle className="text-red-500" />;
      case 'loading': return <FaSync className="text-yellow-500 animate-spin" />;
      default: return <FaExclamationTriangle className="text-gray-500" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'market_data': return 'bg-blue-100 text-blue-800';
      case 'ai_analysis': return 'bg-purple-100 text-purple-800';
      case 'compliance': return 'bg-green-100 text-green-800';
      case 'risk_assessment': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleConfigSubmit = async () => {
    if (!selectedPlugin) return;
    
    try {
      const parsedConfig = JSON.parse(config);
      await handlePluginAction(selectedPlugin.name, 'configure', parsedConfig);
      setShowConfig(false);
      setSelectedPlugin(null);
      setConfig('{}');
    } catch (error) {
      alert('Invalid JSON configuration');
    }
  };

  if (loading && plugins.length === 0) {
    return (
      <div className="p-8 text-center">
        <FaSync className="mx-auto text-4xl text-blue-500 animate-spin mb-4" />
        <p className="text-gray-600">Loading plugin manager...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <FaPlug className="text-blue-600" />
          Enterprise Plugin Manager
        </h1>
        <p className="text-gray-600">Manage plugins and enterprise features in real-time</p>
      </div>

      {/* System Status Overview */}
      {systemStatus && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FaChartBar className="text-green-600" />
            System Status
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{systemStatus.plugins.active_plugins}</div>
              <div className="text-sm text-blue-700">Active Plugins</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{systemStatus.plugins.total_plugins}</div>
              <div className="text-sm text-purple-700">Total Plugins</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{systemStatus.status.toUpperCase()}</div>
              <div className="text-sm text-green-700">System Status</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">v{systemStatus.version}</div>
              <div className="text-sm text-orange-700">Enterprise Version</div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {Object.entries(systemStatus.features).map(([feature, enabled]) => (
              <span
                key={feature}
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}
              >
                {enabled ? '✅' : '❌'} {feature.replace('_', ' ').toUpperCase()}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Plugin Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plugins.map((plugin) => (
          <div key={plugin.name} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                {getStatusIcon(plugin.status)}
                <div>
                  <h3 className="font-semibold text-gray-900">{plugin.name}</h3>
                  <p className="text-sm text-gray-600">{plugin.description}</p>
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full font-medium ${getCategoryColor(plugin.category)}`}>
                {plugin.category.replace('_', ' ')}
              </span>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Version:</span>
                <span className="font-medium">{plugin.version}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Tools:</span>
                <span className="font-medium flex items-center gap-1">
                  <FaTools size={12} />
                  {plugin.tools_count}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status:</span>
                <span className={`font-medium ${
                  plugin.status === 'active' ? 'text-green-600' : 
                  plugin.status === 'error' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {plugin.status.toUpperCase()}
                </span>
              </div>
            </div>

            {plugin.error_message && (
              <div className="bg-red-50 border border-red-200 rounded p-2 mb-4">
                <div className="flex items-center gap-2 text-red-700 text-xs">
                  <FaExclamationTriangle size={12} />
                  <span className="font-medium">Error:</span>
                </div>
                <p className="text-red-600 text-xs mt-1">{plugin.error_message}</p>
              </div>
            )}

            <div className="flex gap-2">
              {plugin.status === 'active' ? (
                <>
                  <button
                    onClick={() => handlePluginAction(plugin.name, 'unload')}
                    disabled={actionLoading === plugin.name}
                    className="flex-1 bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded text-xs font-medium disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    {actionLoading === plugin.name ? <FaSync className="animate-spin" size={12} /> : <FaStop size={12} />}
                    Unload
                  </button>
                  <button
                    onClick={() => handlePluginAction(plugin.name, 'reload')}
                    disabled={actionLoading === plugin.name}
                    className="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-2 rounded text-xs font-medium disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    {actionLoading === plugin.name ? <FaSync className="animate-spin" size={12} /> : <FaSync size={12} />}
                    Reload
                  </button>
                </>
              ) : (
                <button
                  onClick={() => handlePluginAction(plugin.name, 'load')}
                  disabled={actionLoading === plugin.name}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded text-xs font-medium disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {actionLoading === plugin.name ? <FaSync className="animate-spin" size={12} /> : <FaPlay size={12} />}
                  Load
                </button>
              )}
              
              <button
                onClick={() => {
                  setSelectedPlugin(plugin);
                  setShowConfig(true);
                }}
                className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded text-xs font-medium flex items-center gap-1"
              >
                <FaCog size={12} />
                Config
              </button>
            </div>
          </div>
        ))}
      </div>

      {plugins.length === 0 && !loading && (
        <div className="text-center py-12">
          <FaInfo className="mx-auto text-4xl text-gray-400 mb-4" />
          <p className="text-gray-600">No plugins found. Check your plugin directory.</p>
        </div>
      )}

      {/* Configuration Modal */}
      {showConfig && selectedPlugin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Configure {selectedPlugin.name}</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Configuration (JSON)
              </label>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 rounded-lg font-mono text-sm"
                placeholder='{"key": "value"}'
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleConfigSubmit}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-medium"
              >
                Apply Configuration
              </button>
              <button
                onClick={() => {
                  setShowConfig(false);
                  setSelectedPlugin(null);
                  setConfig('{}');
                }}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PluginManager; 