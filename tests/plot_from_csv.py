# py .\tests\plot_from_csv.py

import csv
import matplotlib.pyplot as plt

# File path to the CSV file
file_path = 'log/00_trace.csv'

# Column index to read from (assuming 0-based index)
column_index = 12

# Lists to store the x (row numbers) and y (values) data
x_values = []
y_values = []

# Read the CSV file
with open(file_path, mode='r') as file:
    csv_reader = csv.reader(file)

    # Read the header (first row)
    header = next(csv_reader)
    plot_title = header[column_index].capitalize()

    # Iterate through the remaining rows in the CSV file
    row_number = 1
    for row in csv_reader:
        # Check if the value in the specified column is not empty
        if row[column_index].strip():
            # Convert the value to a float and store it
            y_values.append(float(row[column_index]))
            # Store the row number
            x_values.append(row_number - 1)
        row_number += 1

# Plot the numbers
plt.scatter(x_values, y_values, marker="o")
plt.title(plot_title)
plt.xlabel('Step')
plt.ylabel('Value')
plt.show()
