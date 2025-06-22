#!/usr/bin/env python3
"""
🛡️ Computer Security Monitoring GUI

Real-time security monitoring system using GLM-4V vision AI with Gradio interface.
Features camera integration, concurrent API processing, and live threat assessment.
"""

import base64
import time
import threading
import queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Tuple, Any
import json

import gradio as gr
import cv2
import numpy as np
from PIL import Image

try:
    from zhipuai import ZhipuAI
except ImportError:
    print(
        "Error: zhipuai package not found. Please install it using: pip install zhipuai"
    )
    exit(1)


class SecurityMonitor:
    """Main security monitoring class handling camera feeds and API requests."""

    def __init__(self):
        self.client: Optional[ZhipuAI] = None
        self.owner_image: Optional[np.ndarray] = None
        self.monitoring_active = False
        self.response_history: List[Dict[str, Any]] = []
        self.response_queue = queue.Queue()
        self.executor: Optional[ThreadPoolExecutor] = None
        self.active_requests = set()
        self.camera = None

    def initialize_client(self, api_key: str) -> str:
        """Initialize the GLM-4V client with API key."""
        try:
            if not api_key.strip():
                return "❌ Please enter a valid API key"

            self.client = ZhipuAI(api_key=api_key.strip())
            return "✅ GLM-4V client initialized successfully"
        except Exception as e:
            return f"❌ Error initializing client: {e}"

    def encode_image(self, image: np.ndarray) -> Optional[str]:
        """Encode image to base64 string."""
        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image

            # Convert to PIL Image and then to bytes
            pil_image = Image.fromarray(image_rgb)
            import io

            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=85)
            image_bytes = buffer.getvalue()

            return base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    def set_owner_from_stream(
        self, current_frame: Optional[np.ndarray]
    ) -> Tuple[Optional[np.ndarray], str]:
        """Set owner reference image from current streaming frame."""
        try:
            if current_frame is None:
                return (
                    None,
                    "❌ No camera feed available. Please ensure webcam is active.",
                )

            # Store the current frame as owner reference
            self.owner_image = current_frame.copy()
            return current_frame, "✅ Owner reference image set from live camera feed"

        except Exception as e:
            return None, f"❌ Error setting owner image: {str(e)}"

    def get_camera_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera."""
        try:
            if self.camera is None:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    return None

            ret, frame = self.camera.read()
            return frame if ret else None

        except Exception as e:
            print(f"Error getting camera frame: {e}")
            return None

    def analyze_security_threat(
        self, current_image: np.ndarray, request_id: str
    ) -> Dict[str, Any]:
        """Analyze security threat using GLM-4V API."""
        try:
            if self.client is None:
                return {
                    "request_id": request_id,
                    "timestamp": datetime.now(),
                    "threat_level": 0,
                    "status": "❌ Client not initialized",
                    "analysis": "API client not properly initialized",
                }

            if self.owner_image is None:
                return {
                    "request_id": request_id,
                    "timestamp": datetime.now(),
                    "threat_level": 0,
                    "status": "❌ No owner reference",
                    "analysis": "Owner reference image not captured",
                }

            # Encode both images
            owner_b64 = self.encode_image(self.owner_image)
            current_b64 = self.encode_image(current_image)

            if not owner_b64 or not current_b64:
                return {
                    "request_id": request_id,
                    "timestamp": datetime.now(),
                    "threat_level": 0,
                    "status": "❌ Image encoding failed",
                    "analysis": "Failed to encode images for analysis",
                }

            # Prepare API request
            message_content = [
                {
                    "type": "text",
                    "text": """You are a computer security monitoring system. I have uploaded 2 images:

1. FIRST IMAGE: This is the authorized owner of the computer (reference image) - this shows the NORMAL, SAFE distance and position
2. SECOND IMAGE: This is the current monitoring image from the camera

Your task:
1. FIRST - Check if the second image is mostly black, very dark, or shows camera malfunction/obstruction
2. SECOND - OWNER IDENTIFICATION: Compare any person in the second image with the owner in the first image
   - Check facial features, clothing, body build, hair, and overall appearance
   - If you can confidently identify the person as the SAME OWNER = SAFE (go to LOW THREAT)
3. THIRD - If NOT the owner OR uncertain about identity, then assess distance and behavior

