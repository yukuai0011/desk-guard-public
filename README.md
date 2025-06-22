# 🛡️ Computer Security Monitoring System

This system uses GLM-4V vision AI to monitor computer access and detect unauthorized users approaching the computer.

## 🔍 How It Works

The system compares two images:
1. **Owner Reference Image**: The authorized computer owner (first image)
2. **Current User Image**: The person currently near the computer (second image)

The AI analyzes both facial features and clothing to determine if the current user is the authorized owner or an unauthorized person.

## 🚨 Security Alert Conditions

The system triggers alerts when:
- The current user is **NOT** the authorized owner (different face OR clothing)
- **AND** they are approaching too closely by:
  - Having their hand reaching toward the computer/keyboard/mouse
  - Putting their face very close to the screen (closer than normal viewing distance)

## 📊 Threat Level Scoring (0-100%)

The system provides a numerical threat assessment:

- **🟢 0-29% (Normal)**: Owner present OR unauthorized person at safe distance
- **🟡 30-69% (Caution)**: Unauthorized person present but not immediately threatening  
- **🔴 70-100% (Alert)**: Unauthorized person approaching computer/reaching for it/face too close

## ✅ Response Categories

**✅ ALL NORMAL (0-29%)**: Current user matches authorized owner OR no immediate threat
**⚠️ CAUTION (30-69%)**: Unauthorized person detected but maintaining safe distance
**🚨 SECURITY ALERT (70-100%)**: Unauthorized person approaching computer dangerously close

## 📋 Prerequisites

- Python 3.11+
- GLM-4V API key from [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- Two test images (owner reference and current user monitoring)

## 🔧 Installation

1. Install dependencies:
```bash
pip install zhipuai
```

Or if you're using this project structure:
```bash
pip install -e .
```

## 🚀 Usage

1. Run the security monitoring system:
```bash
python app.py
```

2. Enter your GLM-4V API key when prompted

3. Choose monitoring mode:
   - **Option 1**: 🔍 Security monitoring (compare owner vs current user)
   - **Option 2**: 📷 Single image analysis  
   - **Option 3**: ❌ Exit

## 📸 Test Images

The system is configured to use these test images:
- **Owner (Reference)**: `C:\Users\yukua\Downloads\WIN_20250622_14_28_40_Pro.jpg`
- **Current User (Monitoring)**: `C:\Users\yukua\Downloads\WIN_20250622_15_21_38_Pro.jpg`

Make sure these files exist, or update the `image_paths` list in the code to point to your images.

## 📚 API Documentation

This system uses the official zhipuai SDK:
- [GLM-4V API Documentation](https://open.bigmodel.cn/dev/api/normal-model/glm-4v)
- [Official Python SDK](https://github.com/MetaGLM/zhipuai-sdk-python-v4)

## 📱 Example Output

### High Threat Example (70-100%):
```
🛡️  Computer Security Monitoring System
=====================================
Choose monitoring mode:
1. 🔍 Security monitoring (compare owner vs current user)
Enter your choice (1-3): 1

--- 🛡️  Security Monitoring Mode ---
✓ GLM-4V client initialized successfully
✓ Found image: WIN_20250622_14_28_40_Pro.jpg
✓ Found image: WIN_20250622_15_21_38_Pro.jpg

Processing 2 image(s) for security analysis...
✓ Successfully encoded Owner (reference): WIN_20250622_14_28_40_Pro.jpg
✓ Successfully encoded Current user (monitoring): WIN_20250622_15_21_38_Pro.jpg

🔍 Analyzing 2 image(s) for security threats...
✓ Security analysis completed

============================================================
🛡️  SECURITY MONITORING RESULT:
============================================================
THREAT LEVEL: 85%

🚨 SECURITY ALERT: Unauthorized person detected approaching computer. 
The person in the second image appears to be different from the owner 
in the first image based on facial features and clothing. They are 
reaching toward the keyboard, indicating potential unauthorized access.
============================================================
```

### Moderate Threat Example (30-69%):
```
============================================================
🛡️  SECURITY MONITORING RESULT:
============================================================
THREAT LEVEL: 45%

⚠️ CAUTION: Different person detected near the computer compared to 
the authorized owner. However, they are maintaining a safe distance 
and not directly interacting with the computer components.
============================================================
```

### Normal Operation Example (0-29%):
```
============================================================
🛡️  SECURITY MONITORING RESULT:
============================================================
THREAT LEVEL: 5%

✅ ALL NORMAL: The person in both images appears to be the same 
individual (authorized owner) based on matching facial features 
and similar clothing. No security threat detected.
============================================================
```

## ⚠️ Error Handling

The system includes comprehensive error handling for:
- Missing API key
- Image files not found
- Image encoding failures
- API connection errors
- Security analysis failures

## 🔒 Security Features

- **Dual Authentication**: Compares both facial features AND clothing
- **Proximity Detection**: Identifies when someone is too close to the computer
- **Gesture Analysis**: Detects hands reaching toward computer components
- **Real-time Monitoring**: Provides immediate security alerts
- **Privacy Focused**: Processes images locally and only sends to secure GLM-4V API

## 📄 License

This project uses the MIT license, same as the zhipuai SDK.