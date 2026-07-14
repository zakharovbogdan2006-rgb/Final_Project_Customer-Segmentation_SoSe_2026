import pandas as pd
# scores to determine the quality of clusteriasion
from sklearn.metrics import silhouette_score,  davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.stats import skew, normaltest
from sklearn.preprocessing import StandardScaler
# df = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv")
data = pd.read_csv(r"C:\Users\zakha\Downloads\salse.csv", header=0)  # get the data

features = ["Recency", "Monetary", "Frequency"]

def prep_clust(data):

    data_T = data.T
    days_since = pd.to_numeric(data_T.loc["DAYSSINCELASTORDER"])
    revenue = pd.to_numeric(data_T.loc["REVENUE"])
    freq = pd.to_numeric(data_T.loc["TOTAL_ORDERS"])

    recency_score = pd.qcut(
        days_since.rank(method="first"), q=5,labels=[5, 4, 3, 2, 1]).astype(int)
    monetary_score = pd.qcut( revenue.rank(method="first"),q=5, labels=[1, 2, 3, 4, 5] ).astype(int)
    freq_score = pd.qcut(freq.rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    data_for_clusters = pd.DataFrame({"Recency": recency_score,"Monetary": monetary_score, "Frequency": freq_score})

    return data_for_clusters

def prep_clust_raw(data):
    data_T = data.T

    data_for_clusters = pd.DataFrame({
        "Recency": pd.to_numeric(
            data_T.loc["DAYSSINCELASTORDER"]),
        "Monetary": pd.to_numeric(
            data_T.loc["REVENUE"]),
        "Frequency": pd.to_numeric(
            data_T.loc["TOTAL_ORDERS"])})

    return data_for_clusters

def clusterisation(d):
    X = d[features].copy()
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    kmeans = KMeans( n_clusters=4, random_state=42, n_init=50)   #best number of clusters based on the scores and RFM logi
    labels = kmeans.fit_predict(X)
    result = d.copy()
    result["Cluster"] = labels
    return result, X, kmeans, scaler

result, X, model, scaler = clusterisation(prep_clust(data))

data[["Recency", "Monetary", "Frequency", "Cluster"]] = (
    result[["Recency", "Monetary", "Frequency", "Cluster"]])

def scores(result, X_scaled):
    silhouette = silhouette_score(X_scaled, result["Cluster"])
    calinski_harabasz = calinski_harabasz_score(X_scaled, result["Cluster"])
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
centroids_pca = pca.transform(model.cluster_centers_)

print(cluster_profile)
print(scores(result, X))
print("data remained:",pca.explained_variance_ratio_.sum())

def build_clusters():
    return { "scores": clusterisation(prep_clust(data)),"raw": clusterisation(prep_clust_raw(data))}
