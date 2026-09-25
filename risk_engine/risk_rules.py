RISK_POINTS = {
    "high_amount": 25,
    "high_frequency": 20,
    "rapid_transactions": 20,
    "shared_device": 20,
    "shared_ip": 15,
    "suspicious_beneficiary": 25
}


def calculate_risk_score(features):
    score = 0

    for feature in features:
        if feature in RISK_POINTS:
            score += RISK_POINTS[feature]

    return score


def classify_risk(score):
    if score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"