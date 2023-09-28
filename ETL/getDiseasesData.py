import requests

def download_file(url, save_path):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

        # Open a file for writing in binary mode and save the content
        with open(save_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded {url} to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")

def download_files(urls, folder_path):
    for url in urls:
        # Extract the filename from the URL
        filename = url.split("/")[-1]
        save_path = folder_path + "/" + filename

        # Call the download_file function with the URL and save path
        download_file(url, save_path)

if __name__ == "__main__":
    # List of URLs to download
    urls_to_download = [
        #"https://download.jensenlab.org/human_disease_textmining_full.tsv",
        "https://download.jensenlab.org/human_disease_knowledge_full.tsv",
        "https://download.jensenlab.org/human_disease_experiments_full.tsv",
    ]

    # Specify the folder where you want to save the downloaded files
    download_folder = "downloaded_files"

    # Create the download folder if it doesn't exist
    import os
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Call the download_files function with the list of URLs and download folder
    download_files(urls_to_download, download_folder)
