import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Đặt cấu hình cho ứng dụng Streamlit
st.set_page_config(page_title="Analytics Dashboard", page_icon="🌎", layout="wide")
st.subheader("📈 Analytics Dashboard ")

# Tải dữ liệu từ file CSV
df = pd.read_csv("equipment_list.csv")

# Danh sách ma_id cần sử dụng
ma_id_list = [
    "ICP-MS", "IC-Anion", "INS003", "LC-MSMS-114", "LC-MSMS-105",
    "GC-MSMS-141", "GC-MSMS-109", "GC-MSMS-108", "LC-MSMS-50",
    "GC-MSMS-79", "GC-MSMS-47", "GC-MSMS-131", "HPLC-FLD106",
    "HPLC-FLD99", "HPLC-FLD-IR101", "HPLC-UV103", "GC-FID60",
    "HPLC-UV98", "HPLC-UV100", "GC-FID9", "HPLC-139",
    "MOAH-MOSH-111", "LC-MSMS-119", "IC-5", "GC-MSMS144"
]

# Lọc dữ liệu dựa trên danh sách ID
filtered_df = df[df['ID'].isin(ma_id_list)]

# Các cột mới để vẽ biểu đồ
columns_to_plot = ['Non-schedule time (min)', 'Non Production time (min)', 'Set up & cleaning time', 
                   'DowntimeBreakdown', 'Quality losses (min)', 'Net Prod Time (min)']
devices = filtered_df['ID']
percentages = filtered_df[columns_to_plot]

# Các nhóm ma_id
ma_groups = {
    "HCMCHEM": {"ICP-MS", "IC-Anion"},
    "HCMPEST": {"INS003", "LC-MSMS-114", "LC-MSMS-105", "GC-MSMS-141", "GC-MSMS-109", "GC-MSMS-108",
                "LC-MSMS-50", "GC-MSMS-79", "GC-MSMS-47", "GC-MSMS-131", "HPLC-FLD106"},
    "HCMMYCO": {"HPLC-FLD99", "HPLC-FLD-IR101", "HPLC-UV103", "GC-FID60", "HPLC-UV98", "HPLC-UV100", "GC-FID9", "HPLC-139"},
    "RD": {"MOAH-MOSH-111", "LC-MSMS-119", "IC-5", "GC-MSMS144"}
}

# Chuyển đổi tất cả các cột trong columns_to_plot thành số, nếu cần
for col in columns_to_plot:
    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')

# Tính phần trăm cho từng giá trị
min_by_month = filtered_df['Calendar time']
percentages = (filtered_df[columns_to_plot].div(min_by_month, axis=0)) * 100

# Chú thích màu cho từng cột
color_map = {
    'Non-schedule time (min)': 'black',  # Không hiển thị số
    'Set up & cleaning time': 'gray',     # Không hiển thị số
    'Quality losses (min)': 'lightblue',
    'Non Production time (min)': 'orange',
    'DowntimeBreakdown': 'red',           # Không hiển thị số
    'Net Prod Time (min)': 'limegreen'
}

# Tạo selectbox để người dùng chọn nhóm ma_id
selected_group = st.selectbox("Chọn Phòng Ban", list(ma_groups.keys()))

# Lọc các ma_id trong nhóm được chọn
filtered_ma_ids = ma_groups[selected_group]
filtered_data = df[df['ID'].isin(filtered_ma_ids)]

# Vẽ biểu đồ dạng cột stacked
plt.figure(figsize=(15, 8))
bottoms = pd.Series([0] * len(devices), dtype='float')  # Đảm bảo bottoms là số

for col in columns_to_plot:
    plt.bar(devices, percentages[col], bottom=bottoms, label=col, color=color_map[col], alpha=0.85)
    
    # Thêm số phần trăm vào từng cột, ngoại trừ những cột không hiển thị số
    if col not in ['Non-schedule time (min)', 'Set up & cleaning time', 'DowntimeBreakdown']:
        for i, value in enumerate(percentages[col]):
            if not pd.isna(value):  # Kiểm tra giá trị hợp lệ
                plt.text(devices.iloc[i], bottoms.iloc[i] + value / 2, f'{value:.1f}%', 
                         ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    
    # Cập nhật bottoms cho vòng lặp tiếp theo
    bottoms += percentages[col]

# Thêm tiêu đề và chú thích
plt.title('Comparison of Time Metrics by Equipment', fontsize=14)
plt.ylabel('Percentage (%)', fontsize=12)
plt.xlabel('Equipment ID', fontsize=12)
plt.xticks(rotation=90)
plt.legend(title="Metrics", bbox_to_anchor=(1.05, 1), loc='upper left')

# Hiển thị biểu đồ
st.pyplot(plt)

# Hiển thị bảng dữ liệu dưới dạng phần trăm trong Streamlit mà không thay đổi dữ liệu gốc
st.subheader("📊 Data Table")
# Chuyển đổi các giá trị phần trăm thành chuỗi khi hiển thị trong bảng
percentages_display = percentages.applymap(lambda x: f'{x:.1f}%')

# Thêm cột ID vào bảng
percentages_display['ID'] = filtered_df['ID']

# Hiển thị bảng dữ liệu đã lọc
st.write(f"Dữ liệu cho nhóm {selected_group}:")
st.dataframe(filtered_data)

# Hiển thị bảng dữ liệu dưới dạng phần trăm
st.dataframe(percentages_display, width=1200, height=600)
