import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ======================
# COLOR PALETTE
# ======================
# KPI
PINK = "#F8C8DC"
YELLOW = "#FCEFB4"
BEIGE = "#E9D5C1"
TEXT = "#4A3F35"

# Transaction Analysis
ORDER_LINE = "#F4A6B8"      # soft coral
REVENUE_BAR = "#F3BF78"    

# RFM Segment Colors (CONSISTENT)
SEGMENT_COLORS = {
    "At Risk": "#F2B5C4",      # dusty rose
    "Potential": "#D6CDEA",    # soft lavender
    "Loyal": "#CFE3D4"         # soft sage
}

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# ======================
# CUSTOM CSS
# ======================
st.markdown(f"""
<style>
.main {{
    background-color: #F7EFE5;
}}

section[data-testid="stSidebar"] {{
    background-color: #EFE6DD;
}}

.kpi-card {{
    padding: 25px;
    border-radius: 20px;
}}

.kpi-card-1 {{ background-color: {PINK}; }}
.kpi-card-2 {{ background-color: {YELLOW}; }}
.kpi-card-3 {{ background-color: {BEIGE}; }}

.kpi-title {{
    font-size: 14px;
    color: {TEXT};
}}

.kpi-value {{
    font-size: 28px;
    font-weight: 600;
    color: #2F2A26;
}}
</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# ======================
# HEADER
# ======================
st.markdown("## E-Commerce Performance Dashboard")

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.title("Filter Date")

min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

filtered_df = df[
    (df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
    (df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
].copy()

# ======================
# KPI SECTION
# ======================
total_revenue = filtered_df['payment_value'].sum()
total_orders = filtered_df['order_id'].nunique()
total_customers = filtered_df['customer_unique_id'].nunique()

col1, col2, col3 = st.columns(3)

for col, title, value, color in zip(
    [col1, col2, col3],
    ["Total Revenue", "Total Orders", "Total Customers"],
    [f"R$ {total_revenue:,.0f}", f"{total_orders:,}", f"{total_customers:,}"],
    ["kpi-card-1", "kpi-card-2", "kpi-card-3"]
):
    with col:
        st.markdown(f"""
        <div class="kpi-card {color}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# TABS
# ======================
tab1, tab2 = st.tabs(["Transaction Analysis", "Customer Segmentation"])

# ======================
# TAB 1 – TRANSACTION ANALYSIS
# ======================
with tab1:

    filtered_df['order_month'] = filtered_df['order_purchase_timestamp'].dt.to_period("M")

    monthly = filtered_df.groupby('order_month').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).reset_index()

    monthly['order_month'] = monthly['order_month'].astype(str)

    colA, colB = st.columns(2)

    # Monthly Orders
    with colA:
        fig1, ax1 = plt.subplots(figsize=(5,3))
        ax1.plot(
            monthly['order_month'],
            monthly['order_id'],
            color=ORDER_LINE,
            linewidth=3
        )
        ax1.set_title("Monthly Orders", color=TEXT)
        ax1.spines[['top','right']].set_visible(False)
        ax1.grid(axis='y', alpha=0.2)
        ax1.set_xticks(range(0, len(monthly), 2))
        ax1.set_xticklabels(monthly['order_month'][::2], rotation=45)
        st.pyplot(fig1)

    # Monthly Revenue
    with colB:
        fig2, ax2 = plt.subplots(figsize=(5,3))
        ax2.bar(
            monthly['order_month'],
            monthly['payment_value'],
            color=REVENUE_BAR
        )
        ax2.set_title("Monthly Revenue", color=TEXT)
        ax2.spines[['top','right']].set_visible(False)
        ax2.grid(axis='y', alpha=0.2)
        ax2.set_xticks(range(0, len(monthly), 2))
        ax2.set_xticklabels(monthly['order_month'][::2], rotation=45)
        st.pyplot(fig2)

# ======================
# TAB 2 – CUSTOMER SEGMENTATION (RFM)
# ======================
with tab2:

    snapshot_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm = filtered_df.groupby('customer_unique_id').agg({
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

    colC, colD = st.columns(2)

    # ======================
    # CUSTOMER DISTRIBUTION
    # ======================
    with colC:
        st.markdown("#### Customer Distribution")

        segment_pct = (
            rfm['Segment']
            .value_counts(normalize=True)
            .mul(100)
            .sort_values(ascending=False)
        )

        colors = [SEGMENT_COLORS[s] for s in segment_pct.index]

        fig3, ax3 = plt.subplots(figsize=(4.5,3))
        ax3.barh(segment_pct.index, segment_pct.values, color=colors)

        for i, v in enumerate(segment_pct.values):
            ax3.text(v + 0.5, i, f"{v:.1f}%", va='center', color=TEXT)

        ax3.invert_yaxis()
        ax3.set_xlabel("Percentage (%)", color=TEXT)
        ax3.spines[['top','right']].set_visible(False)
        ax3.grid(axis='x', alpha=0.2)

        st.pyplot(fig3)

    # ======================
    # REVENUE CONTRIBUTION
    # ======================
    with colD:
        st.markdown("#### Revenue Contribution")

        segment_rev_pct = (
            rfm.groupby("Segment")["Monetary"]
            .sum()
            .pipe(lambda x: x / x.sum() * 100)
            .sort_values(ascending=False)
        )

        colors = [SEGMENT_COLORS[s] for s in segment_rev_pct.index]

        fig4, ax4 = plt.subplots(figsize=(4.5,3))
        ax4.barh(segment_rev_pct.index, segment_rev_pct.values, color=colors)

        for i, v in enumerate(segment_rev_pct.values):
            ax4.text(v + 0.5, i, f"{v:.1f}%", va='center', color=TEXT)

        ax4.invert_yaxis()
        ax4.set_xlabel("Revenue (%)", color=TEXT)
        ax4.spines[['top','right']].set_visible(False)
        ax4.grid(axis='x', alpha=0.2)

        st.pyplot(fig4)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.markdown("Submission Project – Dicoding Data Analysis")
st.markdown("By Shyfa Salsabila")

