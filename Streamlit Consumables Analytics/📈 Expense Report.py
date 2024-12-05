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
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#get data from files
df = pd.read_csv("test_file.csv")

allowed_phongban = ["HCMCHEM", "HCMPEST", "HCMMICR", "HCMMYCO", "HCMOTH"]

#switcher for main dashboard
st.sidebar.header("Vui Lòng Filter")
phongban = st.sidebar.multiselect(
    "Filter Phòng Ban",
    options=allowed_phongban,
    default=allowed_phongban,
)
commodityy = st.sidebar.multiselect(
    "Filter Commodity",
    options=df["Commodity"].unique(),
    default=df["Commodity"].unique(),
)
monthh = st.sidebar.multiselect(
    "Filter Month",
    options=df["Month"].unique(),
    default=df["Month"].unique(),
)

df_selection = df.query(
    "phong_ban==@phongban & Commodity==@commodityy & Month==@monthh"
)

#functions for metrics
def metrics():
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Tổng Mặt Hàng", value=df_selection.Item.count(), delta="All Item")
    col2.metric(label="Tổng Chi Phí", value=f"{df_selection.Total.sum():,.0f}", delta="KPI 1,200,000,000")
    col3.metric(label="Chi Phí Lớn", value=f"{df_selection.Total.max()-df.Total.min():,.0f}", delta="Total Range")
    style_metric_cards(background_color="#7a7aff", border_left_color="#f20045", box_shadow="3px")

#pie chart
def pie():
    with div1:
        fig = px.pie(df_selection, values='Total', names='phong_ban', title='% Total by Account')
        fig.update_layout(legend_title="Phòng_Ban", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

#bar chart
def barchart():
    with div2:
        fig = px.bar(df_selection, y='Total', x='phong_ban', text_auto='.2s', title="Chi phí by Phòng")
        fig.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

def box_plot(df):
    fig = px.box(df, x='phong_ban', y='Total', color='phong_ban',
                 title="Phân bố chi phí theo phòng ban",
                 labels={'Total': 'Chi phí', 'phong_ban': 'Phòng ban'})
    st.plotly_chart(fig, use_container_width=True)


def commodity_piechart():
    # Đưa biểu đồ xuống dưới cùng và tăng kích thước biểu đồ
    with st.container():
        fig = px.pie(df_selection, values='Total', names='Commodity', title="Tỷ lệ Tồn giữa các nhóm Commodity")
        fig.update_traces(textinfo='percent+label', textposition='inside')
        fig.update_layout(height=600)  # Tăng chiều cao của biểu đồ
        st.plotly_chart(fig, use_container_width=True)

#bar chart by Type - thêm hàm này
def bar_chart_by_type(df):
    # Nhóm chi phí theo cột "Type"
    df_grouped = df.groupby('Type').agg({'Total': 'sum'}).reset_index()
    
    # Định dạng số VND với dấu phân cách hàng nghìn
    df_grouped['Total'] = df_grouped['Total'].apply(lambda x: f"{x:,.0f} VND")
    
    # Vẽ biểu đồ cột
    fig = px.bar(df_grouped, 
                 x='Type', 
                 y='Total', 
                 title="Phân Loại Chi Phí",
                 labels={'Type': 'Nhóm Chi Phí'},
                 color='Type',  # Màu sắc theo nhóm
                 text='Total')
    # Tinh chỉnh biểu đồ
    fig.update_traces(texttemplate='%{text}', textposition='outside')  # Hiển thị giá trị đã định dạng
    fig.update_layout(
        xaxis_title="Nhóm Chi Phí",
        yaxis_title="Tổng Chi Phí",
        showlegend=False
    )
    
    # Hiển thị biểu đồ
    st.plotly_chart(fig, use_container_width=True)


#table
def table():
    with st.expander("Tabular"):
        shwdata = st.multiselect('Filter :', df.columns, default=["Created Date", "Month", "Type", "phong_ban", "Commodity", "Item Number", "Item", "Quantity", "Price", "Total"])
        st.dataframe(df_selection[shwdata], use_container_width=True)

#option menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Table"],
        icons=["house", "book"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

if selected == "Home":
    div1, div2, div3 = st.columns(3)
    pie()
    barchart()
    metrics()
    commodity_piechart()
    bar_chart_by_type(df_selection)

elif selected == "Table":
    metrics()
    table()
    st.dataframe(df_selection.describe().T, use_container_width=True)
