import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from globalticker.ticker import GlobalTicker
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Ticker Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Ticker Analysis Dashboard")
st.markdown("Analyze multiple tickers with customizable time ranges and currencies")

# Sidebar for controls
st.sidebar.header("Configuration")

# Currency selection
currencies = ['USD', 'THB']
selected_currency = st.sidebar.selectbox("Select Currency", currencies, index=1)  # Default to THB

# Time range selection
st.sidebar.subheader("Time Range")
time_range_options = {
    "1 Month": 30,
    "3 Months": 90,
    "6 Months": 180,
    "1 Year": 365,
    "2 Years": 730,
    "Custom": None
}

selected_range = st.sidebar.selectbox("Select Time Range", list(time_range_options.keys()), index=3)  # Default to 1 Year

if selected_range == "Custom":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", datetime.today())
else:
    end_date = datetime.today().date()
    start_date = (datetime.today() - timedelta(days=time_range_options[selected_range])).date()

# Ticker management
st.sidebar.subheader("Ticker Management")

# Initialize session state for tickers
if 'tickers' not in st.session_state:
    st.session_state.tickers = []

# Add new ticker
new_ticker = st.sidebar.text_input("Add Ticker Symbol", placeholder="e.g., KFAFIX-A, NVDA")
if st.sidebar.button("Add Ticker") and new_ticker:
    if new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
        st.sidebar.success(f"Added {new_ticker}")
    else:
        st.sidebar.warning(f"{new_ticker} already exists")

# Display current tickers with remove option
st.sidebar.write("Current Tickers:")
tickers_to_remove = []
for i, ticker in enumerate(st.session_state.tickers):
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(ticker)
    if col2.button("❌", key=f"remove_{i}"):
        tickers_to_remove.append(ticker)

# Remove selected tickers
for ticker in tickers_to_remove:
    st.session_state.tickers.remove(ticker)

# Analysis button
analyze_button = st.sidebar.button("🔄 Analyze", type="primary")

