import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Transaction Stats Dashboard", layout="wide")

# -------- READ FILE --------
file_path = "./output/wallet_report.xlsx"
df = pd.read_excel(file_path)

# ---------------- CLEAN & PREPARE DATA ----------------
numeric_cols = ["amount", "vat", "oldBalance", "newBalance", "paymentBalance"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ---------------- FILTER BY USER ----------------
all_users = df["userId"].dropna().unique()
selected_user = st.selectbox("Select User", sorted(all_users))

user_df = df[df["userId"] == selected_user]

st.subheader(f"Transactions for User: {selected_user}")
st.dataframe(user_df)

# ---------------- MONTHLY & YEARLY VISUALIZATION ----------------
if not user_df.empty and "timestamp" in user_df.columns:
    # Add month/year columns
    user_df["Year"] = user_df["timestamp"].dt.year
    user_df["Month"] = user_df["timestamp"].dt.month

    # ---- Monthly Aggregation ----
    monthly_data = user_df.groupby(["Year", "Month"])["amount"].sum().reset_index()
    monthly_data["Month-Year"] = monthly_data["Year"].astype(str) + "-" + monthly_data["Month"].astype(str).str.zfill(2)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(monthly_data["Month-Year"], monthly_data["amount"], marker='o', color='blue')
    ax1.set_title(f"Monthly Transaction Amount - {selected_user}")
    ax1.set_xlabel("Month-Year")
    ax1.set_ylabel("Total Amount")
    ax1.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # ---- Yearly Aggregation ----
    yearly_data = user_df.groupby("Year")["amount"].sum().reset_index()

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.bar(yearly_data["Year"], yearly_data["amount"], color='orange')
    ax2.set_title(f"Yearly Transaction Amount - {selected_user}")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Total Amount")
    ax2.grid(axis='y')
    st.pyplot(fig2)

# ---------------- EXISTING DASHBOARD KPIs ----------------
st.subheader("Summary KPIs for Selected User")
total_amount = user_df["amount"].sum()
transaction_count = len(user_df)
avg_transaction_value = user_df["amount"].mean()
max_transaction_value = user_df["amount"].max()
min_transaction_value = user_df["amount"].min()

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", transaction_count)
col2.metric("Total Amount", f"{total_amount:,.2f}")
col3.metric("Average Transaction Value", f"{avg_transaction_value:,.2f}")

col4, col5 = st.columns(2)
col4.metric("Max Transaction Value", f"{max_transaction_value:,.2f}")
col5.metric("Min Transaction Value", f"{min_transaction_value:,.2f}")
