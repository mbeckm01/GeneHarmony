import streamlit as st
import psycopg2
import pandas as pd


# Function to connect to the database and fetch disease names
def get_disease_names():
    try:
        conn = psycopg2.connect(
            dbname="lab_db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT disease_name FROM disease_names;")
        disease_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return disease_names
    except psycopg2.OperationalError:
        st.error("Unable to connect to the database.")
        return []


# Function to execute a query to retrieve gene names for selected disease names
def get_gene_names_for_diseases(disease_group):
    try:
        conn = psycopg2.connect(
            dbname="lab_db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        # Assuming your "gene_disease" table has columns "gene_name" and "disease_name"
        cursor.execute("SELECT DISTINCT gene_name FROM gene_disease WHERE disease_name IN %s;", (tuple(disease_group),))
        gene_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return gene_names
    except psycopg2.OperationalError:
        st.error("Unable to connect to the database.")
        return []


# Initialize Streamlit app
st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add/remove groups:")

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = {
        'num_groups': 1,
        'selections': {},
        'search_results': None
    }

# Fetch disease names
disease_names = get_disease_names()

# Add Group button
if st.button("Add Group"):
    st.session_state.state['num_groups'] += 1

# Remove Group button
if st.button("Remove Group") and st.session_state.state['num_groups'] > 1:
    st.session_state.state['num_groups'] -= 1

# Set the number of groups
num_groups = st.session_state.state['num_groups']

# Create and update multiselects for each group
for i in range(num_groups):
    key = f"group_{i}"
    st.session_state.state['selections'].setdefault(key, [])
    selected_names = st.multiselect(f"Select Disease Names - Group {i + 1}", disease_names, key=key,
                                    default=st.session_state.state['selections'][key])
    st.session_state.state['selections'][key] = selected_names

# Search button
if st.button("Search"):
    # Execute queries and perform self-join
    search_results = None
    for key, selected_names in st.session_state.state['selections'].items():
        if selected_names:
            gene_names = get_gene_names_for_diseases(selected_names)
            if search_results is None:
                search_results = set(gene_names)
            else:
                search_results = search_results.intersection(gene_names)

    # Convert results to a DataFrame
    if search_results:
        search_results = pd.DataFrame(list(search_results), columns=["Common Gene Names"])
    else:
        search_results = pd.DataFrame(columns=["Common Gene Names"])

    st.session_state.state['search_results'] = search_results

# Display search results
if st.session_state.state['search_results'] is not None:
    st.write("Common Gene Names:")
    st.write(st.session_state.state['search_results'])
