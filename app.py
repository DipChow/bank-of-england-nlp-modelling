import streamlit as st
import pandas as pd
import re
import io
import os
from openai import OpenAI
from PyPDF2 import PdfReader  # For PDF parsing

################################################################################
# LLM Calls (Your Provided Functions)
################################################################################

def sonar_chat(system_msg: str, user_msg: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg},
    ]
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    return response.choices[0].message.content

def ask_llm_for_summary(text: str, api_key: str) -> str:
    system_message = (
        "You are a thoroughly experienced financial analyst with the aim of providing "
        "information to national financial regulators about the performance and perspective "
        "of banks in England."
    )
    user_message = (
        "Summarize the following bank earnings call transcript:\n\n"
        f"{text}\n\n"
        "**In your summary, be sure to cover:**\n"
        "- Overall financial performance (revenues, expenses, profit/loss, margins)\n"
        "- Key operational highlights (business segments, new initiatives, major deals)\n"
        "- Management’s outlook or guidance for future quarters\n"
        "- Market conditions or external factors that impacted performance\n"
        "- Any risks, challenges, or concerns mentioned\n\n"
        "Keep your response concise, well-structured, and focused on the main points. "
        "Whenever possible, provide specific figures or examples mentioned in the transcript.\n"
    )
    return sonar_chat(system_message, user_message, api_key)

def ask_llm_for_topics(text: str, api_key: str) -> str:
    system_message = (
        "You are a thoroughly experienced financial analyst with the aim of providing "
        "information to national financial regulators about the performance and perspective "
        "of banks in England."
    )
    user_message = (
        "Please read the following bank earnings call transcript:\n\n"
        f"{text}\n\n"
        "Identify the **top 3 topics** discussed and provide them in a consistent format.\n"
        "Use bullet points, and label them clearly as follows:\n\n"
        "TOPICS:\n"
        "1) [Topic One]\n"
        "2) [Topic Two]\n"
        "3) [Topic Three]\n\n"
        "For each topic:\n"
        "- Provide a short title.\n"
        "- Include a concise 1-2 sentence description.\n\n"
        "Do not include any additional commentary outside of these bullet points.\n"
        "Ensure the final output appears exactly in the 'TOPICS:' format described."
    )
    return sonar_chat(system_message, user_message, api_key)

def ask_llm_for_takeaways(text: str, api_key: str) -> str:
    system_message = (
        "You are a thoroughly experienced financial analyst with the aim of providing "
        "information to national financial regulators about the performance and perspective "
        "of banks in England."
    )
    user_message = (
        "Please read the following bank earnings call transcript:\n\n"
        f"{text}\n\n"
        "Identify the **top 3 takeaways** and present them in bullet-point format.\n"
        "Use the exact format:\n\n"
        "TAKEAWAYS:\n"
        "1) [Takeaway One]\n"
        "2) [Takeaway Two]\n"
        "3) [Takeaway Three]\n\n"
        "For each takeaway:\n"
        "- Provide a concise 1-2 sentence explanation.\n\n"
        "Do not include any additional commentary outside of these bullet points.\n"
        "Ensure the final output appears exactly in the 'TAKEAWAYS:' format described."
    )
    return sonar_chat(system_message, user_message, api_key)

def ask_llm_for_concerns(text: str, api_key: str) -> str:
    system_message = (
        "You are a thoroughly experienced financial analyst with the aim of providing "
        "information to national financial regulators about the performance and perspective "
        "of banks in England."
    )
    user_message = (
        "Please read the following bank earnings call transcript:\n\n"
        f"{text}\n\n"
        "Identify the **top 3 concerns or risks** discussed and present them in bullet-point format.\n"
        "Use the exact format:\n\n"
        "CONCERNS:\n"
        "1) [Concern One]\n"
        "2) [Concern Two]\n"
        "3) [Concern Three]\n\n"
        "For each concern:\n"
        "- Provide a concise 1-2 sentence explanation.\n\n"
        "Do not include any additional commentary outside of these bullet points.\n"
        "Ensure the final output appears exactly in the 'CONCERNS:' format described."
    )
    return sonar_chat(system_message, user_message, api_key)

