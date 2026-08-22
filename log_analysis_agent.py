import re


def analyze_log(text):

    result = {
        "exception": "Not Found",
        "error_message": "No error message detected",
        "failure_point": "Not Found",
        "class_name": "Unknown",
        "method_name": "Unknown",
        "line_number": "Unknown",
        "stack_trace": [],
        "severity": "Low",
        "root_cause": "Unknown runtime failure",
        "recommended_fix": "Review stack trace and debug failing module."
    }


    if not text:
        return result


    # Exception / Error detection
    match = re.search(
        r'([A-Za-z]+(?:Exception|Error))',
        text
    )

    if match:
        result["exception"] = match.group(1)
        result["severity"] = "High"
        # Additional exception patterns

    if "sql" in text.lower() or "database" in text.lower():
        result["exception"] = "SQLException"
        result["severity"] = "High"

    elif "sockettimeoutexception" in text.lower():
        result["exception"] = "SocketTimeoutException"
        result["severity"] = "High"


    # Error line
    for line in text.splitlines():

        if (
            "error" in line.lower()
            or "exception" in line.lower()
            or "failed" in line.lower()
        ):

            result["error_message"] = line.strip()
            break



    # Java stack trace
    java_trace = re.findall(
        r'at\s+(.+?)\((.+?\.java):(\d+)\)',
        text
    )


    for trace in java_trace:

        result["stack_trace"].append(
            f"at {trace[0]}({trace[1]}:{trace[2]})"
        )


    if java_trace:

        first = java_trace[0]

        result["failure_point"] = (
            f"{first[1]} Line {first[2]}"
        )

        result["line_number"] = first[2]


        parts = first[0].split(".")


        if len(parts) >= 2:

            result["class_name"] = parts[-2]
            result["method_name"] = parts[-1]



    # Python traceback support
    python_trace = re.findall(
        r'File "(.+?)", line (\d+), in (.+)',
        text
    )


    for trace in python_trace:

        result["stack_trace"].append(
            f"{trace[0]} Line {trace[1]} Method {trace[2]}"
        )


    if python_trace and result["failure_point"] == "Not Found":

        result["failure_point"] = (
            f"{python_trace[0][0]} Line {python_trace[0][1]}"
        )



    # Root cause
    if result["exception"] == "NullPointerException":

        result["root_cause"] = "Object reference is null"

        result["recommended_fix"] = (
            "Add null checks before accessing object"
        )


    elif result["exception"] != "Not Found":

        result["root_cause"] = (
            "Runtime exception detected"
        )

        result["recommended_fix"] = (
            "Fix exception and validate input"
        )


    # If stack trace empty, show error lines
    if len(result["stack_trace"]) == 0:

        for line in text.splitlines():

            if "error" in line.lower():

                result["stack_trace"].append(line)



    return result
