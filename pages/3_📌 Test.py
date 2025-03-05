import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64

# Thiết lập trang
st.set_page_config(page_title="Kho Hàng Quản Lý", page_icon="📦", layout="wide")

import calendar

def get_month_name(month_value):
    """
    Returns the month name based on the input value.
    If the input is a number, it uses the standard 1-12 mapping.
    If the input is a date object or a string that can be converted to a date,
    it extracts the month name from the date.
    Otherwise, returns "Không xác định".
    """
    try:
        month_number = int(month_value)  # Try converting to integer first
        months = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                  "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]
        return months[month_number - 1] if 1 <= month_number <= 12 else "Không xác định"
    except (ValueError, TypeError):
        try:
            date_object = pd.to_datetime(month_value)  # Try converting to date object
            return f"Tháng {date_object.month}" #OR calendar.month_name[date_object.month] # if you can get the right Encoding
        except:
            return "Không xác định"
def format_currency(value):
    return f"{value:,.0f} VNĐ"


if 'inventory_df' not in st.session_state:
    # Cố gắng đọc dữ liệu từ các tệp CSV
    try:
        inventory_df = pd.read_csv("tonkho2024.csv")
        outbound_df = pd.read_csv("xuatkho2024.csv")

        # Xác thực xem các cột có tồn tại hay không (quan trọng!)
        inventory_required_columns = ['month', 'itemNumber', 'item', 'phongBan', 'quantity', 'uom', 'price', 'total', 'commodity']
        outbound_required_columns = ['month', 'account', 'itemNumber', 'item', 'quantity', 'uom', 'price', 'total', 'currency', 'receiver', 'commodity']

        if not all(col in inventory_df.columns for col in inventory_required_columns):
            st.error("File tonkho2024.csv thiếu một hoặc nhiều cột bắt buộc.")
            inventory_df = pd.DataFrame()  # Tạo DataFrame rỗng để tránh lỗi sau này

        if not all(col in outbound_df.columns for col in outbound_required_columns):
            st.error("File xuatkho2024.csv thiếu một hoặc nhiều cột bắt buộc.")
            outbound_df = pd.DataFrame() # Tạo DataFrame rỗng để tránh lỗi sau này

        # Convert 'month' to integer and handle errors
        try:
            inventory_df['month'] = pd.to_datetime(inventory_df['month'], errors='raise').dt.month.astype(int)
             # Validate month values
            if not ((inventory_df['month'] >= 1) & (inventory_df['month'] <= 12)).all():
                st.error("Giá trị tháng trong tonkho2024.csv phải nằm trong khoảng từ 1 đến 12.")
                inventory_df = pd.DataFrame() # Tạo DataFrame rỗng

        except ValueError as e:
            st.error(f"Lỗi trong cột 'month' của tonkho2024.csv: {str(e)}")
            inventory_df = pd.DataFrame()  # Tạo DataFrame rỗng
        except Exception as e:
            st.error(f"Lỗi không xác định khi chuyển đổi cột 'month' của tonkho2024.csv: {str(e)}")
            inventory_df = pd.DataFrame()

        try:
            outbound_df['month'] = pd.to_datetime(outbound_df['month'], errors='raise').dt.month.astype(int)
             # Validate month values
            if not ((outbound_df['month'] >= 1) & (outbound_df['month'] <= 12)).all():
                st.error("Giá trị tháng trong xuatkho2024.csv phải nằm trong khoảng từ 1 đến 12.")
                outbound_df = pd.DataFrame() # Tạo DataFrame rỗng

        except ValueError as e:
            st.error(f"Lỗi trong cột 'month' của xuatkho2024.csv: {str(e)}")
            outbound_df = pd.DataFrame()  # Tạo DataFrame rỗng
        except Exception as e:
            st.error(f"Lỗi không xác định khi chuyển đổi cột 'month' của xuatkho2024.csv: {str(e)}")
            outbound_df = pd.DataFrame()

    except FileNotFoundError:
        st.error("Không tìm thấy file tonkho2024.csv hoặc xuatkho2024.csv. Vui lòng đảm bảo rằng các file này nằm trong cùng thư mục với ứng dụng Streamlit.")
        inventory_df, outbound_df = pd.DataFrame(), pd.DataFrame() # Trả về Dataframe rỗng thay vì dữ liệu mẫu để nhất quán
    except Exception as e:
        st.error(f"Lỗi khi đọc file CSV: {e}")
        inventory_df, outbound_df = pd.DataFrame(), pd.DataFrame() # Trả về Dataframe rỗng thay vì dữ liệu mẫu để nhất quán

    st.session_state.inventory_df = inventory_df
    st.session_state.outbound_df = outbound_df
    st.session_state.using_custom_data = True  # Đánh dấu là đang sử dụng dữ liệu tùy chỉnh
