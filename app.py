from flask import Flask
import streamlit as st
import requests
import os
import pandas as pd
import json
import io

from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000/analyze"
# ---------------------------------------------------------
# OPTIONAL PDF SUPPORT
# ---------------------------------------------------------

try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PdfReader = None
    PDF_AVAILABLE = False


# ---------------------------------------------------------
# PROJECT MODULES
# ---------------------------------------------------------

from defect_analytics import (
    analytics_dashboard,
    save_bug_analysis
)

from knowledge_base import (
    update_knowledge_base,
    get_knowledge_base_stats
)


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Intelligent Bug Diagnosis Platform | Group 1",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000/analyze"

# =========================================================
# SESSION STATE
# =========================================================

if "data" not in st.session_state:
    st.session_state.data = None

if "bug_text" not in st.session_state:
    st.session_state.bug_text = ""

if "analysis_filename" not in st.session_state:
    st.session_state.analysis_filename = "bug_analysis_report.json"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🐞 Group 1")

    st.caption(
        "Creation of Intelligent Bug Diagnosis Platform "
        "with Fix Recommendation Assistance"
    )

    page = st.radio(
        "Navigation",
        [
            "Bug Analyzer",
            "Defect Analytics"
        ]
    )

    st.divider()

    st.success("✔ Triage Agent")
    st.success("✔ Log Analysis Agent")
    st.success("✔ Root Cause Agent")
    st.success("✔ Duplicate Detection Agent")
    st.success("✔ Remediation Agent")
    st.success("✔ Knowledge Base Growth")

    st.divider()

    st.subheader("📊 System")

    st.write("Version : 4.0")
    st.write("Status : 🟢 Running")
    st.write("Project : Group 1")

    st.divider()

    st.info(
        f"Date : {datetime.now().strftime('%d %b %Y')}"
    )


# =========================================================
# DEFECT ANALYTICS PAGE
# =========================================================

if page == "Defect Analytics":

    analytics_dashboard()

    st.divider()

    st.subheader(
        "📚 Knowledge Base Statistics"
    )

    try:

        stats = get_knowledge_base_stats()

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Verified Bugs in Vector DB",
                stats.get(
                    "total_verified_bugs",
                    0
                )
            )

        with c2:

            st.write(
                "**Collection:**",
                stats.get(
                    "collection",
                    "Unknown"
                )
            )

    except Exception as e:

        st.warning(
            f"Knowledge Base unavailable: {e}"
        )

    st.stop()


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "🐞 Intelligent Bug Diagnosis Platform"
)

st.caption(
    "Creation of Intelligent Bug Diagnosis Platform "
    "with Fix Recommendation Assistance - Group 1"
)

st.info(
    """
### 🚀 AI Multi-Agent Workflow

📄 Bug Submission
⬇️
🎯 Triage Agent
⬇️
🔍 Log Analysis Agent
⬇️
📚 RAG Similarity Search
⬇️
🧠 Root Cause Detection
⬇️
🔎 Duplicate Detection
⬇️
🛠 Remediation Recommendation
⬇️
🌱 Knowledge Base Growth
⬇️
📊 Defect Pattern Analytics
"""
)

st.divider()


# =========================================================
# BUG INPUT
# =========================================================

st.header("📥 Bug Submission")

input_type = st.radio(
    "Choose Input Method",
    [
        "📄 Upload File",
        "📝 Paste Bug Report"
    ],
    horizontal=True
)

uploaded_file = None
current_bug_text = ""


# =========================================================
# FILE UPLOAD
# =========================================================

if input_type == "📄 Upload File":

    uploaded_file = st.file_uploader(
        "Upload Bug Report",
        type=[
            "txt",
            "log",
            "pdf"
        ],
        key="bug_file"
    )


# =========================================================
# PASTE TEXT
# =========================================================

else:

    current_bug_text = st.text_area(
        "Paste Bug Report",
        height=250,
        placeholder=(
            "Paste exception, stack trace, "
            "error message or complete bug description..."
        ),
        key="bug_text_input"
    )


# =========================================================
# ANALYZE BUTTON
# =========================================================

analyze = st.button(
    "🚀 Analyze Bug",
    use_container_width=True,
    type="primary"
)


# =========================================================
# ANALYSIS REQUEST
# =========================================================

