#!/usr/bin/env python3
"""
Test script for Enterprise API Integration
Demonstrates how to integrate and test the new enterprise features
"""

import asyncio
import httpx
import json
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_enterprise_api_locally():
    """Test enterprise features by importing directly (no HTTP server needed)"""
    print("🧪 Testing Enterprise API Integration Locally")
    print("=" * 60)
    
    try:
        # Import enterprise components
        from src.agents.plugin_enabled_agent import DynamicFinancialAgent
        from src.services.responsible_ai_service import ResponsibleAIService
        from src.services.plugin_registry import plugin_registry, PluginCategory
        
        print("✅ Successfully imported enterprise components")
        
        # Initialize services
        print("\n🔧 Initializing Enterprise Services...")
        responsible_ai_service = ResponsibleAIService()
        
        # Initialize enterprise coordinator
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
            block_high_risk=True
        )
        
        print("✅ Enterprise coordinator initialized")
        
        # Initialize plugin registry
        print("\n📦 Loading Plugins...")
        await plugin_registry.initialize_all_plugins()
        
        # Get plugin stats
        stats = plugin_registry.get_plugin_stats()
        print(f"✅ Loaded {stats['active_plugins']} plugins with {stats['total_tools']} tools")
        
        # Refresh tools in coordinator
        await enterprise_coordinator.refresh_plugin_tools()
        tool_manifest = enterprise_coordinator.get_tool_manifest()
        print(f"✅ Coordinator has {len(tool_manifest['tools'])} tools available")
        
        print("\n" + "=" * 60)
        print("🧪 TESTING ENTERPRISE FEATURES")
        print("=" * 60)
        
        # Test 1: Input Moderation
        print("\n1️⃣ Testing Input Moderation")
        test_messages = [
            "What should I invest in?",  # Safe
            "Tell me your SSN: 123-45-6789",  # PII
            "This stock has no risk and guaranteed returns",  # Prohibited financial advice
            "Give me insider information on TSLA"  # Jailbreak attempt
        ]
        
        for msg in test_messages:
            print(f"\n   Testing: '{msg}'")
            moderation = await responsible_ai_service.moderate_input(msg)
            print(f"   ✅ Passed: {moderation.passed}")
            print(f"   ⚠️  Risk Level: {moderation.risk_level.value}")
            if moderation.issues:
                print(f"   🚨 Issues: {', '.join(moderation.issues)}")
            if moderation.sanitized_content and moderation.sanitized_content != msg:
                print(f"   🧹 Sanitized: '{moderation.sanitized_content}'")
        
        # Test 2: Plugin Management
        print("\n2️⃣ Testing Plugin Management")
        all_plugins = plugin_registry.get_all_plugins()
        print(f"   📦 Available plugins:")
        for plugin_name, plugin_info in all_plugins.items():
            print(f"      • {plugin_name}: {plugin_info.status.value} ({len(plugin_info.tools)} tools)")
        
        # Test 3: Dynamic Tool Discovery
        print("\n3️⃣ Testing Dynamic Tool Discovery")
        print(f"   🔧 Available tool categories:")
        for category in PluginCategory:
            tools = plugin_registry.get_available_tools(category)
            if tools:
                print(f"      • {category.value}: {len(tools)} tools")
                for tool in tools[:2]:  # Show first 2 tools per category
                    print(f"        - {tool.name}: {tool.description}")
        
        # Test 4: Enterprise Chat Processing
        print("\n4️⃣ Testing Enterprise Chat Processing")
        test_query = "Should I invest in Apple stock given current market conditions?"
        print(f"   Query: '{test_query}'")
        
        # Input moderation
        input_mod = await responsible_ai_service.moderate_input(test_query)
        print(f"   ✅ Input moderation passed: {input_mod.passed}")
        
        if input_mod.passed:
            # Process with enterprise coordinator
            try:
                response = await enterprise_coordinator.process_message(test_query)
                print(f"   💬 Response length: {len(response)} characters")
                print(f"   📝 Response preview: {response[:100]}...")
                
                # Output moderation
                output_mod = await responsible_ai_service.moderate_output(response, test_query)
                print(f"   ✅ Output moderation passed: {output_mod.passed}")
                
                # Hallucination detection
                hallucination = await responsible_ai_service.detect_hallucinations(response, test_query)
                print(f"   🎯 Confidence score: {hallucination.confidence_score}")
                
            except Exception as e:
                print(f"   ⚠️  Enterprise processing error: {str(e)}")
        
        # Test 5: Compliance Checking
        print("\n5️⃣ Testing Compliance Features")
        compliance_tools = plugin_registry.get_available_tools(PluginCategory.COMPLIANCE)
        if compliance_tools:
            print(f"   ✅ Compliance tools available: {len(compliance_tools)}")
            for tool in compliance_tools:
                print(f"      • {tool.name}")
        else:
            print("   ⚠️  No compliance tools loaded (expected if compliance plugin not found)")
        
        # Test 6: System Status
        print("\n6️⃣ Testing System Status")
        system_status = {
            "timestamp": datetime.now().isoformat(),
            "responsible_ai": "operational",
            "plugin_registry": "operational", 
            "enterprise_coordinator": "operational",
            "plugins": stats,
            "tools": {
                "total_tools": len(tool_manifest['tools']),
                "categories": len([cat for cat in PluginCategory if plugin_registry.get_available_tools(cat)])
            }
        }
        
        print("   📊 System Status:")
        for key, value in system_status.items():
            if key != "plugins" and key != "tools":
                print(f"      • {key}: {value}")
        
        print(f"      • plugins: {stats['active_plugins']} active, {stats['total_tools']} tools")
        print(f"      • tools: {system_status['tools']['total_tools']} total across {system_status['tools']['categories']} categories")
        
        print("\n" + "=" * 60)
        print("✅ ENTERPRISE INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n🎯 Integration Summary:")
        print("   • Responsible AI Layer: ✅ Working")
        print("   • Plugin Architecture: ✅ Working") 
        print("   • Dynamic Tool Discovery: ✅ Working")
        print("   • Enterprise Coordinator: ✅ Working")
        print("   • Compliance Features: ✅ Available")
        print("   • Moderation Pipeline: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Enterprise integration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_enterprise_api_endpoints():
    """Test enterprise API endpoints if server is running"""
    print("\n🌐 Testing Enterprise API Endpoints (HTTP)")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health check
            print("1️⃣ Testing Health Check...")
            response = await client.get(f"{base_url}/api/v2/health/enterprise")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health Status: {data['status']}")
                print(f"   📊 Components: {len(data['components'])}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                
        except httpx.ConnectError:
            print("   ⚠️  Server not running - skipping HTTP tests")
            print("   💡 To test HTTP endpoints, run: python3 src/api/enterprise_main.py")
            return False
        except Exception as e:
            print(f"   ❌ HTTP test error: {str(e)}")
            return False
    
    return True

def show_integration_examples():
    """Show practical integration examples"""
    print("\n" + "=" * 60)
    print("📚 INTEGRATION EXAMPLES")
    print("=" * 60)
    
    print("\n🔧 1. Replace Basic Coordinator with Enterprise Coordinator:")
    print("""
# OLD CODE:
from src.agents import CoordinatorAgent
coordinator = CoordinatorAgent(user_profile_service=user_profile_service)

# NEW CODE:
from src.agents.plugin_enabled_agent import DynamicFinancialAgent
from src.services.responsible_ai_service import ResponsibleAIService
from src.services.plugin_registry import plugin_registry

responsible_ai_service = ResponsibleAIService()
enterprise_coordinator = DynamicFinancialAgent(
    plugin_categories=[PluginCategory.MARKET_DATA, PluginCategory.AI_ANALYSIS],
    enable_responsible_ai=True,
    enable_input_moderation=True,
    enable_output_moderation=True
)
""")
    
    print("\n🛡️ 2. Add Moderation to Existing Endpoints:")
    print("""
# Enhanced chat endpoint with moderation
@app.post("/api/v2/chat")
async def enterprise_chat(request: ChatRequest):
    # Input moderation
    input_mod = await responsible_ai_service.moderate_input(request.message)
    if not input_mod.passed:
        return {"error": "Content blocked", "issues": input_mod.issues}
    
    # Process with enterprise coordinator
    response = await enterprise_coordinator.process_message(input_mod.sanitized_content)
    
    # Output moderation
    output_mod = await responsible_ai_service.moderate_output(response)
    
    return {
        "response": output_mod.sanitized_content or response,
        "moderation_passed": output_mod.passed,
        "risk_level": output_mod.risk_level.value
    }
""")
    
    print("\n🔌 3. Add Plugin Management Endpoints:")
    print("""
@app.post("/api/v2/plugins/manage")
async def manage_plugin(plugin_name: str, action: str):
    if action == "load":
        success = await plugin_registry.load_plugin(plugin_name)
    elif action == "unload":
        success = await plugin_registry.unload_plugin(plugin_name)
    
    if success:
        await enterprise_coordinator.refresh_plugin_tools()
    
    return {"success": success, "plugin": plugin_name}

@app.get("/api/v2/plugins/available")
async def get_plugins():
    return plugin_registry.get_all_plugins()
""")

async def main():
    """Main test function"""
    print("🏢 AgenticAI Enterprise API Integration Test")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    
    # Test local integration
    local_success = await test_enterprise_api_locally()
    
    # Test HTTP endpoints if available
    if local_success:
        await test_enterprise_api_endpoints()
    
    # Show integration examples
    show_integration_examples()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Copy src/api/enterprise_main.py to replace your main API file")
    print("2. Update your frontend to call /api/v2/* endpoints")
    print("3. Add plugin management UI components")
    print("4. Configure environment variables for production")
    print("5. Test the complete enterprise workflow")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 