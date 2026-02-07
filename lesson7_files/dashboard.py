"""
E-commerce Business Analytics Dashboard
A professional Streamlit dashboard for business performance analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

from data_loader import EcommerceDataLoader, load_and_process_data

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
        color: #1f1f1f;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin: 0;
        margin-bottom: 0.5rem;
    }

    .metric-trend {
        font-size: 0.85rem;
        margin: 0;
    }

    .trend-positive {
        color: #28a745;
    }

    .trend-negative {
        color: #dc3545;
    }

    .bottom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }

    .stars {
        color: #ffc107;
        font-size: 1.2rem;
    }

    .stSelectbox > div > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_dashboard_data():
    """Load and cache data for dashboard."""
    try:
        loader, processed_data = load_and_process_data('ecommerce_data/')
        return loader, processed_data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_currency_short(value):
    """Format currency with K/M suffixes (e.g. $300K, $2M)."""
    if abs(value) >= 1e6:
        return f"${value / 1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"${value / 1e3:.0f}K"
    return f"${value:.0f}"


def format_trend(current, previous):
    """Return an HTML span with arrow and two-decimal-place percentage."""
    if previous == 0 or pd.isna(previous):
        return "N/A"
    change_pct = ((current - previous) / previous) * 100
    arrow = "\u2197" if change_pct >= 0 else "\u2198"        # ↗ / ↘
    css = "trend-positive" if change_pct >= 0 else "trend-negative"
    return f'<span class="{css}">{arrow} {abs(change_pct):.2f}%</span>'


def _tick_currency(value):
    """Plotly tickformat callback string isn't flexible enough, so we build
    tick values / text ourselves for K/M formatting."""
    if abs(value) >= 1e6:
        return f"${value / 1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"${value / 1e3:.0f}K"
    return f"${value:,.0f}"


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def create_revenue_trend_chart(current_data, previous_data,
                               current_year, previous_year):
    """Revenue trend line chart (solid current, dashed previous)."""
    fig = go.Figure()

    current_months = current_data['purchase_month'].nunique()

    if current_months > 1:
        cur = current_data.groupby('purchase_month')['price'].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=cur['purchase_month'], y=cur['price'],
            mode='lines+markers',
            name=str(current_year),
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
        ))

        if previous_data is not None and not previous_data.empty:
            prev = previous_data.groupby('purchase_month')['price'].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=prev['purchase_month'], y=prev['price'],
                mode='lines+markers',
                name=str(previous_year),
                line=dict(color='#7baaf0', width=3, dash='dash'),
                marker=dict(size=8),
            ))

        fig.update_layout(title="Monthly Revenue Trend",
                          xaxis_title="Month", yaxis_title="Revenue")
    else:
        cur_rev = current_data['price'].sum()
        prev_rev = (previous_data['price'].sum()
                    if previous_data is not None and not previous_data.empty else 0)
        fig.add_trace(go.Bar(
            x=[str(current_year), str(previous_year)],
            y=[cur_rev, prev_rev],
            marker=dict(color=['#1f77b4', '#7baaf0']),
            text=[format_currency_short(cur_rev),
                  format_currency_short(prev_rev)],
            textposition='outside',
        ))
        fig.update_layout(title="Revenue Comparison",
                          xaxis_title="Year", yaxis_title="Revenue")

    # Compute nice tick values for K/M formatting on the Y axis
    all_y = list(current_data.groupby('purchase_month')['price'].sum())
    if previous_data is not None and not previous_data.empty:
        all_y += list(previous_data.groupby('purchase_month')['price'].sum())
    if all_y:
        y_max = max(all_y) * 1.15
        step = _nice_step(y_max)
        tick_vals = list(np.arange(0, y_max + step, step))
        tick_text = [_tick_currency(v) for v in tick_vals]
    else:
        tick_vals, tick_text = None, None

    fig.update_layout(
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0',
                   tickvals=tick_vals, ticktext=tick_text),
        height=350,
        margin=dict(t=50, b=50, l=60, r=30),
    )
    return fig


def _nice_step(y_max):
    """Choose a round tick step for the Y axis."""
    raw = y_max / 5
    magnitude = 10 ** int(np.floor(np.log10(max(raw, 1))))
    residual = raw / magnitude
    if residual <= 1:
        nice = 1
    elif residual <= 2:
        nice = 2
    elif residual <= 5:
        nice = 5
    else:
        nice = 10
    return nice * magnitude


def create_category_chart(sales_data):
    """Top 10 categories horizontal bar chart, sorted descending, blue gradient."""
    if 'product_category_name' not in sales_data.columns:
        fig = go.Figure()
        fig.add_annotation(text="Product category data not available",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False)
        return fig

    cat_rev = (sales_data.groupby('product_category_name')['price']
               .sum().sort_values(ascending=True).tail(10))

    fig = go.Figure(data=[
        go.Bar(
            y=cat_rev.index,
            x=cat_rev.values,
            orientation='h',
            marker=dict(color=cat_rev.values, colorscale='Blues',
                        showscale=False),
            text=[format_currency_short(v) for v in cat_rev.values],
            textposition='outside',
            hovertemplate='%{y}<br>Revenue: %{text}<extra></extra>',
        )
    ])

    # K/M tick values on X axis
    x_max = cat_rev.max() * 1.25
    step = _nice_step(x_max)
    tick_vals = list(np.arange(0, x_max + step, step))
    tick_text = [_tick_currency(v) for v in tick_vals]

    fig.update_layout(
        title="Top 10 Product Categories",
        xaxis_title="Revenue",
        yaxis_title="",
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0',
                   tickvals=tick_vals, ticktext=tick_text),
        yaxis=dict(showgrid=False),
        height=350,
        margin=dict(t=50, b=50, l=150, r=60),
    )
    return fig


def create_state_map(sales_data):
    """US choropleth map, blue gradient."""
    if 'customer_state' not in sales_data.columns:
        fig = go.Figure()
        fig.add_annotation(text="Geographic data not available",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False)
        return fig

    state_rev = (sales_data.groupby('customer_state')['price']
                 .sum().reset_index())
    state_rev.columns = ['state', 'revenue']

    fig = go.Figure(data=go.Choropleth(
        locations=state_rev['state'],
        z=state_rev['revenue'],
        locationmode='USA-states',
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Revenue", tickformat='$,.0f'),
    ))
    fig.update_layout(
        title="Revenue by State",
        geo_scope='usa',
        height=350,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    return fig


def create_satisfaction_delivery_chart(sales_data):
    """Bar chart: delivery-time buckets (x) vs avg review score (y)."""
    if ('delivery_days' not in sales_data.columns
            or 'review_score' not in sales_data.columns):
        fig = go.Figure()
        fig.add_annotation(text="Delivery or review data not available",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False)
        return fig

    def _bucket(days):
        if pd.isna(days):
            return 'Unknown'
        if days <= 3:
            return '1-3 days'
        if days <= 7:
            return '4-7 days'
        return '8+ days'

    tmp = sales_data.copy()
    tmp['delivery_bucket'] = tmp['delivery_days'].apply(_bucket)

    avg_scores = (tmp[tmp['delivery_bucket'] != 'Unknown']
                  .groupby('delivery_bucket')['review_score']
                  .mean().reset_index())

    order = ['1-3 days', '4-7 days', '8+ days']
    avg_scores['delivery_bucket'] = pd.Categorical(
        avg_scores['delivery_bucket'], categories=order, ordered=True)
    avg_scores = avg_scores.sort_values('delivery_bucket')

    fig = go.Figure(data=[
        go.Bar(
            x=avg_scores['delivery_bucket'],
            y=avg_scores['review_score'],
            marker=dict(color='#1f77b4'),
            text=[f'{v:.2f}' for v in avg_scores['review_score']],
            textposition='outside',
        )
    ])
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', range=[0, 5]),
        height=350,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    loader, processed_data = load_dashboard_data()
    if loader is None:
        st.error("Failed to load data. Please check your data files.")
        return

    # -----------------------------------------------------------------------
    # Header row: title left, filters right
    # -----------------------------------------------------------------------
    hdr_left, hdr_year, hdr_month = st.columns([2, 1, 1])

    with hdr_left:
        st.title("E-commerce Analytics Dashboard")

    orders_data = processed_data['orders']
    available_years = sorted(orders_data['purchase_year'].unique(), reverse=True)

    with hdr_year:
        default_idx = available_years.index(2023) if 2023 in available_years else 0
        selected_year = st.selectbox("Select Year", available_years,
                                     index=default_idx, key="year_filter")

    with hdr_month:
        month_opts = ['All Months'] + [f'Month {i}' for i in range(1, 13)]
        month_display = st.selectbox("Select Month", month_opts,
                                     index=0, key="month_filter")
        selected_month = (None if month_display == 'All Months'
                          else int(month_display.split(' ')[1]))

    # -----------------------------------------------------------------------
    # Build datasets
    # -----------------------------------------------------------------------
    current_data = loader.create_sales_dataset(
        year_filter=selected_year,
        month_filter=selected_month,
        status_filter='delivered',
    )

    previous_year = selected_year - 1
    previous_data = None
    if previous_year in available_years:
        previous_data = loader.create_sales_dataset(
            year_filter=previous_year,
            month_filter=selected_month,
            status_filter='delivered',
        )

    # -----------------------------------------------------------------------
    # Calculate KPI values
    # -----------------------------------------------------------------------
    total_revenue = current_data['price'].sum()
    total_orders = current_data['order_id'].nunique()
    avg_order_value = current_data.groupby('order_id')['price'].sum().mean()

    prev_revenue = (previous_data['price'].sum()
                    if previous_data is not None else 0)
    prev_orders = (previous_data['order_id'].nunique()
                   if previous_data is not None else 0)
    prev_aov = (previous_data.groupby('order_id')['price'].sum().mean()
                if previous_data is not None else 0)

    monthly_sums = current_data.groupby('purchase_month')['price'].sum()
    monthly_growth = (monthly_sums.pct_change().mean() * 100
                      if len(monthly_sums) > 1 else 0)

    # -----------------------------------------------------------------------
    # KPI row — 4 cards
    # -----------------------------------------------------------------------
    st.markdown("### Key Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Total Revenue</p>
            <p class="metric-value">{format_currency_short(total_revenue)}</p>
            <p class="metric-trend">{format_trend(total_revenue, prev_revenue)}</p>
        </div>""", unsafe_allow_html=True)

    with k2:
        css = "trend-positive" if monthly_growth >= 0 else "trend-negative"
        arrow = "\u2197" if monthly_growth >= 0 else "\u2198"
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Monthly Growth</p>
            <p class="metric-value">{monthly_growth:.2f}%</p>
            <p class="metric-trend"><span class="{css}">{arrow}</span></p>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Average Order Value</p>
            <p class="metric-value">{format_currency_short(avg_order_value)}</p>
            <p class="metric-trend">{format_trend(avg_order_value, prev_aov)}</p>
        </div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-label">Total Orders</p>
            <p class="metric-value">{total_orders:,}</p>
            <p class="metric-trend">{format_trend(total_orders, prev_orders)}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Charts grid — 2 x 2
    # -----------------------------------------------------------------------
    st.markdown("### Performance Analytics")
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        st.plotly_chart(
            create_revenue_trend_chart(current_data, previous_data,
                                       selected_year, previous_year),
            use_container_width=True)
    with r1c2:
        st.plotly_chart(create_category_chart(current_data),
                        use_container_width=True)
    with r2c1:
        st.plotly_chart(create_state_map(current_data),
                        use_container_width=True)
    with r2c2:
        st.plotly_chart(create_satisfaction_delivery_chart(current_data),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Bottom row — 2 cards
    # -----------------------------------------------------------------------
    st.markdown("### Customer Experience Metrics")
    b1, b2 = st.columns(2)

    with b1:
        if 'delivery_days' in current_data.columns:
            avg_del = current_data['delivery_days'].mean()
            prev_del = (previous_data['delivery_days'].mean()
                        if previous_data is not None else 0)
            st.markdown(f"""
            <div class="bottom-card">
                <p class="metric-label">Average Delivery Time</p>
                <p class="metric-value">{avg_del:.1f} days</p>
                <p class="metric-trend">{format_trend(avg_del, prev_del)}</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <p class="metric-label">Average Delivery Time</p>
                <p class="metric-value">N/A</p>
                <p class="metric-trend">Data not available</p>
            </div>""", unsafe_allow_html=True)

    with b2:
        if 'review_score' in current_data.columns:
            avg_rev = current_data['review_score'].mean()
            filled = int(round(avg_rev))
            stars_str = "\u2605" * filled + "\u2606" * (5 - filled)
            st.markdown(f"""
            <div class="bottom-card">
                <p class="metric-value">{avg_rev:.1f}/5.0</p>
                <p class="stars">{stars_str}</p>
                <p class="metric-label">Average Review Score</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <p class="metric-value">N/A</p>
                <p class="metric-label">Average Review Score</p>
                <p class="metric-trend">Data not available</p>
            </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
