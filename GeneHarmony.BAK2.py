import streamlit as st
import psycopg2

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
except psycopg2.OperationalError:
    st.error("Unable to connect to the database.")
    disease_names = []

# initialize Session State
if 'num_groups' not in st.session_state:
    st.session_state['num_groups'] = 1

# Create a streamlit app
st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add new groups:")

# the number of groups can be increased or decreased with this slider
num_groups = st.number_input('Number of Groups', min_value=1, value=st.session_state['num_groups'])
st.session_state['num_groups'] = num_groups

# the selections are stored in lists that in a dictionary in session state
if 'selections' not in st.session_state:
    st.session_state['selections'] = {}

# now we can dynamically create the dropdowns, store their selections
for i in range(num_groups):
    st.session_state['selections'][i] = st.multiselect(f"Select Disease Names - Group {i+1}", disease_names, key=str(i), default=st.session_state['selections'].get(i, []))

# and display all the multiselect widgets
for idx in range(num_groups):
    st.write(f"Group {idx + 1}: {st.session_state['selections'][idx]}")