def ask_llm_for_score(text: str, api_key: str) -> str:
    system_message = (
        "You are a thoroughly experienced financial analyst with the aim of providing "
        "information to national financial regulators about the performance and perspective "
        "of banks in England."
    )
    user_message = (
        "Please read the following bank earnings call transcript:\n\n"
        f"{text}\n\n"
        "Give an **overall performance score** for the quarter, on a scale of 0 to 100.\n"
        "Use the exact format:\n\n"
        "SCORE:\n"
        "[Score Value]\n\n"
        "REASON:\n"
        "[1-2 sentence reason explaining the assigned score]\n\n"
        "Do not include any additional commentary or text outside of the above two fields.\n"
        "Ensure the final output appears exactly as 'SCORE:' then 'REASON:'."
    )
    return sonar_chat(system_message, user_message, api_key)

################################################################################
# Utility to Convert Uploaded File to Text
################################################################################

def convert_file_to_text(uploaded_file) -> str:
    """
    Reads text from an uploaded .txt or .pdf file.
    """
    if uploaded_file is None:
        return ""

    if uploaded_file.name.lower().endswith(".txt"):
        text_data = uploaded_file.read().decode("utf-8", errors="ignore")
        return text_data
    elif uploaded_file.name.lower().endswith(".pdf"):
        pdf_reader = PdfReader(uploaded_file)
        text_data = ""
        for page in pdf_reader.pages:
            text_data += page.extract_text() or ""
        return text_data

    return "Unsupported file format. Please upload a .txt or .pdf file."

################################################################################
# Main App
################################################################################

