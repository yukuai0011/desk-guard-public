# 🛡️ Computer Security Monitoring GUI

An advanced real-time security monitoring system using GLM-4V vision AI with Gradio web interface. Features live camera integration, concurrent API processing, and intelligent threat assessment.

## 🎯 Key Features

### 🔧 **Core Functionality**
- **Real-time Camera Monitoring**: Live camera feed with automatic threat detection
- **GLM-4V AI Analysis**: Advanced vision AI for security threat assessment  
- **Concurrent Processing**: Multi-threaded API requests (up to 10 concurrent)
- **Owner Recognition**: Compare current users against authorized owner
- **Threat Level Scoring**: 0-100% threat assessment with visual indicators

### 📊 **Smart Analytics**
- **Threat Categories**: 🟢 Normal (0-29%) | 🟡 Caution (30-69%) | 🔴 Alert (70-100%)
- **Response History**: Latest 10 analysis results sorted by request timestamp
- **Live Updates**: Auto-refreshing displays every 2 seconds
- **Detailed Analysis**: Full AI reasoning for each security assessment

### ⚙️ **Configurable Settings**
- **Capture Interval**: 1-30 seconds between security checks
- **Concurrent Limits**: 1-10 parallel API requests (respects GLM-4V limits)
- **Visual Feedback**: Real-time status indicators and progress updates

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install gradio opencv-python Pillow numpy zhipuai
```

### 2. **Launch the GUI**
```bash
python gui_app.py
```

### 3. **Setup Process**
1. **Initialize API**: Enter your GLM-4V API key from [open.bigmodel.cn](https://open.bigmodel.cn)
2. **Capture Owner**: Take a reference photo of the authorized computer owner
3. **Start Monitoring**: Configure settings and begin real-time security monitoring

### 4. **Access Interface**
- Open your browser and go to: `http://127.0.0.1:7860`
- The interface will automatically open after launch

## 🖥️ Interface Overview

### **Left Panel - Configuration**
```
🔧 Configuration
├── GLM-4V API Key Input
├── Initialize API Client Button
└── API Status Display

👤 Owner Reference  
├── Capture Owner Image Button
├── Owner Image Preview
└── Capture Status

⚙️ Monitoring Settings
├── Capture Interval Slider (1-30s)
├── Max Concurrent Requests (1-10)
├── Start/Stop Monitoring Buttons
└── Monitoring Status
```

### **Right Panel - Live Monitoring**
```
📹 Live Camera Feed
├── Real-time Camera Stream
└── Auto-refresh every 0.5s

📊 Security Analysis Results
├── Latest 10 Results Display
├── Threat Level & Status
├── Timestamp Sorting
└── Auto-refresh every 2s
```

## 🛡️ Security Analysis System

### **How It Works**
1. **Owner Identification**: System captures reference image of authorized user
2. **Continuous Monitoring**: Camera continuously captures current user images
3. **AI Comparison**: GLM-4V compares current user with owner reference
4. **Threat Assessment**: Evaluates proximity, behavior, and authorization level
5. **Real-time Alerts**: Immediate notifications of security threats

### **Threat Detection Logic**
```
🔍 Analysis Criteria:
• Facial feature comparison
• Clothing/appearance matching  
• Distance from computer
• Hand positioning near keyboard/mouse
• Face proximity to screen

📊 Scoring System:
• 0-29%: ✅ Owner present OR safe distance
• 30-69%: ⚠️ Unauthorized but not threatening
• 70-100%: 🚨 Unauthorized approaching dangerously
```

## 🔧 Configuration Options

### **Capture Interval**
- **Range**: 1-30 seconds
- **Recommended**: 3-5 seconds for balance of accuracy and API usage
- **High Security**: 1-2 seconds for maximum vigilance
- **Low Activity**: 10+ seconds for minimal API usage

### **Max Concurrent Requests**
- **Range**: 1-10 requests
- **GLM-4V Limit**: Maximum 10 concurrent requests per account
- **Recommended**: 3-5 for stability
- **High Volume**: 8-10 for maximum throughput (ensure API limits)

### **Response Time Optimization**
- **Average API Response**: ~5 seconds
- **Concurrent Processing**: Multiple requests in parallel
- **Smart Queuing**: Automatic request management
- **Error Handling**: Graceful failure recovery

## 📈 Performance Metrics

### **System Requirements**
- **Camera**: USB/Built-in webcam required
- **Memory**: ~200MB RAM for GUI + camera processing
- **Network**: Stable internet for GLM-4V API calls
- **CPU**: Multi-core recommended for concurrent processing

