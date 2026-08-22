import os
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

KB_PATH = os.path.join(
    BASE_DIR,
    "vector_db"
)

COLLECTION_NAME = "verified_bug_knowledge"

_embedding_model = None
_chroma_client = None
_collection = None


# =========================================================
# INITIALIZE KNOWLEDGE BASE
# =========================================================

def _initialize():

    global _embedding_model
    global _chroma_client
    global _collection

    try:

        if _embedding_model is None:

            _embedding_model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        if _chroma_client is None:

            os.makedirs(
                KB_PATH,
                exist_ok=True
            )

            _chroma_client = (
                chromadb.PersistentClient(
                    path=KB_PATH
                )
            )

            _collection = (
                _chroma_client
                .get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={
                        "description":
                        "Verified resolved bugs and historical fixes"
                    }
                )
            )

        return True

    except Exception as e:

        print(
            "Knowledge Base initialization error:",
            repr(e)
        )

        raise


# =========================================================
# CREATE SEARCH DOCUMENT
# =========================================================

def _create_document(bug):

    recommended_fix = bug.get(
        "recommended_fix",
        ""
    )

    if isinstance(
        recommended_fix,
        list
    ):

        recommended_fix = " | ".join(
            str(x)
            for x in recommended_fix
        )

    return f"""
Bug ID:
{bug.get("bug_id", "")}

Bug Title:
{bug.get("title", "")}

Description:
{bug.get(
    "description",
    bug.get("summary", "")
)}

Category:
{bug.get("category", "")}

Component:
{bug.get("component", "")}

Severity:
{bug.get("severity", "")}

Priority:
{bug.get("priority", "")}

Error Message:
{bug.get(
    "error_message",
    bug.get("exception", "")
)}

Stack Trace:
{bug.get("stack_trace", "")}

Failure Point:
{bug.get("failure_point", "")}

Root Cause:
{bug.get(
    "root_cause",
    bug.get("cause", "")
)}

Resolution:
{bug.get(
    "resolution",
    bug.get("solution", "")
)}

Recommended Fix:
{recommended_fix}
""".strip()


# =========================================================
# ADD VERIFIED BUG
# =========================================================

def add_verified_bug(bug):

    _initialize()

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not bug:

        return {
            "success": False,
            "message": "No bug data was provided."
        }

    # -----------------------------------------------------
    # BUG ID
    # -----------------------------------------------------

    bug_id = str(
        bug.get(
            "bug_id",
            bug.get(
                "id",
                ""
            )
        )
    ).strip()

    if not bug_id:

        return {
            "success": False,
            "message": "Bug ID is required."
        }

    # -----------------------------------------------------
    # FIX VERIFICATION
    # -----------------------------------------------------

    if bug.get(
        "fix_verified",
        False
    ) is not True:

        return {
            "success": False,
            "message":
                "Bug cannot be added because "
                "the fix is not verified."
        }

    # -----------------------------------------------------
    # VERIFICATION STATUS
    # -----------------------------------------------------

    if bug.get(
        "verification_status"
    ) != "verified":

        return {
            "success": False,
            "message":
                "Bug cannot be added because "
                "verification status is not 'verified'."
        }

    # -----------------------------------------------------
    # CONFIRMED RESOLUTION
    # -----------------------------------------------------

    resolution = str(
        bug.get(
            "resolution",
            bug.get(
                "solution",
                ""
            )
        )
    ).strip()

    if not resolution:

        return {
            "success": False,
            "message":
                "Confirmed resolution is required."
        }

    # -----------------------------------------------------
    # CREATE DOCUMENT
    # -----------------------------------------------------

    document = _create_document(
        bug
    )

    # -----------------------------------------------------
    # CREATE EMBEDDING
    # -----------------------------------------------------

    embedding = (
        _embedding_model
        .encode(document)
        .tolist()
    )

    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    metadata = {

        "bug_id":
            bug_id,

        "title":
            str(
                bug.get(
                    "title",
                    ""
                )
            ),

        "component":
            str(
                bug.get(
                    "component",
                    ""
                )
            ),

        "category":
            str(
                bug.get(
                    "category",
                    ""
                )
            ),

        "severity":
            str(
                bug.get(
                    "severity",
                    ""
                )
            ),

        "priority":
            str(
                bug.get(
                    "priority",
                    ""
                )
            ),

        "root_cause":
            str(
                bug.get(
                    "root_cause",
                    bug.get(
                        "cause",
                        ""
                    )
                )
            ),

        "resolution":
            resolution,

        "fix_verified":
            "true",

        "verification_status":
            "verified",

        "source":
            str(
                bug.get(
                    "source",
                    "human_verified"
                )
            ),

        "verified_at":
            str(
                bug.get(
                    "verified_at",
                    datetime.now().isoformat()
                )
            )
    }

    # -----------------------------------------------------
    # DUPLICATE BUG ID CHECK
    # -----------------------------------------------------

    existing = _collection.get(
        ids=[bug_id]
    )

    existing_ids = existing.get(
        "ids",
        []
    )

    if existing_ids:

        return {
            "success": False,
            "message":
                f"Bug {bug_id} already exists "
                "in knowledge base."
        }

    # -----------------------------------------------------
    # STORE IN CHROMADB
    # -----------------------------------------------------

    _collection.add(

        ids=[bug_id],

        documents=[
            document
        ],

        embeddings=[
            embedding
        ],

        metadatas=[
            metadata
        ]
    )

    return {

        "success": True,

        "message":
            f"Bug {bug_id} added to knowledge base."
    }


# =========================================================
# SEARCH KNOWLEDGE BASE
# =========================================================

def search_knowledge_base(
    query,
    top_k=5
):

    _initialize()

    if not query or not query.strip():

        return []

    total = _collection.count()

    if total == 0:

        return []

    try:

        top_k = min(
            max(
                1,
                int(top_k)
            ),
            total
        )

    except Exception:

        top_k = min(
            5,
            total
        )

    embedding = (
        _embedding_model
        .encode(query)
        .tolist()
    )

    result = _collection.query(

        query_embeddings=[
            embedding
        ],

        n_results=top_k,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    ids = result.get(
        "ids",
        [[]]
    )[0]

    documents = result.get(
        "documents",
        [[]]
    )[0]

    distances = result.get(
        "distances",
        [[]]
    )[0]

    metadatas = result.get(
        "metadatas",
        [[]]
    )[0]

    matches = []

    for i, bug_id in enumerate(ids):

        distance = (
            distances[i]
            if i < len(distances)
            else 1.0
        )

        # Approximate similarity score
        similarity = max(
            0,
            min(
                100,
                (1 - float(distance)) * 100
            )
        )

        matches.append({

            "bug_id":
                bug_id,

            "similarity":
                round(
                    similarity,
                    2
                ),

            "document":
                documents[i]
                if i < len(documents)
                else "",

            "metadata":
                metadatas[i]
                if i < len(metadatas)
                else {}
        })

    return matches


# =========================================================
# KNOWLEDGE BASE STATISTICS
# =========================================================

def get_knowledge_base_stats():

    _initialize()

    total = _collection.count()

    return {

        "total_verified_bugs":
            total,

        "collection":
            COLLECTION_NAME
    }


# =========================================================
# STREAMLIT HELPER
# =========================================================

def update_knowledge_base(bug):

    return add_verified_bug(
        bug
    )
