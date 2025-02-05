import json

import yfinance as yf
import pandas as pd


def safe_loc(df, row_label, col_label):
    """
    Safely retrieve the value at (row_label, col_label) in df.
    Returns None if either is missing.
    """
    if df is None or df.empty:
        return None
    if (row_label not in df.index) or (col_label not in df.columns):
        return None
    return df.loc[row_label, col_label]


def fetch_financial_metrics(ticker, years=3):
    """
    Fetch and compute key financial metrics for the last `years` columns
    for the given ticker.
    Returns a dictionary with metrics for each of those years.
    """

    stock = yf.Ticker(ticker)

    # Fetch statements
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    income_statement = stock.financials

    # If any DF is empty, we won't have valid data
    if balance_sheet is None or balance_sheet.empty:
        print(f"Warning: No balance sheet data for {ticker}.")
    if cash_flow is None or cash_flow.empty:
        print(f"Warning: No cash flow data for {ticker}.")
    if income_statement is None or income_statement.empty:
        print(f"Warning: No income statement data for {ticker}.")

    # Columns are often in descending order (most recent first).
    # Grab the first `years` columns:
    available_years = balance_sheet.columns[:years]  # might be e.g. [2022-12-31, 2021-12-31, 2020-12-31]

    # Initialize a dict that will hold multi-year data in a single row
    company_data = {"Ticker": ticker}

    # Loop over each year column
    for col_date in available_years:
        # Get raw values (replace row labels with the actual ones from your data)
        total_debt = safe_loc(balance_sheet, "Total Debt", col_date)
        stockholders_equity = safe_loc(balance_sheet, "Stockholders Equity", col_date)
        current_assets = safe_loc(balance_sheet, "Current Assets", col_date)
        current_liabilities = safe_loc(balance_sheet, "Current Liabilities", col_date)
        total_revenue = safe_loc(income_statement, "Total Revenue", col_date)
        operating_income = safe_loc(income_statement, "Operating Income", col_date)
        operating_cash_flow = safe_loc(cash_flow, "Operating Cash Flow", col_date)
        capital_expenditures = safe_loc(cash_flow, "Capital Expenditure", col_date)


        # Store each metric in the dict, keyed by year
        # `.year` is available if `col_date` is a Timestamp. If it's just a string,
        # you can store the string directly or parse it first.
        year_str = str(col_date.year) if hasattr(col_date, "year") else str(col_date)

        company_data[f"{year_str} Debt"] = total_debt
        company_data[f"{year_str} Equity"] = stockholders_equity
        company_data[f"{year_str} Revenue"] = total_revenue
        company_data[f"{year_str} Operating Cash Flow"] = operating_cash_flow
        company_data[f"{year_str} Capital Expenditure"] = capital_expenditures
        company_data[f"{year_str} Current Assets"] = current_assets
        company_data[f"{year_str} Current Liabilities"] = current_liabilities
        company_data[f"{year_str} Current Income"] = operating_income

    return company_data


def main():
    with open('financial_tickers.json') as fl:
        tickers = json.load(fl)

    data = []
    for ticker in tickers:
        metrics = fetch_financial_metrics(ticker, years=3)
        data.append(metrics)
        print(f"Finished {ticker}")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    csv_filename = "financial_metrics_last_3_years.csv"
    df.to_csv(csv_filename, index=False)
    print(f"✅ Financial data saved to {csv_filename}")


if __name__ == "__main__":
    main()
