import os
import json
import openai

client = None

SYSTEM_PROMPT = """You are an intelligent email assistant. Analyze emails and decide the best action.

Think step by step (internally):
1. What is the email about?
2. Is it urgent?
3. Does it require scheduling?
4. Does it need a reply?
5. Is it spam?

Few-shot examples:
- Email about urgent deadline → flag_urgent
- Email requesting a meeting → schedule_meeting
- Email asking a question → reply
- Promotional/spam email → archive
- Unclear intent → request_info

Always respond with STRICT JSON only, no markdown, no extra text:
{
  "action_type": "<flag_urgent|schedule_meeting|reply|archive|request_info>",
  "content": "<drafted reply or action description>",
  "proposed_time": "<ISO datetime or empty string>"
}"""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": json.dumps({
            "sender": "boss@company.com",
            "subject": "URGENT: Report due today",
            "body": "I need the Q3 report by 5 PM today, no exceptions."
        })
    },
    {
        "role": "assistant",
        "content": json.dumps({
            "action_type": "flag_urgent",
            "content": "This email has been flagged as urgent. The Q3 report is due by 5 PM today.",
            "proposed_time": ""
        })
    },
    {
        "role": "user",
        "content": json.dumps({
            "sender": "client@acme.com",
            "subject": "Can we schedule a call?",
            "body": "I'd like to discuss the project. Are you free tomorrow afternoon?"
        })
    },
    {
        "role": "assistant",
        "content": json.dumps({
            "action_type": "schedule_meeting",
            "content": "Hi, thank you for reaching out! I'd be happy to connect. I've scheduled a meeting for tomorrow afternoon. Looking forward to discussing the project with you.",
            "proposed_time": "2025-07-15T14:00:00"
        })
    },
    {
        "role": "user",
        "content": json.dumps({
            "sender": "promo@store.com",
            "subject": "50% OFF everything this weekend!",
            "body": "Don't miss our biggest sale of the year! Shop now for amazing deals."
        })
    },
    {
        "role": "assistant",
        "content": json.dumps({
            "action_type": "archive",
            "content": "Promotional email archived automatically.",
            "proposed_time": ""
        })
    }
]


def rule_based_logic(state: dict) -> dict:
    subject = state.get("subject", "").lower()
    body = state.get("body", "").lower()
    text = subject + " " + body

    if any(word in text for word in ["urgent", "asap", "immediately", "deadline"]):
        return {
            "action_type": "flag_urgent",
            "content": "This email has been marked as urgent. Please address it immediately.",
            "proposed_time": ""
        }

    elif any(word in text for word in ["meeting", "schedule", "call", "appointment"]):
        return {
            "action_type": "schedule_meeting",
            "content": "Hi, I’ve scheduled a meeting for tomorrow at 3 PM. Looking forward to it.",
            "proposed_time": "2025-07-15T15:00:00"
        }

    elif any(word in text for word in ["offer", "sale", "discount", "buy now", "limited time"]):
        return {
            "action_type": "archive",
            "content": "Promotional email archived automatically.",
            "proposed_time": ""
        }

    elif any(word in text for word in ["?", "can you", "please", "help"]):
        return {
            "action_type": "reply",
            "content": "Thank you for your email. I’ll review your request and get back to you shortly.",
            "proposed_time": ""
        }

    else:
        return {
            "action_type": "request_info",
            "content": "Could you please provide more details regarding your request?",
            "proposed_time": ""
        }


def get_action(state: dict) -> dict:
    fallback = {
        "action_type": "reply",
        "content": "Thank you for your email. I will get back to you shortly.",
        "proposed_time": ""
    }

    api_key = os.getenv("OPENAI_API_KEY")

    # 🚨 If no API key → use fallback logic
    if not api_key:
        return rule_based_logic(state)

    try:
        global client
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(FEW_SHOT_EXAMPLES)
        messages.append({
            "role": "user",
            "content": json.dumps({
                "sender": state.get("sender", ""),
                "subject": state.get("subject", ""),
                "body": state.get("body", "")
            })
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=400
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if exists
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)

        return result

    # 🔥 If ANY API failure → fallback to rule-based
    except Exception as e:
        print("⚠️ API failed, using fallback:", str(e))
        return rule_based_logic(state)

    except json.JSONDecodeError as e:
        fallback["content"] = f"[JSON parse error] {fallback['content']}"
        return fallback
    except openai.APIConnectionError:
        fallback["content"] = "[Connection error] " + fallback["content"]
        return fallback
    except openai.AuthenticationError:
        fallback["content"] = "[Invalid API key] " + fallback["content"]
        return fallback
    except openai.RateLimitError:
        fallback["content"] = "[Rate limit exceeded] " + fallback["content"]
        return fallback
    except Exception as e:
        fallback["content"] = f"[Error: {str(e)}] {fallback['content']}"
        return fallback
