import streamlit as st
import psycopg2

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

# Initialize Streamlit app
st.title("Disease Name Dropdown Groups")
st.write("Type to search and select disease names or add/remove groups:")

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = {
        'num_groups': 1,
        'selections': {}
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
    selected_names = st.multiselect(f"Select Disease Names - Group {i+1}", disease_names, key=key, default=st.session_state.state['selections'][key])

    # Use a "Confirm Selections" button for each group
    if st.button(f"Confirm Selections - Group {i+1}"):
        st.session_state.state['selections'][key] = selected_names

# Display selections for each group
for i in range(num_groups):
    key = f"group_{i}"
    st.write(f"Group {i + 1}: {st.session_state.state['selections'][key]}")
