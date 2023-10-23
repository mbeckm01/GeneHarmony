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


***


# Setting up PostgreSQL on Ubuntu Container (Proxmox)

Setting up PostgreSQL on an Ubuntu container running on Proxmox involves several steps. Here's a step-by-step guide to help you get PostgreSQL up and running:

## Step 1: Create an Ubuntu Container

- Use the Proxmox web interface or command-line tools to create an Ubuntu container (CT). Ensure it has network connectivity.

## Step 2: Access the Container

- You can access the container using SSH or Proxmox's built-in console feature.

## Step 3: Update the System

- Update the package list and upgrade installed packages to ensure you have the latest software:

```bash
sudo apt update
sudo apt upgrade
```

## Step 4: Install PostgreSQL

- Install PostgreSQL and its dependencies:

```bash
sudo apt install postgresql postgresql-contrib
```

## Step 5: Start and Enable PostgreSQL

- Start the PostgreSQL service and enable it to start on boot:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 6: Secure PostgreSQL (Optional but Recommended)

- PostgreSQL is configured to be secure by default, but you should set a password for the PostgreSQL superuser `postgres`:

```bash
sudo -u postgres psql
```

- Within the PostgreSQL prompt, set a password for the `postgres` user:

```sql
\password postgres
```

- Follow the prompts to set the password.

- Exit the PostgreSQL prompt:

```sql
\q
```

## Step 7: Configure PostgreSQL Access

- By default, PostgreSQL allows local connections, but you might want to configure it to allow remote connections if necessary. Edit the PostgreSQL configuration file:

```bash
sudo nano /etc/postgresql/<version>/main/pg_hba.conf
```

- Modify the `pg_hba.conf` file to specify the IP addresses or ranges that are allowed to connect to the database. For example, to allow connections from any IP address, add the following line:

```
host    all             all             0.0.0.0/0               md5
```

- Save the file and exit the text editor.

- Modify `sudo nano /etc/postgresql/16/main/postgresql.conf` to uncomment the line `listen_addresses` and set it equal to `listen_addresses = '*'`.

## Step 8: Restart PostgreSQL

- Restart PostgreSQL to apply the changes to the `pg_hba.conf` file:

```bash
sudo systemctl restart postgresql
```


***



# Use Mount Point in Proxmox CT to Store Postgres DBs on HDD

## Transfer PostgreSQL Data Directory

#### PostgreSQL stores its data in a directory typically located at /var/lib/postgresql/<version>/main. To move this data to the larger hard disk, you'll need to stop PostgreSQL first:
```bash
sudo systemctl stop postgresql
```

#### Copy the existing PostgreSQL data to the new mount point:
```bash
sudo rsync -av /var/lib/postgresql/<version>/main/ /mnt/postgres_data/
```

#### Next, you'll need to update PostgreSQL's configuration to point to the new data directory. Edit the PostgreSQL configuration file:
```bash
sudo nano /etc/postgresql/<version>/main/postgresql.conf
```

#### Find and modify the data_directory setting to point to your new data directory:
```conf
data_directory = '/mnt/postgres_data/main'
```

#### Save the file and exit the text editor.


#### Adjust Permissions
Ensure that the PostgreSQL system user and group have appropriate permissions to access the new data directory:
```bash
sudo chown -R postgres:postgres /mnt/postgres_data/main
```

Update SELinux or AppArmor (if applicable):

If you're using SELinux or AppArmor, you may need to update their policies to allow PostgreSQL to access the new data directory.
Restart PostgreSQL and Verify:


#### Restart the PostgreSQL service:
```bash
sudo systemctl start postgresql
```

Verify that PostgreSQL is running without any issues and that your data is accessible from the new location.

#### You can check the PostgreSQL logs for any errors:
```bash
sudo journalctl -u postgresql
```