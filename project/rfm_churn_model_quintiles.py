import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_PATH = r"C:\Users\zakha\Downloads\salse.csv"
SUMMARY_PATH = "potential_churn_cluster_summary.csv"
RFM_FEATURES = ["Recency", "Monetary", "Frequency"]

def prep_clust(data): #from RFM_calculation.py
    data_T = data.T
    days = pd.to_numeric(data_T.loc["DAYSSINCELASTORDER"], errors="coerce")
    revenue = pd.to_numeric(data_T.loc["REVENUE"], errors="coerce")
    orders = pd.to_numeric(data_T.loc["TOTAL_ORDERS"], errors="coerce")
    return pd.DataFrame({
        "Recency": pd.qcut(days.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]),
        "Monetary": pd.qcut(revenue.rank(method="first"), 5,labels=[1, 2, 3, 4, 5]),
        "Frequency": pd.qcut(orders.rank(method="first"), 5,labels=[1, 2, 3, 4, 5]),
    })

def clusterisation(d):
    d = d.copy()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(d[RFM_FEATURES])
    model = KMeans(n_clusters=4, random_state=42, n_init=100)
    d["Cluster"] = model.fit_predict(scaled)
    return d

def prepare_data(data):
    for col in data.columns:
        if col == "FIRST_ORDER_DATE" or col == "LATEST_ORDER_DATE":
            data[col] = pd.to_datetime(data[col])
        elif col != "CustomerID" and col != "index":
            data[col] = pd.to_numeric(data[col])

    return data

def create_churn(data):
    """this is generally a proposition of a churn, 
    becuase it is impossible to calculate "real" churn rate on the data provideed"""

    days_q80 = data["DAYSSINCELASTORDER"].quantile(0.80) 
    orders_q20 = data["TOTAL_ORDERS"].quantile(0.20)
    revenue_q20 = data["REVENUE"].quantile(0.20)

    # all three must be satisfied
    data["CHURN"] = ((data["DAYSSINCELASTORDER"] >= days_q80)
    & (data["TOTAL_ORDERS"] <= orders_q20) 
    & (data["REVENUE"] <= revenue_q20))

    print(f"DAYSSINCELASTORDER >= {days_q80:.2f}")
    print(f"TOTAL_ORDERS <= {orders_q20:.2f}")
    print(f"REVENUE <= {revenue_q20:.2f}")
    print(f"Клиентов по правилу: {data['CHURN'].sum()}")
    return data


def train_model(data):
    excl = [
        "index",
        "CustomerID",
        "FIRST_ORDER_DATE",
        "LATEST_ORDER_DATE",
        "DAYSSINCELASTORDER",
        "TOTAL_ORDERS",
        "REVENUE",
        "CHURN",
        "Cluster",
        "Recency",
        "Frequency",
        "Monetary"
    ]

    n_cols = data.select_dtypes(include="number").columns
    features = []

    for col in n_cols:
        if col not in excl:
            features.append(col)

    x = data[features]
    y = data["CHURN"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )

    model.fit(x_train, y_train)

    pred = model.predict(x_test)

    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred, zero_division=0)
    recall = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)

    print("\n--- Качество логистической регрессии ---")
    print("Accuracy:", round(accuracy, 3))
    print("Precision:", round(precision, 3))
    print("Recall:", round(recall, 3))
    print("F1-score:", round(f1, 3))

    # делаем прогноз для всех клиентов
    all_x = data[features]
    all_x = scaler.transform(all_x)

    probabilities = model.predict_proba(all_x)
    data["CHURN_PROBABILITY"] = probabilities[:, 1]
    data["PREDICTED_CHURN"] = model.predict(all_x)

    return data
def main():
    data = prepare_data(pd.read_csv(DATA_PATH))
    clusters = clusterisation(prep_clust(data))
    data = data.join(clusters[["Recency", "Monetary", "Frequency", "Cluster"]])
    data = train_model(create_churn(data))

    total = len(data)
    churn_total = int(data["PREDICTED_CHURN"].sum())
    summary = data.groupby("Cluster")
    summary = summary.agg( TOTAL_CLIENTS=("CustomerID", "count"), CHURN_CLIENTS=("PREDICTED_CHURN", "sum"),)
    summary = summary.reset_index()
    summary["CHURN_SHARE_IN_CLUSTER"] = (summary["CHURN_CLIENTS"] / summary["TOTAL_CLIENTS"])
    summary["SHARE_OF_ALL_CHURN"] = (summary["CHURN_CLIENTS"] / churn_total)

    print("\n--- Итоговый прогноз ---")
    print(f"Number of clients {total}")
    print(f"probabaly will leave {churn_total}")
    print(f"fraction of all clients {churn_total / total:.2%}")
    shown = summary.copy()
    for col in ["CHURN_SHARE_IN_CLUSTER", "SHARE_OF_ALL_CHURN"]:
        shown[col] = shown[col].map(lambda value: f"{value:.2%}")
    print("\n", shown.to_string(index=False))
    summary.to_csv(SUMMARY_PATH, index=False)


if __name__ == "__main__":
    main()
