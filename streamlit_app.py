import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Org Chart with Physics Control Panel (No Auto-Disable)")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Ensure we have required columns
    required_cols = {"Handle", "Name", "ReportsTo", "Image"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
        st.stop()

    # Create the PyVis network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # Show the built-in physics controls so the user can see/toggle them
    net.show_buttons(filter_=['physics'])

    # Enable physics (with some stabilization) via valid JSON
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

    # Save and load the generated HTML
    net.save_graph("orgchart.html")
    with open("orgchart.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Embed in Streamlit
    components.html(html_content, height=800, scrolling=True)

    # Optional: Display DataFrame
    st.write("Data Preview:")
    st.dataframe(df)
