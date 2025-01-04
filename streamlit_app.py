import streamlit as st
import pandas as pd
from pyvis.network import Network
import base64
import os

# If you need to embed PyVis HTML in Streamlit, we can use st.components.v1.html
import streamlit.components.v1 as components

st.title("Org Chart Viewer with Photos")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    # Read Excel into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Check columns
    required_cols = {"Handle", "Name", "ReportsTo", "Image"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"Your Excel file is missing the following columns: {missing_cols}")
        st.stop()

    # Create a directed Network
    net = Network(
        height="750px", 
        width="100%", 
        directed=True, 
        bgcolor="#ffffff", 
        font_color="black"
    )
    
    # Add nodes
    for _, row in df.iterrows():
        handle = row["Handle"]
        name = row["Name"]
        image = row["Image"]  # URL or file path

        # Node label can be whatever you like (Handle, Name, or both)
        label = f"{name}\n({handle})"

        # Add node with shape "image" and the image URL
        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image,
            size=50
        )
    
    # Add edges
    for _, row in df.iterrows():
        handle = row["Handle"]
        reports_to = row["ReportsTo"]

        # If there's a valid manager handle in ReportsTo, link them
        if pd.notna(reports_to) and str(reports_to).strip():
            net.add_edge(
                source=reports_to, 
                to=handle
            )

    # Generate the PyVis network in HTML
    net.show("orgchart.html")
    
    # Load the generated HTML and display in Streamlit
    with open("orgchart.html", "r", encoding="utf-8") as f:
        html_content = f.read()
        components.html(html_content, height=800, scrolling=True)

    # Optional: Show uploaded DataFrame
    st.write("Data Preview:")
    st.dataframe(df)
