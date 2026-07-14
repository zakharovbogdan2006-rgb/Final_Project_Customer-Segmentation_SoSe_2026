# --------------------------------------------------------
# RFM Analysis and Customer Segmentation Results
# --------------------------------------------------------
# This part of the code creates and saves three final output tables:
# 1. rfm_analysis_result.csv
# 2. cluster_profile_summary.csv
# 3. rfm_code_distribution_by_cluster.csv
#
# It should be run after the RFM scores, RFM_code, and Cluster columns
# have already been created in the result dataframe.
# --------------------------------------------------------

# --------------------------------------------------------
# 1. RFM Analysis Result with CustomerID from original data
# --------------------------------------------------------

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


# --------------------------------------------------------
# 2. Cluster Profile Summary
# --------------------------------------------------------

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


# --------------------------------------------------------
# 3. RFM Code Distribution by Cluster
# --------------------------------------------------------

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

print("File 'rfm_code_distribution_by_cluster.csv' has been created.")