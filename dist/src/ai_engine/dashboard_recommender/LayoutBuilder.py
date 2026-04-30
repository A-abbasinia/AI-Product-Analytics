class LayoutBuilder:
    def __init__(self):
        pass

    def build_dashboard(self, title, chart_blocks):
        sections = []

        overview_cards = [
            block for block in chart_blocks if block["type"] == "kpi_card"
        ]

        other_charts = [
            block for block in chart_blocks if block["type"] != "kpi_card"
        ]

        sections.append({
            "title": "Overview KPIs",
            "layout": {
                "type": "row",
                "items": overview_cards
            }
        })

        sections.append({
            "title": "Detailed Analysis",
            "layout": {
                "type": "grid",
                "items": other_charts
            }
        })

        final = {
            "dashboard_title": title,
            "sections": sections
        }

        return final
