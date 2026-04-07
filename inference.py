import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.baseline import get_action

# ─── Task definitions ────────────────────────────────────────────────────────

TASKS = [
    # EASY
    {
        "task_id": "E001",
        "difficulty": "easy",
        "state": {
            "sender": "promo@deals.com",
            "subject": "Flash Sale: 70% off today only!",
            "body": "Huge discounts on all items. Limited time offer!"
        },
        "expected_action": "archive",
        "reward_map": {"archive": 1.0, "reply": 0.2, "flag_urgent": 0.0, "schedule_meeting": 0.1, "request_info": 0.3}
    },
    {
        "task_id": "E002",
        "difficulty": "easy",
        "state": {
            "sender": "newsletter@techblog.com",
            "subject": "Weekly Tech Digest",
            "body": "Here are this week's top tech stories..."
        },
        "expected_action": "archive",
        "reward_map": {"archive": 1.0, "reply": 0.1, "flag_urgent": 0.0, "schedule_meeting": 0.0, "request_info": 0.2}
    },
    # MEDIUM
    {
        "task_id": "M001",
        "difficulty": "medium",
        "state": {
            "sender": "colleague@company.com",
            "subject": "Quick question about the project",
            "body": "Hey, do you have a moment to discuss the timeline for the new feature rollout?"
        },
        "expected_action": "reply",
        "reward_map": {"reply": 1.0, "schedule_meeting": 0.8, "archive": 0.0, "flag_urgent": 0.1, "request_info": 0.6}
    },
    {
        "task_id": "M002",
        "difficulty": "medium",
        "state": {
            "sender": "partner@business.com",
            "subject": "Partnership proposal",
            "body": "We'd love to explore a collaboration. Could we set up a meeting next week?"
        },
        "expected_action": "schedule_meeting",
        "reward_map": {"schedule_meeting": 1.0, "reply": 0.7, "archive": 0.0, "flag_urgent": 0.0, "request_info": 0.4}
    },
    {
        "task_id": "M003",
        "difficulty": "medium",
        "state": {
            "sender": "hr@company.com",
            "subject": "Performance review scheduling",
            "body": "It's time for your annual review. Please let me know your availability next week."
        },
        "expected_action": "schedule_meeting",
        "reward_map": {"schedule_meeting": 1.0, "reply": 0.6, "archive": 0.0, "flag_urgent": 0.2, "request_info": 0.3}
    },
    # HARD
    {
        "task_id": "H001",
        "difficulty": "hard",
        "state": {
            "sender": "ceo@company.com",
            "subject": "CRITICAL: System outage affecting production",
            "body": "Our main system is down. All customers are affected. I need an immediate status update and resolution plan NOW."
        },
        "expected_action": "flag_urgent",
        "reward_map": {"flag_urgent": 1.0, "reply": 0.6, "archive": 0.0, "schedule_meeting": 0.1, "request_info": 0.2}
    },
    {
        "task_id": "H002",
        "difficulty": "hard",
        "state": {
            "sender": "unknown@suspicious.net",
            "subject": "Your account",
            "body": "Click here."
        },
        "expected_action": "request_info",
        "reward_map": {"request_info": 1.0, "archive": 0.8, "reply": 0.2, "flag_urgent": 0.3, "schedule_meeting": 0.0}
    },
    {
        "task_id": "H003",
        "difficulty": "hard",
        "state": {
            "sender": "client@bigcorp.com",
            "subject": "Urgent: Contract deadline tomorrow",
            "body": "We need the signed contract by tomorrow morning or the deal is off. Please confirm receipt and next steps."
        },
        "expected_action": "flag_urgent",
        "reward_map": {"flag_urgent": 1.0, "reply": 0.7, "archive": 0.0, "schedule_meeting": 0.3, "request_info": 0.2}
    }
]

# ─── Evaluation ───────────────────────────────────────────────────────────────

def compute_reward(task: dict, action: dict) -> float:
    action_type = action.get("action_type", "reply")
    return task["reward_map"].get(action_type, 0.0)


def run_inference():
    print("\n" + "=" * 70)
    print("  AI EMAIL AGENT — INFERENCE EVALUATION")
    print("=" * 70)

    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Using fallback responses.\n")

    results = []
    col_w = [8, 12, 12, 8, 10]
    header = f"{'Task ID':<{col_w[0]}} {'Difficulty':<{col_w[1]}} {'Action':<{col_w[2]}} {'Score':>{col_w[3]}} {'Reward':>{col_w[4]}}"
    print(header)
    print("-" * 70)

    for task in TASKS:
        action = get_action(task["state"])
        reward = compute_reward(task, action)
        score = reward  # 0–1 range

        results.append({
            "task_id": task["task_id"],
            "difficulty": task["difficulty"],
            "action": action.get("action_type", "unknown"),
            "expected": task["expected_action"],
            "score": score,
            "reward": reward
        })

        match = "✓" if action.get("action_type") == task["expected_action"] else "✗"
        row = (f"{task['task_id']:<{col_w[0]}} "
               f"{task['difficulty']:<{col_w[1]}} "
               f"{action.get('action_type', 'unknown'):<{col_w[2]}} "
               f"{score:>{col_w[3]}.2f} "
               f"{reward:>{col_w[4]}.2f}  {match}")
        print(row)

    print("-" * 70)

    # Summary stats
    total_reward = sum(r["reward"] for r in results)
    avg_grade = total_reward / len(results)

    by_difficulty = {}
    for r in results:
        d = r["difficulty"]
        by_difficulty.setdefault(d, []).append(r["reward"])

    print(f"\n{'SUMMARY':}")
    print(f"  Total Reward : {total_reward:.3f}")
    print(f"  Average Grade: {avg_grade:.3f} / 1.000")
    print(f"  Tasks Run    : {len(results)}")
    print()

    for diff, scores in sorted(by_difficulty.items()):
        avg = sum(scores) / len(scores)
        print(f"  {diff.capitalize():8} avg: {avg:.3f}  ({len(scores)} tasks)")

    print("\n" + "=" * 70 + "\n")

    return {
        "results": results,
        "total_reward": total_reward,
        "average_grade": avg_grade
    }


if __name__ == "__main__":
    run_inference()
