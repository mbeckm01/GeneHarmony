import streamlit as st
import psycopg2

# Page configuration
st.set_page_config(
    page_title="Genes Between Diseases",
    page_icon="🧬",
    layout="wide"
)

# Title
st.title("Genes Between Diseases")

# Initialize session state to store additional search terms
if 'additional_terms' not in st.session_state:
    st.session_state.additional_terms = []

# Search terms input
search_terms = st.text_input("Enter a search term:", key="search_term_0")

# Additional search terms
for i, term in enumerate(st.session_state.additional_terms, start=1):
    term_input = st.text_input(f"Enter search term {i}:", key=f"search_term_{i}", value=term)
    st.session_state.additional_terms[i-1] = term_input

# Button to add search fields
if st.button("Add Search Term"):
    st.session_state.additional_terms.append("")

# Add search button
if st.button("Search"):
    # Combine all search terms
    all_terms = [term for term in [search_terms] + st.session_state.additional_terms if term]

    # Connect to the database
    conn = psycopg2.connect(host="localhost", database="sjogren", user="adam", password="password")
    cur = conn.cursor()

    # SQL queries
    executed_queries = []
    gene_counts = []

    for i, term in enumerate(all_terms, start=1):
        sql_query = f"SELECT gene_name, disease_name, confidence_score FROM diseases_db_experiments WHERE LOWER(disease_name) LIKE '%{term.lower()}%'"
        executed_queries.append(sql_query)

        # Execute the query and fetch results
        cur.execute(sql_query)
        result = cur.fetchall()

        # Display gene count
        count = len(result)
        gene_counts.append(f"Search term '{term}' found {count} genes.")

        # Display query results
        if result:
            st.dataframe(result)

    # Display executed queries and gene counts
    st.markdown("### Executed Queries:")
    for query in executed_queries:
        st.code(query)

    st.markdown("### Gene Counts:")
    for count in gene_counts:
        st.write(count)

    conn.close()