### **API Usage Estimation**
```
Example: 3-second interval, 8 hours monitoring
• Captures per hour: 1200
• Daily API calls: ~9,600
• Concurrent requests: 3-5 average
• Expected response time: 5-8 seconds
```

## 🔒 Security & Privacy

### **Data Handling**
- **Local Processing**: Images processed locally before API upload
- **Temporary Storage**: No permanent image storage
- **API Transmission**: Encrypted HTTPS to GLM-4V
- **Memory Management**: Automatic cleanup after analysis

### **Privacy Protection**
- **Owner Reference**: Stored locally in memory only
- **No Recording**: System analyzes but doesn't record video
- **Secure API**: Uses official zhipuai SDK with proper authentication
- **Session-based**: Data cleared when application closes

## 🚨 Alert System

### **Visual Indicators**
- **🟢 Normal**: Green background, normal operation
- **🟡 Caution**: Yellow background, monitoring required
- **🔴 Alert**: Red background, immediate attention needed

### **Response Format**
```
THREAT LEVEL: 85%
🚨 SECURITY ALERT: Unauthorized person detected approaching computer. 
Different facial features from owner detected. Subject's hand is 
reaching toward the keyboard area, indicating potential unauthorized access.
```

## 🛠️ Troubleshooting

### **Common Issues**

**Camera Not Detected**
```bash
# Check camera permissions
# Ensure no other apps are using camera
# Try different camera index in code (0, 1, 2...)
```

**API Connection Errors**
```bash
# Verify API key is correct
# Check internet connection
# Ensure GLM-4V service is available
# Check API rate limits
```

**Performance Issues**
```bash
# Reduce capture interval
# Lower max concurrent requests
# Check system resources
# Close unnecessary applications
```

**GUI Not Loading**
```bash
# Check port 7860 is available
# Try different port in main() function
# Verify all dependencies installed
# Check firewall settings
```

## 📝 Advanced Usage

### **Custom Configuration**
```python
# Modify these values in gui_app.py
server_port = 7860        # Change web interface port
camera_index = 0          # Change camera source
quality = 85              # Adjust image quality (50-100)
temperature = 0.3         # API temperature setting
```

### **Integration Options**
- **Webhook Support**: Add custom alert endpoints
- **Database Logging**: Store threat events
- **Multi-Camera**: Extend for multiple camera feeds
- **Custom Models**: Integrate other vision AI APIs

## 📊 Monitoring Dashboard

### **Real-time Metrics**
- Active monitoring status
- Request queue length  
- Response time averages
- Threat level history
- API usage statistics

### **Historical Data**
- Last 10 analysis results
- Threat level trends
- Response time tracking
- Error rate monitoring

## 🔄 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Camera Feed   │───▶│   Image Capture  │───▶│   Base64 Encode │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Owner Storage  │───▶│  Threat Analysis │◀───│  Current Image  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Response Queue │◀───│   GLM-4V API    │───▶│ Concurrent Pool │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ History Display │◀───│   Result Parser  │───▶│  Gradio GUI     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📚 API Reference

### **SecurityMonitor Class Methods**
- `initialize_client(api_key)`: Setup GLM-4V client
- `capture_owner_image()`: Take owner reference photo
- `start_monitoring(interval, max_concurrent)`: Begin security monitoring
- `stop_monitoring()`: End security monitoring
- `get_response_history_display()`: Format results for display

### **Gradio Interface Functions**
- `initialize_api(api_key)`: API initialization wrapper
- `capture_owner()`: Owner capture wrapper  
- `get_camera_feed()`: Live camera stream
- `update_response_display()`: Refresh results display

## 🎓 Best Practices

### **Setup Recommendations**
1. **Good Lighting**: Ensure adequate lighting for facial recognition
2. **Stable Camera**: Mount camera securely to avoid movement
3. **Clear View**: Position camera for unobstructed face/body view
4. **Reference Photo**: Take clear, well-lit owner reference image

### **Monitoring Guidelines**
1. **Regular Updates**: Retake owner reference if appearance changes significantly
2. **Interval Tuning**: Balance security needs with API costs
3. **Alert Response**: Establish clear procedures for security alerts
4. **Backup Plans**: Have alternative security measures available

## 📄 License

This project uses the MIT license, same as the zhipuai SDK.

---

**🛡️ Stay secure with intelligent AI-powered monitoring!** 🛡️ 