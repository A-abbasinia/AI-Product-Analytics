class ChartRecommender:
    def __init__(self):
        pass

    def choose_chart(self, metric):
        metric = metric.lower()

        time_series_metrics = ["revenue", "orders", "sessions"]
        ratio_metrics = ["conversion_rate", "ctr", "retention_rate"]
        categorical_metrics = ["top_categories", "campaign_performance"]
        distribution_metrics = ["aov", "clv"]

        if metric in time_series_metrics:
            return "line_chart"

        if metric in ratio_metrics:
            return "bar_chart"

        if metric in categorical_metrics:
            return "horizontal_bar"

        if metric in distribution_metrics:
            return "distribution_plot"

        return "kpi_card"
