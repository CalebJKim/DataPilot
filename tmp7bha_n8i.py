import matplotlib.pyplot as plt
import seaborn as sns

# SQL Data
total_profit = 151312291
average_msrp = 48524.63345
average_horsepower = 291.743493
average_torque = 301.977417
total_vehicles_sold = 17662

# Data for visualization
categories = ['Total Profit', 'Average MSRP', 'Average Horsepower', 'Average Torque', 'Total Vehicles Sold']
values = [total_profit, average_msrp, average_horsepower, average_torque, total_vehicles_sold]

# Setting the seaborn style
sns.set(style="whitegrid")

# Create a figure for the bar plot
plt.figure(figsize=(10, 6))
sns.barplot(x=categories, y=values, palette="viridis")

# Adding title and labels
plt.title('Revenue Generation Metrics')
plt.ylabel('Values')
plt.xticks(rotation=45)

# Save the plot
plt.savefig('revenue_generation_metrics.png')
plt.close()