from triage_rules import COMPONENTS, EXCEPTIONS, IMPACT
def analyze_triage(text):

    text = text.lower()


    result = {
        "severity": "Low",
        "priority": "P3",
        "component": "General",
        "confidence": 70,
        "reasoning": "Minor application issue detected"
    }


    if any(x in text for x in [
        "exception",
        "error",
        "crash",
        "failed",
        "fatal"
    ]):

        result.update({

            "severity":"High",
            "priority":"P1",
            "component":"Backend",
            "confidence":92,
            "reasoning":
            "Runtime failure detected from error logs"

        })


    if "nullpointerexception" in text:

        result.update({

        "severity":"Critical",
            "priority":"P1",
            "component":"Application Logic",
            "confidence":98,
            "reasoning":
            "Null object access detected"

        })


    elif "sql" in text or "database" in text:

        result.update({

            "severity":"High",
            "priority":"P1",
            "component":"Database",
            "confidence":95,
            "reasoning":
            "Database failure detected"

        })


    elif "api" in text or "timeout" in text:

        result.update({

            "severity":"Medium",
            "priority":"P2",
            "component":"API",
            "confidence":90,
            "reasoning":
            "API communication issue detected"

        })


    return result
