import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from helper import create_daily_orders_df, get_top_bottom_categories, calculate_inactive_customers, brazil_state_map, \
    get_top_cities_and_states, get_top_customers

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
                 "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("dasboard/data/all_data.csv")
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('dasboard/data/geo_data.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Sidebar
with st.sidebar:
    st.title("Zulfahmi M. Ardianto")
    st.image("dasboard/dashboard/logo.png")
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = get_top_bottom_categories(main_df)
active_customers, inactive_customers, inactive_percentage, total_customers = calculate_inactive_customers(main_df)
city_orders, state_orders = get_top_cities_and_states(main_df)
top_customer = get_top_customers(main_df)

# Dashboard
st.header('E-Commerce Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Best & Worst Performing Products
st.subheader("Best & Worst Performing Products 🏆📉")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_item_id", y="product_category_name_english",
            data=sum_order_items_df.sort_values(by="order_item_id", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="order_item_id", y="product_category_name_english",
            data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Customer Activity in Last 3 Months
st.subheader("Purchases in The Last 3 Months 📊")

col1, col2 = st.columns(2)

with col1:
    st.metric("Active Customers", value=active_customers)

with col2:
    st.metric("Inactive Customers", value=inactive_customers)

# Pie chart
labels = ["Melakukan Pembelian", "Tidak Melakukan Pembelian"]
sizes = [active_customers, inactive_customers]
colors = ["#5CB338", "#FB4141"]

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct=lambda p: f'{math.floor(p)}%',
    startangle=140
)

ax.set_title("Berapa Persen Yang Melakukan Pembelian Dalam 3 Bulan Terakhir")
st.pyplot(fig)

# Top customer
st.subheader("Top 5 Customers by Spending 💰")
fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(
    x=top_customer["customer_id"],
    y=top_customer["payment_value"],
    palette="Blues_r",
    ax=ax
)

ax.set_title("10 Pelanggan dengan Total Pembelian Tertinggi", fontsize=15)
ax.set_xlabel("Customer ID")
ax.set_ylabel("Total Pembelian (Revenue)")
ax.set_xticklabels(top_customer["customer_id"], rotation=90)
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)

# Menampilkan kota dan negara bagian
st.subheader("Customer Demographics 🌍")
tab1, tab2 = st.tabs(["City & State", "Geolocation"])

with tab1:
    st.subheader("Customer Dengan Kota dan Negara Bagian Terbanyak")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))

    colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="total_orders", y="customer_city_x",
                data=city_orders.head(5), palette=colors,
                ax=ax[0])
    ax[0].set_title("10 Kota dengan Pesanan Terbanyak", fontsize=14)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("10 Kota dengan Pesanan Terbanyak:", loc="center", fontsize=25)
    ax[0].tick_params(axis='y', labelsize=20)
    ax[0].tick_params(axis='x', labelsize=20)

    sns.barplot(x="total_orders", y="customer_state_x", data=state_orders.head(5), palette=colors, ax=ax[1])
    ax[1].set_title("10 Negara Bagian dengan Pesanan Terbanyak", fontsize=14)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("10 Negara Bagian dengan Pesanan Terbanyak", loc="center", fontsize=25)
    ax[1].tick_params(axis='y', labelsize=20)
    ax[1].tick_params(axis='x', labelsize=20)

    st.pyplot(fig)

with tab2:
    # Map
    brazil_state_map(data)
    with st.expander("See Explanation"):
        st.write(
            'Dominasi São Paulo menunjukkan bahwa aktivitas e-commerce paling tinggi terjadi di wilayah ini, '
            'baik dari segi kota maupun negara bagian.')

st.caption('Copyright (C) Zulfahmi M. A. 2024')
