import streamlit as st
import psycopg2
import pandas as pd

# Function to connect to the database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="lab_db",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error("Unable to connect to the database: " + str(e))
        return None

# Function to connect to the database and fetch disease names
def get_disease_names(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT disease_name FROM disease_names;")
        disease_names = [row[0] for row in cursor.fetchall()]
        return disease_names
    except psycopg2.OperationalError as e:
        st.error("Cannot fetch disease names: " + str(e))
        return []

# Function to execute a query to retrieve gene names for selected disease names
def get_gene_names_for_diseases(conn, disease_group):
    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT gene_name FROM gene_disease WHERE disease_name IN %s;"
        cursor.execute(query, (tuple(disease_group),))
        gene_names = [row[0] for row in cursor.fetchall()]
        return gene_names
    except psycopg2.DatabaseError as e:
        st.error("Error fetching gene names: " + str(e))
        return []

conn = connect_to_database()
st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add/remove groups:")

# Fetch disease names
disease_names = get_disease_names(conn)

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
    if conn is not None:
        for key, selected_names in st.session_state['selections'].items():
            if selected_names:
                gene_names = get_gene_names_for_diseases(conn, selected_names)
                if search_results is None:
                    search_results = set(gene_names)
                else:
                    search_results = search_results.intersection(gene_names)
        conn.close()

    if search_results:
        search_results = pd.DataFrame(list(search_results), columns=["Common Gene Names"])
    else:
        search_results = pd.DataFrame(columns=["Common Gene Names"])

    st.session_state['search_results'] = search_results

# Display search results
if st.session_state['search_results'] is not None:
    st.write("Common Gene Names:")
    st.write(st.session_state['search_results'])