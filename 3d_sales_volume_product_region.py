import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Set Streamlit page config
st.set_page_config(layout="wide")
st.title("3D Sales Volume: Product vs Region")
st.markdown("**Files used: Sales, Territories, Customers, Products**")

# Load and clean data
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

# Merge datasets
merged = sales.merge(customers, on="CustomerKey", how="left") \
              .merge(territories, on="TerritoryKey", how="left") \
              .merge(products, on="ProductKey", how="left")

# Group and aggregate for plotting
df_3d = merged.groupby(["ProductName", "Region"]).agg({"OrderQuantity": "sum"}).reset_index()

# Scale dot size based on OrderQuantity
sizes = df_3d["OrderQuantity"] / df_3d["OrderQuantity"].max() * 20

# Generate 3D plot
fig = go.Figure(data=[go.Scatter3d(
    x=df_3d["ProductName"],
    y=df_3d["Region"],
    z=df_3d["OrderQuantity"],
    mode="markers",
    marker=dict(
        size=sizes,
        color=df_3d["Region"].astype("category").cat.codes,
        colorscale="Rainbow",
        opacity=0.8
    ),
    text=df_3d["ProductName"] + " / " + df_3d["Region"]
)])

fig.update_layout(
    title=dict(
        text="3D Sales Volume: Product vs Region<br><sub>Files used: Sales, Territories, Customers, Products</sub>",
        x=0.5,
        xanchor='center'
    ),
    scene=dict(
        xaxis=dict(title=dict(text="Product"), tickangle=30, tickfont=dict(size=10)),
        yaxis=dict(title=dict(text="Region"), tickangle=30, tickfont=dict(size=10)),
        zaxis=dict(title=dict(text="Order Quantity"), tickfont=dict(size=10)),
        camera=dict(eye=dict(x=2, y=2, z=1))
    ),
    margin=dict(l=0, r=0, b=0, t=60),
    height=800
)

# Render in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Optionally export
if st.button("Download HTML Report"):
    fig.write_html("3d_sales_volume_product_region.html")
    st.success("HTML file saved as 3d_sales_volume_product_region.html")
