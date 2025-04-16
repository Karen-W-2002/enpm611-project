import json
import matplotlib.pyplot as plt
from collections import defaultdict

class LabelCommentGraph:
    def __init__(self, json_path="fetch_issues/poetry_data.json"):
        self.json_path = json_path
        self.issues = self.load_issues()

    def load_issues(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {self.json_path}")
            return []
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON format.")
            return []

    def analyze_comments_by_label(self):
        label_comment_count = defaultdict(int)

        for issue in self.issues:
            labels = issue.get("labels", [])
            events = issue.get("events", [])

            comment_count = sum(1 for e in events if e.get("event_type") == "commented")

            for label in labels:
                label_comment_count[label] += comment_count

        return label_comment_count

    def plot_results(self, label_comment_count, top_n=15):
        if not label_comment_count:
            print("[INFO] No data to display.")
            return

        # Sort by number of comments and take top N
        sorted_labels = sorted(label_comment_count.items(), key=lambda x: x[1], reverse=True)[:top_n]
        labels, counts = zip(*sorted_labels)

        plt.figure(figsize=(12, 6))
        bars = plt.bar(labels, counts)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8)

        plt.xlabel("Issue Labels", fontsize=12)
        plt.ylabel("Number of Comments", fontsize=12)
        plt.title(f"Top {top_n} Labels by Number of Comments on Issues", fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()


    def run(self):
        comment_data = self.analyze_comments_by_label()
        self.plot_results(comment_data, top_n=15)
