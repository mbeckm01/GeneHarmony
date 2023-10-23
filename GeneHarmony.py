# Import libraries
import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    layout="wide"
)

# Function to connect to the database
def connect_to_database():
        # Define DB connection parameters
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="password",
            host='10.0.0.119', #"localhost", #(10.0.0.119 is postgres on proxmox, must be local or use vpn)
            port="5432"
        )
        return conn

# Function to connect to the database and fetch disease names for the multiselect boxes
def get_disease_names(conn):
        # Cursor object to interact with the DB
        cursor = conn.cursor()
        # SQL query to fetch disease names
        cursor.execute("SELECT disease_name FROM disease_names;")
        # Extract disease names from the result and return as a list
        disease_names = [row[0] for row in cursor.fetchall()]
        return disease_names

# Function to execute a query to retrieve gene names for selected disease names
def get_gene_names_for_diseases(conn, disease_group, min_confidence, max_confidence, selected_sources):
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT gd.gene_name, gd.disease_name 
        FROM gene_disease gd
        INNER JOIN diseases_full df ON gd.gene_name = df.gene_name
        WHERE gd.disease_name IN %s AND df.confidence_score BETWEEN %s AND %s
    """

    params = [tuple(disease_group), min_confidence, max_confidence]

    # Add the source_clean condition if selected_sources is not empty
    if selected_sources:
        query += " AND df.source_clean IN %s"
        params.append(tuple(selected_sources))

    cursor.execute(query, params)
    gene_disease_pairs = cursor.fetchall()
    cursor.close()
    return gene_disease_pairs


# Load gene expression data from .tsv file
gene_expression_df = pd.read_csv('/home/adam/PycharmProjects/Gene-Disease-DB/gtex_output.tsv', sep="\t")

# Function to get gene expression values for common genes
def get_gene_expression_values(gene_expression_df, common_genes):
        gene_expression_subset = gene_expression_df[gene_expression_df['Description'].isin(common_genes)]
        return gene_expression_subset

def get_source_clean_values(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source_clean FROM diseases_full;")
    values = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return values


conn = connect_to_database()
st.sidebar.title("GeneHarmony")
st.sidebar.write("Add diseases to groups to identify genes associated with all diseases within the group.")
st.sidebar.write("Add groups to filter genes associated across diseases groups.")


# Fetch disease names
disease_names = get_disease_names(conn)

# Initialize session state
st.session_state['num_groups'] = 1
st.session_state['selections'] = {}
st.session_state['search_results'] = None
st.session_state['temp_selections'] = {}
st.session_state.setdefault('searched', False)


# Add Group button, adds to num_groups
if st.sidebar.button("Add Group"):
    st.session_state['num_groups'] += 1

# Remove Group button, subtracts from num_groups
if st.sidebar.button("Remove Group") and st.session_state['num_groups'] > 1:
    st.session_state['num_groups'] -= 1

# Set the number of groups
num_groups = st.session_state['num_groups']


# Add a confidence score filter slider
min_confidence, max_confidence = st.sidebar.slider(
    "Filter based on gene-disease confidence score",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0),
    step=0.1
)

# Fetch source_clean values
source_clean_values = get_source_clean_values(conn)

selected_source_clean = st.sidebar.multiselect(
    "Select a gene-disease data source",
    source_clean_values
)



# Create and update multiselects for each group
for i in range(num_groups):
    key = f"group_{i}"
    st.session_state['selections'].setdefault(key, [])
    selected_names = st.multiselect(f"Select Disease Names - Group {i+1}", disease_names, key=key, default=st.session_state['selections'][key])
    st.session_state['temp_selections'][key] = selected_names


# Function to consolidate genes for each disease
def consolidate_gene_data(gene_disease_pairs):
    # Convert pairs into a dictionary: {disease_name: [gene1, gene2,...]}
    consolidated_data = {}
    for gene, disease in gene_disease_pairs:
        if disease in consolidated_data:
            consolidated_data[disease].append(gene)
        else:
            consolidated_data[disease] = [gene]

    # Convert the dictionary into a dataframe with additional gene counts
    df_list = [
        {
            "Disease": disease,
            "Genes": ", ".join(genes),
            "Gene Count": len(genes)
        }
        for disease, genes in consolidated_data.items()
    ]
    consolidated_df = pd.DataFrame(df_list)

    return consolidated_df


# Search button (to perform search)
if st.button("Search"):
    st.session_state['selections'] = st.session_state['temp_selections']

    # For consolidating gene-disease results
    all_gene_disease_pairs = []

    if conn is not None:
        for key, selected_names in st.session_state['selections'].items():
            if selected_names:
                gene_disease_pairs = get_gene_names_for_diseases(conn, selected_names, min_confidence, max_confidence, selected_source_clean)
                all_gene_disease_pairs.extend(gene_disease_pairs)
        conn.close()

    consolidated_df = consolidate_gene_data(all_gene_disease_pairs)
    st.dataframe(consolidated_df)

    # For the heatmap, we only want to display common genes
    # Extracting only the gene names
    common_genes = [gene for gene, _ in all_gene_disease_pairs]
    st.session_state['search_results'] = pd.DataFrame(common_genes, columns=["Common Gene Names"])


if gene_expression_df is not None:
    # Display gene expression values for common genes as a heatmap
    if st.session_state['search_results'] is not None:
        common_genes = st.session_state['search_results']["Common Gene Names"].tolist()
        gene_expression_subset = get_gene_expression_values(gene_expression_df, common_genes)

        if gene_expression_subset is not None:
            # Display gene names in the heatmap
            st.dataframe(pd.DataFrame(common_genes, columns=["Gene Names in Heatmap"]))

            # Create a long-format DataFrame for Plotly heatmap
            gene_expression_long = gene_expression_subset.melt(id_vars=["Description"], var_name="Tissue", value_name="Expression")

            # Apply natural logarithm adjustment + 1 to the z values
            gene_expression_long["Expression"] = np.log1p(gene_expression_long["Expression"])

            # Create a Plotly heatmap
            fig = go.Figure(data=go.Heatmap(
                z=gene_expression_long["Expression"],
                x=gene_expression_long["Tissue"],
                y=gene_expression_long["Description"],
                colorscale="Viridis"
            ))

            # Customize the heatmap layout
            fig.update_layout(
                xaxis_title="Tissue",
                yaxis_title="Common Genes",
                title="Gene Expression Heatmap"
                #height=1000,  # Adjust the height as needed
                #width=2000
            )

            # Display the heatmap
            st.plotly_chart(fig)