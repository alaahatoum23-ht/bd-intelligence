import re

def analyze(text):

    score = 0
    insights = []

    # Contextual logic
    if "enterprise" in text or "b2b" in text:
        score += 20
        insights.append("B2B model")

    if "platform" in text or "software" in text:
        score += 15
        insights.append("Product company")

    if "clients" in text or "customers" in text:
        score += 10
        insights.append("Active market presence")

    if "expand" in text or "growth" in text:
        score += 20
        insights.append("Growth signals")

    if "hiring" in text:
        score += 10
        insights.append("Scaling team")

    if "partner" in text:
        score += 15
        insights.append("Partnership potential")

    score = min(score,100)

    # Decision
    if score > 70:
        priority = "HIGH"
        deal = "Strategic Partnership"
        contact = "Head of Partnerships"
    elif score > 40:
        priority = "MEDIUM"
        deal = "Pilot / Intro Deal"
        contact = "BD Manager"
    else:
        priority = "LOW"
        deal = "Low priority"
        contact = "N/A"

    return {
        "score": score,
        "priority": priority,
        "insights": insights,
        "deal": deal,
        "contact": contact
    }
