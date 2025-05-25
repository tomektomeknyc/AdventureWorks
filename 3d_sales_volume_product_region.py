import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Title
st.title("📊 3D Sales Volume: Product vs Region")
st.caption("Files used: Sales, Territories, Customers, Products")

# Load data
sales_2021 = pd.read_csv("files/sales_2021.csv")
sales_2022 = pd.read_csv("files/sales_2022.csv")
sales = pd.concat([sales_2021, sales_2022], ignore_index=True)
products = pd.read_csv("files/AdventureWorks Product Lookup.csv")
territories = pd.read_csv("files/AdventureWorks Territory Lookup.csv")
customers = pd.read_csv("files/AdventureWorks Customer Lookup.csv", encoding="ISO-8859-1")

# Clean and merge
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

# Plot with legend (one trace per Region)
fig = go.Figure()

for region in df_3d["Region"].unique():
    subset = df_3d[df_3d["Region"] == region]
    fig.add_trace(go.Scatter3d(
        x=subset["ProductName"],
        y=[region] * len(subset),
        z=subset["OrderQuantity"],
        mode="markers",
        marker=dict(
            size=subset["OrderQuantity"] / 100 + 2,  # Scaled by value
            opacity=0.8,
        ),
        name=region,  # <- this shows in legend
        showlegend=True,
        text=subset["ProductName"] + " / " + region
    ))

# Layout
fig.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    height=700,
    title=dict(
        text="3D Sales Volume: Product vs Region<br><sub>Interactive with toggleable regions</sub>",
        x=0.5
    ),
    scene=dict(
        xaxis=dict(title="Product", tickangle=30, tickfont=dict(size=10)),
        yaxis=dict(title="Region", tickangle=30, tickfont=dict(size=10)),
        zaxis=dict(title="Order Quantity", tickfont=dict(size=10)),
        camera=dict(eye=dict(x=2, y=2, z=1))
    ),
    showlegend=True,
    legend=dict(title="Region", x=0.85, y=0.95)
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Save to HTML with button
if st.button("📥 Download HTML"):
    fig.write_html("3d_sales_volume_product_region.html")
    st.success("HTML file generated.")
