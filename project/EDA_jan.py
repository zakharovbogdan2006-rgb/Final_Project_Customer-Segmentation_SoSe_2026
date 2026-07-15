import pandas as pd
import matplotlib.pyplot as plt
# 1. Open the cleaned file from the previous step
df = pd.read_csv(r'C:\Users\zakha\TUM_programming_Sose2026\project\final_cleaned_sales.csv', sep = ';')

# POINT 1: Sorting Customers based on Recency for making Recency Segmentation

top_recency = df.sort_values(by='DAYS_SINCE_LAST_ORDER', ascending=True)

# POINT 2: Sorting Customers based on Frequency for making frequency segmentation

top_frequency = df.sort_values(by='TOTAL_ORDERS', ascending=False)

# POINT 3: Sorting Customers based on Monetary value for making monetary segmentation

top_monetary = df.sort_values(by='TOTAL_REVENUE', ascending=False)

# POINT 4: Simple Visualization with Matpotlib
#RECENCY TABLE
df["DAYS_SINCE_LAST_ORDER"].hist(bins=100, weights=[100/len(top_recency)]*len(top_recency))
title = 'Distribution of Recency'
median = top_recency['DAYS_SINCE_LAST_ORDER'].median()
skewness = top_recency['DAYS_SINCE_LAST_ORDER'].skew()
plt.text(skewness + 100, plt.ylim()[1] * 0.8, f'Skewness: {skewness:.3f}', color='b', fontsize=10)
plt.title(title)
plt.axvline(median, color='r', linestyle='dashed', linewidth=1)
plt.text(median + 40, plt.ylim()[1] * 0.9, f'Median: {median}', color='r', fontsize=10)
plt.xlabel("Recency (Days Since Last Order)")
plt.ylabel("Percentage of Customers (%)")
plt.show()

#FREQUENCY TABLE
df["TOTAL_ORDERS"].hist(bins=100, weights=[100/len(top_frequency)]*len(top_frequency))
title = 'Distribution of Frequency'
median = top_frequency['TOTAL_ORDERS'].median()
skewness = top_frequency['TOTAL_ORDERS'].skew()
plt.title(title)
plt.text(skewness + 18, plt.ylim()[1] * 0.8, f'Skewness: {skewness:.3f}', color='b', fontsize=10)
plt.axvline(median, color='r', linestyle='dashed', linewidth=1)
plt.text(median + 12, plt.ylim()[1] * 0.9, f'Median: {median}', color='r', fontsize=10)
plt.xlabel("Frequency (Total Orders)")
plt.ylabel("Percentage of Customers (%)")
plt.show()

#MONETARY TABLE
df["TOTAL_REVENUE"].hist(bins=100, weights=[100/len(top_monetary)]*len(top_monetary))
title = 'Distribution of Monetary'
median = top_monetary['TOTAL_REVENUE'].median()
skewness = top_monetary['TOTAL_REVENUE'].skew()
plt.title(title)
plt.text(skewness + 5000, plt.ylim()[1] * 0.8, f'Skewness: {skewness:.3f}', color='b', fontsize=10)
plt.axvline(median, color='r', linestyle='dashed', linewidth=1)
plt.text(median + 4034, plt.ylim()[1] * 0.9, f'Median: {median}', color='r', fontsize=10)
plt.xlabel("Monetary (Total Revenue)")
plt.ylabel("Percentage of Customers (%)")
plt.show()

#CUSTOMER DAY OF VISIT TABLE
day_visit = df[['MONDAY_ORDERS', 'TUESDAY_ORDERS', 'WEDNESDAY_ORDERS', 'THURSDAY_ORDERS', 'FRIDAY_ORDERS', 'SATURDAY_ORDERS', 'SUNDAY_ORDERS']].sum()
day_visit.index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_visit.plot.bar()
plt.xlabel("Day")
plt.ylabel('Number of Visits')
plt.title("Customer Visits by Day of the Week")

plt.show()

df.to_csv('Sales+EDA.csv', index=False)
print("-> File 'Sales+EDA.csv' has been successfully created.")