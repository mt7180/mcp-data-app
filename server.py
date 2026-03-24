import json
import os
import csv
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP

VIEW_URI: str = "ui://data-server/view.html"

mcp: FastMCP = FastMCP("Data Server")
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "static" / "data.csv"

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
    data: optional mapping like {"Python": 31.0, "Go": 14.3}."""

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


EMBEDDED_VIEW_HTML: str = """\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light dark" />
    <style>
      body { margin: 0; padding: 8px; background: transparent; }
      .wrap { width: 100%; height: 360px; }
      #chart { width: 100%; height: 100%; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
  </head>
  <body>
    <div class="wrap">
      <canvas id="chart"></canvas>
    </div>
    <script type="module">
      import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

      const app = new App({ name: "Data Chart View", version: "1.0.0" });
      let chart = null;

      function chartConfig(chartType, labels, values, title) {
        const palette = [
          "rgba(54, 162, 235, 0.75)",
          "rgba(255, 99, 132, 0.75)",
          "rgba(255, 206, 86, 0.75)",
          "rgba(75, 192, 192, 0.75)",
          "rgba(153, 102, 255, 0.75)",
          "rgba(255, 159, 64, 0.75)",
        ];

        const mappedType = chartType === "area" ? "line" : chartType;
        const isCircular = mappedType === "pie" || mappedType === "doughnut";

        return {
          type: mappedType,
          data: {
            labels,
            datasets: [{
              label: title || "Chart",
              data: values,
              backgroundColor: isCircular ? labels.map((_, i) => palette[i % palette.length]) : "rgba(54, 162, 235, 0.7)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 1.5,
              fill: chartType === "area",
              tension: chartType === "line" || chartType === "area" ? 0.25 : 0,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: { display: true, text: title || "Chart" },
              legend: { display: isCircular },
            },
          },
        };
      }

      function render(payload) {
        const entries = Object.entries(payload?.data || {});
        const labels = entries.map(([label]) => label);
        const values = entries.map(([, value]) => Number(value) || 0);
        const type = payload?.chart_type || "bar";
        const title = payload?.title || "Chart";

        if (chart) chart.destroy();
        const ctx = document.getElementById("chart").getContext("2d");
        chart = new Chart(ctx, chartConfig(type, labels, values, title));
      }

      app.ontoolresult = ({ content }) => {
        const text = content?.find((c) => c.type === "text")?.text;
        if (!text) return;
        try { render(JSON.parse(text)); } catch { render({ data: {} }); }
      };

      await app.connect();
    </script>
  </body>
</html>
"""


@mcp.resource(
    VIEW_URI,
  app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com", "https://cdn.jsdelivr.net"])),
)
def view_resource() -> str:
    """Interactive chart viewer for MCP Apps."""
    return EMBEDDED_VIEW_HTML

if __name__ == "__main__":
    mcp.run()
