import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# ======================
# HEADER
# ======================
st.title("E-Commerce Performance Dashboard")

st.markdown("""
Dashboard ini dibuat untuk menjawab dua pertanyaan bisnis:
1. Bagaimana perkembangan jumlah transaksi 2016–2018 dan apakah terdapat seasonality?
2. Pelanggan mana yang berkontribusi terbesar berdasarkan RFM (2017–2018)?
""")

st.markdown("---")

# ============================================================
# TAB SECTION
# ============================================================
tab1, tab2 = st.tabs([
    "Transaction Trend (2016–2018)",
    "Customer Segmentation RFM (2017–2018)"
])

# ============================================================
# TAB 1 – TREND & SEASONALITY
# ============================================================
with tab1:

    df_trend = df[
        (df['order_purchase_timestamp'] >= "2016-01-01") &
        (df['order_purchase_timestamp'] <= "2018-12-31")
    ].copy()

    df_trend['year_month'] = df_trend['order_purchase_timestamp'].dt.to_period("M")

    monthly = df_trend.groupby('year_month').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()

    monthly['year_month'] = monthly['year_month'].astype(str)

    # KPI Ringkas
    total_orders = df_trend['order_id'].nunique()
    total_revenue = df_trend['payment_value'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Orders (2016–2018)", f"{total_orders:,}")
    col2.metric("Total Revenue (2016–2018)", f"R$ {total_revenue:,.0f}")

    st.subheader("Monthly Orders")

    fig1, ax1 = plt.subplots(figsize=(10,4))
    ax1.plot(monthly['year_month'], monthly['order_id'])
    ax1.set_xticks(range(0, len(monthly), 3))
    ax1.set_xticklabels(monthly['year_month'][::3], rotation=45)
    ax1.set_ylabel("Number of Orders")
    ax1.grid(True)
    st.pyplot(fig1)

    st.subheader("Monthly Revenue")

    fig2, ax2 = plt.subplots(figsize=(10,4))
    ax2.bar(monthly['year_month'], monthly['payment_value'])
    ax2.set_xticks(range(0, len(monthly), 3))
    ax2.set_xticklabels(monthly['year_month'][::3], rotation=45)
    ax2.set_ylabel("Revenue (R$)")
    ax2.grid(True)
    st.pyplot(fig2)

    st.markdown("""
    **Insight:**  
    Transaksi meningkat dari 2016 ke 2018. Lonjakan transaksi terlihat konsisten 
    pada kuartal keempat setiap tahun, menunjukkan adanya pola seasonality.
    """)

# ============================================================
# TAB 2 – RFM (2017–2018 ONLY)
# ============================================================
with tab2:

    rfm_df = df[
        (df['order_purchase_timestamp'] >= "2017-01-01") &
        (df['order_purchase_timestamp'] <= "2018-12-31")
    ].copy()

    snapshot_date = rfm_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm = rfm_df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()

    rfm.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

    rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])

    def segment(row):
        if row['R_score'] == 4 and row['F_score'] >= 3:
            return "Loyal"
        elif row['R_score'] >= 3:
            return "Potential"
        else:
            return "At Risk"

    rfm['Segment'] = rfm.apply(segment, axis=1)

    # KPI RFM
    total_customers = rfm['customer_unique_id'].nunique()
    st.metric("Total Customers (2017–2018)", f"{total_customers:,}")

    col3, col4 = st.columns(2)

    # Distribution
    with col3:
        st.subheader("Customer Segment Distribution")
        segment_count = rfm['Segment'].value_counts()

        fig3, ax3 = plt.subplots()
        ax3.bar(segment_count.index, segment_count.values)
        ax3.set_ylabel("Number of Customers")
        st.pyplot(fig3)

    # Revenue Contribution
    with col4:
        st.subheader("Revenue Contribution by SegSSment")
        segment_revenue = rfm.groupby('Segment')['Monetary'].sum()

        fig4, ax4 = plt.subplots()
        ax4.bar(segment_revenue.index, segment_revenue.values)
        ax4.set_ylabel("Total Revenue (R$)")
        st.pyplot(fig4)

    st.subheader("Top 10 Customers by Monetary Value")
    top10 = rfm.sort_values(by="Monetary", ascending=False).head(10)
    st.dataframe(top10[['customer_unique_id', 'Monetary']])

    st.markdown("""
    **Insight:**  
    Segment Loyal memberikan kontribusi revenue terbesar. 
    Sebagian kecil pelanggan menyumbang proporsi pendapatan yang signifikan.
    """)

st.markdown("---")
st.caption("Submission Project – Dicoding Data Analysis | Shyfa Salsabila")