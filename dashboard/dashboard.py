import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Fungsi untuk menghitung status pelanggan
def get_customers_status(orders, customers):
  active_customer = orders['customer_id'].drop_duplicates().reset_index(drop=True)
  inactive_customer = customers[~customers['customer_id'].isin(active_customer)]['customer_id'].reset_index(drop=True)
  return active_customer, inactive_customer

# Fungsi untuk menghitung jumlah pelanggan yang aktif dan kurang aktif melakukan pembelian tiap hari
def get_daily_customers_count(orders, customers):
  daily_active_customers = {}
  daily_inactive_customers = {}

  start_date = orders['date'].min()
  end_date = orders['date'].max()
  date_range = pd.date_range(start=start_date, end=end_date).date

  all_customers = set(df_customers['customer_id'].unique())
  for date in date_range:
    active_customers_on_date = set(orders[orders['date'] == date]['customer_id'].unique())
    daily_active_customers[date] = len(active_customers_on_date)
  
    inactive_customers_on_date = all_customers - active_customers_on_date
    daily_inactive_customers[date] = len(inactive_customers_on_date)

  daily_active_customers = pd.Series(daily_active_customers)
  daily_inactive_customers = pd.Series(daily_inactive_customers)
  return daily_active_customers, daily_inactive_customers

# Fungsi untuk menghitung status kota
def get_cities_status(orders, customers, inactive_customer):
  active_customer_city = orders.groupby('customer_city')['customer_id'].nunique().sort_values(ascending=False)
  inactive_customer_city = customers[customers['customer_id'].isin(inactive_customer)].groupby('customer_city')['customer_id'].nunique().sort_values(ascending=False)
  return active_customer_city, inactive_customer_city

# Fungsi untuk menghitung status negara bagian
def get_states_status(orders, customers, inactive_customer):
  active_customer_state = orders.groupby('customer_state')['customer_id'].nunique().sort_values(ascending=False)
  inactive_customer_state = customers[customers['customer_id'].isin(inactive_customer)].groupby('customer_state')['customer_id'].nunique().sort_values(ascending=False)
  return active_customer_state, inactive_customer_state

# Memuat data
df_customers = pd.read_csv('customers_final.csv')
df_order_customer = pd.read_csv('order_customer_2018_final.csv')
df_order_customer['date'] = pd.to_datetime(df_order_customer['date'], errors='coerce').dt.date

# Sidebar rentang waktu
min_date = df_order_customer['date'].min()
max_date = df_order_customer['date'].max()

