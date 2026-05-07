import pandas as pd

def load_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine='openpyxl')
    return df


def clean_data(df):
    df.columns = df.columns.str.strip()

    # Convert OrderDate → datetime
    df['OrderDate'] = pd.to_datetime(df['OrderDate'], dayfirst=True)

    # Create Sales column
    df['Sales'] = df['Quantity'] * df['UnitPrice']

    return df


def total_sales(df):
    return df['Sales'].sum()


def total_orders(df):
    return df['OrderID'].nunique()


def sales_by_region(df):
    return df.groupby('Region')['Sales'].sum().reset_index()


def sales_by_product(df):
    return df.groupby('Product')['Sales'].sum().reset_index()


def monthly_sales(df):
    df['Month'] = df['OrderDate'].dt.to_period('M').astype(str)
    return df.groupby('Month')['Sales'].sum().reset_index()


def top_products(df, n=5):
    return (
        df.groupby('Product')['Sales']
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )