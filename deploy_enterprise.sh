#!/bin/bash
# Enterprise AgenticAI Deployment Script
# Complete workflow for deploying enterprise features

echo "🏢 ========================================"
echo "🏢 Enterprise AgenticAI Deployment"
echo "🏢 ========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment active: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    echo "   Recommendation: source venv/bin/activate"
fi

# Check enterprise files exist
echo -e "\n${BLUE}🔍 Checking enterprise files...${NC}"
enterprise_files=(
    "src/api/main.py"
    "src/services/responsible_ai_service.py"
    "src/services/plugin_registry.py"
    "src/agents/plugin_enabled_agent.py"
    "src/plugins/compliance_plugin.py"
    "frontend/src/components/EnterpriseChatWindow.tsx"
    "frontend/src/components/PluginManager.tsx"
)

all_files_exist=true
for file in "${enterprise_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}   ✅ $file${NC}"
    else
        echo -e "${RED}   ❌ $file${NC}"
        all_files_exist=false
    fi
done

if [[ "$all_files_exist" = false ]]; then
    echo -e "${RED}❌ Missing enterprise files. Cannot deploy.${NC}"
    exit 1
fi

# Test enterprise components
echo -e "\n${BLUE}🧪 Testing enterprise components...${NC}"
python3 -c "
import sys
sys.path.append('src')
try:
    from src.services.responsible_ai_service import ResponsibleAIService
    from src.services.plugin_registry import plugin_registry
    from src.agents.plugin_enabled_agent import DynamicFinancialAgent
    print('✅ All enterprise components imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || exit 1

# Environment configuration
echo -e "\n${BLUE}🔧 Environment configuration...${NC}"
if [[ -f ".env" ]]; then
    echo -e "${GREEN}   ✅ .env file exists${NC}"
    # Check for critical environment variables
    if grep -q "OPENAI_API_KEY=" .env; then
        echo -e "${GREEN}   ✅ OpenAI API key configured${NC}"
    else
        echo -e "${YELLOW}   ⚠️  OpenAI API key not found in .env${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  .env file not found${NC}"
    echo -e "${BLUE}   📋 To create .env file:${NC}"
    echo "      cp config/enterprise.env.template .env"
    echo "      # Then edit .env with your API keys"
fi

# Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
directories=("data" "logs" "cache/plugins" "backups")
for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo -e "${GREEN}   ✅ $dir/${NC}"
done

# Frontend setup
echo -e "\n${BLUE}🌐 Frontend setup...${NC}"
if [[ -d "frontend/node_modules" ]]; then
    echo -e "${GREEN}   ✅ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}   ⚠️  Frontend dependencies not installed${NC}"
    echo -e "${BLUE}   📋 To install frontend dependencies:${NC}"
    echo "      cd frontend && npm install"
fi

# Start instructions
echo -e "\n${BLUE}🚀 Deployment Instructions:${NC}"
echo ""
echo -e "${YELLOW}1. Start the Enterprise API Server:${NC}"
echo "   python3 src/api/main.py"
echo ""
echo -e "${YELLOW}2. Start the Frontend (in a new terminal):${NC}"
echo "   cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}3. Access the Application:${NC}"
echo "   http://localhost:5173 (or port shown by Vite)"
echo ""
echo -e "${YELLOW}4. Enable Enterprise Features:${NC}"
echo "   • Toggle 'Enterprise Mode' in the navigation"
echo "   • Toggle 'Admin Access' to access Plugin Manager"
echo "   • Test enterprise chat features"
echo ""
echo -e "${YELLOW}5. Test Enterprise Endpoints:${NC}"
echo "   • API Health: http://localhost:8000/api/v2/health/enterprise"
echo "   • System Status: http://localhost:8000/api/v2/enterprise/status"
echo "   • Plugin Management: Frontend -> Plugin Manager tab"

# Test commands
echo -e "\n${BLUE}🧪 Test Commands:${NC}"
echo ""
echo -e "${YELLOW}Test enterprise integration:${NC}"
echo "   python3 test_api_integration.py"
echo ""
echo -e "${YELLOW}Test enterprise features:${NC}"
echo "   python3 test_enterprise_features.py"
echo ""
echo -e "${YELLOW}Interactive setup:${NC}"
echo "   python3 setup_enterprise.py"

# Architecture summary
echo -e "\n${BLUE}🏗️  Enterprise Architecture:${NC}"
echo ""
echo "   ┌─────────────────────────────────────────────┐"
echo "   │              Frontend (React)               │"
echo "   │  • EnterpriseChatWindow                     │"
echo "   │  • PluginManager                            │"
echo "   │  • Enhanced Components                      │"
echo "   └─────────────────┬───────────────────────────┘"
echo "                     │"
echo "   ┌─────────────────▼───────────────────────────┐"
echo "   │           Enterprise API (FastAPI)          │"
echo "   │  • /api/v2/chat (enhanced)                  │"
echo "   │  • /api/v2/plugins/* (management)           │"
echo "   │  • /api/v2/moderation/* (safety)            │"
echo "   │  • /api/v2/enterprise/* (monitoring)        │"
echo "   └─────────────────┬───────────────────────────┘"
echo "                     │"
echo "   ┌─────────────────▼───────────────────────────┐"
echo "   │            Enterprise Layer                  │"
echo "   │  • Responsible AI Service                   │"
echo "   │  • Plugin Registry                          │"
echo "   │  • Dynamic Financial Agent                  │"
echo "   └─────────────────────────────────────────────┘"

# Features summary
echo -e "\n${BLUE}✨ Enterprise Features:${NC}"
echo -e "${GREEN}   ✅ Responsible AI Layer${NC} - Content moderation, PII protection"
echo -e "${GREEN}   ✅ Plugin Architecture${NC} - Hot-swappable functionality"
echo -e "${GREEN}   ✅ Dynamic Tool Discovery${NC} - Automatic tool integration"
echo -e "${GREEN}   ✅ Compliance Checking${NC} - Financial regulatory compliance"
echo -e "${GREEN}   ✅ Enterprise Monitoring${NC} - Health checks and analytics"
echo -e "${GREEN}   ✅ Backward Compatibility${NC} - Legacy endpoints still work"

echo -e "\n${GREEN}🎉 Enterprise AgenticAI deployment ready!${NC}"
echo -e "${BLUE}📚 Documentation: ENTERPRISE_INTEGRATION_GUIDE.md${NC}" 