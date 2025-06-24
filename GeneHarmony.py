import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from io import BytesIO
import kaleido
st.set_page_config(layout="wide")

# --- Session State Initialization ---
if 'num_groups' not in st.session_state:
    st.session_state['num_groups'] = 1
if 'selections' not in st.session_state:
    st.session_state['selections'] = {}
if 'temp_selections' not in st.session_state:
    st.session_state['temp_selections'] = {}
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None
if 'searched' not in st.session_state:
    st.session_state['searched'] = False
if 'shared_genes' not in st.session_state:
    st.session_state['shared_genes'] = []

# --- Database Connection ---
def connect_to_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="PASSWORD",  # Replace with your actual password
        host="localhost",
        port="5432"
    )
    return conn

def get_disease_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT disease_name FROM disease_names;")
    return [row[0] for row in cursor.fetchall()]

def get_gene_names_for_diseases_with_scores(conn, disease_group, min_confidence, max_confidence, selected_sources):
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT gd.gene_name, gd.disease_name, df.confidence_score 
        FROM gene_disease gd
        INNER JOIN diseases_full df ON gd.gene_name = df.gene_name AND gd.disease_name = df.disease_name
        WHERE gd.disease_name IN %s AND df.confidence_score BETWEEN %s AND %s
    """
    params = [tuple(disease_group), min_confidence, max_confidence]
    if selected_sources:
        query += " AND df.source_clean IN %s"
        params.append(tuple(selected_sources))
    cursor.execute(query, params)
    return cursor.fetchall()

def get_source_clean_values(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source_clean FROM diseases_full;")
    return [row[0] for row in cursor.fetchall()]

def get_gene_expression_values(df, common_genes):
    return df[df['Description'].isin(common_genes)]

# --- Load Gene Expression Data ---
gene_expression_df = pd.read_csv('/PATH/TO/FILE/gtex_output.tsv', sep="\t") #paste the path to where you have gtex_output.tsv stored

# --- Sidebar Layout ---
st.sidebar.title("GeneHarmony")
st.sidebar.write("Add diseases to groups to identify genes associated with all diseases within each group.")
st.sidebar.write("Add groups to filter genes across disease groups.")

if st.sidebar.button("Add Group"):
    st.session_state['num_groups'] += 1

if st.sidebar.button("Remove Group") and st.session_state['num_groups'] > 1:
    st.session_state['num_groups'] -= 1

num_groups = st.session_state['num_groups']

min_confidence, max_confidence = st.sidebar.slider(
    "Filter by confidence score",
    0.0, 5.0, (0.0, 5.0), step=0.1
)

conn = connect_to_database()
disease_names = get_disease_names(conn)
source_clean_values = get_source_clean_values(conn)

selected_source_clean = st.sidebar.multiselect(
    "Select data sources",
    source_clean_values
)

# --- Disease Group Selectors ---
for i in range(num_groups):
    key = f"group_{i}"
    if key not in st.session_state['selections']:
        st.session_state['selections'][key] = []
    selected = st.multiselect(
        f"Disease Names - Group {i+1}",
        disease_names,
        default=st.session_state['selections'][key],
        key=key
    )
    st.session_state['temp_selections'][key] = selected

# --- Search Button and Results ---
if st.button("Search"):
    st.session_state['selections'] = st.session_state['temp_selections']
    all_rows = []
    group_gene_sets = {}
    st.session_state['shared_genes'] = []

    for group_index, disease_list in st.session_state['selections'].items():
        if disease_list:
            results = get_gene_names_for_diseases_with_scores(
                conn, disease_list, min_confidence, max_confidence, selected_source_clean
            )
            group_genes = set()
            for gene, disease, score in results:
                all_rows.append({
                    "Group": group_index,
                    "Disease": disease,
                    "Gene": gene,
                    "Confidence Score": score
                })
                group_genes.add(gene)
            group_gene_sets[group_index] = group_genes

    conn.close()
    result_df = pd.DataFrame(all_rows)

    if not result_df.empty:
        st.dataframe(result_df)

        unique_gene_count = result_df['Gene'].nunique()
        st.info(f"The total number of unique genes from this search is: **{unique_gene_count}**")

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download gene-disease results with confidence scores",
            data=csv,
            file_name='gene_disease_grouped.csv',
            mime='text/csv'
        )

        # --- Genes in Common Across All Groups ---
        if group_gene_sets:
            common_genes = set.intersection(*group_gene_sets.values()) if len(group_gene_sets) > 1 else set()
            st.session_state['shared_genes'] = sorted(common_genes)
            common_df = pd.DataFrame(st.session_state['shared_genes'], columns=["Genes in Common Across All Groups"])
            st.write("")
            st.dataframe(common_df)
            st.info(f"The total number of genes in common among the disease groups from this search is: **{len(common_genes)}**")

            if not common_df.empty:
                shared_csv = common_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download shared genes as CSV",
                    data=shared_csv,
                    file_name='shared_genes.csv',
                    mime='text/csv'
                )

            # --- Venn Diagram ---
            if 2 <= len(group_gene_sets) <= 3:
                st.subheader("Gene Overlap Venn Diagram")
                fig, ax = plt.subplots()
                sets = list(group_gene_sets.values())
                labels = [f"Group {int(i.split('_')[1]) + 1}" for i in group_gene_sets.keys()]
                if len(sets) == 2:
                    venn2(sets, set_labels=labels, ax=ax)
                elif len(sets) == 3:
                    venn3(sets, set_labels=labels, ax=ax)

                st.pyplot(fig)

                # Save Venn diagram to PNG
                buf = BytesIO()
                fig.savefig(buf, format="png")
                st.download_button(
                    label="Download Venn diagram as PNG",
                    data=buf.getvalue(),
                    file_name="venn_diagram.png",
                    mime="image/png"
                )
            elif len(group_gene_sets) > 3:
                st.warning("Venn diagram supports up to 3 groups. For more, consider using an UpSet plot.")
        else:
            st.warning("No gene sets found to compare across groups.")

        st.session_state['search_results'] = pd.DataFrame(result_df['Gene'].unique(), columns=["Common Gene Names"])
    else:
        st.warning("No gene-disease results found for the selected parameters.")
        st.session_state['search_results'] = None

# --- Heatmap Visualization (for shared genes only) ---
if gene_expression_df is not None and st.session_state['shared_genes']:
    shared_gene_list = st.session_state['shared_genes']
    subset = get_gene_expression_values(gene_expression_df, shared_gene_list)
    if not subset.empty:
        gene_expression_long = subset.melt(id_vars=["Description"], var_name="Tissue", value_name="Expression")
        gene_expression_long["Expression"] = np.log1p(gene_expression_long["Expression"])
        fig = go.Figure(data=go.Heatmap(
            z=gene_expression_long["Expression"],
            x=gene_expression_long["Tissue"],
            y=gene_expression_long["Description"],
            colorscale="Viridis",
            colorbar=dict(
                title="Log(Expression)",
                tickmode="auto",  # or "array" if you want custom ticks
                ticks="outside",
                tickfont=dict(color="black", size=12)
            )
        ))
        fig.update_layout(
            xaxis_title="Tissue",
            yaxis_title="Shared Genes",
            title="Gene Expression Heatmap (Shared Genes Only)",
            font=dict(color="black"),
            margin=dict(l=200, r=50, t=50, b=400),
            yaxis=dict(automargin=True),
            xaxis=dict(tickangle=45)
        )
        # Save high-res PNG image of the heatmap
        fig.write_image("heatmap_output.png", format="png", scale=3, width=1200, height=1000)

        #Load the saved image and let user download it
        with open("heatmap_output.png", "rb") as f:
            st.download_button(
                label="Download Heatmap as High-Resolution PNG",
                data=f,
                file_name="heatmap_output.png",
                mime="image/png"
            )

        # Also show the interactive version in app
        st.plotly_chart(fig, use_container_width=True)
