from datetime import datetime
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

    def analyze_most_used_labels_by_year(self, prefix):
        year_label_count = defaultdict(lambda: defaultdict(int))

        for issue in self.issues:
            created = issue.get("created_date")
            year = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").year if created else None

            if year:
                for label in issue.get("labels", []):
                    if label.startswith(prefix):
                        year_label_count[year][label] += 1

        most_used_by_year = {
            year: max(label_dict.items(), key=lambda x: x[1])
            for year, label_dict in year_label_count.items() if label_dict
        }

        return most_used_by_year

    def analyze_specific_label_over_years(self, target_label):
        yearly_counts = defaultdict(int)

        for issue in self.issues:
            created = issue.get("created_date")
            year = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").year if created else None
            if year and target_label in issue.get("labels", []):
                yearly_counts[year] += 1

        return dict(sorted(yearly_counts.items()))

    def plot_results(self, label_comment_count, top_n=15):
        if not label_comment_count:
            print("[INFO] No data to display.")
            return

        sorted_labels = sorted(label_comment_count.items(), key=lambda x: x[1], reverse=True)[:top_n]
        labels, counts = zip(*sorted_labels)

        plt.figure(figsize=(12, 6))
        bars = plt.bar(labels, counts)

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

    def plot_most_used_by_year(self, most_used_by_year, title):
        if not most_used_by_year:
            print("[INFO] No data to display for yearly label usage.")
            return

        years = sorted(most_used_by_year.keys())
        labels = [most_used_by_year[year][0] for year in years]
        counts = [most_used_by_year[year][1] for year in years]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(years, counts)

        for bar, label in zip(bars, labels):
            height = bar.get_height()
            plt.annotate(label, xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8, rotation=45)

        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Most Used Label Count", fontsize=12)
        plt.title(title, fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_label_trend_over_years(self, yearly_counts, label):
        if not yearly_counts:
            print(f"[INFO] No usage data for label: {label}")
            return

        years = list(yearly_counts.keys())
        counts = list(yearly_counts.values())

        plt.figure(figsize=(10, 5))
        plt.plot(years, counts, marker='o', linestyle='-', color='blue')
        plt.fill_between(years, counts, color='skyblue', alpha=0.4)
        plt.title(f"Yearly Trend of '{label}' Usage")
        plt.xlabel("Year")
        plt.ylabel("Number of Labels")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

    def run(self):
        comment_data = self.analyze_comments_by_label()
        self.plot_results(comment_data, top_n=15)

        # kind_yearly = self.analyze_most_used_labels_by_year("kind/")
        # self.plot_most_used_by_year(kind_yearly, "Most Used 'kind/' Label per Year")

        area_yearly = self.analyze_most_used_labels_by_year("area/")
        self.plot_most_used_by_year(area_yearly, "Most Used 'area/' Label per Year")

        bug_trend = self.analyze_specific_label_over_years("kind/bug")
        self.plot_label_trend_over_years(bug_trend, "kind/bug")

        bug_trend = self.analyze_specific_label_over_years("kind/feature")
        self.plot_label_trend_over_years(bug_trend, "kind/feature")
