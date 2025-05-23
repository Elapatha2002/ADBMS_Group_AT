import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pyodbc
from datetime import datetime, timedelta
import numpy as np

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Vehicle Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database connection configuration
def connect_to_sql_server():
    try:
        connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=your_server_name;"
            "Database=your_database_name;"
            "UID=your_username;"
            "PWD=your_password;"
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def load_data_from_sql():
    conn = connect_to_sql_server()
    if conn:
        query = "SELECT * FROM vehicle_sales"  # Replace with your table name
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return None

# Sample data creation (replace with SQL data loading)
@st.cache_data
def load_sample_data():
    # Vehicle models
    bike_models = ['Dio', 'Pulsar', 'Fz', 'Ct100', 'Platina']
    three_wheel_models = ['Auto Rickshaw', 'Three Wheeler']
    
    # Generate sample data
    data = []
    for i in range(1, 101):
        vehicle_type = np.random.choice(['Bike', 'Three Wheeler'], p=[0.7, 0.3])
        if vehicle_type == 'Bike':
            model = np.random.choice(bike_models)
            price_range = (400000, 600000)
        else:
            model = np.random.choice(three_wheel_models)
            price_range = (800000, 1000000)
        
        data.append({
            'VehicleNumber': f"ABC {np.random.randint(1000, 9999)}",
            'CustomerId': i,
            'CustomerName': f"Customer_{i}",
            'VehicleType': vehicle_type,
            'Model': model,
            'PurchaseDate': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 365*2)),
            'Payment': np.random.randint(*price_range),
            'PaymentMethod': np.random.choice(['Cash', 'Credit Card', 'Bank Transfer', 'Cheque']),
            'EmployeeId': np.random.randint(1, 100),
            'Status': np.random.choice(['Sold', 'Available', 'Under Repair']),
            'RepairCost': np.random.randint(5000, 50000) if np.random.random() > 0.7 else 0,
            'RepairStatus': np.random.choice(['Completed', 'In Progress', 'Pending']) if np.random.random() > 0.7 else 'None'
        })
    
    return pd.DataFrame(data)