else:
    # Để tránh việc đọc lại file CSV mỗi khi có tương tác, giữ lại giá trị đã đọc
    pass

# --- Tập hợp dữ liệu ---
def combine_data(inventory_df, outbound_df, filters=None):
    # Kiểm tra DataFrames rỗng
    if inventory_df.empty or outbound_df.empty:
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu một trong hai DataFrame rỗng

    # Áp dụng bộ lọc nếu có
    if filters:
        filtered_inventory = inventory_df.copy()
        filtered_outbound = outbound_df.copy()

        if 'month' in filters and filters['month']:
            filtered_inventory = filtered_inventory[filtered_inventory['month'] == filters['month']]
            filtered_outbound = filtered_outbound[filtered_outbound['month'] == filters['month']]

        if 'commodity' in filters and filters['commodity']:
            filtered_inventory = filtered_inventory[filtered_inventory['commodity'] == filters['commodity']]
            filtered_outbound = filtered_outbound[filtered_outbound['commodity'] == filters['commodity']]

        if 'phongBan' in filters and filters['phongBan']:
            filtered_inventory = filtered_inventory[filtered_inventory['phongBan'] == filters['phongBan']]

        if 'account' in filters and filters['account']:
            filtered_outbound = filtered_outbound[filtered_outbound['account'] == filters['account']]
    else:
        filtered_inventory = inventory_df.copy()
        filtered_outbound = outbound_df.copy()

    # Lấy danh sách các mã sản phẩm duy nhất từ cả hai dữ liệu
    all_item_numbers = pd.concat([
        filtered_inventory['itemNumber'],
        filtered_outbound['itemNumber']
    ]).unique()

    combined_data = []

    for item_number in all_item_numbers:
        inventory_items = filtered_inventory[filtered_inventory['itemNumber'] == item_number]
        outbound_items = filtered_outbound[filtered_outbound['itemNumber'] == item_number]

        # Kết hợp các tháng
        months = pd.concat([
            inventory_items['month'],
            outbound_items['month']
        ]).unique()

        for month in months:
            month_inventory = inventory_items[inventory_items['month'] == month]
            in_stock = month_inventory['quantity'].sum() if not month_inventory.empty else 0

            month_outbound = outbound_items[outbound_items['month'] == month]
            outbound = month_outbound['quantity'].sum() if not month_outbound.empty else 0

            # Tính giá trung bình
            if not month_inventory.empty:
                total_value = month_inventory['total'].sum()
                total_quantity = month_inventory['quantity'].sum()
                average_price = total_value / total_quantity if total_quantity > 0 else 0
            elif not month_outbound.empty:
                average_price = month_outbound['price'].iloc[0]
            else:
                average_price = 0

            # Lấy thông tin sản phẩm từ một trong hai nguồn dữ liệu
            if not month_inventory.empty:
                item_info = month_inventory.iloc[0]
            elif not month_outbound.empty:
                item_info = month_outbound.iloc[0]
            else:
                continue

            combined_data.append({
                'itemNumber': item_number,
                'item': item_info['item'],
                'month': month,
                'inStock': in_stock,
                'outbound': outbound,
                'balance': in_stock - outbound,
                'uom': item_info['uom'],
                'commodity': item_info['commodity'],
                'averagePrice': average_price
            })

    return pd.DataFrame(combined_data)

