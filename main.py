import streamlit as st
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gst_verification.gst_extractor import extract_invoice_data
from gst_verification.gst_api import verify_gst, customer_gst
from gst_verification.data_manager import load_all_data, save_all_data
from rag_chatbot.rag_chain import run_chatbot

# Load API Key and setup Gemini
api_key = os.getenv("GOOGLE_API_KEY")
assert api_key is not None, "GOOGLE_API_KEY is not set in Railway!"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Page configuration
st.set_page_config(page_title="GST AI Verifier & Chatbot", layout="wide", initial_sidebar_state="expanded")

# Enhanced CSS with Black Background and Eye-Friendly Colors
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    .stApp {
        font-family: 'Poppins', sans-serif;
        color: #e0e0e0; /* Light gray for text */
        transition: all 0.3s ease;
    }

    /* Light and Dark Theme */
    :root {
        --card-bg: rgba(50, 50, 50, 0.8); /* Dark gray for cards */
        --text-color: #e0e0e0; /* Light gray for contrast */
        --accent-color: #00bcd4; /* Cyan for vibrancy */
        --hover-color: #ff5722; /* Orange for hover effects */
        --background-color: #121212; /* Deep black background */
    }

    [data-theme="light"] {
        --card-bg: rgba(200, 200, 200, 0.8);
        --text-color: #1a1a1a;
        --background-color: #e0e0e0; /* Light gray for light theme */
    }

    .stApp {
        background: var(--background-color);
    }

    .block-style {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .block-style:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.3);
    }

    h1, h2, h3, h4 {
        color: var(--accent-color);
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 0 8px rgba(0, 188, 212, 0.4);
    }

    .stButton>button, .stDownloadButton>button {
        background-color: var(--accent-color) !important;
        color: #ffffff !important;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 12px rgba(0, 188, 212, 0.4);
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: var(--hover-color) !important;
        transform: scale(1.05);
        box-shadow: 0 0 18px rgba(255, 87, 34, 0.5);
    }

    .stTextInput>div>input, .stTextArea>div>textarea {
        background-color: rgba(60, 60, 60, 0.9); /* Dark gray for inputs */
        color: #e0e0e0;
        border-radius: 12px;
        padding: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTextInput>label, .stTextArea>label {
        color: var(--text-color);
        font-weight: 600;
        opacity: 0.8;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--hover-color);
    }

    /* Theme Toggle Button */
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }

    /* God-Level Background Animation */
    canvas {
        position: fixed;
        top: 0;
        left: 0;
        z-index: -1;
        width: 100%;
        height: 100%;
    }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script>
    // Advanced Eye-Friendly 3D Black Background
    function initGodLevelBackground() {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        renderer.domElement.style.position = 'fixed';
        renderer.domElement.style.top = '0';
        renderer.domElement.style.left = '0';
        renderer.domElement.style.zIndex = '-1';

        // Ethereal Black Gradient Background
        const gradientGeometry = new THREE.PlaneGeometry(200, 200);
        const gradientMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec2 vUv;
                uniform float time;
                uniform vec2 resolution;
                void main() {
                    vec2 uv = vUv * 2.0 - 1.0;
                    vec3 color = vec3(0.1, 0.1, 0.1); // Deep black base
                    float t = time * 0.04;
                    color += vec3(0.05, 0.1, 0.15) * (sin(uv.x * 2.0 + t) * 0.2 + 0.8);
                    color += vec3(0.1, 0.05, 0.15) * (cos(uv.y * 1.8 + t * 0.3) * 0.2 + 0.8);
                    color = mix(color, vec3(0.15, 0.15, 0.2), 0.5); // Blend with subtle dark blue
                    gl_FragColor = vec4(color, 0.5);
                }
            `,
            transparent: true
        });
        const gradient = new THREE.Mesh(gradientGeometry, gradientMaterial);
        scene.add(gradient);

        // Glowing Orbs with Enhanced Effects
        const orbs = new THREE.Group();
        const orbCount = 600;
        const orbGeometry = new THREE.SphereGeometry(0.06, 16, 16);
        const orbMaterial = new THREE.MeshBasicMaterial({ color: 0x00bcd4, transparent: true, opacity: 0.55 });

        for (let i = 0; i < orbCount; i++) {
            const orb = new THREE.Mesh(orbGeometry, orbMaterial);
            orb.position.set(
                (Math.random() - 0.5) * 140,
                (Math.random() - 0.5) * 140,
                (Math.random() - 0.5) * 140
            );
            orb.userData = { speed: Math.random() * 0.006 + 0.002, orbit: Math.random() * 5 + 2 };
            orbs.add(orb);
        }

        scene.add(orbs);
        camera.position.z = 50;

        function animate() {
            requestAnimationFrame(animate);
            gradientMaterial.uniforms.time.value += 0.007;
            orbs.children.forEach(orb => {
                orb.position.x = Math.sin(gradientMaterial.uniforms.time.value * orb.userData.speed) * orb.userData.orbit;
                orb.position.y = Math.cos(gradientMaterial.uniforms.time.value * orb.userData.speed) * orb.userData.orbit;
                orb.scale.setScalar(1.0 + 0.1 * Math.sin(gradientMaterial.uniforms.time.value * 0.8));
            });
            orbs.rotation.y += 0.0002;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            renderer.setSize(window.innerWidth, window.innerHeight);
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            gradientMaterial.uniforms.resolution.value.set(window.innerWidth, window.innerHeight);
        });
    }

    // Theme Toggle
    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        initGodLevelBackground();
    });
    </script>
""", unsafe_allow_html=True)

# Theme Toggle Button
st.markdown("""
    <div class='theme-toggle'>
        <button onclick="toggleTheme()" class="stButton">Change Theme</button>
    </div>
""", unsafe_allow_html=True)

# Simplified Main Title
st.markdown("""
    <h1 style='text-align:center; animation: fadeIn 1.5s ease-in-out;'>Easy GST Tool</h1>
    <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar with Navigation
with st.sidebar:
    st.markdown("<h3 style='color: var(--accent-color);'>Menu</h3>", unsafe_allow_html=True)
    page = st.radio(
        "Pick a Part",
        ["Home", "GST Check", "Chat"],
        label_visibility="collapsed",
        format_func=lambda x: f"📍 {x}"
    )

# Home Page
if page == "Home":
    st.markdown("<div class='block-style'>", unsafe_allow_html=True)
    st.markdown("""
        <h2>Your GST Helper</h2>
        <p style='color: var(--text-color);'>This tool helps you check GST numbers and read invoices easily with AI. Upload your invoice, check GST details, or ask our AI chat for help.</p>
        <p style='color: var(--text-color);'>What You Can Do:</p>
        <ul style='color: var(--text-color);'>
            <li>📄 Read Invoice Details</li>
            <li>✅ Check GST Numbers</li>
            <li>💬 Ask AI for Help</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# GST Verification Page
elif page == "GST Check":
    st.markdown("<div class='block-style'>", unsafe_allow_html=True)
    uploaded_file, upload_option = extract_invoice_data()
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file and upload_option:
       
        extracted_data, vendor_gstin, response1, customer_gstin, response2 = extract_invoice_data(uploaded_file, upload_option)
        all_data = load_all_data()
        all_data = save_all_data(all_data, extracted_data, uploaded_file.name)

        if vendor_gstin:
            gst_info = verify_gst(vendor_gstin)
            if gst_info:
                prompt = f"""
Generate a professional GST report from this JSON data:
{json.dumps(gst_info, indent=2)}

Guidelines:
- No markdown (no ###, **, etc.)
- Use numbered sections and bullet points
- Include: Business Name, PAN, GSTIN, Registration Type, Address, Jurisdiction, Filing Details
- Format cleanly for official reports
"""
                response = model.generate_content(prompt)

                st.markdown("<div class='block-style'>", unsafe_allow_html=True)
                st.subheader(" Seller GST Info")
                st.write(response1.text)
                st.subheader(" AI-Made Seller GST Report")
                st.download_button("📥 Get Report", response.text, file_name="Seller_GST_Report.txt")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(" Can't find seller GST info.")
        else:
            st.warning(" No seller GST number in invoice.")

        if customer_gstin:
            gst_info = customer_gst(customer_gstin)
            if gst_info:
                prompt = f"""
Generate a customer GST report using:
{json.dumps(gst_info, indent=2)}

Follow same structure and format as vendor GST report.
"""
                response = model.generate_content(prompt)

                st.markdown("<div class='block-style'>", unsafe_allow_html=True)
                st.subheader("📌 Buyer GST Info")
                st.write(response2.text)
                st.subheader("🧠 AI-Made Buyer GST Report")
                st.download_button("📥 Get Report", response.text, file_name="Buyer_GST_Report.txt")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ Can't find buyer GST info.")
        else:
            st.info("ℹ️ No buyer GST number available.")

# Chatbot Page
elif page == "Chat":
    st.markdown("<div class='block-style'>", unsafe_allow_html=True)
    st.subheader("💬 AI Chat")
    run_chatbot()
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: var(--text-color); opacity: 0.9;'>
        
      
    </div>
""", unsafe_allow_html=True)
