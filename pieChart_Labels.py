from typing import Counter, List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import DataLoader
from model import Issue,Event
import config

class LabelPieChartAnalysis:
    def __init__(self):
        self.issues = DataLoader().get_issues()

    def analyze_label_distribution(self, prefix):
        label_counter = Counter()
        for issue in self.issues:
            labels = issue.labels if issue.labels else []
            filtered_labels = [label for label in labels if label.startswith(prefix)]
            label_counter.update(filtered_labels)
        return label_counter

    def plot_pie_chart(self, label_counter, title):
        labels = list(label_counter.keys())
        counts = list(label_counter.values())

        if not labels:
            print(f"No labels found to display for {title}.")
            return

        explode = [0.05] * len(labels)
        colors = plt.cm.tab20.colors[:len(labels)]

        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(
            counts,
            labels=None,
            autopct=lambda pct: f'{pct:.1f}%\n({int(round(pct/100.*sum(counts)))})',
            startangle=140,
            explode=explode,
            colors=colors,
            textprops={"fontsize": 12}
        )

        total = sum(counts)
        legend_labels = [f"{label} - {count / total * 100:.1f}%" for label, count in zip(labels, counts)]

        plt.legend(wedges, legend_labels, title="Labels", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title(title, fontsize=16)
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def run(self):
        print("Running 'kind/' Label Pie Chart Analysis...")
        kind_counter = self.analyze_label_distribution("kind/")
        print("Kind Label counts:", kind_counter)
        self.plot_pie_chart(kind_counter, 'Distribution of Issues by Kind Label')

        print("\nRunning 'status/' Label Pie Chart Analysis...")
        status_counter = self.analyze_label_distribution("status/")
        print("Status Label counts:", status_counter)
        self.plot_pie_chart(status_counter, 'Distribution of Issues by Status Label')

        print("\nRunning 'area/' Label Pie Chart Analysis...")
        area_counter = self.analyze_label_distribution("area/")
        print("Area Label counts:", area_counter)
        self.plot_pie_chart(area_counter, 'Distribution of Issues by Area Label')
