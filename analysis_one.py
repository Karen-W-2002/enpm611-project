from typing import List, Dict, Set
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import Issue, Event
import config

class AnalysisOne:
    """
    Analyze GitHub issues grouped by label and outputs statistics:
    - Avg. issue lifespan
    - Avg. number of comments
    - Number of contributors involved
    """

    def __init__(self):
        self.USER: str = config.get_parameter('user')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        label_stats: Dict[str, List[Dict]] = defaultdict(list)

        for issue in issues:
            if not issue.labels:
                continue

            # Compute lifespan (in hours)
            if issue.closed_date and issue.created_date:
                lifespan = (issue.closed_date - issue.created_date).total_seconds() / 3600
            else:
                lifespan = None

            # Count comments
            num_comments = sum(1 for e in issue.events if e.event_type == "commented")

            # Collect contributors: creator + anyone who authored an event
            contributors: Set[str] = set()
            if issue.creator:
                contributors.add(issue.creator)
            contributors.update(e.author for e in issue.events if e.author)

            for label in issue.labels:
                label_stats[label].append({
                    "lifespan": lifespan,
                    "comments": num_comments,
                    "contributors": contributors
                })

        results = []
        for label, stats in label_stats.items():
            valid_lifespans = [s["lifespan"] for s in stats if s["lifespan"] is not None]
            avg_lifespan = sum(valid_lifespans) / len(valid_lifespans) if valid_lifespans else None
            avg_comments = sum(s["comments"] for s in stats) / len(stats)
            all_contributors = set().union(*[s["contributors"] for s in stats])

            results.append({
                "label": label,
                "avg_lifespan_hours": round(avg_lifespan, 2) if avg_lifespan is not None else "N/A",
                "avg_comments": round(avg_comments, 2),
                "num_contributors": len(all_contributors)
            })

        df = pd.DataFrame(results)
        print(df.sort_values(by="avg_lifespan_hours", ascending=False).to_string(index=False))

        # Plot top labels by avg lifespan
        df_plot = df[df['avg_lifespan_hours'] != "N/A"]
        df_plot["avg_lifespan_hours"] = pd.to_numeric(df_plot["avg_lifespan_hours"])
        df_plot.nlargest(10, 'avg_lifespan_hours').plot(
            x="label", y="avg_lifespan_hours", kind="bar",
            title="Top 10 Labels by Avg. Issue Lifespan", figsize=(12, 6)
        )
        plt.ylabel("Avg. Lifespan (hours)")
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    AnalysisOne().run()
