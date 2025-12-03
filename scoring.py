# scoring.py
"""
Simple conversation scoring heuristics:
  - outcome_rating: heuristic number 0-100
  - confidence_score: based on assertive language (naive)
  - objection_score: how well objections are handled
Returns (scores_dict, tips_list)
"""

from typing import List, Dict
import textdistance

OBJECTIONS = [
    "i'm not interested", "send me an email", "we don’t have budget", "we already use another vendor",
    "not a priority", "no budget", "send info"
]

def score_conversation(conversation: List[Dict], scenario: str = ""):
    rep_turns = [t for t in conversation if t["speaker"] == "rep"]
    ai_turns = [t for t in conversation if t["speaker"] == "ai"]
    rep_text = " ".join([t["text"].lower() for t in rep_turns])
    ai_text = " ".join([t["text"].lower() for t in ai_turns])

    # Basic confidence heuristics: length, presence of action-oriented words
    action_words = ["schedule", "book", "demo", "try", "purchase", "sign", "agree", "next step"]
    action_count = sum(1 for w in action_words if w in rep_text)
    confidence_score = min(100, 20 + len(rep_text.split())*2 + action_count*10)

    # Objection detection: count objections and whether rep addresses them
    objection_count = sum(ai_text.count(o) for o in OBJECTIONS)
    handled_count = 0
    # naive: check if rep mentions keywords addressing objection (price, discount, benefit, ROI, timeline)
    remedy_words = ["price", "discount", "roi", "benefit", "save", "cost", "timeline", "implementation"]
    for t in rep_turns:
        if any(r in t["text"].lower() for r in remedy_words):
            handled_count += 1
    if objection_count == 0:
        objection_score = 100
    else:
        objection_score = max(0, int(100 * (handled_count / objection_count)))

    # script adherence: compare rep_text similarity to sample script (if dataset available)
    # Simple placeholder: if scenario appears in rep_text, increment
    scenario_match = 1 if scenario.lower().split()[0] in rep_text else 0
    outcome_rating = int((confidence_score*0.5 + objection_score*0.4 + scenario_match*10)/1.0)
    outcome_rating = min(100, outcome_rating)

    # Tips
    tips = []
    if confidence_score < 40:
        tips.append("Use more action-oriented phrases (e.g., 'Can we schedule a demo', 'Let's book 30 minutes').")
    if objection_score < 60:
        tips.append("Practice handling objections: acknowledge, probe, and present a concise value response (price/ROI).")
    if len(rep_text.split()) < 10:
        tips.append("Try to expand your responses with clear next steps and benefits.")

    scores = {
        "confidence_score": int(confidence_score),
        "objection_score": int(objection_score),
        "outcome_rating": int(outcome_rating)
    }
    return scores, tips
