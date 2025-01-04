import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.title("Org Chart Viewer")

# Step 1: Let user upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Step 2: Create a directed graph
    G = nx.DiGraph()

    # Step 3: Add nodes (persons)
    for _, row in df.iterrows():
        # We'll use the Handle as the node identifier
        handle = row["Handle"]
        # We can store other attributes in the node if needed (like Title, Name, etc.)
        G.add_node(handle, name=row["Name"], title=row["Title"])
    
    # Step 4: Add edges (manager -> report)
    for _, row in df.iterrows():
        handle = row["Handle"]
        reports_to = row["ReportsTo"]
        # If `reports_to` is not blank or NaN, then create an edge
        if pd.notna(reports_to) and reports_to.strip():
            G.add_edge(reports_to, handle)
    
    # Step 5: Draw the org chart using networkx
    # (Note: "spring_layout" might not look exactly like a classic org chart, 
    #  but is a quick way to visualize)
    pos = nx.spring_layout(G, k=1, seed=42)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1500, node_color='#87CEEB')
    nx.draw_networkx_labels(G, pos, ax=ax, labels={n: n for n in G.nodes()}, font_size=10)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', arrows=True)
    
    plt.axis('off')
    st.pyplot(fig)

    # Optional: display the DataFrame so the user can see what was uploaded
    st.write("Data Preview:")
    st.dataframe(df)
