import matplotlib.pyplot as plt
import pandas as pd
#reading the csv file
df = pd.read_csv(r'C:\Users\zakha\TUM_programming_Sose2026\project\final_cleaned_sales.csv', sep = ';')
#the names of the hourly revenue columns
hours = [
    'TIME_0000_0600_REVENUE',
    'TIME_0601_1200_REVENUE',
    'TIME_1200_1800_REVENUE',
    'TIME_1801_2359_REVENUE'
]

#total revenue for each hour range 
totals = df[hours].sum()
#creating labels for x axis
labels = ["0-6", "6-12", "12-18", "18-24"]
#making a bar chart
plt.bar(labels, totals)

#Adding names for axis, graph
plt.xticks(rotation=0)
plt.xlabel("Hours")
plt.ylabel("Total Revenue")
plt.title("Total Revenue by Hours")
#showing the graph
plt.show()