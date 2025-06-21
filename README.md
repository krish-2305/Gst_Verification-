
# 🧾 GST AI Verifier & Chatbot

A powerful and intuitive **AI-powered Streamlit web app** to extract and verify GST details from PDF/image invoices, generate professional reports, and interact with your invoice data using an intelligent chatbot built on **LangChain + Gemini**.

---

## 🔍 Features

- 📤 Upload invoices (PDF/Image) and extract key details using **Gemini Vision**
- ✅ Verify **Seller and Buyer GSTIN** using real-time API lookup
- 🧠 Generate official-style GST reports with AI
- 💬 **Chatbot (RAG)** for question-answering over all processed invoices
- 🌌 Beautiful dark-themed UI with responsive design and animated 3D background

---

## 🛠️ Technologies Used

- **Streamlit** for web UI
- **Google Gemini (1.5 & 2.0 Flash)** for vision + text generation
- **LangChain** + **Chroma DB** for Retrieval Augmented Generation
- **RapidAPI** for GSTIN verification
- **pdf2image** + **Pillow** for PDF/Image conversion
- **dotenv** for secure API key management

---

## 🚀 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/gst-ai-verifier-chatbot.git
cd gst-ai-verifier-chatbot
```

### 2. Setup Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the root:

```ini
GOOGLE_API_KEY=your_google_api_key
RAPIDAPI_KEY=your_key
```

> Replace with your **Gemini API key** (from Google AI Studio).

---

### 4. Run the App

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
├── app.py                        # Main Streamlit App
├── .env                          # API keys (not committed)
├── requirements.txt              # Python dependencies
├── gst_verification/
│   ├── gst_extractor.py          # Invoice OCR + Gemini-based parsing
│   ├── gst_api.py                # GSTIN verification using RapidAPI
│   └── data_manager.py           # JSON storage and updates
├── rag_chatbot/
│   ├── rag_chain.py              # RAG chatbot logic
│   └── data_loader.py            # Load invoice JSONs into LangChain
├── Project/
│   └── all_invoices_data.json    # Extracted invoice data
└── database/
    └── vector_db/                # Persistent vector store for LangChain
```

---

## 🧠 RAG Chatbot

The chatbot loads all invoices stored in `all_invoices_data.json` and uses:

- **Gemini-2.0 Flash** (via LangChain) for responses
- **GoogleEmbeddings** + **Chroma** for context-aware answers

You can ask:
- “What’s the GSTIN of [vendor]?”
- “Which invoice has highest value?”
- “List all buyers with Tamil Nadu GST numbers.”

---

## ✅ GST Verification API

GST details are retrieved using:

```
https://gst-return-status.p.rapidapi.com/free/gstin/<GSTIN>
```

You can switch to another provider or mock API if needed.

---

## 🎨 UI Highlights

- Responsive layout with sidebar navigation
- Toggle between light/dark themes
- Real-time animated **Three.js** background
- Stylish buttons and card layout

---

## 📝 Future Improvements

- OCR fallback for low-quality scans
- Email/WhatsApp report delivery


## 👨‍💻 Developed by

**Krishnan**  
🛠️ Powered by Gemini + LangChain + Streamlit  
📧 [krishnanr2305@gmail.com] | 🌐 [www.linkedin.com/in/krish2305]