CRITICAL SECURITY EVALUATION ORDER:
🔍 STEP 1 - CAMERA STATUS: Check for blackout/obstruction/malfunction
🔍 STEP 2 - OWNER VERIFICATION: Is this definitely the same person as in reference image?
   - Same face, similar clothing, matching physical characteristics
   - If YES = SAFE regardless of position/arms (proceed to LOW THREAT)
   - If NO or UNCERTAIN = proceed to threat assessment
🔍 STEP 3 - THREAT ASSESSMENT: Only if NOT confirmed owner
   - Distance comparison with reference image
   - Arms/hands positioning and proximity
   - Suspicious behavior detection

SECURITY ALERT CONDITIONS:
🚨 HIGH THREAT (70-100%):
- Camera is blacked out/obstructed/malfunctioned
- UNAUTHORIZED person (NOT the owner) at same or closer distance than reference
- UNAUTHORIZED person with ANY visible arm/hand/fingers that appears close to camera
- UNAUTHORIZED person reaching toward computer/keyboard/mouse/screen area
- UNAUTHORIZED person's face much closer to screen than reference shows
- UNAUTHORIZED person's arms extending toward computer area
- UNAUTHORIZED person's hands/arms appear larger/closer than reference image

⚠️ MODERATE THREAT (30-69%):
- UNAUTHORIZED person present but at farther distance than reference
- UNCERTAIN if same person as owner due to lighting/angle/partial view
- Person approaching but not yet at reference distance (identity unclear)

✅ LOW THREAT (0-29%):
- CONFIRMED OWNER (same person as reference) - SAFE regardless of position/arms
- No person visible but camera working normally
- UNAUTHORIZED person at much farther distance than reference with no threatening behavior

RESPONSE FORMAT:
THREAT LEVEL: [0-100]%
[Analysis result below]

For HIGH threat (70-100%): "🚨 SECURITY ALERT: [Describe the specific threat - camera issue, unauthorized access, suspicious approach, etc.]"

For MODERATE threat (30-69%): "⚠️ CAUTION: [Describe the situation and specific concerns]"

For LOW threat (0-29%): "✅ ALL NORMAL: [Describe what you see and why it's safe]"

IMPORTANT: Always compare the distance/positioning in the second image to the reference distance shown in the first image. The first image establishes what "normal computer use distance" looks like.

