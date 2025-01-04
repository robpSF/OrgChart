import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

def main():
    st.title("Org Chart with Hierarchical Layout")

    # 1) File uploader for Excel
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        # 2) Read the Excel into a DataFrame
        df = pd.read_excel(uploaded_file)
        
        # Optional: Validate required columns
        required_cols = {"Handle", "Name", "ReportsTo", "Image"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            st.error(f"Your Excel file is missing the following columns: {missing_cols}")
            st.stop()

        # 3) Create a directed PyVis network
        net = Network(
            height="750px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
        )

        # 4) (Optional) Show layout/physics buttons so users can experiment
        # net.show_buttons(filter_=['layout', 'physics'])

        # 5) Set hierarchical layout options (top-to-bottom)
        net.set_options("""
        var options = {
          layout: {
            hierarchical: {
              enabled: true,
              levelSeparation: 150,
              nodeSpacing: 100,
              treeSpacing: 200,
              direction: 'UD',    // 'UD' = top to bottom
              sortMethod: 'directed'
            }
          },
          physics: {
            enabled: false
          }
        }
        """)

        # 6) Add nodes
        for _, row in df.iterrows():
            handle = row["Handle"]
            name = row["Name"]
            image = row["Image"]  # URL or file path to the person's image

            # Customize the label (Name + Handle, or just Name)
            label = f"{name}\n({handle})"

            net.add_node(
                n_id=handle,
                label=label,
                shape="image",
                image=image,
                size=50
            )

        # 7) Add edges (manager -> person)
        for _, row in df.iterrows():
            handle = row["Handle"]
            reports_to = row["ReportsTo"]
            # If valid manager reference, add a directed edge from manager to handle
            if pd.notna(reports_to) and str(reports_to).strip():
                net.add_edge(source=reports_to, to=handle)

        # 8) Generate the interactive chart
        net.save_graph("orgchart.html")

        # 9) Display the chart in Streamlit
        with open("orgchart.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=800, scrolling=True)

        # 10) Display the uploaded DataFrame
        st.write("Data Preview:")
        st.dataframe(df)

if __name__ == "__main__":
    main()
