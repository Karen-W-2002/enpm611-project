import json
import matplotlib.pyplot as plt
from collections import defaultdict

def run_feature_1():
    with open("data/poetry_data.json") as f:
        issues = json.load(f)

    label_comment_count = defaultdict(int)

    for issue in issues:
        comments = issue.get("comments", 0)
        labels = [label["name"] for label in issue.get("labels", [])]
        for label in labels:
            label_comment_count[label] += comments

    # Plot
    labels = list(label_comment_count.keys())
    counts = list(label_comment_count.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts)
    plt.xlabel("Issue Labels")
    plt.ylabel("Total Number of Comments")
    plt.title("Label vs Number of Comments on Issues")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
