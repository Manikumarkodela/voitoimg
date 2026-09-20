# VoiToImg — Voice & Text Photorealistic Generator & Global Internet Image Search

**VoiToImg** is a state-of-the-art web application and REST API that combines **AI Photorealistic Image Generation** (powered by Google Gemini 2.0 Flash & Google Imagen 3) with **Global Internet Image Search & Aggregation** (searching millions of web domains across the total open internet without closed API restrictions).

---

## 🌟 Key Features

- 🔮 **Gemini Capsule Search Bar & Inline Mode Dropdown**:
  - Centered Gemini capsule input bar with JetBrains Mono brand typography.
  - Dedicated inline **Mode Dropdown Menu** (`Imagen 3`, `Web Search`, `Dual Engine`) anchored directly under the mode badge.
  - Quick **`+` Tools Popover** for Reference Photo Upload, Aspect Ratio (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`), and Style Presets (`Real Photo`, `Cinematic`, `Studio Portrait`, `Cyberpunk`, `Anime`).

- 🌐 **Total Internet Web Image Aggregator**:
  - Searches real photographs and media across **billions of indexed web pages** on the open internet (news sites, blogs, wallpaper archives, photography platforms, and public domain repositories).
  - Eliminates "walled-garden" API restrictions (unlike closed APIs like Pinterest).
  - Clean card UI with domain badges (`Web Image`, clean hostnames), completely free of raw search engine indices.

- 🎙️ **Voice & Natural Language Interface**:
  - Interactive speech recognition (Web Speech API) with real-time canvas audio visualizer.

- ⚡ **Google Gemini 2.0 Flash Optimization**:
  - **AI Prompt Enhancer**: Transforms simple voice ideas into rich photorealistic generation prompts with realistic lighting, lens choices, and atmosphere.
  - **Search Query Optimizer**: Converts conversational voice queries into high-precision, keyword-dense web search engine terms.

- 🎨 **Google Imagen 3 Engine**:
  - Generates 8K high-resolution photorealistic imagery using `imagen-3.0-generate-002`.

- ⚡ **Tri-Mode UI Console**:
  - **🎨 AI Gen (Imagen 3)**: Synthesize brand-new AI photorealistic artwork.
  - **🌐 Total Internet Search**: Search real photos across the open web.
  - **⚡ Dual Engine**: Execute both real web search and AI image generation simultaneously!

---

## 🏗️ System Architecture

```
                               ┌─────────────────────────────┐
                               │  User Voice / Text Input    │
                               └──────────────┬──────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
        [ Mode: AI Generation ]                     [ Mode: Total Internet Search ]
                       │                                             │
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │   Google Gemini 2.0 Flash   │               │   Google Gemini 2.0 Flash   │
        │   (AI Prompt Optimizer)     │               │   (Search Query Optimizer)  │
        └──────────────┬──────────────┘               └──────────────┬──────────────┘
                       │                                             │
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │    Google Imagen 3 API      │               │ Multi-Engine Web Aggregator │
        │ (imagen-3.0-generate-002)   │               │ (DDG Web, Wikimedia, etc.)  │
        └──────────────┬──────────────┘               └──────────────┬──────────────┘
                       │                                             │
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │  Generated 8K AI Photograph │               │ Real Open Web Image Cards   │
        └─────────────────────────────┘               └─────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.10+, FastAPI, Uvicorn
- **AI Models & LLMs:** Google Gemini 2.0 Flash (`gemini-2.0-flash`), Google Imagen 3 (`imagen-3.0-generate-002`)
- **Web Search Engine Aggregator:** `ddgs`, `beautifulsoup4`, `requests`, Wikimedia Commons Web API
- **SDK:** `google-genai` (Official Google GenAI SDK)
- **Frontend Target:** Glassmorphic HTML5, Vanilla CSS3, JavaScript (ES6+), Web Speech API, HTML5 Canvas Visualizer

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key (Get a free key from [Google AI Studio](https://aistudio.google.com/))

### 2. Setup Virtual Environment
```bash
# Navigate to project directory
cd voitoimg

# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or update `.env` in the root directory:
```env
HOST=127.0.0.1
PORT=8000
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key_here
IMAGE_API_PROVIDER=gemini
```

### 5. Start Backend Server
```bash
python backend/main.py
```

- **Web Application:** `http://127.0.0.1:8000`
- **Interactive API Docs (Swagger):** `http://127.0.0.1:8000/docs`  
- **Health Check Endpoint:** `http://127.0.0.1:8000/api/health`

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/search-internet-images` | `POST` | Searches the total open internet for real web images matching the query. |
| `/api/generate` | `POST` | Generates a photorealistic AI image via Google Imagen 3 / Pollinations. |
| `/api/enhance-prompt` | `POST` | Enhances simple text into a detailed photorealistic AI prompt using Gemini. |
| `/api/health` | `GET` | Health check and system status. |

---

## 📁 Project Structure

```
voitoimg/
├── main.py                          # Main root launcher
├── requirements.txt                 # Python dependencies (google-genai, fastapi, ddgs, bs4, etc.)
├── tasks.md                         # Project development task tracking
├── README.md                        # Primary project documentation
├── INTERNET_IMAGE_SEARCH_GUIDE.md   # Architectural deep-dive for Total Internet Search
├── .env.example                     # Environment template
├── .env                             # Local configuration & GEMINI_API_KEY
├── backend/
│   ├── main.py                      # FastAPI API routes & static server
│   ├── prompt_optimizer.py          # Gemini 2.0 Flash Prompt & Search Query Optimizer
│   ├── image_generator.py           # Google Imagen 3 & Pollinations Engine
│   └── internet_image_search.py     # Multi-Engine Global Internet Image Aggregator
└── frontend/
    ├── index.html                   # Glassmorphic UI layout & mode controls
    ├── css/
    │   └── styles.css               # Obsidian glassmorphic styling system
    └── js/
        ├── app.js                   # Application state, mode dispatcher & API handlers
        ├── voice_agent.js           # Web Speech API voice assistant module
        └── visualizer.js            # HTML5 Canvas live audio waveform renderer
```
