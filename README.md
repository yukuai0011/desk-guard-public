# 🛡️ Computer Security Monitoring System

Real-time computer security monitoring system using GLM-4V vision AI with Gradio web interface. Features live camera monitoring, distance-based threat assessment, and Discord notifications.

## ✨ Key Features

- 🖥️ **Live Camera Monitoring**: Real-time webcam surveillance with streaming
- 📏 **Distance-Based Assessment**: Uses reference image to determine normal vs suspicious proximity  
- 🏷️ **Smart Image Labeling**: Automatically labels images for better AI understanding
- 🔔 **Discord Integration**: High-threat alerts sent directly to Discord with images
- ⚡ **Speed Optimized**: Fast threat assessment with minimal response time
- 🌐 **Web GUI**: User-friendly Gradio interface accessible via browser
- 🔍 **Camera Blackout Detection**: Alerts when camera is obstructed or malfunctioning

## 🔍 How It Works

### Distance-Based Security Model
The system establishes a security baseline using a reference image:

1. **Reference Image**: Shows normal, safe computer use distance and positioning
2. **Current Monitoring**: Live camera feed analyzed for security threats
3. **Distance Comparison**: AI compares current distance to reference baseline
4. **Threat Assessment**: Proximity and behavior determine threat level

### Smart Image Processing
- **Automatic Labeling**: Images are labeled as "REFERENCE" and "CURRENT MONITORING"
- **Color Correction**: Proper RGB handling for accurate Discord image sharing
- **Real-time Processing**: Concurrent API requests for fast response

## 🚨 Enhanced Security Conditions

### 🔴 HIGH THREAT (70-100%)
- Camera blackout/obstruction/malfunction
- Person **closer** than reference distance
- Arms/hands **closer** than reference baseline  
- Anyone reaching toward computer/keyboard/mouse
- Face closer to screen than reference shows
- Large difference between reference and current positioning

### 🟡 MODERATE THREAT (30-69%)
- Person at **similar distance** as reference (normal working range)
- Unclear view but within reference distance range
- Person approaching but not yet closer than reference distance

### 🟢 LOW THREAT (0-29%)
- No person visible (camera working normally)
- Person at **further distance** than reference with no threatening behavior
- Person well beyond reference working distance

## 🔔 Discord Integration

### Setup Instructions
1. Go to your Discord server
2. Right-click the channel for alerts → "Edit Channel" → "Integrations"
3. Click "Create Webhook" and copy the webhook URL
4. Paste URL into the application's Discord settings
5. High threats (70%+) automatically send alerts with images

### Alert Format
```
🚨 HIGH SECURITY ALERT - Threat Level: 85%

[Embedded Message]
🚨 COMPUTER SECURITY ALERT
Threat Level: 85%
Status: 🚨 HIGH ALERT  
Time: 2024-01-15 14:30:25

[Attached Image: security_alert.png]
```

## 📋 Prerequisites

