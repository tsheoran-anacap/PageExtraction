import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs

# Function to extract URLs from iframe tags in a given page
def extract_iframe_urls(page_url):
    response = requests.get(page_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        iframe_tags = soup.find_all('iframe')
        
        iframe_urls = []
        for iframe_tag in iframe_tags:
            src = iframe_tag.get('src')
            if src:
                iframe_urls.append(urljoin(page_url, src))

        return iframe_urls
    else:
        print(f"Failed to retrieve the page: {page_url}. Status code: {response.status_code}")
        return []

# Function to filter out URLs with .pdf extension
def filter_pdf_urls(urls):
    pdf_urls = [url for url in urls if url.lower().endswith('.pdf')]
    return pdf_urls

# Function to extract the "file" query parameter from a URL
def extract_file_param(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'file' in query_params:
        return query_params['file'][0]
    return None

# Function to download and save a PDF from a given URL
def download_pdf(pdf_url, save_folder):
    filename = extract_file_param(pdf_url)
    response = requests.get(filename)

    if response.status_code == 200:
        # Extract the filename from the "file" query parameter
        if pdf_url:
            # Sanitize the filename (remove any path traversal)
            filename = os.path.basename(filename)
            filename = os.path.join(save_folder, filename)
            
            # Save the PDF to the specified folder
            with open(filename, 'wb') as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to extract 'file' query parameter from URL: {pdf_url}")
    else:
        print(f"Failed to download PDF: {pdf_url}. Status code: {response.status_code}")

# URL of the web page you want to start from
start_url = 'https://sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0' # Replace with the URL of your choice
save_folder = 'pdfs'  # Replace with the path to your desired save folder

# Create the save folder if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Send an HTTP GET request to the start URL
start_response = requests.get(start_url)

# Check if the request to the start URL was successful (status code 200)
if start_response.status_code == 200:
    # Parse the HTML content of the start page using BeautifulSoup
    start_soup = BeautifulSoup(start_response.text, 'html.parser')
    
    # Find all valid URLs within <a> tags on the start page
    valid_urls = []
    a_tags = start_soup.find_all('a')
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href and urlparse(href).scheme and ("javascript" not in href):
            valid_urls.append(href)

    # Loop over the valid URLs and extract iframe URLs from each page
    for valid_url in valid_urls:
        iframe_urls = extract_iframe_urls(valid_url)
        
        # Filter out URLs with .pdf extension
        pdf_urls = filter_pdf_urls(iframe_urls)
        
        # Download and save the PDFs to the folder
        for pdf_url in pdf_urls:
            download_pdf(pdf_url, save_folder)
else:
    print(f"Failed to retrieve the start page: {start_url}. Status code: {start_response.status_code}")
