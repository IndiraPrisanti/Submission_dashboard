import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set Konfigurasi Halaman
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# load data
def load_data():
    df_reviews = pd.read_csv('order_reviews_dataset.csv')
    df_orders = pd.read_csv('orders_dataset.csv')
    
    # Konversi kolom tanggal
    df_reviews['review_creation_date'] = pd.to_datetime(df_reviews['review_creation_date'])
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    
    return df_reviews, df_orders

df_reviews, df_orders = load_data()

# Header Dashboard
st.header('E-Commerce Data Analysis Dashboard 📊')
st.subheader('Analisis Kepuasan Pelanggan & Tren Order')

# Sidebar untuk Filter Tahun
with st.sidebar:
    st.markdown("## 📊")

    year_selected = st.selectbox(
        "📅 Pilih Tahun Analisis",
        options=[2017, 2018],
        index=1
    )

# --- BAGIAN 1: Rata-rata Skor Kepuasan ---
st.markdown(f"### Skor Rata-rata Kepuasan Pelanggan Tahun {year_selected}")

# Filter data berdasarkan tahun
reviews_filtered = df_reviews[df_reviews['review_creation_date'].dt.year == year_selected]
avg_score = reviews_filtered['review_score'].mean()

# Tampilkan Metric
col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"Rata-rata Rating {year_selected}", value=f"{avg_score:.2f} / 5.0")

# Visualisasi Distribusi Rating
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.countplot(data=reviews_filtered, x='review_score', palette='viridis', ax=ax1)
ax1.set_title(f'Distribusi Skor Review Tahun {year_selected}')
ax1.set_xlabel('Skor Rating')
ax1.set_ylabel('Jumlah Review')
st.pyplot(fig1)

# --- BAGIAN 2: Tren Order Per Bulan ---
st.markdown(f"### Tren Jumlah Order Bulanan Tahun {year_selected}")

# Filter dan Grouping Data Order
orders_filtered = df_orders[df_orders['order_purchase_timestamp'].dt.year == year_selected].copy()
orders_filtered['month'] = orders_filtered['order_purchase_timestamp'].dt.month_name()
# Mengurutkan bulan
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_orders = orders_filtered.groupby('month').size().reindex(month_order).fillna(0)

# Visualisasi Line Chart Tren Order
fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.plot(monthly_orders.index, monthly_orders.values, marker='o', linewidth=2, color='#3970F1')
ax2.set_title(f'Tren Jumlah Order per Bulan di Tahun {year_selected}', fontsize=15)
ax2.set_xlabel('Bulan')
ax2.set_ylabel('Total Order')
plt.xticks(rotation=45)
st.pyplot(fig2)

# --- Kesimpulan Berdasarkan Analisis Notebook ---
st.markdown("---")
st.markdown("#### Insight Utama:")
st.info("""
- **Kepuasan Pelanggan:** Terjadi sedikit penurunan skor rating pada tahun 2018 dibandingkan tahun sebelumnya.
- **Tren Operasional:** Terjadi penurunan signifikan pada jumlah order di bulan September.
""")

st.caption('Copyright (C) Indira Putri Dewi Prisanti 2026')