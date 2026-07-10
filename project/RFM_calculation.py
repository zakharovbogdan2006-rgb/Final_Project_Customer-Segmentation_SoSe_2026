import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # visualisation
# scores to determine the quality of clusteriasion
from sklearn.metrics import silhouette_score,  davies_bouldin_score, calinski_harabasz_score
import seaborn as sns  # for heatmap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import skew, normaltest
# df = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv")
# df.to_excel("salse.xlsx", index= False)
data = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv",
                   header=0)  # get the data
# all_sums = np.sum(data, axis = 0)

def distribution_report(series):
    x = pd.to_numeric(series, errors="coerce").dropna()

    result = {
        "mean": x.mean(),
        "median": x.median(),
        "std": x.std(),
        "skewness": skew(x),
        "normal_p": normaltest(x).pvalue,
        "q25": x.quantile(0.25),
        "q50": x.quantile(0.50),
        "q75": x.quantile(0.75),
        "q90": x.quantile(0.90),
        "q95": x.quantile(0.95),
        "q99": x.quantile(0.99), }

    if (x > 0).all():
        log_x = np.log(x)
        result["log_skewness"] = skew(log_x)
        result["lognormal_p"] = normaltest(log_x).pvalue
    else:
        result["log_skewness"] = np.nan
        result["lognormal_p"] = np.nan

    return pd.Series(result)

features = ["Recency", "Monetary", "Frequency"]

def prep_clust(data):

    data_T = data.T

    days_since = pd.to_numeric(data_T.loc["DAYSSINCELASTORDER"], errors="coerce")
    revenue = pd.to_numeric(data_T.loc["REVENUE"], errors="coerce")
    frequency = pd.to_numeric(data_T.loc["TOTAL_ORDERS"], errors="coerce")

    recency_score = pd.qcut(
        days_since.rank(method="first"),
        q=5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    monetary_score = pd.qcut(
        revenue.rank(method="first"),
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    frequency_score = pd.qcut(
        frequency.rank(method="first"),
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    data_for_clusters = pd.DataFrame({
        "Recency": recency_score,
        "Monetary": monetary_score,
        "Frequency": frequency_score
    })

    return data_for_clusters

def prep_clust_raw(data):
    data_T = data.T

    data_for_clusters = pd.DataFrame({
        "Recency": pd.to_numeric(
            data_T.loc["DAYSSINCELASTORDER"], errors="coerce"
        ),
        "Monetary": pd.to_numeric(
            data_T.loc["REVENUE"], errors="coerce"
        ),
        "Frequency": pd.to_numeric(
            data_T.loc["TOTAL_ORDERS"], errors="coerce"
        )
    })

    return data_for_clusters.dropna()

def clusterisation(d):
    d = d.dropna()
    X = d[features].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(
        n_clusters=4,  # besr number of clusters based on the scores and RFM logic
        random_state=42,
        n_init=50
    )

    labels = kmeans.fit_predict(X_scaled)

    result = d.copy()
    result["Cluster"] = labels

    return result, X_scaled, kmeans, scaler

def heatmap(d):
    d = pd.DataFrame(d.iloc[2::])
    X_only_numbers = d.select_dtypes(include=["number"])

    columns_to_drop = ["CustomerID", "index", "DAYSSINCELASTORDER"]
    X_only_numbers = X_only_numbers.drop(
        columns=[col for col in columns_to_drop if col in X_only_numbers.columns]
    )
    corr_matrix = X_only_numbers.corr()

    plt.figure(figsize=(30, 30))

    sns.heatmap(
        corr_matrix,
        annot=False,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
    )
    plt.title("Correlation matrix", fontsize=16)
    plt.tight_layout()
    plt.show()

# print(clusterisation(prep_clust(data)))
result, X_scaled, model, scaler = clusterisation(prep_clust(data))

def scores(result, X_scaled):
    silhouette = silhouette_score(X_scaled, result["Cluster"])
    calinski_harabasz = calinski_harabasz_score(X_scaled, result["Cluster"])
    davies_bouldin = davies_bouldin_score(X_scaled, result["Cluster"])

    print(f"Silhouette Score = {silhouette:.3f}")
    print(f"ch_score = {calinski_harabasz}")
    print(f"davies_bouldin = {davies_bouldin}")
    return silhouette, calinski_harabasz, davies_bouldin

cluster_profile = result.groupby("Cluster")[features].mean()
points = X_scaled
labels = result["Cluster"].to_numpy()
centroids = model.cluster_centers_
print(cluster_profile)
print(scores(result, X_scaled))

pca = PCA(n_components=2)

points_pca = pca.fit_transform(X_scaled)
centroids_pca = pca.transform(model.cluster_centers_)

print(
    "data remained:",
    pca.explained_variance_ratio_.sum()
)

def build_clusters():
    return {
        "scores": clusterisation(prep_clust(data)),
        "raw": clusterisation(prep_clust_raw(data))
    }

