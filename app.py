#!/usr/bin/env python3
"""
🛡️ Computer Security Monitoring GUI

Real-time security monitoring system using GLM-4.1V-Thinking-Flash vision AI with Gradio interface.
Features camera integration, concurrent API processing, and live threat assessment.
"""

import base64
import json
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import cv2
import gradio as gr
import numpy as np
import requests
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
        self.discord_webhook_url: Optional[str] = None

    def initialize_client(self, api_key: str) -> str:
        """Initialize the GLM-4.1V-Thinking-Flash client with API key."""
        try:
            if not api_key.strip():
                return "❌ Please enter a valid API key"

            self.client = ZhipuAI(api_key=api_key.strip())
            return "✅ GLM-4.1V-Thinking-Flash client initialized successfully"
        except Exception as e:
            return f"❌ Error initializing client: {e}"

    def encode_image(self, image: np.ndarray, label_text: str = "") -> Optional[str]:
        """Encode image to base64 string with optional text label."""
        try:
            # Create a copy to avoid modifying the original
            image_copy = image.copy()

            # Add text label if provided
            if label_text:
                # Add text overlay to image
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.0
                color = (0, 255, 0)  # Green color in BGR
                thickness = 2

                # Get text size to position it properly
                text_size = cv2.getTextSize(label_text, font, font_scale, thickness)[0]

                # Position text at top-left with some padding
                x = 10
                y = 30

                # Add a background rectangle for better visibility
                cv2.rectangle(
                    image_copy,
                    (x - 5, y - 25),
                    (x + text_size[0] + 5, y + 5),
                    (0, 0, 0),
                    -1,
                )

                # Add the text
                cv2.putText(
                    image_copy, label_text, (x, y), font, font_scale, color, thickness
                )

            # Convert BGR to RGB if needed
            if len(image_copy.shape) == 3 and image_copy.shape[2] == 3:
                image_rgb = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_copy

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
        """Analyze security threat using GLM-4.1V-Thinking-Flash API."""
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

            # Encode both images with clear labels
            owner_b64 = self.encode_image(
                self.owner_image, "REFERENCE IMAGE - NORMAL WORKING DISTANCE"
            )
            current_b64 = self.encode_image(current_image, "CURRENT MONITORING IMAGE")

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
                    "text": """You are a computer security monitoring system. I have uploaded 2 images with clear labels:

1. FIRST IMAGE (labeled "REFERENCE IMAGE - NORMAL WORKING DISTANCE"): This shows the baseline for normal, safe computer use distance and positioning
2. SECOND IMAGE (labeled "CURRENT MONITORING IMAGE"): This is the live camera feed to analyze for security threats

SECURITY ALERT CONDITIONS:
(Satisfy any of the following conditions to trigger a security alert,
evaluate by the order of highest to lowest threat level)

🚨 HIGH THREAT (70-100%):
- Camera is blacked out/obstructed/malfunctioned
- Person at a distance closer than or similar to the referenced working distance, or up to 0.5m beyond it
- ANY visible arm/hand/fingers that appears closer than or similar to reference baseline
- Person reaching toward computer/keyboard/mouse/screen area
- Person's face closer to or at similar distance to screen as reference distance
- Arms extending toward computer area beyond or at reference positioning
- Hands/arms appear larger/closer than or similar size to what reference image shows
- Large difference between the reference image and the current image
- Any suspicious behavior

⚠️ MODERATE THREAT (30-69%):
- Person approaching but not yet at reference distance
- Unclear view but person appears to be approaching reference distance range

✅ LOW THREAT (0-29%):
- No person visible but camera working normally
- Person at FURTHER distance than reference image with no threatening behavior
- Person well beyond the reference working distance

RESPONSE FORMAT (KEEP IT BRIEF):
THREAT LEVEL: [0-100]%
STATUS: [Choose one: "🚨 HIGH ALERT" / "⚠️ CAUTION" / "✅ NORMAL"]

IMPORTANT: Just provide the threat level number and status. No detailed analysis needed.

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
                model="glm-4.1v-thinking-flash",
                messages=[{"role": "user", "content": message_content}],
                extra_body={"temperature": 0.1, "max_tokens": 300},
            )

            # Parse response and handle <think> tags
            response_text = response.choices[0].message.content
            processed_response = self.process_thinking_response(response_text)
            threat_level = self.extract_threat_level(processed_response)
            status_emoji = self.get_status_emoji(threat_level)

            return {
                "request_id": request_id,
                "timestamp": datetime.now(),
                "threat_level": threat_level,
                "status": status_emoji,
                "analysis": processed_response,
            }

        except Exception as e:
            return {
                "request_id": request_id,
                "timestamp": datetime.now(),
                "threat_level": 0,
                "status": "❌ API Error",
                "analysis": f"Error during security analysis: {e}",
            }

    def process_thinking_response(self, response_text: str) -> str:
        """Remove <think> tags from the GLM-4.1V-Thinking-Flash response."""
        try:
            import re
            
            # Remove <think>...</think> content including multiline
            processed_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            
            # Clean up any extra whitespace or newlines
            processed_text = re.sub(r'\n\s*\n', '\n', processed_text).strip()
            
            return processed_text
        except Exception as e:
            print(f"Error processing thinking response: {e}")
            return response_text  # Return original if processing fails

    def extract_threat_level(self, response_text: str) -> int:
        """Extract threat level percentage from response text."""
        try:
            import re

            match = re.search(r"THREAT LEVEL:\s*(\d+)%", response_text)
            return int(match.group(1)) if match else 0
        except Exception:
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

                        # Send Discord alert for high threats
                        if result["threat_level"] >= 70:
                            self.send_discord_alert(result, current_image)

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

    def set_discord_webhook(self, webhook_url: str) -> str:
        """Set Discord webhook URL for notifications."""
        try:
            if not webhook_url.strip():
                self.discord_webhook_url = None
                return "Discord notifications disabled"

            # Validate webhook URL format
            if not webhook_url.startswith(
                "https://discord.com/api/webhooks/"
            ) and not webhook_url.startswith("https://ptb.discord.com/api/webhooks/"):
                return "❌ Invalid Discord webhook URL format"

            self.discord_webhook_url = webhook_url.strip()
            return "✅ Discord webhook configured successfully"
        except Exception as e:
            return f"❌ Error setting Discord webhook: {e}"

    def send_discord_alert(self, threat_result: Dict[str, Any], image: np.ndarray):
        """Send high threat alert to Discord."""
        try:
            if not self.discord_webhook_url or threat_result["threat_level"] < 70:
                return  # Only send high threat alerts

            # Prepare Discord message
            timestamp = threat_result["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

            embed = {
                "title": "🚨 COMPUTER SECURITY ALERT",
                "description": f"**Threat Level:** {threat_result['threat_level']}%\n**Status:** {threat_result['status']}\n**Time:** {timestamp}",
                "color": 0xFF0000,  # Red color
                "footer": {"text": "Computer Security Monitor"},
                "timestamp": threat_result["timestamp"].isoformat(),
                "image": {
                    "url": "attachment://security_alert.png"
                },  # Reference the attached image
            }

            # Convert image to bytes for file upload
            import io

            # The image is already in RGB format from the camera stream processing
            # No need for color conversion as it was already done in get_camera_frame()
            pil_image = Image.fromarray(image.astype("uint8"))
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Prepare payload and files for single combined request
            payload = {
                "embeds": [embed],
                "content": f"🚨 **HIGH SECURITY ALERT** - Threat Level: {threat_result['threat_level']}%",
            }

            files = {
                "file": ("security_alert.png", buffer, "image/png"),
                "payload_json": (None, json.dumps(payload), "application/json"),
            }

            # Send message and image together in single request
            requests.post(self.discord_webhook_url, files=files, timeout=10)

        except Exception as e:
            print(f"Error sending Discord alert: {e}")

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


def set_discord_webhook(webhook_url: str) -> str:
    """Set Discord webhook URL."""
    return monitor.set_discord_webhook(webhook_url)


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
            "Real-time security monitoring using GLM-4.1V-Thinking-Flash vision AI with camera integration"
        )

        with gr.Row():
            # Left Column: Configuration
            with gr.Column(scale=1):
                gr.Markdown("## 🔧 Configuration")

                # API Key input
                api_key_input = gr.Textbox(
                    label="GLM-4.1V-Thinking-Flash API Key",
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
                    info="Maximum parallel API requests (GLM-4.1V-Thinking-Flash limit: 10)",
                )

                gr.Markdown("---")

                # Discord notifications
                gr.Markdown("## 🔔 Notification Settings")

                discord_webhook_input = gr.Textbox(
                    label="Discord Webhook URL",
                    type="password",
                    placeholder="https://discord.com/api/webhooks/...",
                    info="High threat alerts (70%+) will be sent to Discord",
                    interactive=True,
                )

                discord_setup_btn = gr.Button(
                    "Setup Discord Notifications", variant="secondary"
                )
                discord_status = gr.Textbox(label="Discord Status", interactive=False)

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

        discord_setup_btn.click(
            set_discord_webhook,
            inputs=[discord_webhook_input],
            outputs=[discord_status],
        )

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
    print("   • GLM-4.1V-Thinking-Flash AI threat analysis")
    print("   • Concurrent API processing")
    print("   • Live threat level assessment")
    print()

    try:
        interface = create_gui()
        interface.launch(
            server_name="0.0.0.0",
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
