class BugReranker:

    def rerank(self, bugs):

        bugs = sorted(
            bugs,
            key=lambda x: x["similarity"],
            reverse=True
        )

        return bugs[:5]
