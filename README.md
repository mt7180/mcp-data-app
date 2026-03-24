mcp-data-app
===========

Minimal FastMCP example that returns chart data and renders it with a small HTML app (Chart.js).


Usage
-----
- The mcp tool `show_chart` is exposed by the server and is paired with the UI resource `ui://data-server/view.html`.
- Chart data is read from `static/data.csv` (first two columns interpreted as label,value). 

Notes
-----
- The UI loads Chart.js from jsDelivr.
- To change chart type, pass `chart_type` (e.g. `bar`, `line`, `pie`, `doughnut`, `area`) when calling the tool.

