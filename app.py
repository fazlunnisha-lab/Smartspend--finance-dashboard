import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib as mpl
import io

st.set_page_config(page_title="Finance Tracker", page_icon=None, layout="wide")

st.markdown(
    '<meta name="description" content="'
    "Finance Tracker — upload your CSV to visualise income, expenses, and savings. "
    "Interactive charts and category breakdowns in Indian Rupees."
    '">',
    unsafe_allow_html=True,
)

st.markdown("""
<style>
    /* Global font and background */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f7f8fa;
        border-right: 1px solid #e4e6ea;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1a1f36;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* Main title */
    h1 {
        color: #1a1f36;
        font-weight: 700;
        font-size: 1.75rem;
        letter-spacing: -0.02em;
    }

    /* Section headers */
    h2 {
        color: #1a1f36;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: -0.01em;
        margin-top: 0.25rem;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e4e6ea;
        border-radius: 8px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #6b7280;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetricValue"] {
        color: #1a1f36;
        font-size: 1.55rem;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.78rem;
        font-weight: 500;
    }

    /* Chart containers */
    .chart-card {
        background: #ffffff;
        border: 1px solid #e4e6ea;
        border-radius: 8px;
        padding: 1.25rem 1.4rem 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    /* Section divider */
    hr {
        border: none;
        border-top: 1px solid #e4e6ea;
        margin: 1.5rem 0;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #e4e6ea;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background-color: #1a1f36;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.45rem 1rem;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #2d3561;
    }

    /* Info / warning banners */
    [data-testid="stAlert"] {
        border-radius: 6px;
        font-size: 0.85rem;
    }

    /* Selectbox label */
    label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

PALETTE = {
    "income":  "#2563eb",
    "expense": "#dc2626",
    "accent":  "#0f172a",
    "grid":    "#f1f5f9",
    "text":    "#374151",
    "muted":   "#9ca3af",
}

mpl.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.edgecolor": "#d1d5db",
    "axes.labelcolor": PALETTE["text"],
    "axes.titlesize": 11,
    "axes.titleweight": "600",
    "axes.titlecolor": PALETTE["accent"],
    "axes.labelsize": 9,
    "xtick.color": PALETTE["muted"],
    "ytick.color": PALETTE["muted"],
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "grid.color": PALETTE["grid"],
    "grid.linewidth": 0.8,
})

REQUIRED_COLUMNS = {"Date", "Category", "Type", "Amount", "Description"}


def load_sample_data():
    data = {
        "Date": [
            "2024-01-05", "2024-01-10", "2024-01-15", "2024-01-20", "2024-01-25",
            "2024-02-03", "2024-02-08", "2024-02-14", "2024-02-19", "2024-02-25",
            "2024-03-02", "2024-03-10", "2024-03-15", "2024-03-22", "2024-03-28",
        ],
        "Category": [
            "Salary", "Food", "Rent", "Transport", "Entertainment",
            "Salary", "Food", "Utilities", "Healthcare", "Shopping",
            "Salary", "Food", "Rent", "Transport", "Dining",
        ],
        "Type": [
            "Income", "Expense", "Expense", "Expense", "Expense",
            "Income", "Expense", "Expense", "Expense", "Expense",
            "Income", "Expense", "Expense", "Expense", "Expense",
        ],
        "Amount": [
            5000, 300, 1200, 150, 100,
            5000, 280, 180, 90, 400,
            5200, 320, 1200, 160, 220,
        ],
        "Description": [
            "Monthly salary", "Groceries", "Monthly rent", "Bus pass", "Subscription",
            "Monthly salary", "Groceries", "Electric bill", "Doctor visit", "Clothing",
            "Monthly salary", "Groceries", "Monthly rent", "Fuel", "Restaurant",
        ],
    }
    return pd.DataFrame(data)


with st.sidebar:
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(
        "<small style='color:#6b7280;font-size:0.78rem;'>"
        "<b>Required columns</b><br>"
        "<code>Date</code> &nbsp; <code>Category</code> &nbsp; <code>Type</code><br>"
        "<code>Amount</code> &nbsp; <code>Description</code><br><br>"
        "<code>Type</code> must be <code>Income</code> or <code>Expense</code>"
        "</small>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    use_sample = st.checkbox("Use sample data", value=True if not uploaded_file else False)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().title() for c in df.columns]
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            st.stop()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
elif use_sample:
    st.info("Displaying sample data. Upload a CSV file to analyse your own transactions.")
    df = load_sample_data()
else:
    st.warning("Upload a CSV file or enable sample data to continue.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=False)
df = df.dropna(subset=["Date"])
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Month"] = df["Date"].dt.to_period("M").astype(str)

income_df = df[df["Type"] == "Income"]
expense_df = df[df["Type"] == "Expense"]

total_income = income_df["Amount"].sum()
total_expense = expense_df["Amount"].sum()
net_savings = total_income - total_expense
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

st.title("Finance Tracker")
st.markdown(
    "<p style='color:#6b7280;font-size:0.9rem;margin-top:-0.5rem;margin-bottom:1.5rem;'>"
    "Personal financial overview — income, expenses, and savings analysis"
    "</p>",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{total_income:,.2f}")
col2.metric("Total Expenses", f"₹{total_expense:,.2f}")
col3.metric("Net Savings", f"₹{net_savings:,.2f}", delta=f"{savings_rate:.1f}% savings rate")
col4.metric("Transactions", len(df))

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("## Monthly Income vs. Expenses")
    monthly = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0).reset_index()
    if "Income" not in monthly.columns:
        monthly["Income"] = 0
    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    x = range(len(monthly))
    width = 0.38
    ax.bar([i - width / 2 for i in x], monthly["Income"], width,
           label="Income", color=PALETTE["income"], zorder=3)
    ax.bar([i + width / 2 for i in x], monthly["Expense"], width,
           label="Expense", color=PALETTE["expense"], zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(monthly["Month"], rotation=30, ha="right")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax.yaxis.grid(True, zorder=0)
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_right:
    st.markdown("## Expense Breakdown by Category")
    cat_expense = expense_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    if not cat_expense.empty:
        fig2, ax2 = plt.subplots(figsize=(6.5, 3.6))
        base_colors = [
            "#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa",
            "#93c5fd", "#bfdbfe", "#dbeafe", "#eff6ff",
        ]
        colors = base_colors[:len(cat_expense)]
        wedges, texts, autotexts = ax2.pie(
            cat_expense.values,
            labels=cat_expense.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=140,
            wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
            textprops={"fontsize": 8, "color": PALETTE["text"]},
        )
        for at in autotexts:
            at.set_fontsize(7.5)
            at.set_color("white")
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)
    else:
        st.info("No expense data available.")

st.markdown("---")

col_l2, col_r2 = st.columns(2)

with col_l2:
    st.markdown("## Spending Trend")
    daily_expense = expense_df.groupby("Date")["Amount"].sum().reset_index()
    fig3, ax3 = plt.subplots(figsize=(6.5, 3.6))
    ax3.plot(daily_expense["Date"], daily_expense["Amount"],
             color=PALETTE["expense"], linewidth=1.8, zorder=3)
    ax3.fill_between(daily_expense["Date"], daily_expense["Amount"],
                     alpha=0.08, color=PALETTE["expense"])
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax3.yaxis.grid(True, zorder=0)
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Amount (₹)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    plt.close(fig3)

with col_r2:
    st.markdown("## Top Expense Categories")
    top_cats = expense_df.groupby("Category")["Amount"].sum().sort_values(ascending=True).tail(8)
    fig4, ax4 = plt.subplots(figsize=(6.5, 3.6))
    bars = ax4.barh(top_cats.index, top_cats.values,
                    color=PALETTE["income"], height=0.55, zorder=3)
    ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax4.xaxis.grid(True, zorder=0)
    ax4.set_xlabel("Total Amount (₹)")
    for bar, val in zip(bars, top_cats.values):
        ax4.text(val + max(top_cats.values) * 0.01,
                 bar.get_y() + bar.get_height() / 2,
                 f"₹{val:,.0f}", va="center", fontsize=8, color=PALETTE["text"])
    plt.tight_layout()
    st.pyplot(fig4, use_container_width=True)
    plt.close(fig4)

st.markdown("---")

st.markdown("## Transaction Details")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
with col_f2:
    categories = ["All"] + sorted(df["Category"].unique().tolist())
    cat_filter = st.selectbox("Category", categories)
with col_f3:
    months = ["All"] + sorted(df["Month"].unique().tolist())
    month_filter = st.selectbox("Month", months)

filtered = df.copy()
if type_filter != "All":
    filtered = filtered[filtered["Type"] == type_filter]
if cat_filter != "All":
    filtered = filtered[filtered["Category"] == cat_filter]
if month_filter != "All":
    filtered = filtered[filtered["Month"] == month_filter]

display_df = filtered[["Date", "Category", "Type", "Amount", "Description"]].copy()
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹{x:,.2f}")
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)
csv_buffer = io.StringIO()
filtered.drop(columns=["Month"]).to_csv(csv_buffer, index=False)
st.download_button(
    label="Download Filtered Data",
    data=csv_buffer.getvalue(),
    file_name="transactions.csv",
    mime="text/csv",
)
