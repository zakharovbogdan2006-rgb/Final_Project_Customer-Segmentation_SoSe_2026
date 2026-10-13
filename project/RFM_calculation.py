import pandas as pd
# scores to determine the quality of clusteriasion
from sklearn.metrics import silhouette_score,  davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA  # needed for different file
from sklearn.preprocessing import StandardScaler
# df = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv")
data = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv",
                   header=0)  # get the data

features = ["Recency", "Monetary", "Frequency"]


def prep_clust(data):

    data_T = data.T  # facilitate the work with data
    days_since = data_T.loc["DAYSSINCELASTORDER"]
    revenue = data_T.loc["REVENUE"]
    freq = data_T.loc["TOTAL_ORDERS"]
# split into quintilies and label correctly
    recency_score = pd.qcut(
        # may not be an integer
        days_since.rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    monetary_score = pd.qcut(revenue.rank(method="first"), q=5, labels=[
                             1, 2, 3, 4, 5]).astype(int)
    freq_score = pd.qcut(freq.rank(method="first"), q=5,
                         labels=[1, 2, 3, 4, 5]).astype(int)
    data_for_clusters = pd.DataFrame(
        {"Recency": recency_score, "Monetary": monetary_score, "Frequency": freq_score})

    return data_for_clusters


def prep_clust_raw(data):
    data_T = data.T
# def for the rfm
    data_for_clusters = pd.DataFrame({
        "Recency": pd.to_numeric(
            data_T.loc["DAYSSINCELASTORDER"]),
        "Monetary": pd.to_numeric(
            data_T.loc["REVENUE"]),
        "Frequency": pd.to_numeric(
            data_T.loc["TOTAL_ORDERS"])})

    return data_for_clusters


def clusterisation(d):
    X = d[features].copy()  # not to change the entire dataset
    scaler = StandardScaler()  # initialization
    X = scaler.fit_transform(X)
    # best number of clusters based on the scores and RFM logi
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=50)
    labels = kmeans.fit_predict(X)
    result = d.copy()
    result["Cluster"] = labels
    return result, X, kmeans, scaler


result, X, model, scaler = clusterisation(prep_clust(data))
# Create column names required by the RFM output code
result["R_score"] = result["Recency"]
result["F_score"] = result["Frequency"]
result["M_score"] = result["Monetary"]

# Create the RFM code in Recency-Frequency-Monetary order
result["RFM_code"] = (
    result["R_score"].astype(str)
    + result["F_score"].astype(str)
    + result["M_score"].astype(str)
)

data[["Recency", "Monetary", "Frequency", "Cluster"]] = (
    result[["Recency", "Monetary", "Frequency", "Cluster"]])


def scores(result, X_scaled):
    '''Measures how well each point fits its own cluster compared to other clusters, higher is better'''
    silhouette = silhouette_score(X_scaled, result["Cluster"])

    # Measures the ratio of between-cluster dispersion to within-cluster dispersion, higher is better
    calinski_harabasz = calinski_harabasz_score(X_scaled, result["Cluster"])

    # Measures cluster similarity based on within-cluster spread and between-cluster separation, lower is better
    davies_bouldin = davies_bouldin_score(X_scaled, result["Cluster"])

    print(f"Silhouette Score = {silhouette:.3f}")
    print(f"ch_score = {calinski_harabasz}")
    print(f"davies_bouldin = {davies_bouldin}")
    return silhouette, calinski_harabasz, davies_bouldin


cluster_profile = result.groupby("Cluster")[features].mean()
points = X
labels = result["Cluster"].to_numpy()
centroids = model.cluster_centers_
pca = PCA(n_components=2)
points_pca = pca.fit_transform(X)
centroids_pca = pca.transform(model.cluster_centers_)  # for visualisation file

print(cluster_profile)
print(scores(result, X))



def build_clusters():  # for visualisation file
    return {"scores": clusterisation(prep_clust(data)), "raw": clusterisation(prep_clust_raw(data))}




rfm_result = result[
    ["R_score", "F_score", "M_score", "RFM_code", "Cluster"]
].copy()

# Take CustomerID from the original dataframe using the same index as result
rfm_result.insert(
    0,
    "CustomerID",
    data.loc[result.index, "CustomerID"].values
)

# Show the customer-level RFM result
try:
    display(rfm_result)
except NameError:
    print(rfm_result.head())

# Save the customer-level RFM result
rfm_result.to_csv(
    "rfm_analysis_result.csv",
    index=False,
    encoding="utf-8-sig"
)

print("File 'rfm_analysis_result.csv' has been created.")

# 2. Cluster Profile Summary

cluster_profile_summary = (
    result
    .groupby("Cluster")
    .agg(
        Total_Customers=("Cluster", "size"),
        Avg_R_score=("R_score", "mean"),
        Avg_F_score=("F_score", "mean"),
        Avg_M_score=("M_score", "mean")
    )
    .reset_index()
)

# Round average RFM scores for a cleaner report table
cluster_profile_summary[["Avg_R_score", "Avg_F_score", "Avg_M_score"]] = (
    cluster_profile_summary[["Avg_R_score", "Avg_F_score", "Avg_M_score"]]
    .round(2)
)

# Business interpretation of clusters
segment_names = {
    0: "Recent low-value customers",
    1: "Regular customers at risk",
    2: "Low-value inactive customers",
    3: "High-value active customers"
}

cluster_profile_summary["Segment_Interpretation"] = (
    cluster_profile_summary["Cluster"].map(segment_names)
)

# Show the cluster summary table
try:
    display(cluster_profile_summary)
except NameError:
    print(cluster_profile_summary)

# Save the cluster profile summary
cluster_profile_summary.to_csv(
    "cluster_profile_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("File 'cluster_profile_summary.csv' has been created.")

# 3. RFM Code Distribution by Cluster

# Count how many customers have each RFM code inside each cluster
rfm_cluster_table = (
    result
    .groupby(["Cluster", "RFM_code"])
    .size()
    .reset_index(name="Customer_Count")
    .sort_values(["Cluster", "RFM_code"])
)

# Count total number of customers in each cluster
cluster_totals = (
    result
    .groupby("Cluster")
    .size()
    .reset_index(name="Cluster_Total")
)

# Add cluster totals to the RFM-code table
rfm_cluster_table = rfm_cluster_table.merge(
    cluster_totals,
    on="Cluster",
    how="left"
)

# Calculate the share of each RFM code inside its cluster
rfm_cluster_table["Share_in_Cluster_%"] = (
    rfm_cluster_table["Customer_Count"] /
    rfm_cluster_table["Cluster_Total"] * 100
).round(2)

# Save the detailed RFM-code distribution in section style
with open("rfm_code_distribution_by_cluster.csv", "w", encoding="utf-8-sig") as f:

    f.write("RFM Code Distribution by Cluster\n\n")

    for cluster in sorted(rfm_cluster_table["Cluster"].unique()):

        cluster_data = rfm_cluster_table[
            rfm_cluster_table["Cluster"] == cluster
        ].copy()

        total = int(cluster_data["Cluster_Total"].iloc[0])

        f.write(f"Cluster {cluster} | Total: {total}\n")

        cluster_data[["RFM_code", "Customer_Count", "Share_in_Cluster_%"]].to_csv(
            f,
            index=False
        )

        f.write("\n")

print("File 'rfАm_code_distribution_by_cluster.csv' has been created.")
