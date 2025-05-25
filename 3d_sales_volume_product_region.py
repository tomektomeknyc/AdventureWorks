import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import io

st.set_page_config(layout="wide")  # make canvas bigger
st.title("📊 3D Sales Volume: Product vs Region")
st.caption("Files used: Sales, Territories, Customers, Products")

# Load and merge data
sales_2021 = pd.read_csv("files/sales_2021.csv")
sales_2022 = pd.read_csv("files/sales_2022.csv")
sales = pd.concat([sales_2021, sales_2022], ignore_index=True)
products = pd.read_csv("files/AdventureWorks Product Lookup.csv")
territories = pd.read_csv("files/AdventureWorks Territory Lookup.csv")
customers = pd.read_csv("files/AdventureWorks Customer Lookup.csv", encoding="ISO-8859-1")

territories.rename(columns={"SalesTerritoryKey": "TerritoryKey"}, inplace=True)
customers.rename(columns={"CustomerID": "CustomerKey"}, inplace=True)
customers = customers.dropna(subset=["CustomerKey"])
customers = customers[customers["CustomerKey"].astype(str).str.match(r"^\d+$")]
customers["CustomerKey"] = customers["CustomerKey"].astype(int)

merged = sales.merge(customers, on="CustomerKey", how="left") \
              .merge(territories, on="TerritoryKey", how="left") \
              .merge(products, on="ProductKey", how="left")

# Aggregate
df_3d = merged.groupby(["ProductName", "Region"]).agg({"OrderQuantity": "sum"}).reset_index()

# Normalize dot size
min_size = 4
max_size = 30
q_min = df_3d["OrderQuantity"].min()
q_max = df_3d["OrderQuantity"].max()
df_3d["Size"] = ((df_3d["OrderQuantity"] - q_min) / (q_max - q_min)) * (max_size - min_size) + min_size

# Get distinct colors per region
region_colors = {
    region: color for region, color in zip(
        df_3d["Region"].unique(),
        px.colors.qualitative.Plotly
    )
}

# Build 3D scatter with legend
fig = go.Figure()

for region in df_3d["Region"].unique():
    sub = df_3d[df_3d["Region"] == region]
    fig.add_trace(go.Scatter3d(
        x=sub["ProductName"],
        y=[region] * len(sub),
        z=sub["OrderQuantity"],
        mode="markers",
        marker=dict(
            size=sub["Size"],
            color=region_colors[region],
            opacity=0.75
        ),
        name=region,
        showlegend=True,
        text=sub["ProductName"] + " / " + region
    ))

# Layout & camera
fig.update_layout(
    height=750,
    margin=dict(l=0, r=0, t=40, b=0),
    title=dict(
        text="3D Sales Volume: Product vs Region<br><sub>Bubble size = order volume</sub>",
        x=0.5
    ),
    scene=dict(
        xaxis=dict(title="Product", tickangle=30, tickfont=dict(size=10)),
        yaxis=dict(title="Region", tickangle=30, tickfont=dict(size=10)),
        zaxis=dict(title="Order Quantity", tickfont=dict(size=10)),
        camera=dict(eye=dict(x=2.1, y=2.1, z=1.4))
    ),
    legend=dict(title="Region", x=0.85, y=0.95)
)

# Show in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Save HTML


html_buffer = io.StringIO()
fig.write_html(html_buffer)
html_bytes = html_buffer.getvalue().encode()

st.download_button(
    label="📥 Download 3D Chart as HTML",
    data=html_bytes,
    file_name="3d_sales_volume_product_region.html",
    mime="text/html"
)
