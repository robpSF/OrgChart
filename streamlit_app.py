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
    
    net.set_options('''
    {
      "configure": {
        "enabled": true,
        "filter": ["physics"]
      },
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
        "timestep": 0.28
      }
    }
    ''')
    
    
    # Add nodes (each person's info)
    for _, row in df.iterrows():
        handle = str(row["Handle"])
        name = str(row["Name"])
        image_url = str(row["Image"])
        label = f"{name}\n({handle})"

        # Get tags and split by comma (or however your tags are separated)
        tag_list = [t.strip().lower() for t in str(row["Tags"]).split(",")]

        #st.write(tag_list)
        # Decide border color based on tags
        if "amplifier" in tag_list:
            border_color = "#0000FF"  # Blue
        elif "sock puppet" in tag_list:
            border_color = "#FF0000"  # Red
        else:
            border_color = "#888888"  # Gray default

        # Create the color dictionary
        color_dict = {
            "border": border_color,
            "background": "#FFFFFF",  # or transparent, but typically a color is needed
            "highlight": {
                "border": border_color,
                "background": "#EFEFEF"
            },
            "hover": {
                "border": border_color,
                "background": "#E0E0E0"
            }
        }

        net.add_node(
            n_id=handle,
            label=label,
            shape="image",
            image=image_url,
            color=color_dict,
            borderWidth=12  # For a noticeable border
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
