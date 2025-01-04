import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Org Chart Viewer with Photos")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Create PyVis network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # Add nodes and edges
    for _, row in df.iterrows():
        handle = row["Handle"]
        name = row["Name"]
        image = row["Image"]

        label = f"{name}\n({handle})"
        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image,
            size=50
        )

    for _, row in df.iterrows():
        handle = row["Handle"]
        reports_to = row["ReportsTo"]
        if pd.notna(reports_to) and reports_to.strip():
            net.add_edge(source=reports_to, to=handle)

    # Save the visualization to an HTML file
    net.save_graph("orgchart.html")

    # Display in Streamlit by reading that HTML file
    with open("orgchart.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=800, scrolling=True)

    st.write("Data Preview:")
    st.dataframe(df)
