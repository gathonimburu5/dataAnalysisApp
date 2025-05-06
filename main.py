import streamlit as st
import pandas as pd
import plotly.express as px
from langdetect import detect
import json
import os

st.set_page_config(page_title="Analysis App", page_icon="📊", layout="wide")

category_file = "category.json"

if "categories" not in st.session_state:
    st.session_state.categories = { "uncategorized": [], }

if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

def save_category():
    with open(category_file, "w") as f:
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

def add_keywords_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_category()
        return True
    return False

def load_transactions(file):
    try:
        if file is not None:
            df = pd.read_csv(file)
            df.columns = [col.strip() for col in df.columns]
            #st.write(df)
            return categorized_transaction(df)
        else:
            os.chdir(r"C:\Users\PAUL\Desktop\pythonApplications\DataAnalysis")
            df = pd.read_csv("bank_transactions.csv")
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
            st.session_state.debit_df = debit_df.copy()
            st.session_state.credit_df = credit_df.copy()

            #add the category
            st.sidebar.header("Category")
            new_category = st.sidebar.text_input("Category Name:", placeholder="enter category name")
            add_button = st.sidebar.button("Add Category")
            if add_button and new_category:
                st.session_state.categories[new_category] = []
                save_category()
                st.rerun()

            tab1, tab2 = st.tabs(["Debit Transaction (Dr)", "Credit Transaction (Cr)"])
            with tab1:
                st.subheader("Debit Expense Tracker")
                with st.expander("Total Dr Expenses"):
                    total_dr = debit_df["Amount"].sum()
                    detail_format = pd.DataFrame([{"Descriptions": "Total Dr Expenses", "Amounts": total_dr}])
                    st.dataframe(detail_format, column_config={"Amount":st.column_config.NumberColumn("Amount", format="%.2f KES")}, use_container_width=True, hide_index=True)

                edited_df = st.data_editor(
                    st.session_state.debit_df[["AccountNumber", "Date", "Amount", "Description", "Category"]],
                    column_config={
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f KES"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category", options=list(st.session_state.categories.keys())
                        )
                    }, hide_index=True, use_container_width=True, key="category_editor"
                )
                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if row["Category"] == st.session_state.debit_df.at[idx, "Category"]:
                            continue
                        details = row["Description"]
                        st.session_state.debit_df.at[idx, "Category"] = new_category
                        add_keywords_to_category(new_category, details)
                #st.write(debit_df)
                tabs1, tabs2 = st.columns((2))
                with tabs1:
                    st.subheader("Dr Transaction Summary")
                    category_totals = st.session_state.debit_df.groupby("Category")["Amount"].sum().reset_index()
                    category_totals = category_totals.sort_values("Amount", ascending=False)
                    st.dataframe(category_totals.style.background_gradient(cmap="Blues"), column_config={"Amount":st.column_config.NumberColumn("Amount", format="%.2f KES")}, use_container_width=True, hide_index=True)

                with tabs2:
                    fig = px.pie(category_totals, values="Amount", names="Category", title="DR Expense wise Category")
                    st.plotly_chart(fig, use_container_width=True)

                debit_df["Date"] = pd.to_datetime(debit_df["Date"], errors="coerce")
                debit_df["month_year"] = debit_df["Date"].dt.to_period("M")
                with st.expander("Debit Time Series Analysis"):
                    linechart = pd.DataFrame(debit_df.groupby(debit_df["month_year"].dt.strftime("%Y : %b"))["Amount"].sum()).reset_index()
                    fig = px.line(linechart, x="month_year", y="Amount", labels="Amount", width=1000, height=500, template="gridon")
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("Debit Time Series Summary"):
                    st.write(linechart.T.style.background_gradient(cmap="Blues"))

            with tab2:
                st.subheader("Credit Payment Tracker")
                #calculate the totals of cr payments
                with st.expander("total_cr_payments"):
                    total_cr = credit_df["Amount"].sum()
                    data_format = pd.DataFrame([{"Detail": "Total Credit Payments", "Amount": total_cr}])
                    st.dataframe(data_format, column_config={"Amount":st.column_config.NumberColumn("Amount", format="%.2f KES")}, use_container_width=True, hide_index=True)

                df_edited = st.data_editor(
                    st.session_state.credit_df[["AccountNumber", "Date", "Amount", "Description", "Category"]],
                    column_config={
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f KES"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category", options=list(st.session_state.categories.keys())
                        )
                    }, hide_index=True, use_container_width=True, key="cr_category_editor"
                )
                saving_btn = st.button("Apply Changes", type="secondary")
                if saving_btn:
                    for idx, row in df_edited.iterrows():
                        new_category = row["Category"]
                        if row["Category"] == st.session_state.credit_df.at[idx, "Category"]:
                            continue
                        detail = row["Description"]
                        st.session_state.credit_df.at[idx, "Category"] = new_category
                        add_keywords_to_category(new_category, detail)
                #st.write(credit_df)
                tabl1, tabl2 = st.columns((2))
                with tabl1:
                    st.subheader("Credit Transaction Summary")
                    total_category = st.session_state.credit_df.groupby("Category")["Amount"].sum().reset_index()
                    total_category = total_category.sort_values("Amount", ascending=False)
                    st.dataframe(total_category.style.background_gradient(cmap="Blues"), column_config={"Amount":st.column_config.NumberColumn("Amount", format="%.2f KES")}, use_container_width=True, hide_index=True)

                with tabl2:
                    fig1 = px.pie(total_category, values="Amount", names="Category", title="Credit Payment wise Category")
                    st.plotly_chart(fig1, use_container_width=True)

                credit_df["Date"] = pd.to_datetime(credit_df["Date"], errors="coerce")
                credit_df["month_year"] = credit_df["Date"].dt.to_period("M")
                with st.expander("Credit Time Series Analysis"):
                    line_chart = pd.DataFrame(credit_df.groupby(credit_df["month_year"].dt.strftime("%Y : %b"))["Amount"].sum()).reset_index()
                    fig2 = px.line(line_chart, x="month_year", y="Amount", labels="Amount", width=1000, height=500, template="gridon")
                    st.plotly_chart(fig2, use_container_width=True)
                
                with st.expander("Credit Time Series Summary"):
                    st.write(line_chart.T.style.background_gradient(cmap="Blues"))

                text_detect = st.text_input("Text To Detect:", placeholder="enter some text to be detected", value="testing here")
                language = detect(text_detect)
                st.write(f"Detected Language: {language}")

main()
