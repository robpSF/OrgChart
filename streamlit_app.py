import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import re

def inject_autodisable_physics(html_content: str) -> str:
    """
    Inject a JS snippet after the network is created to disable physics
    once the layout is stabilized.
    """
    # We'll look for the line: "var network = new vis.Network(container, data, options);"
    # and inject a snippet right after it.
    pattern = r"(var network = new vis\.Network\(container,\s*data,\s*options\);\s*)"
    
    # This snippet calls network.setOptions({ physics: { enabled: false } }) 
    # once the network finishes stabilizing.
    injection = (
        r"\1\n"
        r"network.once('stabilized', function() {\n"
        r"    network.setOptions({ physics: { enabled: false } });\n"
        r"});\n"
    )
    # Insert our code right after the matched line
    new_html = re.sub(pattern, injection, html_content, count=1)
    return new_html

st.title("Org Chart with Auto-Disable Physics")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_cols = {"Handle", "Name", "ReportsTo", "Image"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        st.stop()

    # Create a PyVis network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # -- 1) Provide JSON-based options (no custom functions here) --
    #    We'll let the network run physics for an initial layout, 
    #    then we plan to patch the final HTML with the onceStabilized callback.
    net.set_options('''
    {
      "physics": {
        "enabled": true,
        "stabilization": {
          "iterations": 200
        }
      }
    }
    ''')

    # Add nodes
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        name   = str(row["Name"])
        image  = str(row["Image"])
        label  = f"{name}\n({handle})"
        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image,
            size=50
        )

    # Add edges
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        reports_to = row["ReportsTo"]
        if pd.notna(reports_to) and str(reports_to).strip():
            net.add_edge(source=str(reports_to), to=handle)

    # -- 2) Generate the HTML (without opening a browser) --
    net.save_graph("temp.html")

    # -- 3) Read the HTML and inject the JS snippet --
    with open("temp.html", "r", encoding="utf-8") as f:
        original_html = f.read()

    patched_html = inject_autodisable_physics(original_html)

    # -- 4) Write the modified HTML to a new file (optional) --
    with open("orgchart.html", "w", encoding="utf-8") as f:
        f.write(patched_html)

    # -- 5) Embed the final HTML in Streamlit --
    components.html(patched_html, height=800, scrolling=True)

    # Display the DataFrame
    st.write("Data Preview:")
    st.dataframe(df)
