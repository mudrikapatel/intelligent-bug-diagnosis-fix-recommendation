from triage_agent import analyze_triage
from log_analysis_agent import analyze_log


# Test Dataset
TEST_CASES = [

    {
        "bug": """
        Application crashes when user clicks login button.
        Exception: NullPointerException
        at LoginService.java:45
        """,
        "expected_severity": "Critical",
        "expected_exception": "NullPointerException"
    },

    {
        "bug": """
        Database connection failed.
        SQL Exception occurred.
        at DatabaseManager.java:78
        """,
        "expected_severity": "High",
        "expected_exception": "SQLException"
    },

    {
        "bug": """
        API request timeout after 30 seconds.
        Exception: SocketTimeoutException
        at HttpClient.java:56
        """,
        "expected_severity": "Medium",
        "expected_exception": "SocketTimeoutException"
    },


    {
        "bug": """
        UI alignment issue in dashboard page.
        Button is not visible.
        """,
        "expected_severity": "Low",
        "expected_exception": "Not Found"
    }
]


triage_correct = 0
log_correct = 0


total = len(TEST_CASES)


print("\n====== AI Bug Analyzer Validation ======\n")


for i, case in enumerate(TEST_CASES, start=1):

    print(f"Test Case {i}")

    bug = case["bug"]


    # Triage Agent
    triage_result = analyze_triage(bug)

    print("Triage Output:")
    print(triage_result)


    if triage_result["severity"] == case["expected_severity"]:
        triage_correct += 1


    # Log Agent
    log_result = analyze_log(bug)

    print("\nLog Output:")
    print(log_result)


    if log_result["exception"] == case["expected_exception"]:
        log_correct += 1


    print("----------------------------")



triage_accuracy = (triage_correct / total) * 100

log_accuracy = (log_correct / total) * 100



print("\n========= VALIDATION REPORT =========")

print(f"Total Bugs Tested : {total}")

print(f"Triage Accuracy : {triage_accuracy:.2f}%")

print(f"Log Analysis Accuracy : {log_accuracy:.2f}%")

print("====================================")
