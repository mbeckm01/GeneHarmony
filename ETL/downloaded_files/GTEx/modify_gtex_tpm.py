import csv

# Input file and output file paths
input_file = 'gtex_input.tsv'
output_file = 'gtex_output.tsv'

# Open the input and output files
with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    # Create a TSV reader and writer
    tsv_reader = csv.reader(infile, delimiter='\t')
    tsv_writer = csv.writer(outfile, delimiter='\t')

    # Skip the first two rows
    next(tsv_reader)
    next(tsv_reader)

    # Iterate over each row in the input file
    for row in tsv_reader:
        # Remove the first column by excluding the first element (column) from each row
        modified_row = row[1:]

        # Write the modified row to the output file
        tsv_writer.writerow(modified_row)

print("First column and first two rows removed. Output saved to '{}'.".format(output_file))
