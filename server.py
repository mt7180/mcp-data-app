import json
import os
import csv
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP

VIEW_URI: str = "ui://data-server/view.html"

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "static" / "data.csv"
HTML_PATH = BASE_DIR / "static" / "view.html"
VIEW_HTML: str = HTML_PATH.read_text(encoding="utf-8")

mcp: FastMCP = FastMCP("Data Server")

def csv_to_records(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    clean_data: dict[str, float] = {}

    if rows:
      first = rows[0]
      if "label" in first and "value" in first:
        clean_data = {
          str(row["label"]): float(row["value"])
          for row in rows
          if row.get("label") and row.get("value")
        }
      elif len(first) >= 2:
        columns = list(first.keys())
        label_col, value_col = columns[0], columns[1]
        clean_data = {
          str(row[label_col]): float(row[value_col])
          for row in rows
          if row.get(label_col) and row.get(value_col)
        }
    return clean_data

   
@mcp.tool(app=AppConfig(resource_uri=VIEW_URI))
def show_chart(
    title: str = "Chart Title",
    chart_type: str = "bar",
) -> str:
    """Show data as an interactive chart.
    chart_type: bar, pie, line, doughnut, or area.
    title: The title of the chart. """

    chart_type = chart_type.lower().strip()
    if chart_type not in {"bar", "pie", "line", "doughnut", "area"}:
        chart_type = "bar"

    data = csv_to_records(str(CSV_PATH) if CSV_PATH.exists() else [])

    payload = {
        "title": title,
        "chart_type": chart_type,
        "data": data,
    }
    return json.dumps(payload)


@mcp.resource(
    VIEW_URI,
  app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com", "https://cdn.jsdelivr.net"])),
)
def view_resource() -> str:
    """Interactive chart viewer for MCP Apps."""
    return VIEW_HTML

if __name__ == "__main__":
    mcp.run()
