import streamlit as st
import pandas as pd
import os

# Define paths to your CSV files
disease_names_file = "disease_names.csv"
gene_disease_file = "gene_disease.csv"

# Load CSV data into Pandas DataFrames
def load_data():
    disease_names_df = pd.read_csv(disease_names_file)
    gene_disease_df = pd.read_csv(gene_disease_file)
    return disease_names_df, gene_disease_df

disease_names_df, gene_disease_df = load_data()

st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add/remove groups:")

# Fetch disease names
disease_names = disease_names_df["disease_name"].tolist()

# Initialize session state
if 'num_groups' not in st.session_state:
    st.session_state['num_groups'] = 1
    st.session_state['selections'] = {}
    st.session_state['search_results'] = None
    st.session_state['temp_selections'] = {}

# Add Group button
if st.button("Add Group"):
    st.session_state['num_groups'] += 1

# Remove Group button
if st.button("Remove Group") and st.session_state['num_groups'] > 1:
    st.session_state['num_groups'] -= 1

# Set the number of groups
num_groups = st.session_state['num_groups']

# Create and update multiselects for each group
for i in range(num_groups):
    key = f"group_{i}"
    st.session_state['selections'].setdefault(key, [])
    selected_names = st.multiselect(f"Select Disease Names - Group {i+1}", disease_names, key=key, default=st.session_state['selections'][key])
    st.session_state['temp_selections'][key] = selected_names

# Search button (to perform search)
if st.button("Search"):
    st.session_state['selections'] = st.session_state['temp_selections']

    # Execute queries and perform self-join
    search_results = None
    for key, selected_names in st.session_state['selections'].items():
        if selected_names:
            # Filter gene_disease_df based on selected disease names
            filtered_df = gene_disease_df[gene_disease_df['disease_name'].isin(selected_names)]
            gene_names = filtered_df["gene_name"].unique().tolist()
            if search_results is None:
                search_results = set(gene_names)
            else:
                search_results = search_results.intersection(gene_names)

    if search_results:
        search_results_df = pd.DataFrame(list(search_results), columns=["Common Gene Names"])
    else:
        search_results_df = pd.DataFrame(columns=["Common Gene Names"])

    st.session_state['search_results'] = search_results_df

# Display search results
if st.session_state['search_results'] is not None:
    st.write("Common Gene Names:")
    st.write(st.session_state['search_results'])
