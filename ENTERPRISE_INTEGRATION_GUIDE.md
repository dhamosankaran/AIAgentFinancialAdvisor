# Enterprise Features Integration Guide

This guide shows you how to integrate the new **Responsible AI Layer**, **Plugin Architecture**, and **Dynamic Tool Discovery** features into your existing AgenticAI API endpoints.

## 🏗️ Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 FastAPI Router                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │   Legacy    │ │ Enterprise  │ │     New Enterprise      ││
│  │ Endpoints   │ │ Enhanced    │ │      Endpoints          ││
│  │ /api/v1/*   │ │ /api/v2/*   │ │   /api/v2/plugins/*     ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Enterprise Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  Responsible    │ │     Plugin      │ │    Dynamic      ││
│  │  AI Service     │ │    Registry     │ │  Coordinator    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Your Existing Services                          │
│     UserProfile, Portfolio, MarketData, etc.                │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Step-by-Step Integration

### Step 1: Update Your Main API File

Replace your existing `src/api/main.py` imports:

```python
# OLD - Basic coordinator
from src.agents import CoordinatorAgent
coordinator = CoordinatorAgent(user_profile_service=user_profile_service)

# NEW - Enterprise coordinator with all features
from src.agents.plugin_enabled_agent import DynamicFinancialAgent
from src.services.responsible_ai_service import ResponsibleAIService
from src.services.plugin_registry import plugin_registry, PluginCategory

# Initialize enterprise services
responsible_ai_service = ResponsibleAIService()
enterprise_coordinator = DynamicFinancialAgent(
    plugin_categories=[
        PluginCategory.MARKET_DATA,
        PluginCategory.AI_ANALYSIS,
        PluginCategory.COMPLIANCE,
        PluginCategory.RISK_ASSESSMENT
    ],
    enable_responsible_ai=True,
    enable_input_moderation=True,
    enable_output_moderation=True,
    enable_hallucination_detection=True,
    block_high_risk=True
)
```

### Step 2: Add Startup Initialization

Add this to initialize enterprise features when your API starts:

```python
@app.on_event("startup")
async def startup_event():
    """Initialize enterprise features on startup"""
    try:
        logger.info("🏢 Starting Enterprise AgenticAI...")
        
        # Initialize plugin registry
        await plugin_registry.initialize_all_plugins()
        
        # Get plugin stats
        stats = plugin_registry.get_plugin_stats()
        logger.info(f"📊 Loaded {stats['active_plugins']} plugins with {stats['total_tools']} tools")
        
        # Initialize enterprise coordinator with latest tools
        await enterprise_coordinator.refresh_plugin_tools()
        
        logger.info("✅ Enterprise AgenticAI initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
```

### Step 3: Enhance Your Existing Chat Endpoint

Transform your basic chat endpoint into an enterprise-grade one:

```python
# BEFORE - Basic chat
@app.post("/api/v1/chat")
async def process_chat(request: ChatRequest):
    response = await coordinator.process_message(request.message, request.user_id)
    return ChatResponse(response=response)

# AFTER - Enterprise chat with full safety and compliance
@app.post("/api/v2/chat", response_model=EnterpriseChatResponse)
async def enterprise_chat(request: ChatRequest):
    logger.info(f"🤖 Processing enterprise chat: {request.message[:50]}...")
    
    # 1. PRE-PROCESSING: Input moderation
    input_moderation = await responsible_ai_service.moderate_input(request.message)
    
    if not input_moderation.passed and request.enable_compliance_check:
        return EnterpriseChatResponse(
            response="I cannot process this request due to safety guidelines. Please rephrase your question.",
            moderation_passed=False,
            risk_level=input_moderation.risk_level.value,
            compliance_issues=input_moderation.issues,
            used_tools=[],
            error="Input blocked by moderation"
        )
    
    # 2. PROCESSING: Use enterprise coordinator with dynamic tools
    response = await enterprise_coordinator.process_message(
        input_moderation.sanitized_content or request.message
    )
    
    # 3. POST-PROCESSING: Output moderation and hallucination detection
    output_moderation = await responsible_ai_service.moderate_output(response, request.message)
    hallucination_result = await responsible_ai_service.detect_hallucinations(response, request.message)
    
    # 4. RESPONSE: Enhanced response with enterprise metadata
    tool_manifest = enterprise_coordinator.get_tool_manifest()
    used_tools = [tool["name"] for tool in tool_manifest["tools"][:5]]
    
    return EnterpriseChatResponse(
        response=output_moderation.sanitized_content or response,
        moderation_passed=output_moderation.passed,
        risk_level=output_moderation.risk_level.value,
        compliance_issues=output_moderation.issues,
        used_tools=used_tools,
        confidence_score=hallucination_result.confidence_score,
        disclaimer_added=output_moderation.sanitized_content != response
    )
```

### Step 4: Enhance Profile Creation with Compliance

Add enterprise validation to profile creation:

```python
@app.post("/api/v2/profile")
async def create_enterprise_profile(request: UserProfileRequest):
    # 1. COMPLIANCE CHECK: Validate profile data
    compliance_check = await responsible_ai_service.moderate_input(
        f"Creating profile for {request.name}, age {request.age}, income {request.income}, risk tolerance {request.risk_tolerance}"
    )
    
    if not compliance_check.passed:
        logger.warning(f"Profile creation blocked: {compliance_check.issues}")
        raise HTTPException(
            status_code=400, 
            detail=f"Profile validation failed: {', '.join(compliance_check.issues)}"
        )
    
    # 2. CREATE PROFILE: Use existing logic
    user_id = str(uuid.uuid4())
    profile = user_profile_service.create_default_profile(
        user_id=user_id,
        name=request.name,
        age=request.age,
        income=request.income
    )
    
    # 3. ENTERPRISE ANALYSIS: Generate initial enterprise report
    enterprise_report = await enterprise_coordinator.process_message(
        f"Generate initial investment guidance for {profile.name}, age {profile.age}, "
        f"income ${profile.income}, {profile.risk_tolerance} risk tolerance"
    )
    
    return UserProfileResponse(...)
```

## 🔧 New Enterprise Endpoints

Add these new endpoints to provide enterprise management capabilities:

### Plugin Management

```python
@app.post("/api/v2/plugins/manage")
async def manage_plugin(request: PluginManagementRequest):
    """Hot-swap plugins without restarting the system"""
    plugin_name = request.plugin_name
    action = request.action.lower()
    
    if action == "load":
        success = await plugin_registry.load_plugin(plugin_name)
        if success:
            await enterprise_coordinator.refresh_plugin_tools()
    elif action == "unload":
        success = await plugin_registry.unload_plugin(plugin_name)
        if success:
            await enterprise_coordinator.refresh_plugin_tools()
    elif action == "reload":
        success = await plugin_registry.reload_plugin(plugin_name)
        if success:
            await enterprise_coordinator.refresh_plugin_tools()
    
    # Return updated plugin status
    plugin_info = plugin_registry.get_plugin_info(plugin_name)
    return PluginStatusResponse(...)

@app.get("/api/v2/plugins/available")
async def get_available_plugins():
    """Get all available plugins and their status"""
    all_plugins = plugin_registry.get_all_plugins()
    
    plugins_list = []
    for plugin_name, plugin_info in all_plugins.items():
        plugins_list.append({
            "name": plugin_name,
            "status": plugin_info.status.value,
            "category": plugin_info.metadata.category.value,
            "version": plugin_info.metadata.version,
            "description": plugin_info.metadata.description,
            "tools_count": len(plugin_info.tools),
            "load_time": plugin_info.load_time.isoformat(),
            "error_message": plugin_info.error_message
        })
    
    return {
        "plugins": plugins_list,
        "total_plugins": len(plugins_list),
        "active_plugins": len([p for p in plugins_list if p["status"] == "active"])
    }
```

### Content Moderation

```python
@app.post("/api/v2/moderation/check")
async def check_content_moderation(request: ModerationRequest):
    """Check any content with responsible AI moderation before processing"""
    if request.content_type == "input":
        moderation_result = await responsible_ai_service.moderate_input(request.content)
    else:
        moderation_result = await responsible_ai_service.moderate_output(request.content)
    
    suggestions = []
    if not moderation_result.passed:
        suggestions = [
            "Remove any prohibited financial terms",
            "Add appropriate disclaimers",
            "Consider compliance requirements",
            "Verify information accuracy"
        ]
    
    return ModerationResponse(
        passed=moderation_result.passed,
        risk_level=moderation_result.risk_level.value,
        issues=moderation_result.issues,
        sanitized_content=moderation_result.sanitized_content,
        suggestions=suggestions
    )
```

### Compliance Checking

```python
@app.post("/api/v2/compliance/check")
async def check_compliance(request: ComplianceCheckRequest):
    """Check content for financial compliance"""
    # Use compliance plugin if available
    compliance_tools = plugin_registry.get_available_tools(PluginCategory.COMPLIANCE)
    
    if not compliance_tools:
        return ComplianceCheckResponse(
            compliant=False,
            required_disclosures=["Plugin not available"],
            regulatory_guidance="Compliance plugin not loaded",
            recommendations=["Load compliance plugin for detailed checking"]
        )
    
    # Perform compliance check
    compliance_result = await responsible_ai_service.moderate_output(request.content)
    
    required_disclosures = [
        "This is not personalized financial advice",
        "Past performance does not guarantee future results", 
        "Investment involves risk of loss",
        "Consult with a qualified financial advisor"
    ]
    
    return ComplianceCheckResponse(
        compliant=compliance_result.passed,
        required_disclosures=required_disclosures,
        regulatory_guidance=f"For {request.advice_type}, ensure proper disclosures and suitability assessment.",
        suitability_assessment="Initial check passed" if compliance_result.passed else "Further review required",
        recommendations=[]
    )
```

## 📊 System Monitoring Endpoints

### Enterprise Status

```python
@app.get("/api/v2/enterprise/status")
async def get_enterprise_status():
    """Get comprehensive enterprise system status"""
    plugin_stats = plugin_registry.get_plugin_stats()
    tool_manifest = enterprise_coordinator.get_tool_manifest()
    
    return {
        "status": "operational",
        "version": "2.0.0",
        "features": {
            "responsible_ai": True,
            "plugin_architecture": True,
            "dynamic_tools": True,
            "compliance_checking": True
        },
        "plugins": plugin_stats,
        "tools": tool_manifest,
        "timestamp": datetime.now().isoformat()
    }
```

### Usage Analytics

```python
@app.get("/api/v2/analytics/usage")
async def get_usage_analytics():
    """Get usage analytics for enterprise features"""
    moderation_stats = responsible_ai_service.get_moderation_stats()
    plugin_stats = plugin_registry.get_plugin_stats()
    tool_usage = await enterprise_coordinator.analyze_tool_usage()
    
    return {
        "moderation": moderation_stats,
        "plugins": plugin_stats,
        "tools": tool_usage,
        "timestamp": datetime.now().isoformat(),
        "system_health": "operational"
    }
```

### Health Check

```python
@app.get("/api/v2/health/enterprise")
async def enterprise_health_check():
    """Comprehensive enterprise health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check plugin registry
    try:
        plugin_stats = plugin_registry.get_plugin_stats()
        health_status["components"]["plugins"] = {
            "status": "healthy",
            "active_plugins": plugin_stats["active_plugins"],
            "total_tools": plugin_stats["total_tools"]
        }
    except Exception as e:
        health_status["components"]["plugins"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check responsible AI service
    try:
        test_moderation = await responsible_ai_service.moderate_input("test message")
        health_status["components"]["responsible_ai"] = {
            "status": "healthy",
            "moderation_working": True
        }
    except Exception as e:
        health_status["components"]["responsible_ai"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check enterprise coordinator
    try:
        tool_count = len(enterprise_coordinator.tools)
        health_status["components"]["enterprise_coordinator"] = {
            "status": "healthy",
            "tools_loaded": tool_count
        }
    except Exception as e:
        health_status["components"]["enterprise_coordinator"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status
```

## 🔄 Backward Compatibility

Keep your existing endpoints working by creating legacy wrappers:

```python
# Legacy endpoint that uses enterprise coordinator but returns simple response
@app.post("/api/v1/chat", response_model=ChatResponse)
async def legacy_chat(request: ChatRequest):
    """Legacy chat endpoint for backward compatibility"""
    try:
        # Use enterprise coordinator but return simple response
        response = await enterprise_coordinator.process_message(request.message, request.user_id)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in legacy chat: {str(e)}")
        return ChatResponse(response="I apologize for the technical difficulty.", error=str(e))
```

## 🎯 Frontend Integration Examples

### Calling Enterprise Chat

```javascript
// Enhanced chat with enterprise features
const response = await fetch('/api/v2/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Should I invest in TSLA?",
    user_id: "user123",
    enable_compliance_check: true,
    risk_tolerance: "moderate"
  })
});

const data = await response.json();
console.log('Response:', data.response);
console.log('Moderation passed:', data.moderation_passed);
console.log('Risk level:', data.risk_level);
console.log('Tools used:', data.used_tools);
console.log('Confidence score:', data.confidence_score);

if (data.compliance_issues.length > 0) {
  console.log('Compliance issues:', data.compliance_issues);
}
```

### Plugin Management

```javascript
// Load a new plugin
const loadPlugin = async (pluginName) => {
  const response = await fetch('/api/v2/plugins/manage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plugin_name: pluginName,
      action: "load"
    })
  });
  
  const result = await response.json();
  console.log(`Plugin ${pluginName} status:`, result.status);
  console.log(`Tools available:`, result.tools_count);
};

// Get all available plugins
const getPlugins = async () => {
  const response = await fetch('/api/v2/plugins/available');
  const data = await response.json();
  
  console.log(`Total plugins: ${data.total_plugins}`);
  console.log(`Active plugins: ${data.active_plugins}`);
  
  data.plugins.forEach(plugin => {
    console.log(`${plugin.name}: ${plugin.status} (${plugin.tools_count} tools)`);
  });
};
```

### Content Moderation

```javascript
// Check content before processing
const checkContent = async (content, contentType) => {
  const response = await fetch('/api/v2/moderation/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content: content,
      content_type: contentType
    })
  });
  
  const result = await response.json();
  
  if (!result.passed) {
    console.log('Content blocked. Issues:', result.issues);
    console.log('Suggestions:', result.suggestions);
    return false;
  }
  
  return true;
};
```

## 🚀 Deployment Considerations

### Environment Variables

Add these to your `.env` file:

```bash
# Enterprise Features
ENABLE_RESPONSIBLE_AI=true
ENABLE_PLUGIN_ARCHITECTURE=true
ENABLE_COMPLIANCE_CHECKING=true
BLOCK_HIGH_RISK_CONTENT=true

# Plugin Configuration
PLUGIN_AUTO_LOAD=true
PLUGIN_DISCOVERY_PATH=./src/plugins
MCP_SERVER_AUTO_START=true

# Monitoring
ENABLE_USAGE_ANALYTICS=true
LOG_MODERATION_EVENTS=true
```

### Production Settings

```python
# In production, use specific configurations
if os.getenv("ENVIRONMENT") == "production":
    enterprise_coordinator = DynamicFinancialAgent(
        plugin_categories=[
            PluginCategory.MARKET_DATA,
            PluginCategory.AI_ANALYSIS,
            PluginCategory.COMPLIANCE
        ],
        enable_responsible_ai=True,
        enable_input_moderation=True,
        enable_output_moderation=True,
        enable_hallucination_detection=True,
        block_high_risk=True,
        compliance_level="strict"
    )
```

## 📈 Benefits Summary

After integration, your API will have:

✅ **Responsible AI Layer**: Automatic content moderation, PII protection, compliance checking
✅ **Plugin Architecture**: Hot-swappable functionality without downtime
✅ **Dynamic Tool Discovery**: Automatic tool integration from plugins
✅ **Enterprise Monitoring**: Health checks, usage analytics, system status
✅ **Backward Compatibility**: Existing endpoints continue working
✅ **Compliance Ready**: Financial regulatory compliance built-in
✅ **Security Enhanced**: Multi-layer security with risk assessment
✅ **Scalability**: Plugin-based architecture for unlimited extensibility

The enterprise features transform your application from a personal financial advisor into a bank-grade system suitable for institutional use while maintaining all existing functionality.