import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Analysis App", page_icon="📊", layout="wide")

category = "category.json"

if "categories" not in st.session_state:
    st.session_state.categories = { "uncategorized": [], }

if os.path.exists(category):
    with open(category, "r") as f:
        st.session_state.categories = json.load(f)

def save_category():
    with open(category, "w") as f:
        json.dump(st.session_state.categories, f)

def categorized_transaction(df):
    df["Category"] = "uncategorized"
    for category, keywords in st.session_state.categories.items():
        if category == "uncategorized" is not keywords:
            continue
        lowered_keyword = [keyword.lower().strip() for keyword in keywords]
        for idx, row in df.iterrows():
            detail = row["Description"].lower().strip()
            if detail in lowered_keyword:
                df.at[idx, "Category"] = category
    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        st.write(df)
        return categorized_transaction(df)
    except Exception as e:
        st.error(f"an error occurred while uploading data file: {str(e)}")
        return None

def main():
    st.subheader("💱Transaction Dashboard")
    uploaded_file = st.file_uploader("Upload File", type=["csv"])
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        if df is not None:
            debit_df = df[df["TransactionType"] == "Debit"].copy()
            credit_df = df[df["TransactionType"] == "Credit"].copy()
            deposit_df = df[df["TransactionType"] == "Deposit"].copy()
            purchase_df = df[df["TransactionType"] == "Purchase"].copy()
            loan_df = df[df["TransactionType"] == "Loan Payment"].copy()
            atm_df = df[df["TransactionType"] == "ATM Withdrawal"].copy()
            out_df = df[df["TransactionType"] == "Transfer Out"].copy()
            in_df = df[df["TransactionType"] == "Transfer In"].copy()
            refund_df = df[df["TransactionType"] == "Refund"].copy()

            #add the category
            new_category = st.text_input("Category Name:")
            add_button = st.button("Add Category")
            if add_button and new_category:
                st.session_state.categories[new_category] = []
                save_category()
                st.rerun()

            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Debit Transaction (Dr)", "Credit Transaction (Cr)", "Deposits Transaction", "Purchases Transaction", "Loan Transaction", "ATM Transactions", "Transfer Out Transaction", "Transfer In Transaction", "Refund Transaction"])
            with tab1:
                st.write(debit_df)
            with tab2:
                st.write(credit_df)
            with tab3:
                st.write(deposit_df)
            with tab4:
                st.write(purchase_df)
            with tab5:
                st.write(loan_df)
            with tab6:
                st.write(atm_df)
            with tab7:
                st.write(out_df)
            with tab8:
                st.write(in_df)
            with tab9:
                st.write(refund_df)

main()
