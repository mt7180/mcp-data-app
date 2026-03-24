import json

from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP

VIEW_URI: str = "ui://data-server/view.html"
mcp: FastMCP = FastMCP("Data Server")

@mcp.tool(app=AppConfig(resource_uri=VIEW_URI))
def show_chart(chart_type: str = "bar") -> str:
    """Show programming language popularity as an interactive chart.
    chart_type: bar, pie, line, doughnut, or area."""

    data = {
        "Python": 31.0,
        "JavaScript": 25.2,
        "Rust": 18.1,
        "Go": 14.3,
        "TypeScript": 11.4,
    }

    chart_type = chart_type.lower().strip()
    if chart_type not in {"bar", "pie", "line", "doughnut", "area"}:
        chart_type = "bar"

    payload = {
        "title": "Programming Language Popularity",
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
            :root {
                color-scheme: light dark;
            }

            body {
                margin: 0;
                padding: 16px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background: transparent;
            }

            .card {
                border: 1px solid color-mix(in srgb, CanvasText 15%, transparent);
                border-radius: 12px;
                padding: 12px;
                background: color-mix(in srgb, Canvas 88%, CanvasText 12%);
            }

            h2 {
                margin: 0 0 12px;
                font-size: 16px;
            }

            .bars {
                display: grid;
                gap: 10px;
            }

            .row {
                display: grid;
                grid-template-columns: 110px 1fr 52px;
                align-items: center;
                gap: 8px;
            }

            .label,
            .value {
                font-size: 13px;
                white-space: nowrap;
            }

            .track {
                position: relative;
                width: 100%;
                height: 20px;
                border-radius: 999px;
                overflow: hidden;
                background: color-mix(in srgb, CanvasText 10%, transparent);
            }

            .bar {
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #4f46e5, #06b6d4);
                transition: width 200ms ease-out;
            }

            #note {
                margin-top: 10px;
                font-size: 12px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2 id="title">Programming Language Popularity</h2>
            <div id="bars" class="bars"></div>
            <div id="note"></div>
        </div>

        <script type="module">
            import { App } from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

            const app = new App({ name: "Data Chart View", version: "1.0.0" });

            function render(payload) {
                const bars = document.getElementById("bars");
                const title = document.getElementById("title");
                const note = document.getElementById("note");

                title.textContent = payload?.title || "Programming Language Popularity";
                bars.replaceChildren();

                const entries = Object.entries(payload?.data || {});
                const maxValue = entries.reduce((max, [, value]) => Math.max(max, Number(value) || 0), 0) || 1;

                for (const [label, rawValue] of entries) {
                    const value = Number(rawValue) || 0;
                    const width = (value / maxValue) * 100;

                    const row = document.createElement("div");
                    row.className = "row";

                    const labelEl = document.createElement("div");
                    labelEl.className = "label";
                    labelEl.textContent = label;

                    const track = document.createElement("div");
                    track.className = "track";

                    const bar = document.createElement("div");
                    bar.className = "bar";
                    bar.style.width = `${width}%`;
                    track.appendChild(bar);

                    const valueEl = document.createElement("div");
                    valueEl.className = "value";
                    valueEl.textContent = `${value.toFixed(1)}%`;

                    row.append(labelEl, track, valueEl);
                    bars.appendChild(row);
                }

                if (payload?.chart_type && payload.chart_type !== "bar") {
                    note.textContent = `Requested chart type: ${payload.chart_type}. Showing bar chart for efficiency.`;
                } else {
                    note.textContent = "";
                }
            }

            app.ontoolresult = ({ content }) => {
                const text = content?.find((c) => c.type === "text");
                if (!text?.text) return;
                try {
                    render(JSON.parse(text.text));
                } catch {
                    render({ data: {} });
                }
            };

            await app.connect();
        </script>
    </body>
</html>
"""


@mcp.resource(
    VIEW_URI,
    app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
)
def view_resource() -> str:
    """Interactive chart viewer — renders tool results as bars."""
    return EMBEDDED_VIEW_HTML

if __name__ == "__main__":
    mcp.run()
