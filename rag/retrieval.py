import pickle
import faiss
import pandas as pd


import os

class BugRetriever:
    def __init__(self):
        self.index = None
        self.vectorizer = None
        self.data = None

        try:
            import faiss
            import pickle
            import pandas as pd

            if os.path.exists("faiss_index/bug.index"):
                self.index = faiss.read_index("faiss_index/bug.index")

                with open("faiss_index/vectorizer.pkl", "rb") as f:
                    self.vectorizer = pickle.load(f)

                self.data = pd.read_pickle("faiss_index/bug_data.pkl")
                print("FAISS loaded successfully")
            else:
                print("FAISS index not found - using dummy mode")
        except Exception as e:
            print(f"RAG load failed, dummy mode: {e}")
            self.index = None

    def search(self, query, top_k=3):
        # Agar index nahi hai to empty return karo - app crash nahi hogi
        if self.index is None or self.data is None:
            print("RAG in dummy mode - returning []")
            return []

        try:
            query_vector = self.vectorizer.transform([query]).toarray().astype("float32")
            top_k = min(top_k, len(self.data))
            distances, indices = self.index.search(query_vector, top_k)
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                row = self.data.iloc[idx]
                similarity = round((1 / (1 + float(distance))) * 100, 2)
                if similarity < 40:
                    continue
                results.append({
                    "Bug_ID": row["Bug_ID"],
                    "Title": row["Title"],
                    "Description": row["Description"],
                    "Severity": row["Severity"],
                    "Priority": row["Priority"],
                    "Component": row["Component"],
                    "Root_Cause": row["Root_Cause"],
                    "Suggested_Fix": row["Suggested_Fix"],
                    "Historical_Summary": f"{row['Title']} - {row['Root_Cause']}",
                    "similarity": similarity
                })
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    # purane functions ke liye
    def retrieve(self, q): return self.search(q)
    def get(self, t): return self.search(t)
