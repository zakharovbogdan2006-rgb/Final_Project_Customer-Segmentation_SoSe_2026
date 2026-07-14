import pandas as pd

#Loading the data from the dataset
df = pd.read_csv(r'C:\Users\zakha\Downloads\salse (3).csv')

# Drop columns where any row is null, after checking how many rows were dropped, we can say we have no null entries. 
#Might change up later and add fillup formulas for missing values, but there is no current need since no empty fields in the cs anywas
initial_cols = df.shape[1]
df = df.dropna(axis=1, how='any')
print(f"Dropped {initial_cols - df.shape[1]} empty columns.")

# Rename columns to better description and standardized wording "AVERAGE from AVG" and word separator "_"
df = df.rename(columns={
    'REVENUE': 'TOTAL_REVENUE',
    'AVERAGESHIPPING': 'AVERAGE_SHIPPING_COST',
    'AVGDAYSBETWEENORDERS': 'AVERAGE_DAYS_BETWEEN_ORDERS',
    'DAYSSINCELASTORDER': 'DAYS_SINCE_LAST_ORDER'
})

#  Drop index because we already use the ID as a unique identifier and the index is redundant. We dont need it for the data analysis
if 'index' in df.columns:
    df = df.drop(columns=['index'])

# Filtering some possible impossible negative values, in case they exist. 
# Also filtering out any customers whose latest order date is before their first order date, which is obviouslyimpossible.
initial_rows = df.shape[0]
df = df[(df['TOTAL_ORDERS'] >= 0) & 
        (df['TOTAL_REVENUE'] >= 0) & 
        (df['LATEST_ORDER_DATE'] >= df['FIRST_ORDER_DATE'])]
print(f"Dropped {initial_rows - df.shape[0]} rows due to negative values/invalid dates.")

# Making sure all entries of Customer ID are unique and only the most recent one counts 
initial_rows = df.shape[0]
df = df.sort_values(by='LATEST_ORDER_DATE', ascending=False)
df = df.drop_duplicates(subset=['CustomerID'], keep='first')
print(f"Dropped {initial_rows - df.shape[0]} duplicate rows.")

# Type Conversions in Pandas. Unfortunately deppending on the app they might still be read as wrong data type, depends on setting of the app
df['FIRST_ORDER_DATE'] = pd.to_datetime(df['FIRST_ORDER_DATE'])
df['LATEST_ORDER_DATE'] = pd.to_datetime(df['LATEST_ORDER_DATE'])

int_cols = [
    'CustomerID', 'TOTAL_ORDERS', 'MONDAY_ORDERS', 'TUESDAY_ORDERS', 'WEDNESDAY_ORDERS', 
    'THURSDAY_ORDERS', 'FRIDAY_ORDERS', 'SATURDAY_ORDERS', 'SUNDAY_ORDERS',
    'WEEK1_DAY01_DAY07_ORDERS', 'WEEK2_DAY08_DAY15_ORDERS', 'WEEK3_DAY16_DAY23_ORDERS', 
    'WEEK4_DAY24_DAY31_ORDERS', 'TIME_0000_0600_ORDERS', 'TIME_0601_1200_ORDERS', 
    'TIME_1200_1800_ORDERS', 'TIME_1801_2359_ORDERS'
]

float_cols = [
    'TOTAL_REVENUE', 'AVERAGE_ORDER_VALUE', 'AVERAGE_SHIPPING_COST', 'CARRIAGE_REVENUE',
    'MONDAY_REVENUE', 'TUESDAY_REVENUE', 'WEDNESDAY_REVENUE', 'THURSDAY_REVENUE', 
    'FRIDAY_REVENUE', 'SATURDAY_REVENUE', 'SUNDAY_REVENUE', 'WEEK1_DAY01_DAY07_REVENUE', 
    'WEEK2_DAY08_DAY15_REVENUE', 'WEEK3_DAY16_DAY23_REVENUE', 'WEEK4_DAY24_DAY31_REVENUE',
    'TIME_0000_0600_REVENUE', 'TIME_0601_1200_REVENUE', 'TIME_1200_1800_REVENUE', 
    'TIME_1801_2359_REVENUE'
]
#fillna not necessary sincewe already filter empty values, but good to keep around 
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

for col in float_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)

#saving to a completely new csv file (the old one is kept as a backup) 
# Reset and Final Save. Using sep=';' instead of ',' is the "European Excel" fix, because , often used as decimal separator.
#  Using ',' is good for the Extreme CSV app, and I am using it
#date format used is international standard (but default for pandas, and most csv readers, thre's actually no need to change it)
df = df.reset_index(drop=True)
df.to_csv('final_cleaned_sales.csv', index=False, sep=',', encoding='utf-8-sig', date_format='%Y-%m-%d')

#making sure operations fibnished

print("Cleanup complete. Saved to 'final_cleaned_sales.csv'.")