def get_monthly_usage():
    # Kiểm tra DataFrames rỗng
    if st.session_state.inventory_df.empty or st.session_state.outbound_df.empty:
        return pd.DataFrame()

    inventory_df = st.session_state.inventory_df
    outbound_df = st.session_state.outbound_df

    # Lấy tất cả các tháng
    all_months = pd.concat([
        inventory_df['month'],
        outbound_df['month']
    ]).unique()

    # Convert to pandas Series before applying operations
    all_months = pd.Series(all_months)

    all_months = pd.to_numeric(all_months, errors='coerce')
    all_months = all_months.dropna()
    all_months = all_months.astype(int)
    all_months = all_months.sort_values()  # Sort the Series

    monthly_summary = []

    for month in all_months:
        monthly_outbound = outbound_df[outbound_df['month'] == month]

        # Tính tổng
        total_items = monthly_outbound['quantity'].sum() if not monthly_outbound.empty else 0
        total_value = monthly_outbound['total'].sum() if not monthly_outbound.empty else 0

        monthly_summary.append({
            'month': month,  # No int() conversion needed here! Important
            'totalItems': total_items,
            'totalValue': total_value
        })

    return pd.DataFrame(monthly_summary)

def get_commodity_breakdown(month=None):
    # Kiểm tra DataFrame rỗng
    if st.session_state.outbound_df.empty:
        return pd.DataFrame()

    outbound_df = st.session_state.outbound_df

    # Lọc theo tháng nếu có
    filtered_outbound = outbound_df[outbound_df['month'] == month] if month else outbound_df

    # Lấy danh mục duy nhất
    commodities = filtered_outbound['commodity'].unique()

    # Tính tổng giá trị
    total_value = filtered_outbound['total'].sum() if not filtered_outbound.empty else 0

    breakdown = []

    for commodity in commodities:
        commodity_items = filtered_outbound[filtered_outbound['commodity'] == commodity]
        count = commodity_items['quantity'].sum()
        value = commodity_items['total'].sum()
        percentage = (value / total_value) * 100 if total_value > 0 else 0

        breakdown.append({
            'name': commodity,
            'count': count,
            'value': value,
            'percentage': percentage
        })

    # Sắp xếp theo giá trị giảm dần
    breakdown_df = pd.DataFrame(breakdown)
    if not breakdown_df.empty:
        breakdown_df = breakdown_df.sort_values(by='value', ascending=False)

    return breakdown_df

def get_top_used_items(limit=10, month=None):
     # Kiểm tra DataFrame rỗng
    if st.session_state.outbound_df.empty:
        return pd.DataFrame()

    outbound_df = st.session_state.outbound_df

    # Lọc theo tháng nếu có
    filtered_outbound = outbound_df[outbound_df['month'] == month] if month else outbound_df

    # Nhóm các mặt hàng theo mã sản phẩm
    if not filtered_outbound.empty:
        grouped_items = filtered_outbound.groupby('itemNumber').agg({
            'item': 'first',
            'quantity': 'sum',
            'total': 'sum',
            'commodity': 'first',
            'uom': 'first',
            'price': 'first'
        }).reset_index()

        # Sắp xếp theo số lượng
        top_items = grouped_items.sort_values(by='quantity', ascending=False).head(limit)
        return top_items

    return pd.DataFrame()

# --- Xử lý tải lên CSV ---
def parse_inventory_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = ['month', 'itemNumber', 'item', 'phongBan', 'quantity', 'uom', 'price', 'total', 'commodity']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return False, None, f"Thiếu các cột: {', '.join(missing_columns)}"

        # Chuyển đổi kiểu dữ liệu
        try:
            # Parse as date, extract month, and convert to int
            df['month'] = pd.to_datetime(df['month'], errors='raise').dt.month.astype(int)
            # Validate month values
            if not ((df['month'] >= 1) & (df['month'] <= 12)).all():
                return False, None, "Giá trị tháng phải nằm trong khoảng từ 1 đến 12."
        except ValueError as e:
            return False, None, f"Lỗi trong cột 'month': {str(e)}"
        except Exception as e:
            return False, None, f"Lỗi không xác định khi chuyển đổi cột 'month': {str(e)}"

        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)

        return True, df, "Phân tích thành công"
    except Exception as e:
        return False, None, f"Lỗi khi phân tích: {str(e)}"

