import base64
import matplotlib.pyplot as plt
import pandas as pd
import io
import tempfile
import subprocess
import sys
import os

def execute_visualization_code(code, sql_result, web_sentiments):
    # Clean the code to replace non-ASCII characters and remove triple quotes
    cleaned_code = code.replace('’', "'").replace('“', '"').replace('”', '"').strip()
    
    # Remove surrounding triple quotes if present
    if cleaned_code.startswith("```") and cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[3:-3].strip()

    # Remove any leading 'python' or markdown syntax
    if code.startswith("python"):
        code = code[len("python"):].strip()

    # Print the cleaned code for inspection
    print("Executing the following visualization code:")
    print(cleaned_code)

    # Get the current working directory
    project_dir = os.getcwd()

    # Create a temporary file in the project directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", dir=project_dir) as temp_file:
        # Write the visualization code to the file
        temp_file.write(cleaned_code.encode('utf-8'))
        temp_file_path = temp_file.name

    # Execute the temporary Python file and capture the output
    try:
        result = subprocess.run([sys.executable, temp_file_path], check=True, capture_output=True, text=True)
        base64_image = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing the visualization script: {e}")
        return None
    finally:
        # Remove the temporary file after execution
        os.remove(temp_file_path)

    # Return the base64 string
    return base64_image

def save_plot_to_base64(fig):
    """
    Saves a matplotlib figure to a base64 encoded string.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
