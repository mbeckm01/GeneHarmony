import streamlit as st
import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="lab_db",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)

# Create a cursor object
cursor = conn.cursor()

# Query the database to get the list of disease names
cursor.execute("SELECT disease_name FROM disease_names;")
disease_names = [row[0] for row in cursor.fetchall()]

# Close the database connection
conn.close()

# Create a Streamlit app
st.title("GeneHarmony")
st.write("Type to search and select one or more disease names:")

# Create a multiselect dropdown menu with autocomplete
selected_diseases = st.multiselect("Select Disease Names", disease_names)

if selected_diseases:
    st.write("You selected:", selected_diseases)