# Enhanced CSS with top navigation
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0 0 15px 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Top navigation */
    .top-nav {
        background: black;
        padding: 0.4rem 0.4rem;
        border-radius: 10px;
        margin-bottom: 0.4rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Navigation buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.2rem 0;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    /* Chart containers */
    .chart-container {
        background: black;
        padding: 0.4rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Hide sidebar completely */
    .css-1d391kg {
        display: none;
    }
    
    /* Page content styling */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_sample_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>CM Vehicle Management System</h1>
</div>
""", unsafe_allow_html=True)

# Top Navigation
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns(6)

with nav_col1:
    dashboard_btn = st.button("🏠 Dashboard", use_container_width=True)
with nav_col2:
    vehicle_btn = st.button("🚗 Vehicle Management", use_container_width=True)
with nav_col3:
    customer_btn = st.button("👥 Customer Management", use_container_width=True)
with nav_col4:
    repair_btn = st.button("🔧 Repair Management", use_container_width=True)
with nav_col5:
    supplier_btn = st.button("🏪 Supplier Management", use_container_width=True)
with nav_col6:
    reports_btn = st.button("💰 Sales Reports", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Page state management
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

if dashboard_btn:
    st.session_state.current_page = 'dashboard'
elif vehicle_btn:
    st.session_state.current_page = 'vehicle_management'
elif customer_btn:
    st.session_state.current_page = 'customer_management'
elif repair_btn:
    st.session_state.current_page = 'repair_management'
elif supplier_btn:
    st.session_state.current_page = 'supplier_management'
elif reports_btn:
    st.session_state.current_page = 'sales_reports'

# Dashboard Page
if st.session_state.current_page == 'dashboard':
    st.markdown('<h1 style="text-align: center; color: #1f77b4; margin-bottom: 2rem;">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = len(df[df['Status'] == 'Sold'])
        st.metric("Number Of Sales", total_sales, delta=f"+{np.random.randint(5, 15)}")
    
    with col2:
        total_revenue = df[df['Status'] == 'Sold']['Payment'].sum()
        st.metric("Total Sales", f"Rs.{total_revenue/1000000:.1f}M", delta="+12%")
    
    with col3:
        monthly_profit = total_revenue * 0.15  # Assuming 15% profit margin
        st.metric("Monthly Profit", f"Rs.{monthly_profit/1000000:.1f}M", delta="+8%")
    
    with col4:
        vehicles_under_repair = len(df[df['Status'] == 'Under Repair'])
        st.metric("Vehicles Under Repair", vehicles_under_repair, delta=f"-{np.random.randint(1, 5)}")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Total Sales 2025")
        monthly_sales = df.groupby(df['PurchaseDate'].dt.month)['Payment'].sum().reset_index()
        monthly_sales['Month'] = pd.to_datetime(monthly_sales['PurchaseDate'], format='%m').dt.strftime('%b')
        
        fig = px.line(monthly_sales, x='Month', y='Payment', 
                     title="Monthly Sales Trend",
                     color_discrete_sequence=['#9467bd'])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Monthly Sales Vehicle")
        monthly_count = df.groupby(df['PurchaseDate'].dt.month).size().reset_index()
        monthly_count['Month'] = pd.to_datetime(monthly_count['PurchaseDate'], format='%m').dt.strftime('%b')
        
        fig = px.bar(monthly_count, x='Month', y=0, 
                    title="Monthly Vehicle Sales Count",
                    color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts Row 2
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Sales Breakdown by Vehicle Type")
        vehicle_sales = df[df['Status'] == 'Sold']['VehicleType'].value_counts()
        
        fig = go.Figure()
        for i, (vehicle_type, count) in enumerate(vehicle_sales.items()):
            fig.add_trace(go.Bar(
                x=[vehicle_type],
                y=[count],
                name=vehicle_type,
                marker_color=['#1f77b4', '#ff7f0e'][i % 2],
                text=[count],
                textposition='auto'
            ))
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Vehicle Type",
            yaxis_title="Sales Count"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Repair Cost Analytics")
        repair_data = df[df['RepairCost'] > 0]
        total_repair_cost = repair_data['RepairCost'].sum()
        avg_repair_time = "23m"  # Sample data
        
        st.write(f"**Total Repair Cost:** Rs.{total_repair_cost/1000:.1f}k")
        st.write(f"**Avg. Repair Time:** {avg_repair_time}")
        st.write(f"**Days:** 1")
        st.write(f"**No. of Vehicles Under Repair:** {vehicles_under_repair}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Inventory Status")
        status_counts = df['Status'].value_counts()
        
        # Create custom labels with count values
        labels = []
        values = []
        for status, count in status_counts.items():
            labels.append(f"{status}")
            values.append(count)
        
        fig = px.pie(
            values=values, 
            names=labels,
            color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99'],
            title="Inventory Distribution"
        )
        
        # Update traces to show count values instead of percentages
        fig.update_traces(
            textposition='inside', 
            textinfo='value+label',
            textfont_size=12,
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        
        fig.update_layout(
            height=400, 
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Vehicle Management Page
elif st.session_state.current_page == 'vehicle_management':
    st.title("Vehicle Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Vehicles", "Add Vehicle", "Update Vehicle", "Vehicle Actions"])
    
    with tab1:
        st.subheader("All Vehicles")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            vehicle_type_filter = st.selectbox("Filter by Type", ["All"] + list(df['VehicleType'].unique()))
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df['Status'].unique()))
        with col3:
            model_filter = st.selectbox("Filter by Model", ["All"] + list(df['Model'].unique()))
        
        # Apply filters
        filtered_df = df.copy()
        if vehicle_type_filter != "All":
            filtered_df = filtered_df[filtered_df['VehicleType'] == vehicle_type_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        if model_filter != "All":
            filtered_df = filtered_df[filtered_df['Model'] == model_filter]
        
        st.dataframe(filtered_df, use_container_width=True)
    
    with tab2:
        st.subheader("Add New Vehicle")
        
        col1, col2 = st.columns(2)
        with col1:
            vehicle_number = st.text_input("Vehicle Number", placeholder="e.g., ABC 1234")
            vehicle_type = st.selectbox("Vehicle Type", ["Bike", "Three Wheeler"])
            
            if vehicle_type == "Bike":
                model = st.selectbox("Model", ['Dio', 'Pulsar', 'Fz', 'Ct100', 'Platina'])
            else:
                model = st.selectbox("Model", ['Auto Rickshaw', 'Three Wheeler'])
            
            purchase_price = st.number_input("Purchase Price (Rs.)", min_value=0, step=1000)
        
        with col2:
            customer_id = st.number_input("Customer ID", min_value=1, step=1)
            employee_id = st.number_input("Employee ID", min_value=1, step=1)
            payment_method = st.selectbox("Payment Method", ['Cash', 'Credit Card', 'Bank Transfer', 'Cheque'])
            status = st.selectbox("Status", ['Available', 'Sold', 'Under Repair'])
        
        if st.button("Add Vehicle", type="primary"):
            # Here you would insert into database
            st.success("Vehicle added successfully!")
    
    with tab3:
        st.subheader("Update Vehicle")
        
        vehicle_to_update = st.selectbox("Select Vehicle to Update", df['VehicleNumber'].tolist())
        
        if vehicle_to_update:
            selected_vehicle = df[df['VehicleNumber'] == vehicle_to_update].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox("Status", ['Available', 'Sold', 'Under Repair'], 
                                        index=['Available', 'Sold', 'Under Repair'].index(selected_vehicle['Status']))
                new_price = st.number_input("Price", value=int(selected_vehicle['Payment']))
            
            with col2:
                new_customer = st.number_input("Customer ID", value=int(selected_vehicle['CustomerId']))
                new_employee = st.number_input("Employee ID", value=int(selected_vehicle['EmployeeId']))
            
            if st.button("Update Vehicle", type="primary"):
                st.success("Vehicle updated successfully!")
    
    with tab4:
        st.subheader("Vehicle Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Repair Vehicle")
            repair_vehicle = st.selectbox("Select Vehicle for Repair", df['VehicleNumber'].tolist())
            repair_details = st.text_area("Repair Details")
            repair_cost = st.number_input("Repair Cost (Rs.)", min_value=0, step=100)
            
            if st.button("Submit for Repair"):
                st.success("Vehicle submitted for repair!")
        
        with col2:
            st.subheader("Sell Vehicle")
            available_vehicles = df[df['Status'] == 'Available']['VehicleNumber'].tolist()
            if available_vehicles:
                sell_vehicle = st.selectbox("Select Vehicle to Sell", available_vehicles)
                if st.button("Mark as Sold"):
                    st.success("Vehicle marked as sold!")
            else:
                st.info("No vehicles available for sale")

# Customer Management Page
elif st.session_state.current_page == 'customer_management':
    st.title("Customer Management")
    
    tab1, tab2, tab3 = st.tabs(["All Customers", "Add Customer", "Update Customer"])
    
    with tab1:
        # Generate customer data
        customers = df[['CustomerId', 'CustomerName']].drop_duplicates()
        customers['Phone'] = [f"07{np.random.randint(10000000, 99999999)}" for _ in range(len(customers))]
        customers['Address'] = [f"Address {i}" for i in customers['CustomerId']]
        customers['NIC'] = [f"{np.random.randint(100000000, 999999999)}V" for _ in range(len(customers))]
        
        st.dataframe(customers, use_container_width=True)
    
    with tab2:
        st.subheader("Add New Customer")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            address = st.text_area("Address")
            nic_number = st.text_input("NIC Number")
        
        with col2:
            last_name = st.text_input("Last Name")
            phone_number = st.text_input("Phone Number")
        
        if st.button("Add Customer", type="primary"):
            st.success("Customer added successfully!")
    
    with tab3:
        st.subheader("Update Customer")
        customers = df[['CustomerId', 'CustomerName']].drop_duplicates()
        customer_to_update = st.selectbox("Select Customer", customers['CustomerName'].tolist())
        
        if customer_to_update:
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("First Name", value="Sample", key="update_fname")
                st.text_area("Address", value="Sample Address", key="update_address")
                st.text_input("NIC Number", value="123456789V", key="update_nic")
            
            with col2:
                st.text_input("Last Name", value="Customer", key="update_lname")
                st.text_input("Phone Number", value="0771234567", key="update_phone")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Customer", type="secondary"):
                    st.warning("Customer deleted!")
            with col2:
                if st.button("Save Changes", type="primary"):
                    st.success("Customer updated successfully!")

# Repair Management Page
elif st.session_state.current_page == 'repair_management':
    st.title("Repair Management")
    
    tab1, tab2, tab3 = st.tabs(["Active Repairs", "Add Repair", "Repair History"])
    
    with tab1:
        st.subheader("Active Repairs")
        repair_data = df[df['Status'] == 'Under Repair']
        st.dataframe(repair_data[['VehicleNumber', 'Model', 'RepairCost', 'RepairStatus']], use_container_width=True)
    
    with tab2:
        st.subheader("Add New Repair")
        
        col1, col2 = st.columns(2)
        with col1:
            repair_vehicle = st.selectbox("Vehicle Number", df['VehicleNumber'].tolist())
            repair_start_date = st.date_input("Repair Start Date")
            repair_details = st.text_area("Repair Details")
            repair_location = st.text_input("Location")
        
        with col2:
            repair_end_date = st.date_input("Repair End Date")
            repair_amount = st.number_input("Repair Amount (Rs.)", min_value=0, step=100)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear"):
                st.rerun()
        with col2:
            if st.button("Save", type="primary"):
                st.success("Repair record saved!")
    
    with tab3:
        st.subheader("Repair History")
        # Sample repair history
        repair_history = df[df['RepairCost'] > 0][['VehicleNumber', 'Model', 'RepairCost', 'RepairStatus']]
        st.dataframe(repair_history, use_container_width=True)

# Supplier Management Page
elif st.session_state.current_page == 'supplier_management':
    st.title("Supplier Management")
    
    tab1, tab2, tab3 = st.tabs(["All Suppliers", "Add Supplier", "Update Supplier"])
    
    with tab1:
        # Generate supplier data
        suppliers = pd.DataFrame({
            'SupplierID': range(1, 11),
            'FirstName': [f"Supplier_{i}" for i in range(1, 11)],
            'LastName': [f"LastName_{i}" for i in range(1, 11)],
            'Address': [f"Supplier Address {i}" for i in range(1, 11)],
            'NIC': [f"{np.random.randint(100000000, 999999999)}V" for _ in range(10)],
            'Phone': [f"07{np.random.randint(10000000, 99999999)}" for _ in range(10)]
        })
        
        st.dataframe(suppliers, use_container_width=True)
    
    with tab2:
        st.subheader("Add New Supplier")
        
        col1, col2 = st.columns(2)
        with col1:
            supplier_first_name = st.text_input("First Name")
            supplier_address = st.text_area("Address")
            supplier_nic = st.text_input("NIC Number")
        
        with col2:
            supplier_last_name = st.text_input("Last Name")
            supplier_phone = st.text_input("Phone Numbers")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear"):
                st.rerun()
        with col2:
            if st.button("Submit", type="primary"):
                st.success("Supplier added successfully!")
    
    with tab3:
        st.subheader("Update Supplier")
        suppliers = pd.DataFrame({
            'SupplierID': range(1, 11),
            'FirstName': [f"Supplier_{i}" for i in range(1, 11)],
            'LastName': [f"LastName_{i}" for i in range(1, 11)]
        })
        supplier_to_update = st.selectbox("Select Supplier", suppliers['FirstName'].tolist())
        
        if supplier_to_update:
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("First Name", value="Sample", key="update_sup_fname")
                st.text_area("Address", value="Sample Address", key="update_sup_address")
                st.text_input("NIC Number", value="123456789V", key="update_sup_nic")
            
            with col2:
                st.text_input("Last Name", value="Supplier", key="update_sup_lname")
                st.text_input("Phone Number", value="0771234567", key="update_sup_phone")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Supplier", type="secondary"):
                    st.warning("Supplier deleted!")
            with col2:
                if st.button("Save Changes", type="primary"):
                    st.success("Supplier updated successfully!")

# Sales Reports Page
elif st.session_state.current_page == 'sales_reports':
    st.title("Sales Reports & Analytics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Filter data by date range
    filtered_sales = df[(df['PurchaseDate'].dt.date >= start_date) & 
                       (df['PurchaseDate'].dt.date <= end_date) & 
                       (df['Status'] == 'Sold')]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", len(filtered_sales))
    with col2:
        st.metric("Total Revenue", f"Rs.{filtered_sales['Payment'].sum()/1000000:.2f}M")
    with col3:
        st.metric("Average Sale", f"Rs.{filtered_sales['Payment'].mean():.0f}")
    with col4:
        st.metric("Top Model", filtered_sales['Model'].mode().iloc[0] if len(filtered_sales) > 0 else "N/A")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Model
        st.subheader("Sales by Model")
        model_sales = filtered_sales['Model'].value_counts()
        fig = px.pie(values=model_sales.values, names=model_sales.index, 
                    title="Sales Distribution by Model")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales by Payment Method
        st.subheader("Sales by Payment Method")
        payment_sales = filtered_sales['PaymentMethod'].value_counts()
        fig = px.bar(x=payment_sales.index, y=payment_sales.values,
                    title="Sales by Payment Method")
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly sales trend
    st.subheader("Monthly Sales Trend")
    monthly_sales = filtered_sales.groupby(filtered_sales['PurchaseDate'].dt.to_period('M')).agg({
        'Payment': 'sum',
        'VehicleNumber': 'count'
    }).reset_index()
    monthly_sales['PurchaseDate'] = monthly_sales['PurchaseDate'].astype(str)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=monthly_sales['PurchaseDate'], y=monthly_sales['Payment'], 
               name="Revenue", marker_color='lightblue'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=monthly_sales['PurchaseDate'], y=monthly_sales['VehicleNumber'], 
                  name="Count", mode='lines+markers', marker_color='red'),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Revenue (Rs.)", secondary_y=False)
    fig.update_yaxes(title_text="Number of Sales", secondary_y=True)
    fig.update_layout(title_text="Monthly Sales Revenue and Count")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed sales table
    st.subheader("Detailed Sales Data")
    st.dataframe(filtered_sales, use_container_width=True)

st.markdown("""
<div style="text-align: center; color: #ecf0f1; padding: 2rem; background: linear-gradient(to bottom, #0d0f14, #000000); border-radius: 15px; margin: 2rem 0;">
    <h3> CM Vehicle Management System</h3>
    <p><strong>Vehicle Sales & Management Dashboard</strong></p>
    <p>Built with Group AT | © 2025 CM Vehicle Management. All rights reserved.</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">
        📧 Email: chamod@cmvehicles.com | 📞 Phone: +94 70 520 6400 
    </p>
</div>
""", unsafe_allow_html=True)


# SQL Server Connection Instructions (commented)
#To connect to Microsoft SQL Server:

#1. Install required packages:
#  pip install pyodbc

#2. Update the connection string in connect_to_sql_server() function with your SQL Server details:
 #  - Server name/IP
  # - Database name
   #- Username and password

#3. Create the required tables in your SQL Server database:

#CREATE TABLE vehicle_sales (
   # VehicleNumber NVARCHAR(50) PRIMARY KEY,
    #CustomerId INT,
    #CustomerName NVARCHAR(100),
    #VehicleType NVARCHAR(50),
    #Model NVARCHAR(50),
    #PurchaseDate DATE,
    #Payment DECIMAL(10,2),
    #PaymentMethod NVARCHAR(50),
    #EmployeeId INT,
    #Status NVARCHAR(50),
    #RepairCost DECIMAL(10,2),
    #RepairStatus NVARCHAR(50)
#);

#CREATE TABLE customers (
    #CustomerId INT PRIMARY KEY IDENTITY(1,1),
    #FirstName NVARCHAR(50),
    #LastName NVARCHAR(50),
    #Address NVARCHAR(200),
    #NIC NVARCHAR(20),
    #Phone NVARCHAR(20)
##;

#CREATE TABLE suppliers (
    #SupplierID INT PRIMARY KEY IDENTITY(1,1),
    #FirstName NVARCHAR(50),
    #LastName NVARCHAR(50),
    #Address NVARCHAR(200),
    #NIC NVARCHAR(20),
    #Phone NVARCHAR(20)
#);

#CREATE TABLE repairs (
#    RepairID INT PRIMARY KEY IDENTITY(1,1),
 ##  RepairStartDate DATE,
   # RepairEndDate DATE,
    #RepairDetails NVARCHAR(500),
    #Location NVARCHAR(100),
    #RepairAmount DECIMAL(10,2),
    #RepairStatus NVARCHAR(50),
    #FOREIGN KEY (VehicleNumber) REFERENCES vehicle_sales(VehicleNumber)
#);

#4. Replace load_sample_data() with load_data_from_sql() in the main code

#5. Add insert/update/delete functions for database operations

#Example database operations:

#def insert_vehicle(vehicle_data):
    #conn = connect_to_sql_server()
   # if conn:
       # cursor = conn.cursor()
       # query = '''INSERT INTO vehicle_sales 
                  # (VehicleNumber, CustomerId, CustomerName, VehicleType, Model, 
                   # PurchaseDate, Payment, PaymentMethod, EmployeeId, Status, 
                   # RepairCost, RepairStatus) 
                   #VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        #cursor.execute(query, vehicle_data)
        #conn.commit()
        #conn.close()
        #return True
    #return False

#def update_vehicle(vehicle_number, update_data):
    #conn = connect_to_sql_server()
    #if conn:
        #cursor = conn.cursor()
        #query = '''UPDATE vehicle_sales SET Status = ?, Payment = ?, 
                  # CustomerId = ?, EmployeeId = ? WHERE VehicleNumber = ?'''
        #cursor.execute(query, update_data + [vehicle_number])
        #conn.commit()
        #conn.close()
        #return True
    #return False
