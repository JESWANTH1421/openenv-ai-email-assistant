# 🚀 OpenEnv Hybrid AI Email & Calendar Assistant

An intelligent, real-world reinforcement learning environment where an AI agent autonomously manages emails — classifying, replying, scheduling meetings, and prioritizing tasks — with a robust hybrid architecture (LLM + fallback intelligence).

---

## 🌟 Overview

This project simulates a **real-world productivity workflow** where an AI agent:

* 📬 Reads incoming emails
* 🧠 Understands intent using AI
* ⚡ Takes actions (reply, schedule, archive, flag urgent)
* 📅 Manages a dynamic calendar
* 📊 Learns and improves via reward-based evaluation

Built following the **OpenEnv standard**, this environment is designed for training and evaluating intelligent agents in practical scenarios.

---

## 🎯 Key Features

### 🤖 Hybrid AI Agent

* Uses **OpenAI GPT (gpt-4o-mini)** for intelligent reasoning
* Falls back to **rule-based logic** if API fails
* Ensures **100% reliability during demos**

---

### 📬 Gmail-Style UI (Streamlit)

* Interactive inbox with email previews
* Urgent email highlighting
* One-click AI execution

---

### ✉️ Smart Email Actions

Agent can:

* Reply to emails
* Schedule meetings
* Flag urgent messages
* Archive spam
* Request more information

---

### 📅 Calendar Integration

* Visual time slots (FREE / BUSY)
* Auto scheduling of meetings
* Conflict detection and handling

---

### 📊 Performance Dashboard

* Task scores (Easy → Medium → Hard)
* Reward tracking
* Improvement visualization (V1 → V2)

---

### 🧠 OpenEnv Compliance

* `step()`, `reset()`, `state()` API structure
* Typed observation/action models
* Multi-task evaluation with graders

---

## 🏗️ Project Structure

```
openenv-hybrid-email-assistant/
│
├── app.py                  # Streamlit UI
├── requirements.txt
├── Dockerfile
├── README.md
│
├── agent/
│   ├── baseline.py         # Hybrid AI agent
│   ├── inference.py        # Evaluation script
│   └── __init__.py
│
├── .env                    # API key (not pushed)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/openenv-hybrid-email-assistant.git
cd openenv-hybrid-email-assistant
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add API Key (Optional but Recommended)

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

> ⚠️ If no API key is provided, the system will automatically switch to fallback mode.

---

## ▶️ Running the Application

### Run UI

```bash
streamlit run app.py
```

Open in browser:

```
http://localhost:8501
```

---

### Run Evaluation

```bash
python agent/inference.py
```

---

## 🧪 Tasks & Evaluation

The agent is evaluated across **3 difficulty levels**:

| Difficulty | Description                    |
| ---------- | ------------------------------ |
| Easy       | Clear intent emails            |
| Medium     | Ambiguous or multi-step emails |
| Hard       | Complex reasoning & scheduling |

---

## 📈 Results

| Version       | Score     |
| ------------- | --------- |
| V1 (Baseline) | 0.871     |
| V2 (Improved) | **0.980** |

✅ Significant improvement through:

* Better prompt engineering
* Hybrid fallback logic
* Robust error handling

---

## 🧠 How It Works

1. Email is received
2. Agent analyzes content
3. Chooses best action
4. Generates response
5. Updates calendar (if needed)
6. Receives reward based on correctness

---

## ☁️ Deployment (Hugging Face Spaces)

### Steps:

1. Create a new Space
2. Select **Docker**
3. Upload project files
4. Add secret:

```
OPENAI_API_KEY=your_key
```

---

## 🐳 Docker Support

Build and run:

```bash
docker build -t email-agent .
docker run -p 7860:7860 email-agent
```

---

## 🚨 Error Handling

* API failures → fallback agent
* Rate limits → retry + fallback
* Missing API key → offline mode

---

## 💡 Future Improvements

* Email threading support
* Voice assistant integration
* Multi-user simulation
* Advanced RL training loop

---

## 🏆 Why This Project Stands Out

* Real-world problem simulation
* Hybrid AI (robust + reliable)
* Full-stack system (Agent + UI + Deployment)
* OpenEnv compliance
* Strong evaluation metrics

---

## 👨‍💻 Author

Developed as part of an AI/ML hackathon project.

---

## 📜 License

MIT License
