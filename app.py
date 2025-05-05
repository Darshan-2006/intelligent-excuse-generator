import streamlit as st
import random
import os
import shutil
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image, ImageDraw
from gtts import gTTS
import base64
from io import BytesIO
import streamlit.components.v1 as components

# Sample excuse templates
EXCUSES = {
    "work": [
        "I have a sudden family emergency that requires my immediate attention.",
        "I'm unwell and need to visit a doctor today.",
        "My car broke down, and I'm waiting for roadside assistance."
    ],
    "school": [
        "I missed the bus and won't make it to class on time.",
        "I had a medical appointment that ran longer than expected.",
        "I was helping a family member with an urgent matter."
    ],
    "social": [
        "I got caught up with some unexpected work and can't make it.",
        "I'm feeling under the weather and need to rest.",
        "A last-minute family obligation came up."
    ],
    "family": [
        "I have to attend an urgent appointment.",
        "I'm dealing with a personal issue that needs my attention.",
        "I got delayed due to transportation issues."
    ]
}

# Apology templates
APOLOGIES = {
    "professional": "I sincerely apologize for any inconvenience caused. Please let me know how I can make this right.",
    "emotional": "I'm so sorry for letting you down. I feel terrible about this and hope you understand."
}

class ExcuseGenerator:
    def __init__(self):
        self.history = []
        self.favorites = []
        self.ratings = {}  # Dictionary to store ratings for excuses

    def generate_excuse(self, scenario, urgency="medium", custom_excuse=None):
        """Generate a context-based excuse."""
        scenario = scenario.lower()
        urgency = urgency.lower()
        if scenario not in EXCUSES:
            scenario = "social"
        if urgency not in ["low", "medium", "high"]:
            urgency = "medium"
        if custom_excuse and custom_excuse.strip():
            excuse = custom_excuse
        else:
            excuse = random.choice(EXCUSES[scenario])
        if urgency == "high":
            excuse = f"Urgent: {excuse}"
        elif urgency == "low":
            excuse = f"Just a heads-up: {excuse}"
        self.history.append({"scenario": scenario, "excuse": excuse, "timestamp": str(datetime.now())})
        return excuse

    def generate_proof(self, excuse, proof_type="document", patient_name=""):
        """Generate proof to support the excuse."""
        proof_type = proof_type.lower()
        if proof_type not in ["document", "chat"]:
            return None, "Invalid proof type. Use 'document' or 'chat'."
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            if proof_type == "document":
                filename = f"medical_certificate_{timestamp}.pdf"
                c = canvas.Canvas(filename, pagesize=letter)

                # Header
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(4.25*inch, 10.7*inch, "Medical Certificate")
                c.setFont("Helvetica", 12)
                c.drawCentredString(4.25*inch, 10.4*inch, "City Health Clinic")
                c.drawCentredString(4.25*inch, 10.2*inch, "123 Health St, Bengaluru, Karnataka 560102")
                c.drawCentredString(4.25*inch, 10.0*inch, "Phone: +91 8062181856 | Email: support@clinic.org")

                # Line separator
                c.setLineWidth(1)
                c.line(1*inch, 9.8*inch, 7.5*inch, 9.8*inch)

                # Patient Details
                c.setFont("Helvetica", 12)
                c.drawString(1*inch, 9.3*inch, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
                c.drawString(1*inch, 9.0*inch, f"Patient Name: {patient_name or 'Not Specified'}")
                c.drawString(1*inch, 8.7*inch, f"Reason for Absence: {excuse}")

                # Medical Details
                styles = getSampleStyleSheet()
                style = styles["Normal"]
                medical_text = (
                    f"This is to certify that {patient_name or 'the patient'} has been examined and diagnosed "
                    "with a temporary medical condition requiring rest. The patient is advised to refrain from "
                    "work or school activities for a period of 1-2 days, starting from the date above."
                )
                para = Paragraph(medical_text, style)
                para.wrapOn(c, 6.5*inch, 2*inch)
                para.drawOn(c, 1*inch, 7.8*inch)

                # Doctor Details
                c.setFont("Helvetica", 12)
                c.drawString(1*inch, 7.0*inch, "Certified by: Dr. John Doe, MD")
                c.drawString(1*inch, 6.7*inch, "License No: KA123456")

                # Simulated Signature
                c.setFont("Helvetica-Oblique", 14)
                c.setFillColor(colors.blue)
                c.drawString(1*inch, 6.4*inch, "John Doe")
                c.setFillColor(colors.black)

                # Clinic Stamp
                c.setFillColor(colors.red)
                c.setLineWidth(2)
                c.circle(6*inch, 6.5*inch, 0.5*inch, stroke=1, fill=0)
                c.setFont("Helvetica", 8)
                c.drawCentredString(6*inch, 6.55*inch, "City Health Clinic")
                c.drawCentredString(6*inch, 6.45*inch, "Bengaluru")
                c.setFillColor(colors.black)

                # Footer
                c.setFont("Helvetica-Oblique", 10)
                c.setFillColor(colors.grey)
                c.drawCentredString(4.25*inch, 0.5*inch, "This certificate is issued for medical purposes only.")

                c.save()
                return filename, None

            elif proof_type == "chat":
                filename = f"chat_screenshot_{timestamp}.png"
                img = Image.new('RGB', (400, 600), color='white')
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), f"Friend: Sorry, {excuse}", fill='black')
                img.save(filename)
                return filename, None

        except Exception as e:
            return None, f"Error generating proof: {str(e)}"
        return None, "Unknown error in proof generation."

    def generate_apology(self, tone="professional"):
        """Generate an apology based on tone."""
        tone = tone.lower()
        return APOLOGIES.get(tone, APOLOGIES["professional"])

    def save_to_favorites(self, excuse):
        """Save an excuse to favorites."""
        if excuse not in self.favorites:
            self.favorites.append(excuse)
            return True
        return False

    def view_history(self):
        """Return excuse history."""
        return self.history

    def auto_schedule(self):
        """Predict when an excuse might be needed (simplified)."""
        if len(self.history) > 0:
            last_excuse = self.history[-1]
            return f"Based on past usage, you might need an excuse for {last_excuse['scenario']} soon."
        return "No history available to predict."

    def generate_speech(self, text, lang="en"):
        """Convert text excuse to speech."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"excuse_speech_{timestamp}.mp3"
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(filename)
            return filename, None
        except Exception as e:
            return None, f"Error generating speech: {str(e)}"

    def rate_excuse(self, excuse, rating):
        """Rate an excuse and store the rating."""
        if excuse not in self.ratings:
            self.ratings[excuse] = []
        self.ratings[excuse].append(rating)

    def get_average_rating(self, excuse):
        """Calculate the average rating for an excuse."""
        if excuse in self.ratings and self.ratings[excuse]:
            return sum(self.ratings[excuse]) / len(self.ratings[excuse])
        return None

# Custom CSS for styling, animations, background, and dark mode
st.markdown("""
    <style>
    /* General Styling */
    body {
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        transition: all 0.3s ease;
        background: url('https://www.transparenttextures.com/patterns/stardust.png'), linear-gradient(135deg, #1a1a3d, #3d2b56);
        background-size: cover, 200%;
        background-attachment: fixed;
        color: #e0e0e0;
    }
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        color: #ff2d55;
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    .section-title {
        font-size: 1.8em;
        font-weight: 600;
        color: #0ff;
        margin-top: 20px;
        margin-bottom: 10px;
        animation: fadeUp 0.8s ease;
    }
    .stButton>button {
        background: linear-gradient(145deg, #ff2d55, #0ff);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        transition: transform 0.2s, background 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(145deg, #0ff, #ff2d55);
        transform: scale(1.05);
        animation: pulse 0.5s infinite;
    }
    .stTextInput>div>input, .stSelectbox>div>select {
        border-radius: 5px;
        padding: 8px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        border: 1px solid #0ff;
    }
    .output-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        animation: rotateIn 0.5s ease;
        border: 1px solid #0ff;
        backdrop-filter: blur(5px);
    }

    /* Dark Mode */
    .dark-mode .stApp {
        background: url('https://www.transparenttextures.com/patterns/stardust.png'), linear-gradient(135deg, #0f0f23, #2b1a3d);
        color: #ffffff;
    }
    .dark-mode .main-title {
        color: #ff2d55;
    }
    .dark-mode .section-title {
        color: #0ff;
    }
    .dark-mode .output-box {
        background-color: rgba(255, 255, 255, 0.05);
    }
    .dark-mode .stButton>button {
        background: linear-gradient(145deg, #ff2d55, #0ff);
    }
    .dark-mode .stButton>button:hover {
        background: linear-gradient(145deg, #0ff, #ff2d55);
    }

    /* Toggle Button Styling */
    .toggle-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .toggle-button {
        background: linear-gradient(145deg, #ff2d55, #0ff);
        color: #fff;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 0 10px rgba(255, 45, 85, 0.5);
        transition: transform 0.3s, background 0.3s, box-shadow 0.3s;
        position: relative;
    }
    .toggle-button:hover {
        transform: scale(1.1);
        background: linear-gradient(145deg, #0ff, #ff2d55);
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
    }
    .toggle-button:active {
        animation: spin 0.5s ease;
    }
    .dark-mode .toggle-button {
        background: linear-gradient(145deg, #ff2d55, #0ff);
        box-shadow: 0 0 10px rgba(255, 45, 85, 0.5);
    }
    .dark-mode .toggle-button:hover {
        background: linear-gradient(145deg, #0ff, #ff2d55);
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
    }
    .toggle-button .tooltip-text {
        visibility: hidden;
        width: 120px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .toggle-button:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    /* Theme Switcher Button */
    .theme-switcher {
        background: linear-gradient(145deg, #39ff14, #ff2d55);
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        transition: transform 0.2s, background 0.3s;
    }
    .theme-switcher:hover {
        transform: scale(1.05);
        background: linear-gradient(145deg, #ff2d55, #39ff14);
    }

    /* Share Button */
    .share-button:hover {
        animation: shake 0.5s ease;
    }

    /* Sidebar Animation */
    .stSidebar {
        animation: scaleIn 0.5s ease;
    }

    /* Footer Animation */
    .footer {
        animation: pulseFooter 2s infinite;
    }

    /* Live Clock */
    .live-clock {
        text-align: center;
        font-size: 1.2em;
        color: #39ff14;
        margin-bottom: 20px;
        font-weight: 600;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes fadeUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes glow {
        from { text-shadow: 0 0 5px #ff2d55, 0 0 10px #ff2d55; }
        to { text-shadow: 0 0 10px #ff2d55, 0 0 20px #0ff; }
    }
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-5px); }
        100% { transform: translateX(0); }
    }
    @keyframes rotateIn {
        from { transform: rotate(-5deg); opacity: 0; }
        to { transform: rotate(0deg); opacity: 1; }
    }
    @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    @keyframes pulseFooter {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }

    /* Responsive Design */
    @media (max-width: 600px) {
        .main-title {
            font-size: 2em;
        }
        .section-title {
            font-size: 1.5em;
        }
        .stButton>button {
            width: 100%;
            padding: 12px;
        }
        .toggle-button {
            width: 35px;
            height: 35px;
            font-size: 18px;
        }
        .live-clock {
            font-size: 1em;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'generator' not in st.session_state:
    st.session_state.generator = ExcuseGenerator()
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []
if 'theme' not in st.session_state:
    st.session_state.theme = "space"
if 'last_excuse' not in st.session_state:
    st.session_state.last_excuse = ""
if 'accent_color' not in st.session_state:
    st.session_state.accent_color = "#ff2d55"
if 'background_image' not in st.session_state:
    st.session_state.background_image = None

# Themes for selection and random switcher
THEMES = {
    "space": "url('https://www.transparenttextures.com/patterns/stardust.png'), linear-gradient(135deg, #1a1a3d, #3d2b56)",
    "gradient": "linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb)",
    "nature": "url('https://www.transparenttextures.com/patterns/leaf.png'), linear-gradient(135deg, #2ecc71, #27ae60)",
    "neon": "url('https://www.transparenttextures.com/patterns/dark-mosaic.png'), linear-gradient(135deg, #1c2526, #2f4858)",
    "ocean": "url('https://www.transparenttextures.com/patterns/wave.png'), linear-gradient(135deg, #0077b6, #00b4d8)",
    "sunset": "url('https://www.transparenttextures.com/patterns/sunset.png'), linear-gradient(135deg, #ff5e62, #feca57)",
    "dark_space": "url('https://www.transparenttextures.com/patterns/stardust.png'), linear-gradient(135deg, #0f0f23, #2b1a3d)",
    "dark_gradient": "linear-gradient(135deg, #d63031, #e17055, #2d3436)",
    "dark_nature": "url('https://www.transparenttextures.com/patterns/leaf.png'), linear-gradient(135deg, #1a7f37, #14532d)",
    "dark_neon": "url('https://www.transparenttextures.com/patterns/dark-mosaic.png'), linear-gradient(135deg, #0b1415, #1f2e38)",
    "dark_ocean": "url('https://www.transparenttextures.com/patterns/wave.png'), linear-gradient(135deg, #003f5c, #005f73)",
    "dark_sunset": "url('https://www.transparenttextures.com/patterns/sunset.png'), linear-gradient(135deg, #ff3f34, #ff9f43)"
}

# Apply custom accent color
accent_color = st.session_state.accent_color
st.markdown(
    f"""
    <style>
    .main-title, .toggle-button, .stButton>button {{
        color: {accent_color} !important;
        border-color: {accent_color} !important;
    }}
    .toggle-button, .stButton>button {{
        background: linear-gradient(145deg, {accent_color}, #0ff) !important;
    }}
    .toggle-button:hover, .stButton>button:hover {{
        background: linear-gradient(145deg, #0ff, {accent_color}) !important;
    }}
    .toggle-button {{
        box-shadow: 0 0 10px {accent_color} !important;
    }}
    .toggle-button:hover {{
        box-shadow: 0 0 15px {accent_color} !important;
    }}
    .output-box, .stTextInput>div>input, .stSelectbox>div>select {{
        border-color: {accent_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Custom background image
uploaded_file = st.file_uploader("Upload a custom background image:", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    st.session_state.background_image = uploaded_file
if st.session_state.background_image:
    image_bytes = st.session_state.background_image.read()
    encoded_image = base64.b64encode(image_bytes).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/png;base64,{encoded_image}) !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
        .dark-mode .stApp {{
            background: url(data:image/png;base64,{encoded_image}) !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Sound effects JavaScript
components.html("""
    <audio id="celebrationSound" src="https://www.soundjay.com/buttons/sounds/button-1.mp3"></audio>
    <audio id="clickSound" src="https://www.soundjay.com/buttons/sounds/button-3.mp3"></audio>
    <audio id="hoverSound" src="https://www.soundjay.com/buttons/sounds/button-4.mp3"></audio>
    <audio id="errorSound" src="https://www.soundjay.com/buttons/sounds/button-2.mp3"></audio>
    <audio id="successSound" src="https://www.soundjay.com/buttons/sounds/button-6.mp3"></audio>
    <script>
    function playCelebrationSound() {
        document.getElementById('celebrationSound').play();
    }
    function playClickSound() {
        document.getElementById('clickSound').play();
    }
    function playHoverSound() {
        document.getElementById('hoverSound').play();
    }
    function playErrorSound() {
        document.getElementById('errorSound').play();
    }
    function playSuccessSound() {
        document.getElementById('successSound').play();
    }
    </script>
""", height=0)

# Confetti JavaScript (using canvas-confetti with updated colors)
components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <script>
    function triggerConfetti() {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#ff2d55', '#0ff', '#39ff14']
        });
    }
    </script>
""", height=0)

# Theme selection and random switcher
def apply_theme(theme_name):
    st.session_state.theme = theme_name
    if not st.session_state.background_image:  # Only apply theme if no custom background
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: {THEMES[theme_name]} !important;
                background-size: cover, 200% !important;
                background-attachment: fixed !important;
            }}
            .dark-mode .stApp {{
                background: {THEMES.get('dark_' + theme_name.split('_')[-1], THEMES[theme_name])} !important;
                background-size: cover, 200% !important;
                background-attachment: fixed !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Live clock JavaScript
components.html("""
    <div class="live-clock" id="clock"></div>
    <script>
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Kolkata', hour12: true });
        document.getElementById('clock').innerText = `🕒 Current Time: ${timeString}`;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
""", height=50)

# Theme selector and color picker
col1, col2 = st.columns([1, 1])
with col1:
    selected_theme = st.selectbox("Select Theme:", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), key="theme_selector")
    if selected_theme != st.session_state.theme:
        apply_theme(selected_theme)
with col2:
    new_accent_color = st.color_picker("Pick Accent Color:", value=st.session_state.accent_color, key="accent_color_picker")
    if new_accent_color != st.session_state.accent_color:
        st.session_state.accent_color = new_accent_color

# Random theme switcher
if st.button("🎨 Random Theme", key="theme_switcher", type="primary"):
    available_themes = list(THEMES.keys())
    current_theme = st.session_state.theme
    available_themes.remove(current_theme)
    new_theme = random.choice(available_themes)
    apply_theme(new_theme)
st.markdown('<style>.stButton>button[key="theme_switcher"] { background: linear-gradient(145deg, #39ff14, #ff2d55); } .stButton>button[key="theme_switcher"]:hover { background: linear-gradient(145deg, #ff2d55, #39ff14); transform: scale(1.05); }</style>', unsafe_allow_html=True)
components.html("<script>document.querySelector('button[key=\"theme_switcher\"]').addEventListener('click', playClickSound); document.querySelector('button[key=\"theme_switcher\"]').addEventListener('mouseover', playHoverSound);</script>", height=0)

# Dark mode toggle
st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
toggle_label = "☀️" if st.session_state.dark_mode else "🌙"
if st.button(
    toggle_label,
    key="dark_mode_toggle",
    help="Toggle Dark Mode",
    type="primary"
):
    st.session_state.dark_mode = not st.session_state.dark_mode
st.markdown(
    f'<button class="toggle-button">{toggle_label}<span class="tooltip-text">Toggle Dark Mode</span></button>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
components.html("<script>document.querySelector('button[key=\"dark_mode_toggle\"]').addEventListener('click', playClickSound); document.querySelector('button[key=\"dark_mode_toggle\"]').addEventListener('mouseover', playHoverSound);</script>", height=0)

# Apply dark mode class
if st.session_state.dark_mode:
    st.markdown('<div class="dark-mode">', unsafe_allow_html=True)

# Main title
st.markdown('<div class="main-title">🧠 Intelligent Excuse Generator 🎉</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.markdown('<div class="section-title">🚀 Navigation</div>', unsafe_allow_html=True)
option = st.sidebar.selectbox(
    "Choose an action:",
    [
        "Generate Excuse",
        "Generate Proof",
        "Generate Apology",
        "Save to Favorites",
        "View History",
        "Auto-Schedule Prediction",
        "Generate Speech"
    ],
    key="action_select"
)

# Clean up temporary files
def cleanup_temp_files():
    for file in st.session_state.temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass
    st.session_state.temp_files = []

# Generate download link for files
def get_binary_file_downloader_html(file_path, file_label):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'
    st.session_state.temp_files.append(file_path)
    return href

# Share to clipboard JavaScript
def share_to_clipboard(text):
    components.html(
        f"""
        <button onclick="copyToClipboard()" class="stButton share-button">📋 Share Excuse</button>
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText("{text}").then(() => {{
                alert("Excuse copied to clipboard!");
                playClickSound();
            }});
        }}
        </script>
        """,
        height=50
    )
    components.html("<script>document.querySelector('.share-button').addEventListener('mouseover', playHoverSound);</script>", height=0)

# Main content based on selected option
if option == "Generate Excuse":
    st.markdown('<div class="section-title">🎭 Generate Excuse</div>', unsafe_allow_html=True)
    scenario = st.selectbox("Select scenario:", ["Work", "School", "Social", "Family"], key="excuse_scenario")
    urgency = st.selectbox("Select urgency:", ["Low", "Medium", "High"], key="excuse_urgency")
    custom_excuse = st.text_input("✏️ Or enter a custom excuse (optional):", key="custom_excuse")
    if st.button("Generate Excuse 🚀"):
        if not custom_excuse.strip() and not EXCUSES.get(scenario.lower()):
            st.error("Please select a valid scenario or enter a custom excuse.")
            components.html("<script>playErrorSound();</script>", height=0)
        else:
            excuse = st.session_state.generator.generate_excuse(scenario, urgency, custom_excuse)
            st.session_state.last_excuse = excuse
            st.markdown(f'<div class="output-box">📜 <strong>Excuse:</strong> {excuse}</div>', unsafe_allow_html=True)
            components.html("<script>triggerConfetti(); playCelebrationSound();</script>", height=0)
            # Excuse rating
            rating = st.slider("Rate this excuse (1-5 stars):", 1, 5, 3, key=f"rating_{excuse}")
            if st.button("Submit Rating", key=f"submit_rating_{excuse}"):
                st.session_state.generator.rate_excuse(excuse, rating)
                st.success("Rating submitted!")
                components.html("<script>playSuccessSound();</script>", height=0)
            avg_rating = st.session_state.generator.get_average_rating(excuse)
            if avg_rating:
                st.markdown(f'<div class="output-box">⭐ Average Rating: {avg_rating:.1f}/5</div>', unsafe_allow_html=True)
            share_to_clipboard(excuse)

elif option == "Generate Proof":
    st.markdown('<div class="section-title">📄 Generate Proof</div>', unsafe_allow_html=True)
    excuse = st.text_input("Enter the excuse for proof:", key="proof_excuse")
    patient_name = st.text_input("Enter patient name (for medical certificate):", key="patient_name")
    proof_type = st.selectbox("Select proof type:", ["Document (Medical Certificate)", "Chat (Screenshot)"], key="proof_type")
    proof_type = "document" if proof_type.startswith("Document") else "chat"
    if st.button("Generate Proof 🖨️"):
        if not excuse.strip():
            st.error("Please enter an excuse.")
            components.html("<script>playErrorSound();</script>", height=0)
        else:
            filename, error = st.session_state.generator.generate_proof(excuse, proof_type, patient_name)
            if error:
                st.error(error)
                components.html("<script>playErrorSound();</script>", height=0)
            elif filename and os.path.exists(filename):
                st.success(f"Proof generated: {filename}")
                components.html("<script>playSuccessSound();</script>", height=0)
                st.markdown(get_binary_file_downloader_html(filename, f"Download {filename} 📥"), unsafe_allow_html=True)
                components.html("<script>triggerConfetti();</script>", height=0)
            else:
                st.error("Error: Proof generation failed.")
                components.html("<script>playErrorSound();</script>", height=0)

elif option == "Generate Apology":
    st.markdown('<div class="section-title">🙏 Generate Apology</div>', unsafe_allow_html=True)
    tone = st.selectbox("Select tone:", ["Professional", "Emotional"], key="apology_tone")
    if st.button("Generate Apology 💌"):
        apology = st.session_state.generator.generate_apology(tone)
        st.session_state.last_excuse = apology
        st.markdown(f'<div class="output-box">📜 <strong>Apology:</strong> {apology}</div>', unsafe_allow_html=True)
        share_to_clipboard(apology)

elif option == "Save to Favorites":
    st.markdown('<div class="section-title">⭐ Save to Favorites</div>', unsafe_allow_html=True)
    excuse = st.text_input("Enter excuse to save to favorites:", key="favorite_excuse")
    if st.button("Save to Favorites 💾"):
        if not excuse.strip():
            st.error("Please enter an excuse.")
            components.html("<script>playErrorSound();</script>", height=0)
        elif st.session_state.generator.save_to_favorites(excuse):
            st.success("Saved to favorites! ⭐")
            components.html("<script>playSuccessSound();</script>", height=0)
        else:
            st.warning("Already in favorites.")

elif option == "View History":
    st.markdown('<div class="section-title">📜 Excuse History</div>', unsafe_allow_html=True)
    history = st.session_state.generator.view_history()
    if history:
        for entry in history:
            st.markdown(
                f'<div class="output-box">🕒 {entry["timestamp"]}: {entry["excuse"]} ({entry["scenario"].capitalize()})</div>',
                unsafe_allow_html=True
            )
            avg_rating = st.session_state.generator.get_average_rating(entry["excuse"])
            if avg_rating:
                st.markdown(f'<div class="output-box">⭐ Average Rating: {avg_rating:.1f}/5</div>', unsafe_allow_html=True)
    else:
        st.info("No history available.")

elif option == "Auto-Schedule Prediction":
    st.markdown('<div class="section-title">🔮 Auto-Schedule Prediction</div>', unsafe_allow_html=True)
    if st.button("Predict Next Excuse 🔍"):
        prediction = st.session_state.generator.auto_schedule()
        st.markdown(f'<div class="output-box">🔮 <strong>Prediction:</strong> {prediction}</div>', unsafe_allow_html=True)

elif option == "Generate Speech":
    st.markdown('<div class="section-title">🎙️ Generate Speech</div>', unsafe_allow_html=True)
    text = st.text_input("Enter text to convert to speech:", key="speech_text")
    lang = st.text_input("Enter language code (e.g., 'en' for English):", value="en", key="speech_lang")
    if st.button("Generate Speech 🎧"):
        if not text.strip():
            st.error("Please enter text.")
            components.html("<script>playErrorSound();</script>", height=0)
        else:
            filename, error = st.session_state.generator.generate_speech(text, lang)
            if error:
                st.error(error)
                components.html("<script>playErrorSound();</script>", height=0)
            elif filename and os.path.exists(filename):
                st.success(f"Speech file generated: {filename}")
                components.html("<script>playSuccessSound();</script>", height=0)
                st.markdown(get_binary_file_downloader_html(filename, f"Download {filename} 📥"), unsafe_allow_html=True)
                audio_file = open(filename, 'rb')
                st.audio(audio_file, format='audio/mp3')
                audio_file.close()
                components.html("<script>triggerConfetti();</script>", height=0)
            else:
                st.error("Error: Speech generation failed.")
                components.html("<script>playErrorSound();</script>", height=0)

# Clean up temporary files
if st.button("🧹 Clean Up Temporary Files"):
    cleanup_temp_files()
    st.success("Temporary files cleaned up!")
    components.html("<script>playSuccessSound();</script>", height=0)

# Close dark mode div if active
if st.session_state.dark_mode:
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="footer" style="text-align: center; margin-top: 20px; color: #888;">'
    'Built with ❤️ by Darshan using Streamlit | © 2025 Excuse Generator'
    '</div>',
    unsafe_allow_html=True
)