# Main content area
if analyze_button and st.session_state.tickers:
    with st.spinner("Fetching data..."):
        try:
            # Load tickers
            tickers = {}
            for ticker_name in st.session_state.tickers:
                tickers[ticker_name] = GlobalTicker(ticker_name, currency=selected_currency)
            
            # Fetch history
            data = {}
            failed_tickers = []
            
            for name, ticker in tickers.items():
                try:
                    df = ticker.history(
                        start=start_date.strftime("%Y-%m-%d"), 
                        end=end_date.strftime("%Y-%m-%d")
                    )
                    if not df.empty:
                        data[name] = df["Price"]
                    else:
                        failed_tickers.append(name)
                except Exception as e:
                    failed_tickers.append(name)
                    st.warning(f"Failed to fetch data for {name}: {str(e)}")
            
            if data:
                # Combine into one DataFrame
                df_all = pd.concat(data.values(), axis=1)
                df_all.columns = data.keys()
                
                # Remove any columns that are entirely NaN
                df_all = df_all.dropna(axis=1, how='all')
                
                if not df_all.empty:
                    # Compute percent change from first valid value
                    df_pct = df_all.pct_change().add(1).cumprod()
                    df_pct = (df_pct - 1) * 100  # convert to percent
                    
                    # Create tabs for different views
                    tab1, tab2, tab3 = st.tabs(["📊 Performance Chart", "📈 Price Chart", "📋 Data Table"])
                    
                    with tab1:
                        st.subheader(f"Performance Comparison ({selected_range})")
                        
                        # Create Plotly figure for better interactivity
                        fig = go.Figure()
                        
                        for col in df_pct.columns:
                            fig.add_trace(go.Scatter(
                                x=df_pct.index,
                                y=df_pct[col],
                                mode='lines',
                                name=col,
                                line=dict(width=2)
                            ))
                        
                        fig.update_layout(
                            title=f"Percent Change from Start Date ({selected_currency})",
                            xaxis_title="Date",
                            yaxis_title="Percent Change (%)",
                            hovermode='x unified',
                            height=600,
                            showlegend=True
                        )
                        
                        fig.update_xaxes(showgrid=True)
                        fig.update_yaxes(showgrid=True)
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Performance summary
                        st.subheader("Performance Summary")
                        summary_data = []
                        # for col in df_pct.columns:
                        #     latest_pct = df_pct[col].iloc[-1]
                        #     max_pct = df_pct[col].max()
                        #     min_pct = df_pct[col].min()
                        #     summary_data.append({
                        #         'Ticker': col,
                        #         'Total Return (%)': f"{latest_pct:.2f}%",
                        #         'Max Gain (%)': f"{max_pct:.2f}%",
                        #         'Max Loss (%)': f"{min_pct:.2f}%"
                        #     })
                        for col in df_pct.columns:
                            series = df_all[col].dropna()
                            
                            # Total return (%)
                            total_return = (series.iloc[-1] / series.iloc[0] - 1) * 100
                            
                            # Volatility: standard deviation of daily returns annualized
                            daily_returns = series.pct_change().dropna()
                            volatility = daily_returns.std() * np.sqrt(252) * 100  # annualized %
                            
                            # Maximum Drawdown
                            cum_returns = (1 + daily_returns).cumprod()
                            running_max = cum_returns.cummax()
                            drawdowns = (cum_returns - running_max) / running_max
                            max_dd = drawdowns.min() * 100  # in %
                            
                            summary_data.append({
                                'Ticker': col,
                                'Total Return (%)': f"{total_return:.2f}%",
                                'Volatility (%)': f"{volatility:.2f}%",
                                'Max Drawdown (%)': f"{max_dd:.2f}%"
                            })
                                                
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True)
                    
                    with tab2:
                        st.subheader(f"Price Chart ({selected_currency})")
                        
                        # Price chart
                        fig_price = go.Figure()
                        
                        for col in df_all.columns:
                            fig_price.add_trace(go.Scatter(
                                x=df_all.index,
                                y=df_all[col],
                                mode='lines',
                                name=col,
                                line=dict(width=2)
                            ))
                        
                        fig_price.update_layout(
                            title=f"Price Chart ({selected_currency})",
                            xaxis_title="Date",
                            yaxis_title=f"Price ({selected_currency})",
                            hovermode='x unified',
                            height=600,
                            showlegend=True
                        )
                        
                        fig_price.update_xaxes(showgrid=True)
                        fig_price.update_yaxes(showgrid=True)
                        
                        st.plotly_chart(fig_price, use_container_width=True)
                    
                    with tab3:
                        st.subheader("Raw Data")
                        
                        # Allow user to choose between price and percentage data
                        data_view = st.radio("Select Data View:", ["Prices", "Percentage Changes"])
                        
                        if data_view == "Prices":
                            display_df = df_all.round(4)
                            st.dataframe(display_df, use_container_width=True)
                        else:
                            display_df = df_pct.round(4)
                            st.dataframe(display_df, use_container_width=True)
                        
                        # Download button
                        csv = display_df.to_csv()
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"ticker_data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    
                    if failed_tickers:
                        st.warning(f"Failed to fetch data for: {', '.join(failed_tickers)}")
                
                else:
                    st.error("No valid data found for the selected tickers and time range.")
            
            else:
                st.error("No data could be retrieved for any of the selected tickers.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif not st.session_state.tickers:
    st.info("Please add at least one ticker symbol to begin analysis.")

else:
    st.info("Configure your settings in the sidebar and click 'Analyze' to begin.")

# Instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("""
1. Select your preferred currency
2. Choose a time range or set custom dates
3. Add ticker symbols (one at a time)
   - For Thai stocks, include the `.BK` suffix (e.g., `BDMS.BK`)
   - For Thai mutual funds, use the fund symbol (e.g., `KFAFIX-A`)
   - For US or other global stocks, just use the ticker (e.g., `NVDA`)
4. Click 'Analyze' to generate charts
5. Use tabs to view different analyses
""")

st.sidebar.markdown("### Supported Exchanges")
st.sidebar.markdown("""
- US stocks (NASDAQ, NYSE)
- Thai stocks (SET, use `.BK` suffix)
- Global indices
- Cryptocurrencies
- Thai mutual funds
- And more...
""")
