import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from RFM_calculation import build_clusters
''' TO RUN THIS FILE AND GET THE PUCTURE YOU NEED TO RUN "python visualization" IN TERMINAL IN THE CORRECT DIRECTORY'''
def plot_pca(ax, result, x_scaled, model, title):
    labels = result["Cluster"].to_numpy()
    pca = PCA(n_components=2)
    p_pca = pca.fit_transform(x_scaled)
    centr_pca = pca.transform(model.cluster_centers_)
    p = 0.5
    x_min = p_pca[:, 0].min() - p
    x_max = p_pca[:, 0].max() + p
    y_min = p_pca[:, 1].min() - p
    y_max = p_pca[:, 1].max() + p
    x_vals = np.linspace(x_min, x_max, 500)
    y_vals = np.linspace(y_min, y_max, 500)

    xx, yy = np.meshgrid(x_vals, y_vals)
    grid_pca = np.column_stack((xx.ravel(), yy.ravel()))
    grid_or = pca.inverse_transform(grid_pca)
    grid_labels = model.predict(grid_or).reshape(xx.shape)

    ax.contourf(xx, yy, grid_labels, levels=np.arange(model.n_clusters + 1) - 0.5,cmap="viridis",alpha=0.2,)
    ax.contour(xx,yy, grid_labels, levels=np.arange(model.n_clusters - 1) + 0.5, colors="black", linewidths=1.5,)
    ax.scatter( p_pca[:, 0],p_pca[:, 1],c=labels, cmap="viridis", s=8, alpha=0.35, edgecolors="none",)
    ax.scatter(centr_pca[:, 0], centr_pca[:, 1], c=np.arange(len(centr_pca)), cmap="viridis",
        marker="^", s=35, edgecolors="black", linewidths=1, label="Centroids", zorder=10, )
    variance = pca.explained_variance_ratio_.sum()
    ax.set_title(f"{title}\nPCA saved {variance:.1%} of variance")
    ax.set_xlabel("PCA 1")
    ax.set_ylabel("PCA 2")
    ax.legend()

def show_visualizations():
    clusters = build_clusters()

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    scores_result, scores_x, scores_model, _ = clusters["scores"]
    plot_pca( axes[0], scores_result, scores_x, scores_model, "RFM scores from 1 to 5",)
    raw_result, raw_x, raw_model, _ = clusters["raw"]
    plot_pca(axes[1], raw_result, raw_x, raw_model,"Raw RFM data",)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_visualizations()