def main():
    st.title("Bank Earnings Call Explorer")

    # 1) Load your main DataFrame
    df_results = pd.read_csv(
        "/Users/diptarko/Documents/Personal/Cambridge ICE DS/BoE Project/alchemist_llm_results.csv"
    )

    # 2) Load your quarter price predictions
    df_price_preds = pd.read_csv("quarter_price_predictions.csv")

    # 3) Load positivity data
    df_pos = pd.read_csv("positivity_per_call.csv")
    # Columns assumed: call_name, ticker, bank_avg_positivity,
    #                 quarter_avg_positivity, finbert_positivity_tuned

    # Map from full bank name to ticker symbol
    company_ticker_map = {
        "Bank Of America": "BAC",
        "Barclays": "BCS",
        "Citigroup": "C",
        "Credit Suisse": "CS",
        "Deustche Bank": "DB",
        "Hsbc": "HSBC",
    }

    # If "company" not in df_results, parse it out
    if "company" not in df_results.columns:
        pattern = r'^q(\d)_(\d{4})_(.*)$'
        df_results[['quarter', 'year', 'company_raw']] = df_results['transcript'].str.extract(pattern)
        df_results['call'] = 'Q' + df_results['quarter'] + ' ' + df_results['year']
        df_results['company'] = (
            df_results['company_raw']
            .str.replace('_', ' ', regex=True)
            .str.title()
        )
        df_results.drop(columns=['quarter', 'year', 'company_raw'], inplace=True)

    # Create top-level tabs: Explorer & Select Bank (renamed from "Database")
    tab_explorer, tab_select_bank = st.tabs(["Explorer", "Database"])

    ############################################################################
    # EXPLORER TAB
    ############################################################################
    with tab_explorer:
        st.subheader("API Key")
        if "api_key" not in st.session_state:
            st.session_state["api_key"] = ""

        st.session_state["api_key"] = st.text_input(
            "Enter your Perplexity API key:",
            value=st.session_state["api_key"] or "",
            type="password"
        )

        if st.button("Clear API Key"):
            st.session_state["api_key"] = ""

        st.markdown("---")
        st.subheader("Upload transcript")
        uploaded_file = st.file_uploader(
            "Drop a .txt or .pdf file here or click to upload",
            type=["txt", "pdf"]
        )

        if st.button("Run"):
            if not st.session_state["api_key"]:
                st.warning("Please enter your API key before running.")
            else:
                text_data = convert_file_to_text(uploaded_file)
                if not text_data:
                    st.warning("Please upload a valid .txt or .pdf file.")
                else:
                    # ...your existing LLM calls...
                    st.write("**Summary**")
                    summary = ask_llm_for_summary(text_data, api_key=st.session_state["api_key"])
                    st.write(summary)

                    st.write("**Topics**")
                    topics = ask_llm_for_topics(text_data, api_key=st.session_state["api_key"])
                    st.write(topics)

                    st.write("**Takeaways**")
                    takeaways = ask_llm_for_takeaways(text_data, api_key=st.session_state["api_key"])
                    st.write(takeaways)

                    st.write("**Concerns**")
                    concerns = ask_llm_for_concerns(text_data, api_key=st.session_state["api_key"])
                    st.write(concerns)

                    st.write("**Score (0-100)**")
                    score = ask_llm_for_score(text_data, api_key=st.session_state["api_key"])
                    st.write(score)

    ############################################################################
    # SELECT BANK TAB (was Database)
    ############################################################################
    with tab_select_bank:
        # Remove the old "Database" subheader
        # st.subheader("Database")  # <-- removed

        # Each unique company => sub-tab
        companies = sorted(df_results["company"].unique())
        sub_tabs = st.tabs(companies)

        for i, company in enumerate(companies):
            with sub_tabs[i]:
                # ---------------------------------------------------------------
                # 1) Display images, *but first* the ones ending with Stock_Price
                # ---------------------------------------------------------------
                # Gather all images for this bank
                image_files = []
                prefix = None
                if company == "Bank Of America":
                    prefix = "bac"
                elif company == "Barclays":
                    prefix = "bcs"
                elif company == "Credit Suisse":
                    prefix = "cs"

                if prefix is not None:
                    # collect all matching PNGs
                    image_files = [
                        f for f in os.listdir(".")
                        if f.lower().startswith(prefix) and f.lower().endswith(".png")
                    ]

                # We'll separate them so Stock_Price images go first
                stock_price_imgs = []
                other_imgs = []
                for img in image_files:
                    name_no_ext = img[:-4].lower()
                    if name_no_ext.endswith("stock_price"):
                        stock_price_imgs.append(img)
                    else:
                        other_imgs.append(img)

                # Show Stock_Price images first
                for img in stock_price_imgs:
                    st.subheader("Stock Price over Time")
                    st.image(img)

                # Then show the rest
                for img in other_imgs:
                    name_no_ext = img[:-4].lower()
                    if name_no_ext.endswith("call sentiment"):
                        st.subheader("Call Sentiment vs Stock Price")
                    elif name_no_ext.endswith("sentiment analyst"):
                        st.subheader("Analyst vs Company Sentiment Analysis")
                    # add other suffixes if you want
                    st.image(img)

                # ---------------------------------------------------------------
                # 2) Sort calls descending (Q4 2024 => Q1 2020)
                # ---------------------------------------------------------------
                company_df = df_results[df_results["company"] == company]
                calls = sorted(
                    company_df["call"].unique(),
                    key=lambda x: (
                        int(x.split()[1]),         # year
                        int(x.split()[0][1:])      # quarter, e.g. "Q3" => 3
                    ),
                    reverse=True
                )

                selected_call = st.selectbox(
                    f"Select a call for {company}:",
                    calls,
                    key=f"{company}_call_selectbox",
                )

                # ---------------------------------------------------------------
                # 3) Stock Price Prediction
                # ---------------------------------------------------------------
                quarter_str, year_str = selected_call.split()  # e.g. "Q3", "2024"
                year_val = int(year_str)
                ticker = company_ticker_map.get(company, None)

                if ticker is not None:
                    row_pred = df_price_preds[
                        (df_price_preds["ticker"] == ticker)
                        & (df_price_preds["call_q"] == quarter_str)
                        & (df_price_preds["call_year"] == year_val)
                    ]
                    if not row_pred.empty:
                        label = row_pred["quarter_price_prediction_label"].iloc[0]
                        label_lower = label.lower()
                        if label_lower == "price up":
                            color = "green"
                        elif label_lower == "price down":
                            color = "red"
                        elif label_lower == "stationary":
                            color = "orange"
                        else:
                            color = "black"
                        
                        st.markdown(
                            f"<h2 style='font-size:1.2em;'>Stock Price Prediction: <span style='color:{color}; font-size:1.2em;'>{label}</span></h2>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("*(No stock-price prediction available for this call.)*")
                else:
                    st.markdown("*(Ticker mapping not found for this company.)*")

                # ---------------------------------------------------------------
                # 4) Positivity data
                #    (1) Positivity for this call is now displayed in larger text.
                #    (2) Average positivity scores are handled below.
                # ---------------------------------------------------------------
                if ticker:
                    # The calls in df_pos look like "Q1 2020 Earnings Call"
                    call_name = f"{selected_call} Earnings Call"

                    # Filter for this ticker
                    df_ticker_pos = df_pos[df_pos["ticker"] == ticker]

                    # Get the row for the selected call
                    row_call = df_ticker_pos[df_ticker_pos["call_name"] == call_name]
                    if not row_call.empty:
                        call_row = row_call.iloc[0]
                        
                        # 1) Compute averages and call positivity
                        overall_positivity = df_ticker_pos["bank_avg_positivity"].mean()
                        quarter_positivity = call_row["quarter_avg_positivity"]
                        call_positivity = call_row["finbert_positivity_tuned"]

                        # Determine colour for positivity for this call:
                        if (call_positivity > overall_positivity) and (call_positivity > quarter_positivity):
                            call_color = "green"
                        elif (call_positivity < overall_positivity) and (call_positivity < quarter_positivity):
                            call_color = "red"
                        else:
                            call_color = "orange"

                        # Display call positivity in larger text with its colour.
                        st.markdown(
                            f"<h2 style='font-size:1.2em;'>Positivity for this call: <span style='font-size:1.2em; color:{call_color};'>{call_positivity:.3f}</span></h2>",
                            unsafe_allow_html=True
                        )

                        # 2) Average Positivity Score for {bank}
                        if overall_positivity > call_positivity:
                            arrow_bank = " \u2B06"  # up arrow
                            arrow_color_bank = "green"
                        elif overall_positivity < call_positivity:
                            arrow_bank = " \u2B07"  # down arrow
                            arrow_color_bank = "red"
                        else:
                            arrow_bank = ""
                            arrow_color_bank = "black"

                        st.markdown(
                            f"**Average Positivity Score for {company}:** "
                            f"<span style='color:{arrow_color_bank}'>{overall_positivity:.3f}{arrow_bank}</span>",
                            unsafe_allow_html=True
                        )

                        # 3) Average Positivity Score for this Quarter
                        if quarter_positivity > call_positivity:
                            arrow_quarter = " \u2B06"  # up arrow
                            arrow_color_quarter = "green"
                        elif quarter_positivity < call_positivity:
                            arrow_quarter = " \u2B07"  # down arrow
                            arrow_color_quarter = "red"
                        else:
                            arrow_quarter = ""
                            arrow_color_quarter = "black"

                        st.markdown(
                            f"**Average Positivity Score for this Quarter:** "
                            f"<span style='color:{arrow_color_quarter}'>{quarter_positivity:.3f}{arrow_quarter}</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("*(No positivity data found for this exact call.)*")

                # ---------------------------------------------------------------
                # 5) Show data from df_results
                # ---------------------------------------------------------------
                row = company_df[company_df["call"] == selected_call].iloc[0]

                st.subheader("Summary")
                st.write(row["summary"])

                st.subheader("Topics")
                st.write(row["topics"])

                st.subheader("Takeaways")
                st.write(row["takeaways"])

                st.subheader("Concerns")
                st.write(row["concerns"])

                st.subheader("Score (out of 100)")
                st.write(row["score"])


if __name__ == "__main__":
    main()