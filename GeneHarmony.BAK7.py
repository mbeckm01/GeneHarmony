import streamlit as st
import psycopg2
import pandas as pd


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


def get_disease_names(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT disease_name FROM disease_names;")
        disease_names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return disease_names
    except psycopg2.DatabaseError as e:
        st.error("Error fetching disease names: " + str(e))
        return []


def get_gene_names_for_diseases(conn, disease_group):
    try:
        cursor = conn.cursor()
        query = "SELECT DISTINCT gene_name FROM gene_disease WHERE disease_name IN %s;"
        cursor.execute(query, (tuple(disease_group),))
        gene_names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return gene_names
    except psycopg2.DatabaseError as e:
        st.error("Error fetching gene names: " + str(e))
        return []


def update_session_state():
    if 'state' not in st.session_state:
        st.session_state.state = {
            'num_groups': 1,
            'selections': {},
            'search_results': None
        }


def add_group_button_pressed():
    st.session_state.state['num_groups'] += 1


def remove_group_button_pressed():
    if st.session_state.state['num_groups'] > 1:
        st.session_state.state['num_groups'] -= 1


def create_multiselect_for_group(group_index, disease_names):
    key = f"group_{group_index}"
    st.session_state.state['selections'].setdefault(key, [])
    selected_names = st.multiselect(f"Select Disease Names - Group {group_index + 1}", disease_names, key=key,
                                    default=st.session_state.state['selections'][key])
    st.session_state.state['selections'][key] = selected_names


def perform_search(disease_names):
    search_results = None
    conn = connect_to_database()
    if conn is not None:
        for key, selected_names in st.session_state.state['selections'].items():
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

    st.session_state.state['search_results'] = search_results


def display_search_results():
    if st.session_state.state['search_results'] is not None:
        st.write("Common Gene Names:")
        st.write(st.session_state.state['search_results'])


def clear_search_results_button_pressed():
    st.session_state.state['search_results'] = None


# Initialize Streamlit app
st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add/remove groups:")

# Initialize session state
update_session_state()

# Fetch disease names
conn = connect_to_database()
disease_names = get_disease_names(conn)

if conn is None:
    st.stop()

# Add Group button
if st.button("Add Group"):
    add_group_button_pressed()

# Remove Group button
if st.button("Remove Group"):
    remove_group_button_pressed()

# Set the number of groups
num_groups = st.session_state.state['num_groups']

# Create and update multiselects for each group
for i in range(num_groups):
    create_multiselect_for_group(i, disease_names)

# Search button
if st.button("Search"):
    perform_search(disease_names)

# Clear button
if st.button("Clear Search Results"):
    clear_search_results_button_pressed()

# Display search results
display_search_results()