def parse_outbound_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = ['month', 'account', 'itemNumber', 'item', 'quantity', 'uom', 'price', 'total', 'currency', 'receiver', 'commodity']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return False, None, f"Thiếu các cột: {', '.join(missing_columns)}"

        # Chuyển đổi kiểu dữ liệu
        try:
            # Parse as date, extract month, and convert to int
            df['month'] = pd.to_datetime(df['month'], errors='raise').dt.month.astype(int)
            # Validate month values
            if not ((df['month'] >= 1) & (df['month'] <= 12)).all():
                return False, None, "Giá trị tháng phải nằm trong khoảng từ 1 đến 12."
        except ValueError as e:
            return False, None, f"Lỗi trong cột 'month': {str(e)}"
        except Exception as e:
            return False, None, f"Lỗi không xác định khi chuyển đổi cột 'month': {str(e)}"

        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
        return True, df, "Phân tích thành công"
    except Exception as e:
        return False, None, f"Lỗi khi phân tích: {str(e)}"
# --- Giao diện người dùng ---
def main():
    # Sidebar với navigation
    st.sidebar.title("Kho Hàng Quản Lý")

    navigation = st.sidebar.radio(
        "Chọn trang:",
        ["Tổng quan", "Tồn kho", "Phân tích", "Tải lên dữ liệu"]
    )

    if navigation == "Tổng quan":
        show_dashboard()
    elif navigation == "Tồn kho":
        show_inventory()
    elif navigation == "Phân tích":
        show_analysis()
    elif navigation == "Tải lên dữ liệu":
        show_upload()

