import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Car Reseller Business Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load clean vehicle data"""
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "vehicles_clean.db"
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM vehicles_clean", conn)
    
    return df

def calculate_profit_margins(df):
    """Calculate potential profit margins by segment"""
    df['price_segment'] = pd.cut(df['price_usd'], 
                                bins=[0, 15000, 25000, 40000, 100000, 300000],
                                labels=['Budget', 'Economy', 'Mid-Range', 'Premium', 'Luxury'])
    
    margins = df.groupby('price_segment').agg({
        'price_usd': ['count', 'mean', 'std'],
        'vehicle_age': 'mean'
    }).round(0)
    
    margins.columns = ['Volume', 'Avg_Price', 'Price_Volatility', 'Avg_Age']
    margins['Est_Margin_10%'] = margins['Avg_Price'] * 0.10
    margins['Est_Margin_15%'] = margins['Avg_Price'] * 0.15
    margins['Turnover_Days'] = np.where(margins['Avg_Price'] < 20000, 30, 
                                       np.where(margins['Avg_Price'] < 40000, 45, 60))
    
    return margins

def create_profit_opportunity_chart(df):
    """Create profit opportunity analysis"""
    margins = calculate_profit_margins(df)
    
    fig = go.Figure()
    
    # Volume bars
    fig.add_trace(go.Bar(
        name='Market Volume',
        x=margins.index,
        y=margins['Volume'],
        yaxis='y',
        marker_color='lightblue',
        text=margins['Volume'],
        textposition='auto'
    ))
    
    # Profit margin line
    fig.add_trace(go.Scatter(
        name='Est. Profit (15%)',
        x=margins.index,
        y=margins['Est_Margin_15%'],
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Profit Opportunity by Market Segment',
        xaxis_title='Price Segment',
        yaxis=dict(title='Number of Vehicles', side='left'),
        yaxis2=dict(title='Estimated Profit ($)', side='right', overlaying='y'),
        height=400
    )
    
    return fig

def create_best_deals_finder(df):
    """Find underpriced vehicles"""
    # Calculate market price by brand and age
    df['market_price'] = df.groupby(['brand', pd.cut(df['vehicle_age'], bins=5)])['price_usd'].transform('median')
    df['price_diff'] = df['market_price'] - df['price_usd']
    df['discount_pct'] = (df['price_diff'] / df['market_price'] * 100).round(1)
    
    # Find best deals (underpriced by >15%)
    best_deals = df[df['discount_pct'] > 15].sort_values('discount_pct', ascending=False)
    
    return best_deals[['brand', 'model', 'year', 'price_usd', 'market_price', 'discount_pct']].head(10)

def create_inventory_recommendations(df):
    """Generate inventory recommendations"""
    # Fast-moving segments
    fast_movers = df[df['price_usd'] < 25000].groupby('brand').size().sort_values(ascending=False).head(5)
    
    # High-margin opportunities
    luxury_brands = df[df['is_luxury'] == True]['brand'].value_counts().head(3)
    
    # Age sweet spot
    age_analysis = df.groupby(pd.cut(df['vehicle_age'], bins=[0, 3, 6, 10, 20, 50]))['price_usd'].agg(['count', 'mean'])
    optimal_age = age_analysis['count'].idxmax()
    
    return {
        'fast_movers': fast_movers,
        'luxury_brands': luxury_brands,
        'optimal_age': optimal_age,
        'age_analysis': age_analysis
    }

def price_prediction_tool(df):
    """Enhanced price prediction for resellers"""
    st.subheader("💰 Vehicle Valuation & Profit Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Vehicle Details**")
        brand = st.selectbox("Brand", options=sorted(df['brand'].unique()))
        model = st.selectbox("Model", options=['Any'] + sorted(df[df['brand']==brand]['model'].dropna().unique().tolist()))
        year = st.slider("Year", min_value=2000, max_value=2025, value=2020)
        mileage = st.number_input("Mileage (km)", min_value=0, max_value=300000, value=50000)
        condition = st.selectbox("Condition", options=['Excellent', 'Good', 'Fair', 'Poor'])
    
    with col2:
        st.write("**Purchase & Sale Strategy**")
        purchase_price = st.number_input("Your Purchase Price ($)", min_value=1000, max_value=200000, value=20000)
        target_margin = st.slider("Target Profit Margin (%)", min_value=5, max_value=30, value=15)
        holding_days = st.slider("Expected Holding Period (days)", min_value=15, max_value=120, value=45)
        
        # Costs
        st.write("**Additional Costs**")
        repair_costs = st.number_input("Repair/Prep Costs ($)", min_value=0, max_value=10000, value=500)
        overhead_daily = st.number_input("Daily Overhead ($)", min_value=0, max_value=50, value=10)
    
    with col3:
        st.write("**Valuation Results**")
        
        if st.button("Calculate Profit Potential", type="primary"):
            # Market valuation
            vehicle_age = 2025 - year
            brand_avg = df[df['brand'] == brand]['price_usd'].median()
            
            # Condition adjustments
            condition_multiplier = {'Excellent': 1.1, 'Good': 1.0, 'Fair': 0.9, 'Poor': 0.8}[condition]
            
            # Age depreciation
            age_factor = max(0.6, 1 - (vehicle_age * 0.06))
            
            # Mileage impact
            mileage_factor = max(0.7, 1 - (mileage / 400000))
            
            market_value = brand_avg * age_factor * mileage_factor * condition_multiplier
            
            # Total costs
            total_costs = purchase_price + repair_costs + (overhead_daily * holding_days)
            
            # Profit calculations
            target_sale_price = total_costs * (1 + target_margin/100)
            potential_profit = market_value - total_costs
            actual_margin = (potential_profit / total_costs * 100) if total_costs > 0 else 0
            
            # Display results
            st.success(f"**Market Value: ${market_value:,.0f}**")
            
            if market_value > target_sale_price:
                st.success(f"✅ **GOOD DEAL**")
                st.write(f"Expected Profit: ${potential_profit:,.0f}")
                st.write(f"Actual Margin: {actual_margin:.1f}%")
                st.write(f"ROI: {(potential_profit/purchase_price*100):.1f}%")
            else:
                st.error(f"❌ **RISKY DEAL**")
                st.write(f"Potential Loss: ${abs(potential_profit):,.0f}")
                st.write(f"Market is {((target_sale_price/market_value-1)*100):.1f}% overpriced")
            
            # Recommendations
            st.write("**💡 Recommendations:**")
            if actual_margin > target_margin:
                st.write("• Strong profit potential - consider buying")
                st.write(f"• Max purchase price: ${market_value - repair_costs - (overhead_daily * holding_days) - (market_value * target_margin/100):,.0f}")
            else:
                st.write("• Negotiate lower purchase price")
                st.write("• Consider faster turnaround to reduce costs")
                st.write("• Look for similar vehicles in better condition")

def market_opportunities_page(df):
    """Market opportunities analysis"""
    st.header("🎯 Market Opportunities")
    
    # Profit opportunity chart
    st.plotly_chart(create_profit_opportunity_chart(df), use_container_width=True)
    st.info("💡 **Insight**: Economy segment ($15K-$25K) offers the best balance of volume and profit margins. Budget segment has highest volume but lower margins.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Best Deals Available")
        best_deals = create_best_deals_finder(df)
        
        if not best_deals.empty:
            for _, deal in best_deals.head(5).iterrows():
                # Get full vehicle data
                vehicle = df[df['price_usd'] == deal['price_usd']].iloc[0]
                
                with st.expander(f"{deal['year']} {deal['brand']} {deal['model']} - {deal['discount_pct']}% below market"):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        # Enhanced ML analysis for deals
                        vehicle_age = 2025 - deal['year']
                        depreciation_score = min(100, vehicle_age * 8)  # Age impact score
                        value_score = 100 - depreciation_score + deal['discount_pct']
                        
                        st.write(f"**Listed Price**: ${deal['price_usd']:,.0f}")
                        st.write(f"**Market Price**: ${deal['market_price']:,.0f}")
                        st.write(f"**Potential Savings**: ${deal['market_price'] - deal['price_usd']:,.0f}")
                        st.write(f"**Discount**: {deal['discount_pct']}%")
                        
                        if value_score > 80:
                            st.success(f"🎆 **Excellent Deal** (Score: {value_score:.0f}/100)")
                        elif value_score > 60:
                            st.info(f"🟡 **Good Deal** (Score: {value_score:.0f}/100)")
                        else:
                            st.warning(f"⚠️ **Fair Deal** (Score: {value_score:.0f}/100)")
                    with col_b:
                        st.write("**Contact:**")
                        if pd.notna(vehicle['seller_whatsapp']):
                            st.markdown(f"[📱 WhatsApp]({vehicle['seller_whatsapp']})")
                        if pd.notna(vehicle['url']):
                            st.markdown(f"[🚗 View on CRAutos]({vehicle['url']})")
                        if pd.notna(vehicle['seller_phone']):
                            st.write(f"📞 {vehicle['seller_phone']}")
        else:
            st.write("No significantly underpriced vehicles found in current inventory.")
    
    with col2:
        st.subheader("📈 Inventory Recommendations")
        recs = create_inventory_recommendations(df)
        
        st.write("**🚀 Fast-Moving Brands:**")
        for brand, count in recs['fast_movers'].items():
            st.write(f"• {brand}: {count} units (high turnover)")
        
        st.write("**💎 High-Margin Luxury:**")
        for brand, count in recs['luxury_brands'].items():
            st.write(f"• {brand}: {count} units (premium pricing)")
        
        st.write(f"**⏰ Optimal Age Range:** {recs['optimal_age']}")
        st.write("Vehicles in this age range have the best volume-to-price ratio.")

def vehicle_inventory_page(df):
    """Vehicle inventory with business links"""
    st.header("🚗 Vehicle Inventory Browser")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        brand_filter = st.selectbox("Brand", options=['All'] + sorted(df['brand'].unique()))
    with col2:
        price_max = st.number_input("Max Price ($)", min_value=0, value=min(100000, int(df['price_usd'].max())))
    with col3:
        age_max = st.number_input("Max Age (years)", min_value=0, value=15)
    with col4:
        show_luxury = st.checkbox("Luxury Only", value=False)
    
    # Apply filters
    filtered_df = df.copy()
    if brand_filter != 'All':
        filtered_df = filtered_df[filtered_df['brand'] == brand_filter]
    filtered_df = filtered_df[filtered_df['price_usd'] <= price_max]
    filtered_df = filtered_df[filtered_df['vehicle_age'] <= age_max]
    if show_luxury:
        filtered_df = filtered_df[filtered_df['is_luxury'] == True]
    
    filtered_df = filtered_df.head(15)  # Limit for performance
    
    st.write(f"Showing {len(filtered_df)} vehicles")
    
    # Display vehicles in cards
    for i in range(0, len(filtered_df), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(filtered_df):
                vehicle = filtered_df.iloc[i + j]
                with col:
                    with st.container():
                        # ML Analysis for inventory cards
                        vehicle_age = 2025 - vehicle['year']
                        brand_avg = df[df['brand'] == vehicle['brand']]['price_usd'].median()
                        predicted_price = brand_avg * max(0.6, 1 - (vehicle_age * 0.06))
                        price_diff_pct = ((vehicle['price_usd'] - predicted_price) / predicted_price * 100)
                        
                        st.subheader(f"{vehicle['year']} {vehicle['brand']} {vehicle['model']}")
                        st.write(f"**${vehicle['price_usd']:,.0f}**")
                        
                        # ML Price Indicator
                        if price_diff_pct < -10:
                            st.success(f"🟢 {abs(price_diff_pct):.0f}% below ML estimate")
                        elif price_diff_pct > 10:
                            st.error(f"🔴 {price_diff_pct:.0f}% above ML estimate")
                        else:
                            st.info(f"🟡 Fair price ({price_diff_pct:+.0f}%)")
                        
                        # Vehicle details
                        if pd.notna(vehicle['mileage']):
                            st.write(f"Mileage: {vehicle['mileage']:,.0f} km")
                        if pd.notna(vehicle['fuel_type']):
                            st.write(f"Fuel: {vehicle['fuel_type']}")
                        
                        # Image
                        if pd.notna(vehicle['images']) and vehicle['images']:
                            first_image = vehicle['images'].split(',')[0].strip()
                            if first_image:
                                try:
                                    st.image(first_image, width=160)
                                except:
                                    st.markdown(f"[View Image]({first_image})")
                        
                        # Contact buttons
                        if pd.notna(vehicle['seller_whatsapp']):
                            st.markdown(f"[📱 WhatsApp]({vehicle['seller_whatsapp']})")
                        if pd.notna(vehicle['url']):
                            st.markdown(f"[🚗 View Details]({vehicle['url']})")
                        
                        st.markdown("---")

def business_insights_page(df):
    """Business insights and KPIs"""
    st.header("📊 Business Intelligence")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    avg_price = df['price_usd'].mean()
    median_days_to_sell = 35  # Estimated
    avg_margin = 12  # Estimated industry average
    inventory_turnover = 365 / median_days_to_sell
    
    with col1:
        st.metric("Average Vehicle Price", f"${avg_price:,.0f}", delta="Market average")
    
    with col2:
        st.metric("Est. Days to Sell", f"{median_days_to_sell}", delta="Industry average")
    
    with col3:
        st.metric("Target Profit Margin", f"{avg_margin}%", delta="Recommended")
    
    with col4:
        st.metric("Annual Turnover", f"{inventory_turnover:.1f}x", delta="Inventory cycles")
    
    st.markdown("---")
    
    # Market trends
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution by segment
        segments = calculate_profit_margins(df)
        
        fig = px.bar(
            segments.reset_index(),
            x='price_segment',
            y='Volume',
            title='Market Volume by Price Segment',
            color='Est_Margin_15%',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Business Insight**: Focus inventory on Economy and Mid-Range segments for optimal volume and margins.")
    
    with col2:
        # Brand performance
        brand_perf = df.groupby('brand').agg({
            'price_usd': ['count', 'mean'],
            'vehicle_age': 'mean'
        }).round(0)
        brand_perf.columns = ['Volume', 'Avg_Price', 'Avg_Age']
        brand_perf = brand_perf[brand_perf['Volume'] >= 10].sort_values('Volume', ascending=False)
        
        fig = px.scatter(
            brand_perf.reset_index(),
            x='Volume',
            y='Avg_Price',
            size='Volume',
            text='brand',
            title='Brand Volume vs Average Price',
            labels={'Volume': 'Market Volume', 'Avg_Price': 'Average Price ($)'}
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Strategy Tip**: Toyota offers high volume with stable pricing. BMW/Mercedes provide higher margins but slower turnover.")
    
    # Seasonal insights (simulated)
    st.subheader("📅 Seasonal Market Trends")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    demand_index = [85, 90, 105, 110, 115, 120, 125, 120, 110, 100, 95, 90]  # Simulated seasonal demand
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=demand_index, mode='lines+markers', name='Demand Index'))
    fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Average Demand")
    fig.update_layout(title='Seasonal Demand Patterns', yaxis_title='Demand Index (%)', height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **Timing Strategy**: Peak demand in summer months (May-Aug). Stock up in winter for spring sales.")

def main():
    """Main reseller dashboard"""
    st.title("💰 Car Reseller Business Intelligence")
    st.markdown("*Maximize profits with data-driven vehicle trading insights*")
    
    # Load data
    df = load_data()
    
    # Sidebar
    st.sidebar.title("🚗 Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis",
        ["Market Opportunities", "Price Calculator", "Vehicle Inventory", "Business Insights", "Inventory Planner"]
    )
    
    # Quick stats sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Market Summary")
    st.sidebar.metric("Total Listings", f"{len(df):,}")
    st.sidebar.metric("Avg Price", f"${df['price_usd'].mean():,.0f}")
    st.sidebar.metric("Price Range", f"${df['price_usd'].min():,.0f} - ${df['price_usd'].max():,.0f}")
    
    # Filters
    st.sidebar.subheader("🔍 Filters")
    price_range = st.sidebar.slider(
        "Price Range ($)",
        min_value=int(df['price_usd'].min()),
        max_value=int(df['price_usd'].max()),
        value=(10000, 50000)
    )
    
    max_age = st.sidebar.slider("Max Vehicle Age (years)", min_value=1, max_value=20, value=10)
    
    # Apply filters
    df_filtered = df[
        (df['price_usd'].between(price_range[0], price_range[1])) &
        (df['vehicle_age'] <= max_age)
    ]
    
    st.sidebar.write(f"📊 Showing {len(df_filtered):,} vehicles")
    
    # Page routing
    if page == "Market Opportunities":
        market_opportunities_page(df_filtered)
    elif page == "Price Calculator":
        price_prediction_tool(df_filtered)
    elif page == "Vehicle Inventory":
        vehicle_inventory_page(df_filtered)
    elif page == "Business Insights":
        business_insights_page(df_filtered)
    elif page == "Inventory Planner":
        st.header("📋 Inventory Planning")
        st.info("🚧 Coming Soon: AI-powered inventory recommendations based on market trends and your business goals.")
        
        # Placeholder content
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Recommended Purchases")
            st.write("• 2018-2020 Toyota Camry: High demand, stable pricing")
            st.write("• 2019-2021 Honda CR-V: Fast turnover, good margins")
            st.write("• 2017-2019 BMW 3 Series: Premium segment opportunity")
        
        with col2:
            st.subheader("Avoid These Segments")
            st.write("• Vehicles >15 years old: Slow turnover")
            st.write("• High-mileage luxury cars: Maintenance risks")
            st.write("• Rare/exotic brands: Limited buyer pool")

if __name__ == "__main__":
    main()