Analyze the images now:""",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{owner_b64}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{current_b64}"},
                },
            ]

            # Make API call
            response = self.client.chat.completions.create(
                model="glm-4v-flash",
                messages=[{"role": "user", "content": message_content}],
                extra_body={"temperature": 0.3, "max_tokens": 1000},
            )

            # Parse response
            response_text = response.choices[0].message.content
            threat_level = self.extract_threat_level(response_text)
            status_emoji = self.get_status_emoji(threat_level)

            return {
                "request_id": request_id,
                "timestamp": datetime.now(),
                "threat_level": threat_level,
                "status": status_emoji,
                "analysis": response_text,
            }

        except Exception as e:
            return {
                "request_id": request_id,
                "timestamp": datetime.now(),
                "threat_level": 0,
                "status": "❌ API Error",
                "analysis": f"Error during security analysis: {e}",
            }

    def extract_threat_level(self, response_text: str) -> int:
        """Extract threat level percentage from response text."""
        try:
            import re

            match = re.search(r"THREAT LEVEL:\s*(\d+)%", response_text)
            return int(match.group(1)) if match else 0
        except:
            return 0

    def get_status_emoji(self, threat_level: int) -> str:
        """Get status emoji based on threat level."""
        if threat_level >= 70:
            return "🚨 HIGH ALERT"
        elif threat_level >= 30:
            return "⚠️ CAUTION"
        else:
            return "✅ NORMAL"

    def start_monitoring(self, capture_interval: float, max_concurrent: int) -> str:
        """Start continuous security monitoring."""
        if self.monitoring_active:
            return "⚠️ Monitoring already active"

        if self.client is None:
            return "❌ Please initialize API client first"

        if self.owner_image is None:
            return "❌ Please capture owner reference image first"

        self.monitoring_active = True
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

        # Store monitoring parameters for streaming
        self.capture_interval = capture_interval
        self.max_concurrent = max_concurrent

        return f"✅ Security monitoring started (interval: {capture_interval}s, max concurrent: {max_concurrent})"

    def stop_monitoring(self) -> str:
        """Stop security monitoring."""
        self.monitoring_active = False
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
        return "⏹️ Security monitoring stopped"

    def process_streaming_frame(
        self, current_image: np.ndarray, capture_interval: float, max_concurrent: int
    ) -> np.ndarray:
        """Process streaming frame for security analysis."""
        if not self.monitoring_active or current_image is None:
            return current_image

        try:
            # Limit concurrent requests
            if len(self.active_requests) >= max_concurrent:
                return current_image

            # Check if enough time has passed since last analysis
            current_time = time.time()
            if hasattr(self, "_last_analysis_time"):
                if current_time - self._last_analysis_time < capture_interval:
                    return current_image

            self._last_analysis_time = current_time

            # Submit analysis task
            request_id = f"req_{int(time.time() * 1000)}"
            self.active_requests.add(request_id)

            if self.executor:
                future = self.executor.submit(
                    self.analyze_security_threat, current_image.copy(), request_id
                )

                # Handle completion in background
                def handle_completion(fut):
                    try:
                        result = fut.result()
                        self.active_requests.discard(result["request_id"])
                        self.response_queue.put(result)
                        self._update_response_history(result)
                    except Exception as e:
                        print(f"Error handling completion: {e}")
                        self.active_requests.discard(request_id)

                future.add_done_callback(handle_completion)

            return current_image

        except Exception as e:
            print(f"Error processing streaming frame: {e}")
            return current_image

    def _update_response_history(self, result: Dict[str, Any]):
        """Update response history with new result."""
        self.response_history.append(result)
        # Keep only last 10 responses, sorted by timestamp
        self.response_history.sort(key=lambda x: x["timestamp"], reverse=True)
        self.response_history = self.response_history[:10]

    def get_response_history_display(self) -> str:
        """Get formatted response history for display."""
        if not self.response_history:
            return "No monitoring results yet..."

        display_text = "📊 LATEST SECURITY MONITORING RESULTS\n"
        display_text += "=" * 60 + "\n\n"

        for i, result in enumerate(self.response_history, 1):
            timestamp_str = result["timestamp"].strftime("%H:%M:%S")
            display_text += f"{i}. [{timestamp_str}] THREAT LEVEL: {result['threat_level']}% | {result['status']}\n"
            # Show first 150 characters of analysis
            analysis_preview = result["analysis"][:150].replace("\n", " ")
            if len(result["analysis"]) > 150:
                analysis_preview += "..."
            display_text += f"   {analysis_preview}\n\n"

        return display_text

    def release_camera(self):
        """Release camera resources."""
        if self.camera:
            self.camera.release()
            self.camera = None


# Global monitor instance
monitor = SecurityMonitor()


def initialize_api(api_key: str) -> str:
    """Initialize API client."""
    return monitor.initialize_client(api_key)


def set_owner_from_current_feed(
    current_frame: Optional[np.ndarray],
) -> Tuple[Optional[np.ndarray], str]:
    """Set owner reference image from current camera feed."""
    return monitor.set_owner_from_stream(current_frame)


def start_monitoring(capture_interval: float, max_concurrent: int) -> str:
    """Start security monitoring."""
    return monitor.start_monitoring(capture_interval, max_concurrent)


def stop_monitoring() -> str:
    """Stop security monitoring."""
    return monitor.stop_monitoring()


def get_camera_feed():
    """Get current camera frame for live preview."""
    frame = monitor.get_camera_frame()
    if frame is not None:
        # Convert BGR to RGB for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame_rgb
    return None


def update_response_display():
    """Update the response history display."""
    return monitor.get_response_history_display()


# Create Gradio Interface
def create_gui():
    """Create the Gradio interface."""

    with gr.Blocks(
        title="🛡️ Computer Security Monitor",
        theme=gr.themes.Soft(),
        css="""
        .threat-high { background-color: #fee2e2 !important; border-left: 4px solid #dc2626 !important; }
        .threat-medium { background-color: #fef3c7 !important; border-left: 4px solid #d97706 !important; }
        .threat-low { background-color: #dcfce7 !important; border-left: 4px solid #16a34a !important; }
        """,
    ) as interface:
        gr.Markdown("# 🛡️ Computer Security Monitoring System")
        gr.Markdown(
            "Real-time security monitoring using GLM-4V vision AI with camera integration"
        )

        with gr.Row():
            # Left Column: Configuration
            with gr.Column(scale=1):
                gr.Markdown("## 🔧 Configuration")

                # API Key input
                api_key_input = gr.Textbox(
                    label="GLM-4V API Key",
                    type="password",
                    placeholder="Enter your API key from open.bigmodel.cn",
                    interactive=True,
                )

                api_init_btn = gr.Button("Initialize API Client", variant="primary")
                api_status = gr.Textbox(label="API Status", interactive=False)

                gr.Markdown("---")

                # Monitoring controls
                gr.Markdown("## ⚙️ Monitoring Settings")

                capture_interval = gr.Slider(
                    minimum=1.0,
                    maximum=30.0,
                    value=3.0,
                    step=0.5,
                    label="Capture Interval (seconds)",
                    info="Time between security checks",
                )

                max_concurrent = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=3,
                    step=1,
                    label="Max Concurrent Requests",
                    info="Maximum parallel API requests (GLM-4V limit: 10)",
                )

            # Middle Column: Camera Feed and Owner Reference
            with gr.Column(scale=2):
                gr.Markdown("## 📹 Live Camera Feed")

                camera_feed = gr.Image(
                    label="Current Camera View",
                    sources=["webcam"],
                    type="numpy",
                    streaming=True,
                    height=300,
                )

                # Owner reference controls under camera feed
                gr.Markdown("## 👤 Owner Reference")
                capture_owner_btn = gr.Button(
                    "📸 Set Latest Image as Owner Reference", variant="secondary"
                )
                owner_image_display = gr.Image(
                    label="Owner Reference Image", height=200
                )
                owner_status = gr.Textbox(label="Reference Status", interactive=False)

            # Right Column: Security Analysis Results
            with gr.Column(scale=2):
                gr.Markdown("## 📊 Security Analysis Results")

                response_display = gr.Textbox(
                    label="Latest 10 Results (Sorted by Request Time)",
                    max_lines=25,
                    lines=20,
                    interactive=False,
                    show_copy_button=True,
                )

                # Auto-refresh response display every 2 seconds
                refresh_timer = gr.Timer(2.0)

                gr.Markdown("---")

                # Monitoring controls moved here for better workflow
                gr.Markdown("## 🎯 Monitoring Controls")

                with gr.Row():
                    start_btn = gr.Button("🚀 Start Monitoring", variant="primary")
                    stop_btn = gr.Button("⏹️ Stop Monitoring", variant="stop")

                monitoring_status = gr.Textbox(
                    label="Monitoring Status", interactive=False
                )

        # Event handlers
        api_init_btn.click(initialize_api, inputs=[api_key_input], outputs=[api_status])

        capture_owner_btn.click(
            set_owner_from_current_feed,
            inputs=[camera_feed],
            outputs=[owner_image_display, owner_status],
        )

        start_btn.click(
            start_monitoring,
            inputs=[capture_interval, max_concurrent],
            outputs=[monitoring_status],
        )

        stop_btn.click(stop_monitoring, outputs=[monitoring_status])

        # Update camera feed using proper streaming
        camera_feed.stream(
            lambda frame: monitor.process_streaming_frame(
                frame, capture_interval.value, max_concurrent.value
            )
            if frame is not None
            else frame,
            inputs=[camera_feed],
            outputs=[camera_feed],
            # time_limit=60,  # 1 minute limit
            stream_every=1,  # Update every 1 second
            concurrency_limit=10,
        )

        # Auto-refresh response display
        refresh_timer.tick(update_response_display, outputs=[response_display])

    return interface


def main():
    """Main function to launch the GUI."""
    print("🛡️ Starting Computer Security Monitoring GUI...")
    print("📋 Features:")
    print("   • Real-time camera monitoring")
    print("   • GLM-4V AI threat analysis")
    print("   • Concurrent API processing")
    print("   • Live threat level assessment")
    print()

    try:
        interface = create_gui()
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True,
            quiet=False,
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down security monitor...")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
    finally:
        # Clean up resources
        monitor.stop_monitoring()
        monitor.release_camera()


if __name__ == "__main__":
    main()