- **Python 3.11+**
- **GLM-4V API key** from [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- **Webcam** for live monitoring
- **Discord webhook URL** (optional, for notifications)

## 🔧 Installation

1. **Install uv:**
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone and run the project:**
```bash
# Install dependencies and run the application
uv run app.py
```

3. **Alternative: Install dependencies first:**
```bash
uv sync
uv run app.py
```

## 🚀 Usage

```bash
uv run app.py
```

Then open your browser to: `http://127.0.0.1:7860`

## 🖥️ GUI Interface Guide

### 1. Configuration Panel
- **GLM-4V API Key**: Enter your API key and click "Initialize API Client"
- **Monitoring Settings**: 
  - Capture Interval: Time between security checks (1-30 seconds)
  - Max Concurrent Requests: Parallel API requests (1-10)
- **Discord Notifications**:
  - Enter webhook URL and click "Setup Discord Notifications"

### 2. Camera & Reference Setup
- **Live Camera Feed**: View real-time webcam stream
- **Owner Reference**: Click "📸 Set Latest Image as Owner Reference" to capture baseline

### 3. Security Monitoring
- **Start/Stop Monitoring**: Control real-time threat detection
- **Latest Results**: View recent security assessments with threat levels

## ⚡ Performance Optimizations

### Speed Enhancements
- **Reduced Token Limit**: 100 tokens max for faster responses
- **Lower Temperature**: 0.1 for deterministic, quick assessment  
- **Simplified Output**: Just threat level and status (no detailed analysis)
- **Concurrent Processing**: Multiple API requests in parallel
- **Efficient Streaming**: 1-second intervals with smart caching

### Example Fast Response
```
THREAT LEVEL: 85%
STATUS: 🚨 HIGH ALERT
```

## 🎯 Monitoring Configuration

### Recommended Settings
- **Capture Interval**: 3 seconds (balance between speed and coverage)
- **Max Concurrent**: 3 requests (within GLM-4V limits)
- **Stream Update**: 1 second (responsive but not overwhelming)

### GLM-4V API Limits
- Maximum 10 concurrent requests
- Recommended: 3-5 concurrent for stability

## 📸 Camera Requirements

- **Resolution**: Any webcam resolution supported by OpenCV
- **Lighting**: Adequate lighting for clear facial/proximity detection
- **Positioning**: Camera should capture computer area and approach paths
- **Stability**: Stable mounting to avoid false motion alerts

## 🔒 Security & Privacy

### Data Handling
- **Local Processing**: Images processed locally before API calls
- **Secure API**: Only sent to official GLM-4V endpoints
- **No Storage**: Images not permanently stored (only in memory)
- **Webhook Security**: Discord URLs are password-protected in GUI

### Network Requirements
- **Internet Connection**: Required for GLM-4V API and Discord alerts  
- **Firewall**: Ensure access to `open.bigmodel.cn` and Discord webhooks
- **HTTPS**: All communications use secure HTTPS protocols

## 🛠️ Technical Architecture

### Components
- **SecurityMonitor Class**: Core monitoring logic and threat assessment
- **Gradio Interface**: Web-based GUI with real-time streaming
- **Discord Integration**: Webhook-based alert system with image uploads
- **Image Processing**: OpenCV + PIL for camera handling and encoding
- **Concurrent Execution**: ThreadPoolExecutor for parallel API requests

### File Structure
```
desk-guard-public/
├── app.py              # Main application with web GUI
├── pyproject.toml      # Project dependencies
└── README.md           # This documentation
```

## 📊 Example Threat Scenarios

### Scenario 1: Normal Use ✅
- **Reference**: Person sitting at normal working distance
- **Current**: Same positioning, typing normally
- **Result**: `THREAT LEVEL: 5% - ✅ NORMAL`

### Scenario 2: Approaching Threat ⚠️
- **Reference**: Normal working distance
- **Current**: Person closer but not yet at computer
- **Result**: `THREAT LEVEL: 45% - ⚠️ CAUTION`

### Scenario 3: High Alert 🚨
- **Reference**: Normal working distance  
- **Current**: Person much closer, reaching toward keyboard
- **Result**: `THREAT LEVEL: 85% - 🚨 HIGH ALERT`
- **Action**: Discord alert sent automatically

### Scenario 4: Camera Issue 🚨
- **Reference**: Clear camera view
- **Current**: Black/obstructed camera
- **Result**: `THREAT LEVEL: 100% - 🚨 HIGH ALERT`
- **Reason**: Camera malfunction/obstruction detected

## ⚠️ Troubleshooting

### Common Issues

**🔸 "API client not initialized"**
- Solution: Enter valid GLM-4V API key and click "Initialize API Client"

**🔸 "Owner reference image not captured"**  
- Solution: Ensure camera is working, then click "📸 Set Latest Image as Owner Reference"

**🔸 Discord alerts not working**
- Check webhook URL format (must start with `https://discord.com/api/webhooks/` or `https://ptb.discord.com/api/webhooks/`)
- Verify webhook is active in Discord channel settings

**🔸 Camera feed not showing**
- Check webcam permissions and ensure no other applications are using camera
- Try restarting the application

**🔸 Colors inverted in Discord images**
- This has been fixed in the latest version - ensure you're using the updated code

### Performance Issues
- **Slow responses**: Reduce concurrent requests or increase capture interval
- **High CPU usage**: Increase capture interval from 1-3 seconds to 5-10 seconds
- **API rate limits**: Ensure concurrent requests ≤ 10 (GLM-4V limit)

## 📚 API References

- **GLM-4V Documentation**: [https://open.bigmodel.cn/dev/api/normal-model/glm-4v](https://open.bigmodel.cn/dev/api/normal-model/glm-4v)
- **Discord Webhooks**: [https://discord.com/developers/docs/resources/webhook](https://discord.com/developers/docs/resources/webhook)
- **Gradio Documentation**: [https://gradio.app/docs](https://gradio.app/docs)

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.

## 📄 License

Mozilla Public License Version 2.0 - See LICENSE file for details.