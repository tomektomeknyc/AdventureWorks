import pandas as pd
import plotly.graph_objects as go

# Load datasets
sales_2021 = pd.read_csv("files/sales_2021.csv")
sales_2022 = pd.read_csv("files/sales_2022.csv")
products = pd.read_csv("files/AdventureWorks Product Lookup.csv")
territories = pd.read_csv("files/AdventureWorks Territory Lookup.csv")
customers = pd.read_csv("files/AdventureWorks Customer Lookup.csv", encoding="ISO-8859-1")

# Combine sales
sales = pd.concat([sales_2021, sales_2022], ignore_index=True)

# Clean and standardize
territories.rename(columns={"SalesTerritoryKey": "TerritoryKey"}, inplace=True)
customers.rename(columns={"CustomerID": "CustomerKey"}, inplace=True)
customers = customers.dropna(subset=["CustomerKey"])
customers = customers[customers["CustomerKey"].astype(str).str.match(r"^\d+$")]
customers["CustomerKey"] = customers["CustomerKey"].astype(int)

# Merge everything
merged = sales.merge(customers, on="CustomerKey", how="left") \
              .merge(territories, on="TerritoryKey", how="left") \
              .merge(products, on="ProductKey", how="left")

# Aggregate order quantity
df_3d = merged.groupby(["ProductName", "Region"]).agg({
    "OrderQuantity": "sum"
}).reset_index()

# Create 3D scatter plot (1 trace per region)
fig = go.Figure()

for region in df_3d["Region"].unique():
    region_data = df_3d[df_3d["Region"] == region]

    fig.add_trace(go.Scatter3d(
        x=region_data["ProductName"],
        y=[region] * len(region_data),
        z=region_data["OrderQuantity"],
        mode="markers",
        name=region,
        marker=dict(
            size=region_data["OrderQuantity"] / 50,  # scale size by volume
            opacity=0.8
        ),
        text=region_data["ProductName"] + " / " + region
    ))

# Layout and camera
fig.update_layout(
    title=dict(
        text="3D Sales Volume: Product vs Region<br><sub>Files used in merge: ...</sub>",
        x=0.5,
        xanchor='center'
    ),
   scene=dict(
    xaxis=dict(
        title=dict(text="Product"),
        tickangle=30,
        tickfont=dict(size=10)
    ),
    yaxis=dict(
        title=dict(text="Region"),
        tickangle=30,
        tickfont=dict(size=10)
    ),
    zaxis=dict(
        title=dict(text="Order Quantity"),
        tickfont=dict(size=10)
    ),
    camera=dict(
        eye=dict(x=2, y=2, z=1)
    )
)

)


# Export to HTML
fig.write_html("3d_sales_volume_product_region.html")
