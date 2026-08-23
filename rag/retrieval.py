import pickle
import faiss
import pandas as pd


class BugRetriever:

    def __init__(self):

        self.index = faiss.read_index("faiss_index/bug.index")

        with open("faiss_index/vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)

        self.data = pd.read_pickle("faiss_index/bug_data.pkl")

    def search(self, query, top_k=3):

        query_vector = self.vectorizer.transform(
            [query]
        ).toarray().astype("float32")

        # Safe top_k
        top_k = min(top_k, len(self.data))

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []

        print("\n========== RAG SEARCH ==========")

        for distance, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx == -1:
                continue

            row = self.data.iloc[idx]

            # Convert FAISS L2 distance to similarity
            similarity = round(
                (1 / (1 + float(distance))) * 100,
                2
            )

            print(f"Bug : {row['Bug_ID']}")
            print(f"Distance : {distance}")
            print(f"Similarity : {similarity}%")

            # Ignore very weak matches
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

                "Historical_Summary":
                    f"{row['Title']} - {row['Root_Cause']}",

                "similarity": similarity

            })

        results.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        print("===== FINAL RAG RESULTS =====")
        print(results)

        return results
