# Gene-Disease-DB

### Methods (Abstract Oct '23)
Data infrastructure was established on a Postgres database using Plotly v5.17.0 and Streamlit v1.27.2 Python v3.8 packages. The Diseases v2.0 and GTEx v8 databases were utilized, providing searchable disease names, affiliated gene symbols, confidence scores (ranging from 0 to 5 with 5 being the most confident), and gene expression across 54 tissue types. The microbe-set enrichment analysis database provided context about bacteria possibly affecting expression of genes.

## Explaining session state in Streamlit
Streamlit's session state allows retaining values across reruns of the app, effectively allowing us to keep track of user interactions, selections, and any other relevant data.

We are checking if the 'num_groups' key is not already present in the session state.
This check is important because, on the first run of the app, this key won't exist. However, on subsequent runs, we don't want to overwrite the existing value. Also note, refreshing the webpage will reset the session state.
<br>
`if 'num_groups' not in st.session_state:`
    
'num_groups' key will store the number of disease groups the user wants to search for.
Initially, we set it to 1, meaning by default, the user can search for genes associated with one group of diseases.
<br>
`st.session_state['num_groups'] = 1`
    
'selections' key is a dictionary that will keep track of the user's disease name selections for each disease group. For instance, if the user selects "Cancer" and "Flu" for Group 1, and "Diabetes" for Group 2, this dictionary will look like: 
<br> **{'group_0': ['Cancer', 'Flu'], 'group_1': ['Diabetes']}**
<br> 
`st.session_state['selections'] = {}`

'search_results' key will store the results after a search is performed. Initially, we set it to None because no search has been performed yet.
<br>
`st.session_state['search_results'] = None`
    
'temp_selections' is similar to 'selections', but it temporarily holds the selections made by the user. This allows us to track the user's current choices without necessarily committing them to the main 'selections' dictionary until the user decides to perform a search. This provides flexibility in allowing the user to make, change, or discard selections before actually processing them.
<br>
`st.session_state['temp_selections'] = {}`
