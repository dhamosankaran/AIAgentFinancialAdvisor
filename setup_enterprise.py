#!/usr/bin/env python3
"""
Enterprise AgenticAI Setup Script
Configures environment variables and enterprise features
"""

import os
import shutil
from pathlib import Path
import subprocess
import sys

def print_banner():
    """Print setup banner"""
    print("🏢" + "="*60)
    print("🏢  Enterprise AgenticAI Setup")
    print("🏢  Configuring enterprise features and environment")
    print("🏢" + "="*60)

def check_environment():
    """Check if we're in a virtual environment"""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: You're not in a virtual environment")
        print("   Consider running: python3 -m venv venv && source venv/bin/activate")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ Virtual environment detected")

def copy_env_template():
    """Copy environment template to .env if it doesn't exist"""
    template_path = Path("config/enterprise.env.template")
    env_path = Path(".env")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        print("   Make sure you're running from the project root directory")
        sys.exit(1)
    
    if env_path.exists():
        print(f"⚠️  .env file already exists")
        response = input("   Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing .env file")
            return False
    
    shutil.copy(template_path, env_path)
    print(f"✅ Created .env from template")
    return True

def configure_api_keys():
    """Interactive API key configuration"""
    print("\n🔑 API Key Configuration")
    print("   Enter your API keys (or press Enter to skip)")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return
    
    # Read existing .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # OpenAI API Key
    openai_key = input("   OpenAI API Key: ").strip()
    if openai_key:
        content = content.replace("your_openai_api_key_here", openai_key)
        print("   ✅ OpenAI API key configured")
    
    # Alpha Vantage API Key
    alpha_key = input("   Alpha Vantage API Key: ").strip()
    if alpha_key:
        content = content.replace("your_alpha_vantage_api_key_here", alpha_key)
        print("   ✅ Alpha Vantage API key configured")
    
    # Write updated .env
    with open(env_path, 'w') as f:
        f.write(content)

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs", 
        "cache/plugins",
        "backups"
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")

def install_dependencies():
    """Install additional enterprise dependencies"""
    print("\n📦 Installing enterprise dependencies...")
    
    enterprise_deps = [
        "httpx",  # For async HTTP requests
        "redis",  # For caching (optional)
        "psycopg2-binary",  # For PostgreSQL (optional)
    ]
    
    for dep in enterprise_deps:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  Failed to install {dep} (optional)")

def configure_enterprise_features():
    """Configure enterprise feature settings"""
    print("\n🏢 Enterprise Feature Configuration")
    
    features = {
        "Responsible AI Layer": "ENABLE_RESPONSIBLE_AI",
        "Plugin Architecture": "ENABLE_PLUGIN_ARCHITECTURE", 
        "Compliance Checking": "ENABLE_COMPLIANCE_CHECKING",
        "Hallucination Detection": "ENABLE_HALLUCINATION_DETECTION",
        "Usage Analytics": "ENABLE_USAGE_ANALYTICS"
    }
    
    env_path = Path(".env")
    if not env_path.exists():
        return
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    for feature, env_var in features.items():
        current_value = "true" if f"{env_var}=true" in content else "false"
        print(f"   {feature}: Currently {current_value}")
    
    response = input("\n   Keep current enterprise feature settings? (Y/n): ")
    if response.lower() == 'n':
        print("   Note: Edit .env file manually to customize enterprise features")

def test_enterprise_setup():
    """Test that enterprise features can be imported"""
    print("\n🧪 Testing enterprise setup...")
    
    try:
        # Test imports
        sys.path.append('src')
        from src.services.responsible_ai_service import ResponsibleAIService
        from src.services.plugin_registry import plugin_registry
        from src.agents.plugin_enabled_agent import DynamicFinancialAgent
        
        print("   ✅ Enterprise services can be imported")
        
        # Test basic initialization
        responsible_ai = ResponsibleAIService()
        print("   ✅ Responsible AI service initializes")
        
        print("   ✅ Enterprise setup test passed!")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Check that all enterprise files are present")
    except Exception as e:
        print(f"   ⚠️  Setup warning: {e}")

def show_next_steps():
    """Show next steps after setup"""
    print("\n🚀 Next Steps:")
    print("   1. Review .env file and customize settings")
    print("   2. Add your API keys if not done already")
    print("   3. Start the enterprise API server:")
    print("      python3 src/api/main.py")
    print("   4. Start the frontend:")
    print("      cd frontend && npm install && npm run dev")
    print("   5. Access Plugin Manager with Admin Access enabled")
    print("   6. Test enterprise chat with Enterprise Mode enabled")
    
    print("\n📚 Documentation:")
    print("   • Enterprise Integration Guide: ENTERPRISE_INTEGRATION_GUIDE.md")
    print("   • Test enterprise features: python3 test_api_integration.py")
    
    print("\n🔧 Configuration files:")
    print("   • Environment: .env")
    print("   • Enterprise API: src/api/main.py")
    print("   • Frontend: frontend/src/App.tsx")

def main():
    """Main setup function"""
    print_banner()
    
    # Check environment
    check_environment()
    
    # Setup steps
    copy_env_template()
    configure_api_keys()
    create_directories()
    install_dependencies()
    configure_enterprise_features()
    test_enterprise_setup()
    
    print("\n✅ Enterprise AgenticAI setup completed!")
    show_next_steps()

if __name__ == "__main__":
    main() 