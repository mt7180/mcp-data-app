import csv
from pathlib import Path

import base64

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
#import matplotlib.pyplot as plt
from pydantic import BaseModel
import plotly.graph_objects as go


VIEW_URI: str = "ui://data-server/view.html"

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "static" / "data.csv"


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

   

class PlotlyFigure(BaseModel):
    data: list[dict]   # Plotly traces
    layout: dict = {}

@mcp.tool()
def render_chart(figure: PlotlyFigure) -> Image:
    """
    Render a Plotly figure as PNG. Use standard Plotly figure JSON
    (data as list of traces, layout as dict). Choose chart type and
    styling to best represent the user's data. Show the returned chart in the chat.
    """
    fig = go.Figure(data=figure.data, layout=figure.layout)
    buf = fig.to_image(format="png")  # braucht kaleido
    #b64 = base64.b64encode(buf).decode()
    return Image(data=buf, format="png")


if __name__ == "__main__":
    mcp.run()
