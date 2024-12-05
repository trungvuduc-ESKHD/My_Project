from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
from numerize.numerize import numerize
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

#set page
st.set_page_config(page_title="Analytics Dashboard", page_icon="🌎", layout="wide")  
st.subheader("📈 Analytics Dashboard ")

#sidebar_logo
st.sidebar.image("images/logo2.png")

# load CSS Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#get data from files
df = pd.read_excel("inventory_balance_list.xlsx")

#switcher for main dashboard
st.sidebar.header("Vui Lòng Filter")
phongban = st.sidebar.multiselect(
    "Filter Phòng Ban",
    options=df["phong_ban"].unique(),
    default=df["phong_ban"].unique(),
)
commodityy = st.sidebar.multiselect(
    "Filter Commodity",
    options=df["Commodity"].unique(),
    default=df["Commodity"].unique(),
)

# Apply the filters correctly
df_selection = df[
    df["phong_ban"].isin(phongban) & df["Commodity"].isin(commodityy)
]

#functions for metrics
def metrics():
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Số Mặt Hàng Tồn Kho", 
        value=df_selection['Item'].count(),
        delta="Tổng số mặt hàng"
    )
    col2.metric(
        label="Chi Phí Tồn Kho Trung Bình", 
        value=f"{df_selection['Total'].mean():,.0f} VND",
        delta="KPI Tồn Kho"
    )
    col3.metric(
        label="Chênh Lệch Chi Phí Tồn Kho", 
        value=f"{df_selection['Total'].max()-df_selection['Total'].min():,.0f} VND",
        delta="Mức Độ Chênh Lệch"
    )
    
    # Tùy chỉnh màu sắc và hiệu ứng
    style_metric_cards(
        background_color="#f4f4f8", 
        border_left_color="#ffa500", 
        box_shadow="5px 5px 10px #aaa"
    )

#pie chart
def pie():
    with div1:
        fig = px.pie(df_selection, values='Total', names='phong_ban', title='% Tồn Kho by Phòng')
        fig.update_layout(legend_title="Phòng Ban", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

#bar chart
def barchart():
    with div2:
        # Sắp xếp dữ liệu theo tổng tồn kho giảm dần
        sorted_data = df_selection.groupby('phong_ban')['Total'].sum().reset_index().sort_values(by='Total', ascending=False)
        
        # Chuyển đổi cột Total sang định dạng có dấu phẩy để hiển thị trên biểu đồ
        sorted_data['Total_formatted'] = sorted_data['Total'].apply(lambda x: f"{x:,.0f}")

        # Tạo biểu đồ thanh (bar chart)
        fig = px.bar(
            sorted_data, 
            y='Total', 
            x='phong_ban', 
            text='Total_formatted',  # Hiển thị giá trị đã định dạng
            title="Tổng Tồn Kho by Phòng"
        )
        
        # Tuỳ chỉnh hiển thị
        fig.update_traces(
            textfont_size=12, 
            textposition="outside", 
            marker_color='rgba(52, 152, 219, 0.8)'
        )
        fig.update_layout(
            xaxis_title="Phòng Ban", 
            yaxis_title="Tổng Tồn Kho (VND)", 
            title_font_size=18
        )
        
        # Hiển thị biểu đồ
        st.plotly_chart(fig, use_container_width=True)



def commodity_piechart():
    with st.container():
        fig = px.pie(
            df_selection, 
            values='Total', 
            names='Commodity', 
            title="Tỷ lệ Tồn Kho giữa các nhóm Commodity",
            hole=0.3  # Biểu đồ dạng "donut"
        )
        fig.update_traces(
            textinfo='percent+value',
            textposition='inside'
        )
        fig.update_layout(
            title_font_size=18,
            legend_title="Nhóm Commodity",
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)


#table
def table():
    with st.expander("Thống kê chi tiết"):
        # Bạn có thể bỏ các chỉ số như count, mean, std,... để chỉ hiển thị các giá trị cụ thể cho chi phí tồn kho
        shwdata = st.multiselect('Lọc:', df.columns, default=["Created Date", "Item Number", "Item", "phong_ban", "Warehouse", "Quantity", "UOM", "TotalPrice", "Total", "Commodity"])
        st.dataframe(df_selection[shwdata], use_container_width=True)
def heatmap():
    with st.container():
        # Xử lý giá trị thiếu
        df_cleaned = df.dropna(subset=['phong_ban', 'Commodity'])

        # Danh sách đầy đủ phòng ban
        all_phong_ban = df_cleaned['phong_ban'].unique()

        # Bảng pivot
        pivot_table = df_selection.pivot_table(
            values='Total',
            index='Commodity',
            columns='phong_ban',
            aggfunc='sum',
            fill_value=0
        ).reindex(columns=all_phong_ban, fill_value=0)

        # Tạo Heatmap
        fig = px.imshow(
            pivot_table,
            color_continuous_scale="Viridis",
            labels=dict(x="Phòng Ban", y="Commodity", color="Tổng Tồn Kho (VND)"),
            text_auto=True
        )

        # Tuỳ chỉnh giao diện
        fig.update_layout(
            title="Heatmap Tồn Kho theo Commodity và Phòng Ban",
            title_font_size=18,
            xaxis_title="Phòng Ban",
            yaxis_title="Commodity",
            coloraxis_colorbar=dict(
                title="Tổng Tồn Kho (VND)",
                title_font_size=14
            )
        )

        st.plotly_chart(fig, use_container_width=True)


#option menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Table"], 
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

if selected == "Home":
    # Thêm phần metric cards
    metrics()
    
    # Thêm biểu đồ Pie và Bar
    st.markdown("### Biểu đồ Tổng Quan")
    div1, div2 = st.columns(2)
    with div1:
        pie()
    with div2:
        barchart()
    
    # Đưa biểu đồ commodity xuống dưới
    st.markdown("### Biểu đồ Tồn Kho chi tiết")
    commodity_piechart()
    
    # Thêm Heatmap
    st.markdown("### Heatmap Tồn Kho theo Phòng và Commodity")
    heatmap()


elif selected == "Table":
    metrics()
    table()
    st.dataframe(df_selection.describe().T, use_container_width=True)
