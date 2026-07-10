import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = r"C:\Users\zakha\Downloads\salse.csv"
SUMMARY_PATH = "potential_churn_cluster_summary.csv"
RANDOM_STATE = 42
RFM_FEATURES = ["Recency", "Monetary", "Frequency"]


def prep_clust(data):
    data_t = data.T
    days = pd.to_numeric(data_t.loc["DAYSSINCELASTORDER"], errors="coerce")
    revenue = pd.to_numeric(data_t.loc["REVENUE"], errors="coerce")
    orders = pd.to_numeric(data_t.loc["TOTAL_ORDERS"], errors="coerce")
    return pd.DataFrame({
        "Recency": pd.qcut(days.rank(method="first"), 5,
                           labels=[5, 4, 3, 2, 1]).astype(int),
        "Monetary": pd.qcut(revenue.rank(method="first"), 5,
                            labels=[1, 2, 3, 4, 5]).astype(int),
        "Frequency": pd.qcut(orders.rank(method="first"), 5,
                             labels=[1, 2, 3, 4, 5]).astype(int),
    })


def clusterisation(d):
    d = d.dropna().copy()
    scaled = StandardScaler().fit_transform(d[RFM_FEATURES])
    model = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=50)
    d["Cluster"] = model.fit_predict(scaled)
    return d


def prepare_data(data):
    dates = {"FIRST_ORDER_DATE", "LATEST_ORDER_DATE"}
    identifiers = {"CustomerID", "index"}
    for column in dates:
        if column in data:
            data[column] = pd.to_datetime(data[column], errors="coerce")
    for column in data.columns:
        if column not in dates | identifiers:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


def create_churn(data):
    days_q80 = data["DAYSSINCELASTORDER"].quantile(0.80)
    orders_q20 = data["TOTAL_ORDERS"].quantile(0.20)
    revenue_q20 = data["REVENUE"].quantile(0.20)

    # Все три условия должны выполняться одновременно.
    data["CHURN"] = (
        (data["DAYSSINCELASTORDER"] >= days_q80)
        & (data["TOTAL_ORDERS"] <= orders_q20)
        & (data["REVENUE"] <= revenue_q20)
    ).astype(int)

    print("--- Границы для определения CHURN ---")
    print(f"DAYSSINCELASTORDER >= {days_q80:.2f}")
    print(f"TOTAL_ORDERS <= {orders_q20:.2f}")
    print(f"REVENUE <= {revenue_q20:.2f}")
    print(f"Клиентов по правилу: {data['CHURN'].sum()}")
    return data


def train_model(data):
    # Три показателя, из которых создан CHURN, исключены во избежание утечки.
    excluded = {
        "index", "CustomerID", "FIRST_ORDER_DATE", "LATEST_ORDER_DATE",
        "DAYSSINCELASTORDER", "TOTAL_ORDERS", "REVENUE", "CHURN",
        "Cluster", "Recency", "Frequency", "Monetary",
    }
    features = [c for c in data.select_dtypes(include=[np.number]).columns
                if c not in excluded]
    x, y = data[features], data["CHURN"]

    if y.nunique() < 2 or y.value_counts().min() < 2:
        raise ValueError(
            "После пересечения трёх условий слишком мало churn-клиентов "
            "для разделения train/test. Ослабьте правило или используйте больше данных."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE
        )),
    ])
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    print("\n--- Качество логистической регрессии ---")
    print(f"Accuracy:  {accuracy_score(y_test, predicted):.3f}")
    print(f"Precision: {precision_score(y_test, predicted, zero_division=0):.3f}")
    print(f"Recall:    {recall_score(y_test, predicted, zero_division=0):.3f}")
    print(f"F1-score:  {f1_score(y_test, predicted, zero_division=0):.3f}")
    data["CHURN_PROBABILITY"] = model.predict_proba(x)[:, 1]
    data["PREDICTED_CHURN"] = model.predict(x)
    return data


def main():
    data = prepare_data(pd.read_csv(DATA_PATH))
    clusters = clusterisation(prep_clust(data))
    data = data.join(clusters[["Recency", "Monetary", "Frequency", "Cluster"]])
    data = train_model(create_churn(data))

    total = len(data)
    churn_total = int(data["PREDICTED_CHURN"].sum())
    summary = data.groupby("Cluster").agg(
        TOTAL_CLIENTS=("CustomerID", "count"),
        CHURN_CLIENTS=("PREDICTED_CHURN", "sum"),
    ).reset_index()
    summary["CHURN_SHARE_IN_CLUSTER"] = (
        summary["CHURN_CLIENTS"] / summary["TOTAL_CLIENTS"]
    )
    summary["SHARE_OF_ALL_CHURN"] = np.where(
        churn_total > 0, summary["CHURN_CLIENTS"] / churn_total, 0
    )

    print("\n--- Итоговый прогноз ---")
    print(f"Всего клиентов: {total}")
    print(f"Скорее всего уйдут: {churn_total}")
    print(f"Доля от всех клиентов: {churn_total / total:.2%}")
    shown = summary.copy()
    for column in ["CHURN_SHARE_IN_CLUSTER", "SHARE_OF_ALL_CHURN"]:
        shown[column] = shown[column].map(lambda value: f"{value:.2%}")
    print("\n", shown.to_string(index=False))
    summary.to_csv(SUMMARY_PATH, index=False)


if __name__ == "__main__":
    main()