def show_dashboard():
    st.title("Tổng quan kho hàng")
    st.subheader("Thống kê dữ liệu kho hàng và xuất nhập kho năm 2024")

    # Dữ liệu hàng tháng
    monthly_data = get_monthly_usage()

    # Data cho commodity breakdown
    commodity_data = get_commodity_breakdown()

    # Tính toán thay đổi theo tháng
    if len(monthly_data) >= 2:
        sorted_data = monthly_data.sort_values(by='month')
        last_month = sorted_data.iloc[-1]
        previous_month = sorted_data.iloc[-2]

        if previous_month['totalValue'] > 0:
            mom_change = ((last_month['totalValue'] - previous_month['totalValue']) / previous_month['totalValue']) * 100
            is_positive = mom_change >= 0
        else:
            mom_change = 0
            is_positive = True
    else:
        mom_change = 0
        is_positive = True

    # Tổng giá trị
    total_value = monthly_data['totalValue'].sum() if not monthly_data.empty else 0

    # Lấy dữ liệu tháng hiện tại
    current_month = datetime.now().month
    current_month_data = monthly_data[monthly_data['month'] == current_month] if not monthly_data.empty else None
    current_month_value = current_month_data['totalValue'].iloc[0] if current_month_data is not None and not current_month_data.empty else 0
    current_month_items = current_month_data['totalItems'].iloc[0] if current_month_data is not None and not current_month_data.empty else 0

    # Hiển thị các card thống kê
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Tổng giá trị hàng hóa",
            value=format_currency(total_value),
            help="Tổng giá trị kho hàng năm 2024"
        )

    with col2:
        st.metric(
            label=f"Giá trị {get_month_name(current_month)}",
            value=format_currency(current_month_value),
            delta=f"{mom_change:.1f}%" if is_positive else f"-{abs(mom_change):.1f}%",
            delta_color="normal" if is_positive else "inverse",
            help=f"So với {get_month_name(current_month-1 if current_month > 1 else 12)}"
        )

    with col3:
        st.metric(
            label="Số lượng xuất trong tháng",
            value=int(current_month_items),
            help=f"{get_month_name(current_month)}"
        )

    with col4:
        st.metric(
            label="Danh mục hàng hóa",
            value=len(commodity_data) if not commodity_data.empty else 0,
            help="Tổng số danh mục"
        )

    # Biểu đồ xu hướng xuất kho theo tháng
    st.subheader("Xu hướng xuất kho theo tháng")

    if not monthly_data.empty:
        # Tạo cột tên tháng để hiển thị đẹp hơn
        chart_data = monthly_data.copy()
        chart_data['month_name'] = chart_data['month'].apply(get_month_name)

        fig = px.line(
            chart_data.sort_values(by='month'),
            x='month_name',
            y='totalValue',
            markers=True,
            labels={'totalValue': 'Giá trị xuất kho', 'month_name': 'Tháng'},
            title='Xu hướng xuất kho theo tháng'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu để hiển thị biểu đồ")

    # Hiển thị phân bố theo danh mục và top sản phẩm xuất nhiều nhất
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Phân bổ theo danh mục")

        if not commodity_data.empty:
            # Lấy top 5 danh mục
            top_commodities = commodity_data.head(5)

            fig = px.pie(
                top_commodities,
                values='value',
                names='name',
                hole=0.4,
                labels={'value': 'Giá trị', 'name': 'Danh mục'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có dữ liệu danh mục để hiển thị")

    with col2:
        st.subheader("Top danh mục theo giá trị")

        if not commodity_data.empty:
            # Hiển thị top danh mục dưới dạng bảng
            st.dataframe(
                commodity_data[['name', 'count', 'value', 'percentage']].head(5).style.format({
                    'value': '{:,.0f} VNĐ',
                    'percentage': '{:.1f}%'
                }),
                hide_index=True,
                column_config={
                    'name': 'Danh mục',
                    'count': 'Số lượng',
                    'value': 'Giá trị',
                    'percentage': 'Tỷ lệ'
                },
                use_container_width=True
            )
        else:
            st.info("Không có dữ liệu danh mục để hiển thị")

    # Hiển thị các mặt hàng xuất nhiều nhất
    st.subheader("Các mặt hàng xuất nhiều nhất")

    top_items = get_top_used_items(5)
    if not top_items.empty:
        st.dataframe(
            top_items[['itemNumber', 'item', 'quantity', 'total', 'commodity']].style.format({
                'total': '{:,.0f} VNĐ'
            }),
            hide_index=True,
            column_config={
                'itemNumber': 'Mã sản phẩm',
                'item': 'Sản phẩm',
                'quantity': 'Số lượng',
                'total': 'Giá trị',
                'commodity': 'Danh mục'
            },
            use_container_width=True
        )
    else:
        st.info("Không có dữ liệu sản phẩm để hiển thị")

def show_inventory():
    st.title("Tồn kho")

    # Bộ lọc
    st.sidebar.header("Bộ lọc")

    # Lấy danh sách tháng, danh mục và phòng ban
    months = sorted(st.session_state.inventory_df['month'].unique()) if not st.session_state.inventory_df.empty else []
    commodities = sorted(st.session_state.inventory_df['commodity'].unique()) if not st.session_state.inventory_df.empty else []

    # Safely handle 'phongBan' if it doesn't exist or has mixed types
    if 'phongBan' in st.session_state.inventory_df.columns and not st.session_state.inventory_df.empty:
        # Convert the 'phongBan' column to strings to handle mixed data types
        phong_ban_series = st.session_state.inventory_df['phongBan'].astype(str)

        # Remove NaN values by replacing them with an empty string
        phong_ban_series = phong_ban_series.replace('nan', '')

        # Get unique values and sort them
        departments = sorted(phong_ban_series.unique())
    else:
        departments = []

    # Tạo bộ lọc
    selected_month = st.sidebar.selectbox("Tháng", [None] + list(months), format_func=lambda x: "Tất cả" if x is None else get_month_name(x))
    selected_commodity = st.sidebar.selectbox("Danh mục", [None] + list(commodities), format_func=lambda x: "Tất cả" if x is None else x)
    selected_department = st.sidebar.selectbox("Phòng ban", [None] + list(departments), format_func=lambda x: "Tất cả" if x is None else x)

    # Tạo bộ lọc
    filters = {}
    if selected_month:
        filters['month'] = selected_month
    if selected_commodity:
        filters['commodity'] = selected_commodity
    if selected_department:
        filters['phongBan'] = selected_department

    # Kết hợp dữ liệu với bộ lọc
    combined_data = combine_data(st.session_state.inventory_df, st.session_state.outbound_df, filters)

    # Hiển thị dữ liệu
    if not combined_data.empty:
        st.dataframe(
            combined_data.style.format({
                'averagePrice': '{:,.0f} VNĐ',
                'month': lambda x: get_month_name(x)
            }),
            hide_index=True,
            column_config={
                'itemNumber': 'Mã sản phẩm',
                'item': 'Sản phẩm',
                'month': 'Tháng',
                'inStock': 'Tồn kho',
                'outbound': 'Xuất',
                'balance': 'Còn lại',
                'uom': 'ĐVT',
                'commodity': 'Danh mục',
                'averagePrice': 'Giá trung bình'
            },
            use_container_width=True
        )
    else:
        st.info("Không có dữ liệu tồn kho phù hợp với bộ lọc")

def show_analysis():
    st.title("Phân tích kho hàng")

    # Các tab phân tích
    tab1, tab2, tab3 = st.tabs(["Phân tích theo danh mục", "Phân tích theo tháng", "Phân tích sản phẩm"])

    with tab1:
        st.header("Phân bổ giá trị theo danh mục")

        # Lấy danh sách tháng
        months = sorted(st.session_state.inventory_df['month'].unique()) if not st.session_state.inventory_df.empty else []
        selected_month = st.selectbox("Chọn tháng", [None] + list(months), format_func=lambda x: "Tất cả" if x is None else get_month_name(x), key="commodity_month")

        # Lấy dữ liệu danh mục
        commodity_data = get_commodity_breakdown(selected_month)

        if not commodity_data.empty:
            # Hiển thị biểu đồ và bảng dữ liệu
            col1, col2 = st.columns([3, 2])

            with col1:
                fig = px.pie(
                    commodity_data,
                    values='value',
                    names='name',
                    hole=0.4,
                    labels={'value': 'Giá trị', 'name': 'Danh mục'}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.dataframe(
                    commodity_data[['name', 'count', 'value', 'percentage']].style.format({
                        'value': '{:,.0f} VNĐ',
                        'percentage': '{:.1f}%'
                    }),
                    hide_index=True,
                    column_config={
                        'name': 'Danh mục',
                        'count': 'Số lượng',
                        'value': 'Giá trị',
                        'percentage': 'Tỷ lệ'
                    },
                    use_container_width=True
                )
        else:
            st.info("Không có dữ liệu danh mục để hiển thị")

    with tab2:
        st.header("Phân tích theo tháng")

        # Lấy dữ liệu hàng tháng
        monthly_data = get_monthly_usage()

        if not monthly_data.empty:
            # Tạo cột tên tháng để hiển thị đẹp hơn
            chart_data = monthly_data.copy()
            chart_data['month_name'] = chart_data['month'].apply(get_month_name)

            # Hiển thị biểu đồ giá trị theo tháng
            st.subheader("Giá trị xuất kho theo tháng")
            fig = px.bar(
                chart_data.sort_values(by='month'),
                x='month_name',
                y='totalValue',
                labels={'totalValue': 'Giá trị xuất kho', 'month_name': 'Tháng'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Hiển thị biểu đồ số lượng theo tháng
            st.subheader("Số lượng xuất kho theo tháng")
            fig = px.bar(
                chart_data.sort_values(by='month'),
                x='month_name',
                y='totalItems',
                labels={'totalItems': 'Số lượng xuất kho', 'month_name': 'Tháng'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Hiển thị bảng dữ liệu
            st.subheader("Bảng dữ liệu chi tiết theo tháng")
            st.dataframe(
                chart_data[['month_name', 'totalItems', 'totalValue']].style.format({
                    'totalValue': '{:,.0f} VNĐ'
                }),
                hide_index=True,
                column_config={
                    'month_name': 'Tháng',
                    'totalItems': 'Số lượng',
                    'totalValue': 'Giá trị'
                },
                use_container_width=True
            )
        else:
            st.info("Không có dữ liệu hàng tháng để hiển thị")

    with tab3:
        st.header("Phân tích sản phẩm")

        # Tìm kiếm sản phẩm
        search_query = st.text_input("Tìm kiếm sản phẩm", placeholder="Nhập mã hoặc tên sản phẩm")

        if search_query:
            # Tìm trong cả hai bộ dữ liệu
            inventory_results = st.session_state.inventory_df[
                st.session_state.inventory_df['itemNumber'].str.contains(search_query, case=False) |
                st.session_state.inventory_df['item'].str.contains(search_query, case=False)
            ] if not st.session_state.inventory_df.empty else pd.DataFrame() # thêm check Dataframe rỗng
            outbound_results = st.session_state.outbound_df[
                st.session_state.outbound_df['itemNumber'].str.contains(search_query, case=False) |
                st.session_state.outbound_df['item'].str.contains(search_query, case=False)
            ] if not st.session_state.outbound_df.empty else pd.DataFrame() # thêm check Dataframe rỗng

            # Lấy mã sản phẩm duy nhất từ kết quả tìm kiếm
            found_items = pd.concat([
                inventory_results[['itemNumber', 'item']],
                outbound_results[['itemNumber', 'item']]
            ]).drop_duplicates(subset=['itemNumber'])

            if not found_items.empty:
                selected_item = st.selectbox(
                    "Chọn sản phẩm",
                    found_items['itemNumber'].tolist(),
                    format_func=lambda x: f"{x} - {found_items[found_items['itemNumber'] == x]['item'].iloc[0]}"
                )

                if selected_item:
                    # Lấy dữ liệu cho sản phẩm đã chọn
                    item_inventory = st.session_state.inventory_df[st.session_state.inventory_df['itemNumber'] == selected_item] if not st.session_state.inventory_df.empty else pd.DataFrame()
                    item_outbound = st.session_state.outbound_df[st.session_state.outbound_df['itemNumber'] == selected_item] if not  st.session_state.outbound_df.empty else pd.DataFrame()

                    # Hiển thị thông tin sản phẩm
                    item_name = item_inventory['item'].iloc[0] if not item_inventory.empty else item_outbound['item'].iloc[0] if not item_outbound.empty else ""
                    commodity = item_inventory['commodity'].iloc[0] if not item_inventory.empty else item_outbound['commodity'].iloc[0] if not item_outbound.empty else ""

                    st.subheader(f"{selected_item} - {item_name}")
                    st.write(f"Danh mục: {commodity}")

                    # Tạo dữ liệu phân tích theo tháng
                    months_data = []
                    for month in range(1, 13):
                        month_inventory = item_inventory[item_inventory['month'] == month] if not item_inventory.empty else pd.DataFrame()
                        month_outbound = item_outbound[item_outbound['month'] == month] if not item_outbound.empty else pd.DataFrame()

                        in_stock = month_inventory['quantity'].sum() if not month_inventory.empty else 0
                        out = month_outbound['quantity'].sum() if not month_outbound.empty else 0

                    months_data.append({
                        'month': month,
                        'month_name': get_month_name(month),
                        'inStock': in_stock,
                        'outbound': out,
                        'balance': in_stock - out
                    })

                months_df = pd.DataFrame(months_data)

                # Hiển thị biểu đồ
                st.subheader("Xu hướng tồn kho và xuất kho theo tháng")

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=months_df['month_name'],
                    y=months_df['inStock'],
                    name='Tồn kho',
                    marker_color='#3b82f6'
                ))
                fig.add_trace(go.Bar(
                    x=months_df['month_name'],
                    y=months_df['outbound'],
                    name='Xuất kho',
                    marker_color='#ef4444'
                ))
                fig.add_trace(go.Line(
                    x=months_df['month_name'],
                    y=months_df['balance'],
                    name='Còn lại',
                    marker_color='#10b981'
                ))

                fig.update_layout(
                    title='Phân tích tồn kho và xuất kho theo tháng',
                    xaxis_title='Tháng',
                    yaxis_title='Số lượng',
                    barmode='group',
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                # Hiển thị bảng dữ liệu
                st.subheader("Bảng dữ liệu chi tiết theo tháng")
                st.dataframe(
                    months_df,
                    hide_index=True,
                    column_config={
                        'month': None,  # Ẩn cột số tháng
                        'month_name': 'Tháng',
                        'inStock': 'Tồn kho',
                        'outbound': 'Xuất kho',
                        'balance': 'Còn lại'
                    },
                    use_container_width=True
                )
        else:
            st.warning("Không tìm thấy sản phẩm phù hợp")

def show_upload():
    st.title("Tải lên dữ liệu")
    st.subheader("Tải lên file dữ liệu CSV")
    
    # Hiển thị thông tin định dạng
    with st.expander("Định dạng file CSV", expanded=False):
        st.write("### File tồn kho")
        st.write("Cần có các cột sau: month, itemNumber, item, phongBan, quantity, uom, price, total, commodity")
        
        st.write("### File xuất kho")
        st.write("Cần có các cột sau: month, account, itemNumber, item, quantity, uom, price, total, currency, receiver, commodity")
    
    # Tải lên file
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("File tồn kho")
        inventory_file = st.file_uploader("Chọn file tồn kho CSV", type=["csv"], key="inventory_file")
        
        if 'inventory_uploaded' not in st.session_state:
            st.session_state.inventory_uploaded = False
        
        if inventory_file is not None and not st.session_state.inventory_uploaded:
            if st.button("Xử lý file tồn kho", key="process_inventory"):
                with st.spinner("Đang xử lý file tồn kho..."):
                    success, df, message = parse_inventory_csv(inventory_file)
                    
                    if success:
                        st.session_state.temp_inventory_df = df
                        st.session_state.inventory_uploaded = True
                        st.success("Đã tải lên dữ liệu tồn kho thành công")
                    else:
                        st.error(f"Lỗi khi phân tích file tồn kho: {message}")
        
        if st.session_state.inventory_uploaded:
            st.success("✅ Đã tải lên file tồn kho")
    
    with col2:
        st.subheader("File xuất kho")
        outbound_file = st.file_uploader("Chọn file xuất kho CSV", type=["csv"], key="outbound_file")
        
        if 'outbound_uploaded' not in st.session_state:
            st.session_state.outbound_uploaded = False
        
        if outbound_file is not None and not st.session_state.outbound_uploaded:
            if st.button("Xử lý file xuất kho", key="process_outbound"):
                with st.spinner("Đang xử lý file xuất kho..."):
                    success, df, message = parse_outbound_csv(outbound_file)
                    
                    if success:
                        st.session_state.temp_outbound_df = df
                        st.session_state.outbound_uploaded = True
                        st.success("Đã tải lên dữ liệu xuất kho thành công")
                    else:
                        st.error(f"Lỗi khi phân tích file xuất kho: {message}")
        
        if st.session_state.outbound_uploaded:
            st.success("✅ Đã tải lên file xuất kho")
    
    # Lưu và áp dụng dữ liệu
    st.subheader("Lưu và áp dụng dữ liệu")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.inventory_uploaded and st.session_state.outbound_uploaded:
            if st.button("Lưu và áp dụng dữ liệu", type="primary"):
                with st.spinner("Đang cập nhật dữ liệu..."):
                    # Cập nhật dữ liệu
                    st.session_state.inventory_df = st.session_state.temp_inventory_df
                    st.session_state.outbound_df = st.session_state.temp_outbound_df
                    st.session_state.using_custom_data = True
                    
                    # Reset upload flags
                    st.session_state.inventory_uploaded = False
                    st.session_state.outbound_uploaded = False
                    
                    st.success("Đã cập nhật dữ liệu thành công")
                    st.balloons()
                    
                    # Add a redirect effect
                    st.markdown("""
                        <meta http-equiv="refresh" content="2; url=/">
                    """, unsafe_allow_html=True)
        else:
            st.warning("Vui lòng tải lên cả hai file tồn kho và xuất kho")

# Run the app
if __name__ == "__main__":
    main()