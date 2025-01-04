import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Org Chart with Photos and Physics Control Panel")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    # Read Excel into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Check minimal required columns
    required_cols = {"Handle", "Name", "ReportsTo", "Image"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        st.error(f"Your Excel file is missing the following columns: {missing_cols}")
        st.stop()

    # Create a directed network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # Show the "Physics" control panel in the top-left corner
    net.show_buttons(filter_=['physics'])
    net.set_options('''
    {
      "physics": {
        "enabled": true,
        "solver": "repulsion",
        "repulsion": {
          "centralGravity": 0,
          "springLength": 240,
          "springConstant": 0.42,
          "nodeDistance": 225,
          "damping": 1
        },
        "maxVelocity": 50,
        "minVelocity": 0.75,
        "timestep": 0.28,
        "wind": {
          "x": 0,
          "y": 0
        }
      }
    }
    ''')

    # Add nodes (each person's info)
    for _, row in df.iterrows():
        handle = row["Handle"]
        name = row["Name"]
        image = row["Image"]  # URL or local path

        # Label could be the person's name, handle, or both
        label = f"{name}\n({handle})"

        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image,
            size=50
        )

    # Add edges (manager -> person)
    for _, row in df.iterrows():
        handle = row["Handle"]
        reports_to = row["ReportsTo"]
        if pd.notna(reports_to) and reports_to.strip():
            net.add_edge(source=reports_to, to=handle)

    # Generate the interactive chart (HTML)
    net.save_graph("orgchart.html")

    # Read that HTML and embed in Streamlit
    with open("orgchart.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=1800, width=1800, scrolling=True)

    # Display the DataFrame preview
    st.write("Data Preview:")
    st.dataframe(df)
