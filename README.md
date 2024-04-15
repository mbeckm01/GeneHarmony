# Gene-Disease-DB Setup Guide

## Step 1: Install PostgreSQL

To set up a PostgreSQL database for the Gene-Disease-DB:

1. **Download PostgreSQL**:
   - Visit the [PostgreSQL official download page](https://www.postgresql.org/download/) to download the installer.

2. **Install PostgreSQL**:
   - Run the installer.
     - Remember to note down the password for the 'postgres' user.

3. **Verify Installation**:
   - Open a terminal or command prompt.
   - Connect to the PostgreSQL database using: `psql -U postgres`
   - Enter your password when prompted.

## Step 2: Download the Database Dump

Download the database dump from OneDrive:

- [Download database dump] (https://1drv.ms/u/s!Al0sfIh-a3z9gYAdvIxLlAjAMPyV8w?e=WLzxGE)
- Save the file to a known location on your computer for use in the next step.

## Step 3: Restore the Database

Restore the database from the downloaded dump file:

```bash
psql -U postgres -f <path-to-downloaded-dump-file> postgres
```
Replace <path-to-downloaded-dump-file> with the actual path where you saved the downloaded SQL dump file.

## Step 4: Install Miniconda (Optional)

If you prefer using Miniconda for managing Python environments:

1. **Download Miniconda**:
   - Go to the [Miniconda download page](https://docs.conda.io/en/latest/miniconda.html) and select the installer for your OS.

2. **Install Miniconda**:
   - Execute the downloaded installer and follow the on-screen instructions.

3. **Create a Conda Environment**:
   - Open a new terminal or command prompt.
   - Create a new environment: `conda create --name geneHarmony`
   - Activate the environment: `conda activate geneHarmony`

## Step 5: Install Required Python Packages

Install Streamlit and other required packages:

```bash
pip install streamlit psycopg2-binary plotly pandas
```

## Step 6: Run the Streamlit App

Navigate to the directory containing the Streamlit app and run:

```bash
streamlit run GeneHarmony.py
```
