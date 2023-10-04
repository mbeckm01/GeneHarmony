import csv

# Input file path
input_file = 'gtex_output.tsv'

# Create a set to store unique values from the first column
unique_values = set()

# Open the input file
with open(input_file, 'r', newline='') as infile:
    # Create a TSV reader
    tsv_reader = csv.reader(infile, delimiter='\t')

    # Iterate over each row in the input file
    for row in tsv_reader:
        # Check if the row has at least one element (non-empty row)
        if row:
            # Get the value in the first column (index 0)
            value = row[0]

            # Add the value to the set
            unique_values.add(value)

# Check if all values in the first column are distinct
if len(unique_values) == 0:
    print("No values found in the first column.")
elif len(unique_values) == 1:
    print("All values in the first column are the same.")
else:
    print("Values in the first column are distinct.")

# Print the unique values for reference
print("Unique values in the first column:", unique_values)
