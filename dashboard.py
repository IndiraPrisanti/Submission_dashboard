import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide",
)

# Load & Cache Data
@st.cache_data
def load_data():
    df_reviews = pd.read_csv("order_reviews_dataset.csv")
    df_orders  = pd.read_csv("orders_dataset.csv")

    # Konversi kolom datetime — reviews
    for col in ["review_creation_date", "review_answer_timestamp"]:
        df_reviews[col] = pd.to_datetime(df_reviews[col])

    # Konversi kolom datetime — orders
    for col in [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        df_orders[col] = pd.to_datetime(df_orders[col], errors="coerce")

    # Kolom bantu
    df_reviews["year"]  = df_reviews["review_creation_date"].dt.year
    df_reviews["month"] = df_reviews["review_creation_date"].dt.month
    df_reviews["month_name"] = df_reviews["review_creation_date"].dt.strftime("%B")

    df_orders["year"]  = df_orders["order_purchase_timestamp"].dt.year
    df_orders["month"] = df_orders["order_purchase_timestamp"].dt.month
    df_orders["month_name"] = df_orders["order_purchase_timestamp"].dt.strftime("%B")
    df_orders["date"]  = df_orders["order_purchase_timestamp"].dt.date

    return df_reviews, df_orders

df_reviews, df_orders = load_data()

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Header
st.title("📊 E-Commerce Data Analysis Dashboard")
st.markdown("**Analisis Kepuasan Pelanggan & Tren Order** — *Interaktif & Dinamis*")
st.divider()

# Sidebar — Filter Panel
with st.sidebar:
    st.header("🎛️ Panel Filter")

    # Filter Tahun
    available_years = sorted(df_reviews["year"].dropna().unique().tolist())
    year_selected = st.selectbox("📅 Pilih Tahun", options=available_years, index=len(available_years) - 1)

    # Filter Bulan
    available_months = ["Semua Bulan"] + MONTH_ORDER
    month_selected = st.selectbox("🗓️ Pilih Bulan", options=available_months, index=0)

    # Filter Rentang Tanggal (reviews)
    st.markdown("---")
    st.markdown("**📆 Rentang Tanggal Review**")
    date_min = df_reviews["review_creation_date"].min().date()
    date_max = df_reviews["review_creation_date"].max().date()
    date_range = st.date_input(
        "Pilih Rentang Tanggal",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    # Filter Skor Rating
    st.markdown("---")
    score_range = st.slider(
        "⭐ Rentang Skor Rating",
        min_value=1, max_value=5,
        value=(1, 5), step=1,
    )

    # Filter Status Order
    st.markdown("---")
    status_options = sorted(df_orders["order_status"].dropna().unique().tolist())
    status_selected = st.multiselect(
        "📦 Status Order",
        options=status_options,
        default=status_options,
    )

    st.markdown("---")
    st.caption("© 2026 Indira Putri Dewi Prisanti")

# Terapkan Filter
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_min
    end_date   = date_max

reviews_f = df_reviews[
    (df_reviews["year"] == year_selected) &
    (df_reviews["review_score"].between(score_range[0], score_range[1])) &
    (df_reviews["review_creation_date"].dt.date >= start_date) &
    (df_reviews["review_creation_date"].dt.date <= end_date)
]

orders_f = df_orders[
    (df_orders["year"] == year_selected) &
    (df_orders["order_status"].isin(status_selected))
]

if month_selected != "Semua Bulan":
    reviews_f = reviews_f[reviews_f["month_name"] == month_selected]
    orders_f  = orders_f[orders_f["month_name"]  == month_selected]

# Bagian 1 — KPI Metrics
st.subheader(f"📌 Ringkasan Tahun {year_selected}"
             + (f" — Bulan {month_selected}" if month_selected != "Semua Bulan" else ""))

avg_score    = reviews_f["review_score"].mean() if not reviews_f.empty else 0
total_review = len(reviews_f)
total_order  = len(orders_f)
pct_delivered = (
    (orders_f["order_status"] == "delivered").sum() / len(orders_f) * 100
    if not orders_f.empty else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("⭐ Rata-rata Rating",   f"{avg_score:.2f} / 5.0")
col2.metric("💬 Total Review",       f"{total_review:,}")
col3.metric("📦 Total Order",        f"{total_order:,}")
col4.metric("✅ % Delivered",        f"{pct_delivered:.1f}%")

st.divider()

# Bagian 2 — Kepuasan Pelanggan
st.subheader("💬 Analisis Kepuasan Pelanggan")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("##### Distribusi Skor Review")
    if not reviews_f.empty:
        dist_df = (
            reviews_f["review_score"]
            .value_counts()
            .reset_index()
            .rename(columns={"review_score": "Skor", "count": "Jumlah Review"})
            .sort_values("Skor")
        )
        fig_dist = px.bar(
            dist_df, x="Skor", y="Jumlah Review",
            color="Skor",
            color_discrete_sequence=["#0d3b8c"],
            text="Jumlah Review",
            title=f"Distribusi Rating {year_selected}",
        )
        fig_dist.update_traces(textposition="outside")
        fig_dist.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(tickmode="linear"),
            height=380,
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

with col_right:
    st.markdown("##### Rata-Rata Rating per Bulan")
    if not reviews_f.empty:
        monthly_score = (
            reviews_f.groupby("month_name")["review_score"]
            .mean()
            .reindex(MONTH_ORDER)
            .dropna()
            .reset_index()
            .rename(columns={"month_name": "Bulan", "review_score": "Rata-rata Score"})
        )
        fig_score = px.line(
            monthly_score, x="Bulan", y="Rata-rata Score",
            markers=True,
            title=f"Tren Rating Bulanan {year_selected}",
            range_y=[1, 5],
        )
        fig_score.update_traces(line_color="#3970F1", marker_size=8)
        fig_score.update_layout(height=380)
        st.plotly_chart(fig_score, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

# Rata-rata rating year-over-year (bar)
st.markdown("##### Perbandingan Rata-Rata Rating Antar Tahun")
yearly_score = (
    df_reviews[df_reviews["review_score"].between(score_range[0], score_range[1])]
    .groupby("year")["review_score"]
    .mean()
    .reset_index()
    .rename(columns={"year": "Tahun", "review_score": "Rata-rata Score"})
)
fig_yoy = px.bar(
    yearly_score, x="Tahun", y="Rata-rata Score",
    color="Rata-rata Score",
    color_continuous_scale="blues",
    text="Rata-rata Score",
    range_y=[0, 5],
    title="Rata-Rata Skor Per Tahun",
)
fig_yoy.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_yoy.update_layout(
    coloraxis_showscale=False,
    xaxis=dict(tickmode="linear"),
    height=320,
)
st.plotly_chart(fig_yoy, use_container_width=True)

st.divider()

# Bagian 3 — Tren Order
st.subheader("📦 Tren Jumlah Order")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("##### Order per Bulan")
    if not orders_f.empty:
        monthly_orders = (
            orders_f.groupby("month_name")["order_id"]
            .count()
            .reindex(MONTH_ORDER)
            .fillna(0)
            .reset_index()
            .rename(columns={"month_name": "Bulan", "order_id": "Total Order"})
        )
        fig_line = px.line(
            monthly_orders, x="Bulan", y="Total Order",
            markers=True,
            title=f"Tren Order Bulanan {year_selected}",
        )
        fig_line.update_traces(line_color="#F14F3E", marker_size=8)
        fig_line.update_layout(height=380)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

with col_b:
    st.markdown("##### Distribusi Status Order")
    if not orders_f.empty:
        status_df = (
            orders_f["order_status"]
            .value_counts()
            .reset_index()
            .rename(columns={"order_status": "Status", "count": "Jumlah"})
        )
        fig_pie = px.pie(
            status_df, names="Status", values="Jumlah",
            title=f"Proporsi Status Order {year_selected}",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_pie.update_layout(height=380)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

# Tren harian (area chart)
st.markdown("##### Tren Order Harian")
if not orders_f.empty:
    daily_orders = (
        orders_f.groupby("date")["order_id"]
        .count()
        .reset_index()
        .rename(columns={"date": "Tanggal", "order_id": "Jumlah Order"})
    )
    fig_area = px.area(
        daily_orders, x="Tanggal", y="Jumlah Order",
        title=f"Volume Order Harian {year_selected}",
        color_discrete_sequence=["#3970F1"],
    )
    fig_area.update_layout(height=300)
    st.plotly_chart(fig_area, use_container_width=True)
else:
    st.info("Tidak ada data untuk filter yang dipilih.")

st.divider()

# Bagian 4 — Tabel Data Mentah (opsional)
with st.expander("🔍 Lihat Data Mentah"):
    tab1, tab2 = st.tabs(["Reviews", "Orders"])
    with tab1:
        st.dataframe(
            reviews_f[["review_id", "review_score", "review_creation_date", "review_comment_title"]].head(200),
            use_container_width=True,
        )
    with tab2:
        st.dataframe(
            orders_f[["order_id", "order_status", "order_purchase_timestamp"]].head(200),
            use_container_width=True,
        )

# Menjawab Pertanyaan Bisnis & Insight Utama 
st.markdown("---")
st.markdown("#### 💡 Insight Utama")

insight_score_trend = ""
if len(yearly_score) >= 2:
    s1 = yearly_score.iloc[-2]["Rata-rata Score"]
    s2 = yearly_score.iloc[-1]["Rata-rata Score"]
    delta = s2 - s1
    insight_score_trend = (
        f"Skor kepuasan **{'naik' if delta >= 0 else 'turun'}** sebesar **{abs(delta):.2f}** "
        f"dari tahun {int(yearly_score.iloc[-2]['Tahun'])} ke {int(yearly_score.iloc[-1]['Tahun'])}."
    )

st.info(
    f"""
- **Pertanyaan Bisnis 1:** Terjadi sedikit penurunan skor rating pada tahun 2018 dibandingkan tahun sebelumnya.
- **Pertanyaan Bisnis 2:** Terjadi penurunan signifikan pada jumlah order di bulan September.
"""
)

st.caption("Copyright © 2026 Indira Putri Dewi Prisanti")
