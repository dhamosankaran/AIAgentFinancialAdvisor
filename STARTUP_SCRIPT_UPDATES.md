# 🚀 Startup Script Updates for Enterprise AgenticAI

## ✅ **What Was Updated**

Your startup scripts have been enhanced to fully support the enterprise features and provide a better user experience.

---

## 📋 **Updated Files**

### **1. `start.sh` - Main Startup Script (Enterprise-Ready)**
- **✅ Updated** with enterprise banner and branding
- **✅ Added** enterprise directory creation (`cache/plugins`, `backups`)
- **✅ Enhanced** prerequisite checking
- **✅ Improved** virtual environment handling
- **✅ Added** dependency installation with error handling
- **✅ Enhanced** server startup with enterprise features
- **✅ Added** enterprise URLs and health checks
- **✅ Improved** error handling and cleanup

### **2. `start_enterprise.sh` - Dedicated Enterprise Script**
- **✅ Created** as a streamlined enterprise startup script
- **✅ Focused** on enterprise features and quick startup
- **✅ Simplified** for production use

---

## 🎯 **Key Improvements**

### **🏢 Enterprise Branding**
```bash
🏢============================================================
🏢  Enterprise AgenticAI - Complete System Startup
🏢  Bank-grade Financial AI with Enterprise Features
🏢============================================================
```

### **📁 Directory Management**
- **Auto-creates** all necessary directories:
  - `logs/` - Server logs
  - `data/` - Application data
  - `cache/plugins/` - Plugin cache
  - `backups/` - System backups

### **🔍 Enhanced Prerequisite Checking**
- **Python 3** validation
- **Node.js** validation
- **npm** validation
- **Virtual environment** auto-creation/activation
- **Dependency** auto-installation

### **🚀 Enterprise Server Startup**
- **Enterprise API Server** (port 8000)
- **Frontend Server** (port 5173)
- **Enhanced logging** with timestamps
- **Better error handling**
- **Auto browser opening**

### **🌐 Enterprise URLs Display**
```bash
🌐 URLs:
   • Frontend:     http://localhost:5173
   • API Docs:     http://localhost:8000/docs
   • Health Check: http://localhost:8000/api/v2/health/enterprise
```

### **🏢 Enterprise Features Reminder**
```bash
🏢 Enterprise Features:
   • Toggle 'Enterprise Mode' ON
   • Toggle 'Admin Access' ON for Plugin Manager
   • Responsible AI with content moderation
   • Hot-swappable plugin architecture
```

---

## 🎮 **How to Use**

### **Option 1: Main Script (Recommended)**
```bash
./start.sh
```

### **Option 2: Enterprise-Only Script**
```bash
./start_enterprise.sh
```

### **Option 3: Manual Steps**
```bash
# Activate virtual environment
source venv/bin/activate

# Start backend
python3 src/api/main.py

# Start frontend (new terminal)
cd frontend && npm run dev
```

---

## 🔧 **What the Script Does**

### **1. Environment Setup**
- ✅ Checks for Python 3, Node.js, npm
- ✅ Creates/activates virtual environment
- ✅ Installs backend and frontend dependencies
- ✅ Creates necessary directories

### **2. Process Management**
- ✅ Kills any existing processes on ports 8000 and 5173
- ✅ Starts enterprise API server with enhanced features
- ✅ Starts frontend development server
- ✅ Monitors server health

### **3. User Experience**
- ✅ Shows enterprise branding and status
- ✅ Displays all relevant URLs
- ✅ Opens browser automatically (macOS)
- ✅ Provides clear instructions for enterprise features
- ✅ Handles graceful shutdown with Ctrl+C

### **4. Logging**
- ✅ Creates timestamped log files
- ✅ Separates backend and frontend logs
- ✅ Provides log file locations

---

## 🎯 **Enterprise Features Available After Startup**

Once the script starts your system, you'll have access to:

### **🛡️ Responsible AI Layer**
- Content moderation with PII protection
- Risk assessment and blocking
- Compliance checking
- Automatic disclaimer addition

### **🔌 Plugin Architecture**
- Hot-swappable plugins
- Dynamic tool discovery
- Real-time plugin management
- Runtime configuration

### **📊 Enterprise Monitoring**
- System health checks
- Usage analytics
- Plugin statistics
- Performance metrics

### **🏢 Admin Interface**
- Plugin Manager tab (with Admin Access)
- Real-time system status
- Configuration management
- Error reporting

---

## 🚨 **Troubleshooting**

### **If Startup Fails:**

1. **Check Prerequisites:**
   ```bash
   python3 --version
   node --version
   npm --version
   ```

2. **Check Virtual Environment:**
   ```bash
   source venv/bin/activate
   pip list
   ```

3. **Check Ports:**
   ```bash
   lsof -i :8000
   lsof -i :5173
   ```

4. **Check Logs:**
   ```bash
   ls -la logs/
   tail -f logs/enterprise_backend_*.log
   tail -f logs/enterprise_frontend_*.log
   ```

5. **Manual Cleanup:**
   ```bash
   killall python3
   killall node
   ./start.sh
   ```

---

## 📚 **Related Files**

- **`deploy_enterprise.sh`** - Complete deployment script
- **`setup_enterprise.py`** - Interactive setup script
- **`config/enterprise.env.template`** - Environment configuration template
- **`ENTERPRISE_DEPLOYMENT_COMPLETE.md`** - Complete deployment guide
- **`ENTERPRISE_END_TO_END_GUIDE.md`** - End-to-end system guide

---

## 🎉 **Success Indicators**

When the startup is successful, you'll see:

```bash
🎉 Enterprise AgenticAI Successfully Started!

🌐 URLs:
   • Frontend:     http://localhost:5173
   • API Docs:     http://localhost:8000/docs
   • Health Check: http://localhost:8000/api/v2/health/enterprise

🏢 Enterprise Features:
   • Toggle 'Enterprise Mode' ON
   • Toggle 'Admin Access' ON for Plugin Manager
   • Responsible AI with content moderation
   • Hot-swappable plugin architecture

⚡ Press Ctrl+C to stop
```

Your **enterprise-ready AgenticAI system** is now running with all advanced features! 🚀

---

*For more detailed information about enterprise features, see `ENTERPRISE_END_TO_END_GUIDE.md`* 