if analyze:

    bug_text_for_analysis = ""

    # -----------------------------------------------------
    # FILE INPUT
    # -----------------------------------------------------

    if input_type == "📄 Upload File":

        if uploaded_file is None:

            st.warning(
                "⚠️ Please upload a bug report file."
            )

            st.stop()

        try:

            # ---------------- PDF ----------------

            if uploaded_file.type == "application/pdf":

                if not PDF_AVAILABLE:

                    st.error(
                        "❌ pypdf is not installed."
                    )

                    st.code(
                        "python -m pip install pypdf"
                    )

                    st.stop()

                reader = PdfReader(
                    io.BytesIO(
                        uploaded_file.getvalue()
                    )
                )

                pages = []

                for pdf_page in reader.pages:

                    pages.append(
                        pdf_page.extract_text() or ""
                    )

                bug_text_for_analysis = "\n".join(
                    pages
                )

            # ---------------- TXT / LOG ----------------

            else:

                bug_text_for_analysis = (
                    uploaded_file
                    .getvalue()
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                )

        except Exception as e:

            st.error(
                f"❌ Unable to read file: {e}"
            )

            st.stop()

    # -----------------------------------------------------
    # TEXT INPUT
    # -----------------------------------------------------

    else:

        bug_text_for_analysis = current_bug_text

    # -----------------------------------------------------
    # EMPTY CHECK
    # -----------------------------------------------------

    if not bug_text_for_analysis.strip():

        st.warning(
            "⚠️ Bug report is empty."
        )

        st.stop()

    # -----------------------------------------------------
    # SAVE ORIGINAL BUG TEXT
    # -----------------------------------------------------

    st.session_state.bug_text = (
        bug_text_for_analysis
    )

    st.success(
        f"✅ Bug report loaded "
        f"({len(bug_text_for_analysis)} characters)."
    )

    # =====================================================
    # CALL FASTAPI BACKEND
    # =====================================================

    with st.spinner(
        "🤖 Running AI Agents..."
    ):

        try:

            response = requests.post(

                BACKEND_URL,

                files={
                    "file": (
                        "bug_report.txt",
                        bug_text_for_analysis.encode(
                            "utf-8"
                        ),
                        "text/plain"
                    )
                },

                timeout=120
            )

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            if response.status_code == 200:

                result = response.json()

                st.session_state.data = result

                # ---------------------------------------------
                # SAVE ANALYTICS RECORD
                # ---------------------------------------------

                try:

                    analytics_record = dict(result)
                    analytics_record["created_at"] = datetime.now().isoformat()

                    save_bug_analysis(analytics_record)

                except Exception as analytics_error:

                    st.warning(
                        "Analytics record could not be saved: "
                        + str(analytics_error)
                    )

                st.success(
                    "✅ AI analysis completed successfully."
                )

            # -------------------------------------------------
            # BACKEND ERROR
            # -------------------------------------------------

            else:

                st.error(
                    f"❌ Backend Error: "
                    f"{response.status_code}"
                )

                st.code(
                    response.text
                )

                st.stop()

        # -----------------------------------------------------
        # CONNECTION ERROR
        # -----------------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(
                """
❌ Cannot connect to FastAPI backend.

Start backend using:

python -m uvicorn main:app --reload --port 8000
"""
            )

            st.stop()

        # -----------------------------------------------------
        # TIMEOUT
        # -----------------------------------------------------

        except requests.exceptions.Timeout:

            st.error(
                "❌ Backend request timed out."
            )

            st.stop()

        # -----------------------------------------------------
        # OTHER ERROR
        # -----------------------------------------------------

        except Exception as e:

            st.error(
                f"❌ Unexpected error: {e}"
            )

            st.stop()


# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.data is not None:

    data = st.session_state.data

    # =====================================================
    # TRIAGE AGENT
    # =====================================================

    st.header("🎯 Triage Agent")

    triage = data.get(
        "triage",
        {}
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🔥 Severity",
            triage.get(
                "severity",
                "Unknown"
            )
        )

    with c2:

        st.metric(
            "⚡ Priority",
            triage.get(
                "priority",
                "Unknown"
            )
        )

    with c3:

        st.metric(
            "🧩 Component",
            triage.get(
                "component",
                "Unknown"
            )
        )

    with c4:

        confidence = triage.get(
            "confidence",
            0
        )

        st.metric(
            "🎯 Confidence",
            f"{confidence}%"
        )

    st.divider()


    # =====================================================
    # LOG ANALYSIS
    # =====================================================

    st.header(
        "🔍 Log Analysis Agent"
    )

    log = data.get(
        "log_analysis",
        {}
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "⚠️ Exception"
        )

        st.write(
            log.get(
                "exception",
                "Unknown"
            )
        )

        st.subheader(
            "📍 Failure Point"
        )

        st.write(
            log.get(
                "failure_point",
                "Unknown"
            )
        )

    with col2:

        st.subheader(
            "🔥 Root Cause From Log"
        )

        st.write(
            log.get(
                "root_cause",
                "Unknown"
            )
        )

        st.subheader(
            "🛠 Suggested Fix"
        )

        st.write(
            log.get(
                "recommended_fix",
                "Unknown"
            )
        )

    st.divider()


    # =====================================================
    # ROOT CAUSE AGENT
    # =====================================================

    st.header(
        "🧠 Root Cause Analysis"
    )

    root = data.get(
        "root_cause",
        {}
    )

    r1, r2 = st.columns(2)

    with r1:

        st.write(
            "**Cause:**"
        )

        st.info(
            root.get(
                "cause",
                "Unknown"
            )
        )

        st.write(
            "**Confidence:**"
        )

        st.info(
            f"{root.get('confidence', 0)}%"
        )

    with r2:

        st.write(
            "**Evidence:**"
        )

        st.write(
            root.get(
                "evidence",
                "No evidence available"
            )
        )

        st.write(
            "**Reasoning:**"
        )

        st.write(
            root.get(
                "reasoning",
                "No reasoning available"
            )
        )

    st.divider()


    # =====================================================
    # DUPLICATE DETECTION
    # =====================================================

    st.header(
        "🔎 Duplicate Detection"
    )

    duplicates = data.get(
        "duplicates",
        []
    )

    if duplicates:

        for index, bug in enumerate(
            duplicates,
            start=1
        ):

            with st.expander(
                f"🔍 Matching Bug {index}"
            ):

                st.write(
                    f"**Bug ID:** "
                    f"{bug.get('bug_id', 'Unknown')}"
                )

                st.write(
                    f"**Title:** "
                    f"{bug.get('title', 'Unknown')}"
                )

                st.write(
                    f"**Similarity:** "
                    f"{bug.get('similarity', 0)}%"
                )

                st.write(
                    f"**Summary:** "
                    f"{bug.get('summary', 'No summary')}"
                )

                st.write(
                    f"**Root Cause:** "
                    f"{bug.get('root_cause', 'Unknown')}"
                )

                st.write(
                    f"**Historical Resolution:** "
                    f"{bug.get('resolution', 'Unknown')}"
                )

    else:

        st.info(
            "No duplicate bugs found."
        )

    st.divider()


    # =====================================================
    # REMEDIATION AGENT
    # =====================================================

    st.header(
        "🛠 Recommended Fix"
    )

    remediation = data.get(
        "remediation",
        {}
    )

    fixes = remediation.get(
        "recommended_fix",
        []
    )

    if isinstance(
        fixes,
        str
    ):

        fixes = [fixes]

    if fixes:

        for fix in fixes:

            st.success(
                f"✔ {fix}"
            )

    else:

        st.info(
            "No recommendation available."
        )

    st.divider()


    # =====================================================
    # RAG HISTORICAL BUGS
    # =====================================================

    st.header(
        "📚 RAG Historical Bugs"
    )

    similar = data.get(
        "similar_bugs",
        []
    )

    if similar:

        st.dataframe(
            pd.DataFrame(similar),
            use_container_width=True
        )

    else:

        st.info(
            "No similar historical bugs found."
        )

    st.divider()


    # =====================================================
    # KNOWLEDGE BASE GROWTH
    # =====================================================

    st.header(
        "🌱 Knowledge Base Growth Mechanism"
)
    st.info(
    """
    **Knowledge Base Growth Mechanism**

    The system stores verified, resolved bugs back into
    the vector database.

    These verified bugs become available for future:

    • RAG similarity search
    • Duplicate detection
    • Root cause analysis
    • Fix recommendations
    • Historical bug retrieval
    """
)
    st.write(
        "Resolved bugs with confirmed fixes are added back "
        "to the knowledge base, improving future "
        "recommendations."
)

    fix_verified = st.checkbox(
        "✅ I have verified that the recommended fix works",
        key="fix_verified"
    )

    if fix_verified:

        bug_id = st.text_input(
            "Bug ID",
            value=(
                "BUG-" +
                datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                )
            ),
            key="kb_bug_id"
        )

        resolution = st.text_area(
            "Confirmed Resolution",
            placeholder=(
                "Describe the actual fix that resolved "
                "the bug..."
            ),
            key="kb_resolution"
        )

        if st.button(
            "📚 Store Verified Bug",
            type="primary",
            key="store_verified_bug"
        ):

            if not bug_id.strip():

                st.warning(
                    "⚠️ Please enter a Bug ID."
                )

            elif not resolution.strip():

                st.warning(
                    "⚠️ Please enter the confirmed resolution."
                )

            else:

                # ---------------------------------------------
                # CREATE VERIFIED BUG
                # ---------------------------------------------

                kb_bug = {

                    "bug_id":
                        bug_id.strip(),

                    "title":
                        (
                            "Resolved "
                            + str(
                                triage.get(
                                    "component",
                                    "Bug"
                                )
                            )
                            + " Issue"
                        ),

                    "description":
                        st.session_state.get(
                            "bug_text",
                            ""
                        ),

                    "category":
                        triage.get(
                            "category",
                            "Unknown"
                        ),

                    "component":
                        triage.get(
                            "component",
                            "Unknown"
                        ),

                    "severity":
                        triage.get(
                            "severity",
                            "Unknown"
                        ),

                    "priority":
                        triage.get(
                            "priority",
                            "Unknown"
                        ),

                    "error_message":
                        log.get(
                            "exception",
                            ""
                        ),

                    "stack_trace":
                        log.get(
                            "stack_trace",
                            ""
                        ),

                    "failure_point":
                        log.get(
                            "failure_point",
                            ""
                        ),

                    "root_cause":
                        root.get(
                            "cause",
                            ""
                        ),

                    "root_cause_evidence":
                        root.get(
                            "evidence",
                            ""
                        ),

                    "resolution":
                        resolution.strip(),

                    "recommended_fix":
                        fixes,

                    "fix_verified":
                        True,

                    "verification_status":
                        "verified",

                    "verified_at":
                        datetime.now().isoformat(),

                    "source":
                        "human_verified"
                }

                # ---------------------------------------------
                # STORE IN VECTOR DB
                # ---------------------------------------------

                try:

                    result = update_knowledge_base(
                        kb_bug
                    )

                    if result.get(
                        "success",
                        False
                    ):

                        st.success(
                            "✅ " +
                            result.get(
                                "message",
                                "Verified bug added successfully."
                            )
                        )

                        st.info(
                            "🌱 This resolved bug is now "
                            "available for future RAG retrieval "
                            "and recommendations."
                        )

                    else:

                        st.warning(
                            result.get(
                                "message",
                                "Bug was not added."
                            )
                        )

                except Exception as e:

                    st.error(
                        f"❌ Knowledge Base Error: {e}"
                    )

    st.divider()


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.header(
        "📥 Analysis Report"
    )

    report_data = dict(data)

    report_data["submitted_bug"] = (
        st.session_state.get(
            "bug_text",
            ""
        )
    )

    report_data["report_generated_at"] = (
        datetime.now().isoformat()
    )

    st.download_button(

        label="📥 Download Complete Analysis Report",

        data=json.dumps(
            report_data,
            indent=4,
            default=str
        ),

        file_name="bug_analysis_report.json",

        mime="application/json",

        use_container_width=True
    )

    st.success(
        "✅ Complete Multi-Agent Bug Analysis Completed"
    )


# =========================================================
# INITIAL SCREEN
# =========================================================

else:

    st.info(
        """
        👋 Welcome to the Intelligent Bug Diagnosis Platform.

        Submit a bug report above to start the complete AI workflow.

        The platform performs:

        • Triage
        • Log Analysis
        • Root Cause Detection
        • Duplicate Detection
        • RAG Retrieval
        • Remediation Recommendation
        • Knowledge Base Growth
        • Defect Pattern Analytics
        """
    )
    app = Flask(__name__)
# ... your code ...

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
