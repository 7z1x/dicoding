import pandas as pd
import os
os.system("pip install matplotlib")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib.request

sns.set(style='dark')


# Helper function
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df


def get_top_bottom_categories(df):
    sum_order_items_df = (
        df.groupby("product_category_name_english")["order_item_id"]
        .sum()
        .reset_index()
    )
    return sum_order_items_df


def calculate_inactive_customers(df, date_col="order_purchase_timestamp", customer_col="customer_id", months=3):
    latest_date = df[date_col].max()
    cutoff_date = latest_date - pd.DateOffset(months=months)

    active_customers = df[df[date_col] >= cutoff_date][customer_col].unique()
    total_customers = df[customer_col].nunique()

    inactive_customers = total_customers - len(active_customers)
    inactive_percentage = (inactive_customers / total_customers) * 100

    return len(active_customers), inactive_customers, inactive_percentage, total_customers


def get_top_cities_and_states(df):
    # Hitung jumlah pesanan per kota
    city_orders = df.groupby("customer_city_x")["order_id"].nunique().reset_index()
    city_orders = city_orders.rename(columns={"order_id": "total_orders"})
    city_orders = city_orders.sort_values(by="total_orders", ascending=False)

    # Hitung jumlah pesanan per negara bagian
    state_orders = df.groupby("customer_state_x")["order_id"].nunique().reset_index()
    state_orders = state_orders.rename(columns={"order_id": "total_orders"})
    state_orders = state_orders.sort_values(by="total_orders", ascending=False)

    return city_orders, state_orders


def get_top_customers(df, top_n=5):
    customer_spending = df.groupby("customer_id", as_index=False)["payment_value"].sum()
    customer_spending = customer_spending.merge(
        df[["customer_id", "customer_unique_id", "customer_city_x", "customer_state_x"]].drop_duplicates(),
        on="customer_id",
        how="left")
    customer_spending = customer_spending.sort_values(by="payment_value", ascending=False)

    return customer_spending.head(top_n)


def brazil_state_map(data):
    brazil = mpimg.imread(urllib.request.urlopen(
        'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    ), 'jpg')

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(
        data["geolocation_lng"],
        data["geolocation_lat"],
        alpha=0.3, s=0.3, c='blue'
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(brazil, extent=(-73.98283055, -33.8, -33.75116944, 5.4))
    st.pyplot(fig)
