import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import re

def inject_autodisable_physics(html_content: str) -> str:
    """
    Injects a JavaScript snippet after the network is created to:
    1) Listen for the 'stabilized' event.
    2) Disable physics automatically once the layout is stable.
    """
    # Regex looks for: var network = new vis.Network(container, data, options);
    pattern = r"(var network = new vis\.Network\(container,\s*data,\s*options\);\s*)"
    
    # We'll insert a small block:
    # network.once('stabilized', function() {
    #     network.setOptions({ physics: { enabled: false } });
    # });
    injection = (
        r"\1\n"
        r"network.once('stabilized', function() {\n"
        r"    network.setOptions({ physics: { enabled: false } });\n"
        r"});\n"
    )
    
    # Insert the snippet right after the matched line
    new_html = re.sub(pattern, injection, html_content, count=1)
    return new_html

st.title("Org Chart with Auto-Disable Physics + Chart Controls")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ensure we have required columns
    required_cols = {"Handle", "Name", "ReportsTo", "Image"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        st.stop()

    # 1) Create the PyVis network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # 2) Show the built-in physics controls so the user can see/toggle them
    net.show_buttons(filter_=['physics'])

    # 3) Set basic physics in valid JSON (no raw JS)
    #    We'll let the chart auto-layout, then patch in the "disable" snippet next.
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

    # 4) Add nodes
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

    # 5) Add edges
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        reports_to = row["ReportsTo"]
        if pd.notna(reports_to) and str(reports_to).strip():
            net.add_edge(source=str(reports_to), to=handle)

    # 6) Generate HTML with PyVis
    net.save_graph("temp.html")

    # 7) Inject custom JS that auto-disables physics once stabilized
    with open("temp.html", "r", encoding="utf-8") as f:
        original_html = f.read()

    patched_html = inject_autodisable_physics(original_html)

    # 8) Display the patched HTML in Streamlit
    #    (Optionally, you could write patched_html to "orgchart.html" first.)
    components.html(patched_html, height=800, scrolling=True)

    # 9) Show the DataFrame preview
    st.write("Data Preview:")
    st.dataframe(df)
