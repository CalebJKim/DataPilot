import base64
import matplotlib.pyplot as plt
import pandas as pd
import io

def execute_visualization_code(code: str, sql_results: pd.DataFrame, web_sentiments: list) -> dict:
    """
    Executes the given visualization code and returns the visualizations as base64 encoded strings.
    """
    # Define a local scope for executing the code
    local_scope = {
        "plt": plt,
        "pd": pd,
        "sql_results": sql_results,
        "web_sentiments": web_sentiments,
        "base64": base64,
        "io": io
    }

    # Execute the code
    exec(code, {}, local_scope)

    # Retrieve the generated visualizations
    visualizations = local_scope.get("visualizations", {})
    return visualizations

def save_plot_to_base64(fig):
    """
    Saves a matplotlib figure to a base64 encoded string.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
