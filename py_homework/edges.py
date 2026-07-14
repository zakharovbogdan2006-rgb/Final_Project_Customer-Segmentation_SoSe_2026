import pandas as pd
import matplotlib.pyplot as plt

def clean_orders(filepath="orders.csv"):
    orders = pd.read_csv(filepath)
    missing_qty = int(orders["quantity"].isnull().sum())
    missing_rev = int(orders["revenue"].isnull().sum())
    before = len(orders)

    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce", dayfirst=True)
    orders["region"] = orders["region"].str.title()
    orders["channel"] = orders["channel"].str.title()
    orders = orders.drop_duplicates()
    dup_removed = before - len(orders)

    orders["quantity"] = orders["quantity"].abs()
    orders["quantity"] = orders["quantity"].fillna(orders["quantity"].median())
    orders["revenue"] = orders["revenue"].fillna(orders["revenue"].median())

    years_ok = int(orders["order_date"].dt.year.eq(2025).all())
    stats = {
        "missing_qty": missing_qty,
        "missing_rev": missing_rev,
        "dup_removed": dup_removed,
        "rows": len(orders),
        "years_ok": years_ok,
    }
    return orders, stats
    
def plot_revenue_by_region(orders):
    revenue_by_region = orders.groupby("region")["revenue"].sum()
    plt.title("Total Revenue by Region")
    plt.plot(revenue_by_region.index, revenue_by_region.values)
    plt.xlabel('region')
    plt.ylabel('revenue')
    plt.show()


plot_type = 'bar'
