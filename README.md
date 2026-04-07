# 📧 AI Email & Calendar Assistant

An intelligent email and calendar management system powered by GPT-4o-mini.

## Features

- **📬 Gmail-style Inbox** — Priority badges, email preview, urgent highlighting
- **🤖 AI Agent** — Analyzes emails and recommends actions (reply, schedule, archive, flag urgent)
- **✉️ Draft Composer** — Auto-generates professional email replies
- **📅 Calendar UI** — Visual 9AM–6PM scheduler with conflict detection
- **📊 Performance Dashboard** — Score tracking and improvement visualization

## Project Structure

```
├── agent/
│   ├── baseline.py      # GPT-4o-mini agent with few-shot prompting
│   └── inference.py     # Evaluation script across easy/medium/hard tasks
├── app.py               # Streamlit UI
├── Dockerfile           # Hugging Face Spaces deployment
├── requirements.txt
└── README.md
```

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd ai-email-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key
export OPENAI_API_KEY=sk-...

# 4. Run the app
streamlit run app.py

# 5. (Optional) Run inference evaluation
python agent/inference.py
```

## 🚀 Hugging Face Spaces Deployment

### Step 1: Create a Hugging Face Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `ai-email-assistant` (or your choice)
   - **License**: MIT
   - **SDK**: Select **Docker**
4. Click **"Create Space"**

### Step 2: Upload Files

Upload all project files to your Space repository:

```bash
# Clone your new Space
git clone https://huggingface.co/spaces/<your-username>/ai-email-assistant
cd ai-email-assistant

# Copy project files
cp -r /path/to/project/* .

# Push
git add .
git commit -m "Initial deployment"
git push
```

Or use the **Files** tab in the Space UI to upload directly.

### Step 3: Add API Secret

1. Go to your Space → **Settings** tab
2. Scroll to **Repository secrets**
3. Click **"New secret"**
4. Name: `OPENAI_API_KEY`
5. Value: your OpenAI API key (starts with `sk-`)
6. Click **"Add secret"**

### Step 4: Deploy

The Space will automatically build and deploy using the Dockerfile. Watch the **Build logs** tab for progress. Once the build completes, your app is live!

## Agent Actions

| Action | Trigger | Reward |
|---|---|---|
| `flag_urgent` | High-priority / deadline emails | 1.0 |
| `schedule_meeting` | Meeting requests | 1.0 |
| `reply` | General inquiries | 0.8 |
| `archive` | Spam / promotional | 1.0 |
| `request_info` | Ambiguous emails | 0.6 |

## Performance Results

| Version | Score | Notes |
|---|---|---|
| V1 Baseline | 0.871 | Zero-shot prompting |
| V2 Improved | 0.980 | Few-shot + CoT reasoning |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key |

## License

MIT
