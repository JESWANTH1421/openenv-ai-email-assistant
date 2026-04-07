import os
import sys
import json
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent.baseline import get_action

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Email & Calendar Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background: #0f1117; }

/* Email card */
.email-card {
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}
.email-card:hover { border-color: #4f6ef7; background: #1e2130; }
.email-card.urgent { border-left: 3px solid #ff4b4b; }
.email-card.selected { border-color: #4f6ef7; background: #1e2235; }

.email-sender { font-size: 13px; font-weight: 600; color: #e0e6ff; }
.email-subject { font-size: 12px; color: #a0aec0; margin-top: 2px; }
.email-preview { font-size: 11px; color: #6b7280; margin-top: 4px; }

.badge-urgent {
    display: inline-block; padding: 2px 8px;
    background: #ff4b4b22; color: #ff4b4b;
    border: 1px solid #ff4b4b44; border-radius: 20px;
    font-size: 10px; font-weight: 600; margin-left: 6px;
}
.badge-normal {
    display: inline-block; padding: 2px 8px;
    background: #22c55e22; color: #22c55e;
    border: 1px solid #22c55e44; border-radius: 20px;
    font-size: 10px; font-weight: 600; margin-left: 6px;
}

/* Email viewer */
.email-viewer {
    background: #1a1d27; border: 1px solid #2a2d3a;
    border-radius: 12px; padding: 24px;
}
.email-header { border-bottom: 1px solid #2a2d3a; padding-bottom: 16px; margin-bottom: 16px; }
.email-from { font-size: 12px; color: #6b7280; }
.email-subject-big { font-size: 18px; font-weight: 600; color: #e0e6ff; }
.email-body { font-size: 14px; color: #a0aec0; line-height: 1.7; }

/* AI Action card */
.action-card {
    background: #1e2235; border: 1px solid #4f6ef755;
    border-radius: 10px; padding: 16px; margin-top: 12px;
}
.action-type {
    display: inline-block; padding: 4px 12px;
    background: #4f6ef722; color: #4f6ef7;
    border: 1px solid #4f6ef744; border-radius: 20px;
    font-size: 12px; font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* Draft email */
.draft-box {
    background: #12151f; border: 1px solid #2a2d3a;
    border-radius: 10px; padding: 20px;
    font-family: 'DM Mono', monospace; font-size: 13px;
    color: #a0aec0; line-height: 1.6;
}
.draft-header { color: #4f6ef7; font-weight: 500; margin-bottom: 8px; }

/* Calendar */
.cal-slot {
    display: inline-block; width: 100%;
    padding: 8px 12px; margin: 3px 0;
    border-radius: 8px; font-size: 13px;
    font-family: 'DM Mono', monospace;
}
.cal-free { background: #22c55e1a; border: 1px solid #22c55e33; color: #22c55e; }
.cal-busy { background: #ff4b4b1a; border: 1px solid #ff4b4b33; color: #ff4b4b; }
.cal-proposed { background: #4f6ef722; border: 2px solid #4f6ef7; color: #4f6ef7; font-weight: 600; }
.cal-conflict { background: #f59e0b1a; border: 2px solid #f59e0b; color: #f59e0b; font-weight: 600; }

/* Reward */
.reward-box {
    background: #22c55e11; border: 1px solid #22c55e33;
    border-radius: 10px; padding: 16px; margin-top: 12px;
    text-align: center;
}
.reward-value { font-size: 32px; font-weight: 700; color: #22c55e; }
.reward-label { font-size: 12px; color: #6b7280; margin-top: 4px; }

/* Section header */
.section-header {
    font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: #4f6ef7; margin-bottom: 12px;
}

/* Sidebar stats */
.stat-box {
    background: #1a1d27; border: 1px solid #2a2d3a;
    border-radius: 10px; padding: 14px; margin-bottom: 8px;
}
.stat-label { font-size: 11px; color: #6b7280; }
.stat-value { font-size: 24px; font-weight: 600; color: #e0e6ff; }
.stat-delta { font-size: 12px; color: #22c55e; }

/* Workflow steps */
.step {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #2a2d3a1a;
    font-size: 13px; color: #a0aec0;
}
.step-num {
    width: 24px; height: 24px; border-radius: 50%;
    background: #4f6ef722; border: 1px solid #4f6ef744;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; color: #4f6ef7; font-weight: 600; flex-shrink: 0;
}
.step.active .step-num { background: #4f6ef7; color: white; }
.step.active { color: #e0e6ff; }
</style>
""", unsafe_allow_html=True)

# ─── Sample emails ────────────────────────────────────────────────────────────
EMAILS = [
    {
        "id": 1,
        "sender": "ceo@mycompany.com",
        "subject": "URGENT: Investor deck needed by EOD",
        "body": "We have an emergency board meeting at 5 PM. I need the Q3 investor presentation finalized and sent to all board members by 4 PM today. This is critical — the funding round depends on it.",
        "priority": "urgent",
        "time": "10:42 AM"
    },
    {
        "id": 2,
        "sender": "sarah.chen@partnercorp.com",
        "subject": "Can we schedule a strategy sync?",
        "body": "Hi! Hope you're well. I'd love to connect and discuss our partnership roadmap for Q4. Would you have 45 minutes sometime next week? Tuesday or Thursday afternoon works best for me.",
        "priority": "normal",
        "time": "9:15 AM"
    },
    {
        "id": 3,
        "sender": "deals@shopexpress.com",
        "subject": "🔥 Black Friday in July — Up to 80% off!",
        "body": "Don't miss the biggest sale of the year! Thousands of products at unbelievable prices. Shop now before stocks run out! Use code JULY80 at checkout.",
        "priority": "normal",
        "time": "8:03 AM"
    },
    {
        "id": 4,
        "sender": "dev@github.com",
        "subject": "New pull request review requested",
        "body": "A pull request was opened in your repository requiring your review. Please check the changes and provide feedback when you get a chance.",
        "priority": "normal",
        "time": "Yesterday"
    },
    {
        "id": 5,
        "sender": "x7z@unknownsource.net",
        "subject": "Re:",
        "body": "Please review the attached.",
        "priority": "normal",
        "time": "Yesterday"
    }
]

# ─── Session state ────────────────────────────────────────────────────────────
if "selected_email_id" not in st.session_state:
    st.session_state.selected_email_id = None
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "calendar_busy" not in st.session_state:
    st.session_state.calendar_busy = {
        "10:00 AM": True,
        "11:00 AM": True,
        "02:00 PM": True
    }
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = 0
if "scheduled_meetings" not in st.session_state:
    st.session_state.scheduled_meetings = {}

# ─── Time slots ──────────────────────────────────────────────────────────────
TIME_SLOTS = [
    "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
    "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM",
    "05:00 PM", "06:00 PM"
]

def parse_proposed_time(proposed_time_str: str) -> str:
    """Convert ISO datetime to slot string."""
    if not proposed_time_str:
        return ""
    try:
        dt = datetime.fromisoformat(proposed_time_str)
        hour = dt.hour
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour:02d}:00 {am_pm}"
    except Exception:
        return ""

def get_reward_for_action(action_type: str, email: dict) -> tuple[float, str]:
    """Return (reward, reason) for an action on an email."""
    priority = email.get("priority", "normal")
    subject_lower = email.get("subject", "").lower()
    body_lower = email.get("body", "").lower()

    is_spam = any(w in subject_lower + body_lower for w in ["sale", "off!", "discount", "shop", "deal"])
    is_meeting = any(w in subject_lower + body_lower for w in ["schedule", "meeting", "sync", "call", "available"])
    is_urgent = priority == "urgent" or "urgent" in subject_lower

    reward_map = {
        "flag_urgent": 1.0 if is_urgent else 0.1,
        "schedule_meeting": 1.0 if is_meeting else 0.3,
        "reply": 0.8 if not is_spam else 0.1,
        "archive": 1.0 if is_spam else 0.2,
        "request_info": 0.6
    }
    reasons = {
        "flag_urgent": "Correctly identified as high-priority urgent email" if is_urgent else "Unnecessary urgency flag applied",
        "schedule_meeting": "Meeting request handled efficiently" if is_meeting else "Scheduling applied to non-meeting email",
        "reply": "Professional response drafted" if not is_spam else "Replied to spam (not ideal)",
        "archive": "Spam filtered correctly" if is_spam else "Important email archived (check manually)",
        "request_info": "Requested clarification on ambiguous email"
    }
    reward = reward_map.get(action_type, 0.5)
    reason = reasons.get(action_type, "Action taken")
    return reward, reason

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Performance Dashboard")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="stat-box">
            <div class="stat-label">V1 Score</div>
            <div class="stat-value">0.871</div>
            <div class="stat-delta">Baseline</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="stat-box">
            <div class="stat-label">V2 Score</div>
            <div class="stat-value">0.980</div>
            <div class="stat-delta">+0.109 ↑</div>
        </div>""", unsafe_allow_html=True)

    # Line chart
    st.markdown("**Score Trend**")
    chart_data = pd.DataFrame({
        "Version": ["V1 Baseline", "V1.5", "V2 Improved"],
        "Score": [0.871, 0.934, 0.980]
    }).set_index("Version")
    st.line_chart(chart_data, color="#4f6ef7")

    # Bar chart per task type
    st.markdown("**Improvement by Type**")
    bar_data = pd.DataFrame({
        "Task": ["Urgent", "Meeting", "Spam", "Ambiguous"],
        "V1": [0.82, 0.91, 0.95, 0.73],
        "V2": [0.96, 0.99, 0.98, 0.94]
    }).set_index("Task")
    st.bar_chart(bar_data)

    st.markdown("---")
    st.markdown("### 🧠 Agent Workflow")
    steps = [
        ("📨", "Email received"),
        ("🔍", "Intent detection"),
        ("⚡", "Action selection"),
        ("✍️", "Response generation"),
        ("🎯", "Reward assignment")
    ]
    wf_step = st.session_state.workflow_step
    for i, (icon, label) in enumerate(steps):
        active = "active" if i < wf_step else ""
        st.markdown(f"""<div class="step {active}">
            <div class="step-num">{i+1}</div>
            {icon} {label}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEY not set. Add it in Settings > Secrets.")
    else:
        st.success("✅ API key configured")

# ─── Main layout ──────────────────────────────────────────────────────────────
st.markdown("## 📧 AI Email & Calendar Assistant")

left_col, right_col = st.columns([1, 2], gap="medium")

# ─── LEFT: Inbox ──────────────────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="section-header">📬 Inbox</div>', unsafe_allow_html=True)

    for email in EMAILS:
        is_urgent = email["priority"] == "urgent"
        is_selected = st.session_state.selected_email_id == email["id"]

        badge = '<span class="badge-urgent">URGENT</span>' if is_urgent else '<span class="badge-normal">normal</span>'
        card_class = "email-card urgent" if is_urgent else "email-card"
        card_class += " selected" if is_selected else ""
        preview = email["body"][:60] + "..."

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span class="email-sender">{email['sender']}</span>
                {badge}
            </div>
            <div class="email-subject">{email['subject']}</div>
            <div class="email-preview">{preview}</div>
            <div style="font-size:10px;color:#4b5563;margin-top:4px;">{email['time']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Open", key=f"open_{email['id']}", use_container_width=True):
            st.session_state.selected_email_id = email["id"]
            st.session_state.ai_result = None
            st.session_state.workflow_step = 1
            st.rerun()

# ─── RIGHT: Viewer + AI ───────────────────────────────────────────────────────
with right_col:
    if st.session_state.selected_email_id is None:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;color:#4b5563;">
            <div style="font-size:48px;margin-bottom:16px;">📬</div>
            <div style="font-size:16px;">Select an email from the inbox to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        email = next((e for e in EMAILS if e["id"] == st.session_state.selected_email_id), None)
        if not email:
            st.error("Email not found.")
        else:
            # Email viewer
            is_urgent = email["priority"] == "urgent"
            urgent_style = "border-left: 3px solid #ff4b4b;" if is_urgent else ""

            st.markdown(f"""
            <div class="email-viewer" style="{urgent_style}">
                <div class="email-header">
                    <div class="email-from">From: <strong style="color:#a0aec0">{email['sender']}</strong></div>
                    <div class="email-subject-big">{email['subject']}</div>
                </div>
                <div class="email-body">{email['body']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # AI Panel
            st.markdown('<div class="section-header">🤖 AI Agent</div>', unsafe_allow_html=True)

            if st.button("▶  Run AI Assistant", type="primary", use_container_width=True):
                with st.spinner("Analyzing email..."):
                    st.session_state.workflow_step = 2
                    result = get_action({
                        "sender": email["sender"],
                        "subject": email["subject"],
                        "body": email["body"],
                        "priority": email["priority"]
                    })
                    st.session_state.ai_result = result
                    st.session_state.workflow_step = 5

                    # Handle scheduling
                    action_type = result.get("action_type", "")
                    proposed_time = result.get("proposed_time", "")
                    if action_type == "schedule_meeting" and proposed_time:
                        slot = parse_proposed_time(proposed_time)
                        if slot:
                            st.session_state.scheduled_meetings[email["id"]] = slot
                st.rerun()

            result = st.session_state.ai_result

            if result:
                action_type = result.get("action_type", "unknown")
                content = result.get("content", "")
                proposed_time = result.get("proposed_time", "")

                # Action type badge
                st.markdown(f"""
                <div class="action-card">
                    <div style="margin-bottom:8px;">
                        <span style="font-size:12px;color:#6b7280;">Action: </span>
                        <span class="action-type">{action_type}</span>
                    </div>
                    <div style="font-size:13px;color:#a0aec0;">{content}</div>
                    {"<div style='font-size:12px;color:#4f6ef7;margin-top:8px;'>⏰ Proposed: " + proposed_time + "</div>" if proposed_time else ""}
                </div>
                """, unsafe_allow_html=True)

                # Drafted reply
                if action_type in ("reply", "flag_urgent", "schedule_meeting", "request_info"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-header">✉️ Drafted Reply</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="draft-box">
                        <div class="draft-header">Subject: Re: {email['subject']}</div>
                        <div style="color:#6b7280;font-size:11px;margin-bottom:12px;">To: {email['sender']}</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Calendar
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">📅 Calendar — Today</div>', unsafe_allow_html=True)

                proposed_slot = ""
                if action_type == "schedule_meeting" and proposed_time:
                    proposed_slot = parse_proposed_time(proposed_time)

                # Check for scheduled meeting for this email
                scheduled_slot = st.session_state.scheduled_meetings.get(email["id"], "")

                conflict = False
                if proposed_slot and st.session_state.calendar_busy.get(proposed_slot):
                    conflict = True

                cal_col1, cal_col2 = st.columns(2)
                slots_per_col = len(TIME_SLOTS) // 2

                for idx, slot in enumerate(TIME_SLOTS):
                    col = cal_col1 if idx < slots_per_col else cal_col2

                    with col:
                        is_busy = st.session_state.calendar_busy.get(slot, False)
                        is_proposed = slot == proposed_slot
                        is_scheduled = slot == scheduled_slot

                        if is_scheduled and not conflict:
                            cls = "cal-proposed"
                            label = f"📅 {slot} — MEETING"
                        elif is_proposed and conflict:
                            cls = "cal-conflict"
                            label = f"⚠️ {slot} — CONFLICT"
                        elif is_busy:
                            cls = "cal-busy"
                            label = f"🔴 {slot} — BUSY"
                        else:
                            cls = "cal-free"
                            label = f"🟢 {slot} — FREE"

                        st.markdown(f'<div class="cal-slot {cls}">{label}</div>', unsafe_allow_html=True)

                if scheduled_slot and not conflict:
                    st.success(f"✅ Meeting scheduled at {scheduled_slot}")
                    # Mark as busy
                    st.session_state.calendar_busy[scheduled_slot] = True
                elif conflict:
                    st.warning(f"⚠️ Time slot {proposed_slot} is already booked! Please select another time.")

                    alt_slots = [s for s in TIME_SLOTS if not st.session_state.calendar_busy.get(s)]
                    if alt_slots:
                        if st.button(f"📅 Schedule at {alt_slots[0]} instead"):
                            st.session_state.scheduled_meetings[email["id"]] = alt_slots[0]
                            st.session_state.calendar_busy[alt_slots[0]] = True
                            st.rerun()

                # Reward display
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">🎯 Reward</div>', unsafe_allow_html=True)
                reward, reason = get_reward_for_action(action_type, email)

                reward_color = "#22c55e" if reward >= 0.7 else "#f59e0b" if reward >= 0.4 else "#ff4b4b"
                st.markdown(f"""
                <div class="reward-box" style="border-color: {reward_color}33; background: {reward_color}11;">
                    <div class="reward-value" style="color:{reward_color};">{reward:.2f}</div>
                    <div class="reward-label">{reason}</div>
                </div>
                """, unsafe_allow_html=True)