with st.sidebar:
  st.image("k-logo.png")
  start_date, end_date = st.date_input('Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date])

# Filter berdasarkan rentang tanggal
df_order_customer_filtered = df_order_customer[(df_order_customer['date'] >= start_date) &
                                               (df_order_customer['date'] <= end_date)]

# Hitung status pelanggan, kota, dan negara bagian
active_customer, inactive_customer = get_customers_status(df_order_customer_filtered, df_customers)
active_customer_city, inactive_customer_city = get_cities_status(df_order_customer_filtered, df_customers, inactive_customer)
active_customer_state, inactive_customer_state = get_states_status(df_order_customer_filtered, df_customers, inactive_customer)


# Visualisasi 1: Pie Chart untuk Pelanggan Aktif vs Kurang Aktif
st.subheader('Pelanggan Aktif vs Pelanggan Kurang Aktif')
st.write(f'Rentang waktu: {start_date} - {end_date}')

labels = [f'Aktif: \n{len(active_customer)} customer', f'Kurang Aktif: \n{len(inactive_customer)} customer']
sizes = [len(active_customer), len(inactive_customer)]
colors = ['#44AA44', '#FF4444']

fig1, ax1 = plt.subplots(figsize=(8, 6))
ax1.pie(sizes, labels=labels, autopct='%.2f%%', startangle=90, colors=colors, wedgeprops={'edgecolor': 'black'})
ax1.set_title('Pelanggan Aktif vs Pelanggan Kurang Aktif Tahun 2018')
st.pyplot(fig1)



# Visualisasi 2: Grafik Garis untuk Pelanggan Aktif vs Kurang Aktif Harian
st.subheader('Pelanggan Aktif vs Kurang Aktif per Tanggal')
st.write(f'Rentang waktu: {start_date} - {end_date}')

daily_active_customers, daily_inactive_customers = get_daily_customers_count(df_order_customer_filtered, df_customers)

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(daily_active_customers.index, daily_active_customers.values, label='Aktif', color='#44AA44')
ax2.plot(daily_inactive_customers.index, daily_inactive_customers.values, label='Kurang Aktif', color='#FF4444')

ax2.set_title('Pelanggan Aktif vs Pelanggan Kurang Aktif per Tanggal')
ax2.set_xlabel('Tanggal')
ax2.set_ylabel('Jumlah Pelanggan')
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.legend()
plt.xticks(rotation=45)

st.pyplot(fig2)



# Visualisasi 3: Bar Chart untuk 5 Kota Teratas
st.subheader('5 Kota Teratas dengan Pelanggan Aktif dan Kurang Aktif')
st.write(f'Rentang waktu: {start_date} - {end_date}')

top_active_customer_city = active_customer_city.head(5)
top_inactive_customer_city = inactive_customer_city.head(5)
max_ytick_city = max(top_active_customer_city.max(), top_inactive_customer_city.max())

fig3, axs3 = plt.subplots(1, 2, figsize=(14, 6))

# Kota Aktif
axs3[0].bar(top_active_customer_city.index, top_active_customer_city.values, color='#44AA44')
axs3[0].set_title('Kota dengan Pelanggan Aktif Terbanyak')
axs3[0].tick_params(axis='x', rotation=45)
axs3[0].set_xlabel('Kota')
axs3[0].set_ylabel('Jumlah Pelanggan Aktif')

# Kota Inaktif
axs3[1].bar(top_inactive_customer_city.index, top_inactive_customer_city.values, color='#FF4444')
axs3[1].set_title('Kota dengan Pelanggan Kurang Aktif Terbanyak')
axs3[1].tick_params(axis='x', rotation=45)
axs3[1].set_xlabel('Kota')
axs3[1].set_ylabel('Jumlah Pelanggan Kurang Aktif')

plt.tight_layout()
st.pyplot(fig3)



# Visualisasi 4: Bar Chart untuk 5 Negara Bagian Teratas
st.subheader('5 Negara Bagian Teratas dengan Pelanggan Aktif dan Kurang Aktif')
st.write(f'Rentang waktu: {start_date} - {end_date}')

top_active_customer_state = active_customer_state.head(5)
top_inactive_customer_state = inactive_customer_state.head(5)
max_ytick_state = max(top_active_customer_state.max(), top_inactive_customer_state.max())

fig4, axs4 = plt.subplots(1, 2, figsize=(14, 6))

# Negara Bagian Aktif
axs4[0].bar(top_active_customer_state.index, top_active_customer_state.values, color='#44AA44')
axs4[0].set_title('Negara Bagian dengan Pelanggan Aktif Terbanyak')
axs4[0].tick_params(axis='x', rotation=45)
axs4[0].set_xlabel('Negara Bagian')
axs4[0].set_ylabel('Jumlah Pelanggan Aktif')

# Negara Bagian Inaktif
axs4[1].bar(top_inactive_customer_state.index, top_inactive_customer_state.values, color='#FF4444')
axs4[1].set_title('Negara Bagian dengan Pelanggan Kurang Aktif Terbanyak')
axs4[1].tick_params(axis='x', rotation=45)
axs4[1].set_xlabel('Negara Bagian')
axs4[1].set_ylabel('Jumlah Pelanggan Kurang Aktif')

plt.tight_layout()
st.pyplot(fig4)
