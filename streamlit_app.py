import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.title("Org Chart with Photos (Stabilize Once, Then Disable Physics)")

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

    # Create a directed PyVis network
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    # Inject custom JavaScript to:
    # 1) Enable physics for an initial layout/stabilization
    # 2) Disable physics once stabilized, so nodes don't drift afterward
    net.set_options("""
    var options = {
      physics: {
        enabled: true,
        stabilization: {
          iterations: 200
        }
      }
    };

    // Once the network is stabilized, turn off physics
    function onceStabilized() {
      network.setOptions({ physics: { enabled: false } });
    }
    network.once("stabilized", onceStabilized);
    """)

    # Add nodes (each person's info)
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        name = str(row["Name"])
        image_url = str(row["Image"])  # could be a URL or local path

        # Label could be the person's name, handle, or both
        label = f"{name}\n({handle})"

        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image_url,
            size=50
        )

    # Add edges (manager -> person)
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        reports_to = str(row["ReportsTo"]) if pd.notna(row["ReportsTo"]) else ""
        if reports_to.strip():
            net.add_edge(
                source=reports_to,
                to=handle
            )

    # Generate the interactive chart (HTML)
    net.save_graph("orgchart.html")

    # Read that HTML file and embed in Streamlit
    with open("orgchart.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=800, width=1000, scrolling=True)

    # Display the DataFrame preview
    st.write("Data Preview:")
    st.dataframe(df)
