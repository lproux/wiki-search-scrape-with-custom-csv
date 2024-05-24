# %% [markdown]
# ### import libraries ###

# %%
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook
from urllib.parse import quote, urljoin, urlparse
import lxml
from PIL import Image
from io import BytesIO
import wget
import socket
import requests.exceptions
import itertools
import warnings
# Disable all warnings
warnings.filterwarnings("ignore")

df_animals = pd.read_csv("data/all_animal_list.csv")
df_animals.head()


# %% [markdown]
# ### Cycle between Headers ##

# %%
headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"},
]

# Create an iterator that cycles through the headers list
headers_cycle = itertools.cycle(headers_list)

# %% [markdown]
# ### Image Function ###

# %%
# Function to download images from a given page  
def download_images(page_soup, animal_dir, animal):  
    images = page_soup.find_all('a', href=True)  
    for img in images:  
        href = img['href']  
        if href.endswith('.jpg') or href.endswith('.png'):  
            img_url = urljoin("https://en.wikipedia.org", href)  
            img_response = make_request(img_url, next(headers_cycle))  
            if img_response:  
                img_extension = os.path.splitext(href)[1]  
                save_path = os.path.join(animal_dir, f"{animal}{img_extension}")  
                if 'Content-Length' in img_response.headers and int(img_response.headers['Content-Length']) <= 2 * 1024 * 1024:  
                    with open(save_path, 'wb') as f:  
                        f.write(img_response.content)  
                    print(f"Image saved: {save_path}")  
                else:  
                    print(f"Image too large, skipped: {href}")  

# %% [markdown]
# ### Create unique file_name ###

# %%
base_dir = "scrape/"

def create_unique_filename(base_dir, filename, extension):
    counter = 1
    unique_filename = os.path.join(base_dir, f"{filename}{extension}")
    while os.path.exists(unique_filename):
        unique_filename = os.path.join(base_dir, f"{filename}_{counter}{extension}")
        counter += 1
    return unique_filename

def save_to_excel(directory, filename, data):
    wb = Workbook()
    ws = wb.active
    ws.append(['URL', 'Title', 'Article'])
    ws.append(data)
    wb.save(create_unique_filename(directory, filename, '.xlsx'))

search_url = "https://en.wikipedia.org/w/index.php?search="

# %% [markdown]
# ### Loop over search results to extract the page one by one ###

# %%
timeout=30
# Loop through each animal name in the dataframe column 'CommonName'  
for animal in df_animals['CommonName']:    ## <-------- CHANGE THIS TO YOUR COLUMN NAME
    # Convert the animal name to a string to ensure compatibility with web requests  
    animal = str(animal)

    # Create a directory for the current animal in the base directory
    animal_dir = os.path.join(base_dir, animal)
    
    if os.path.exists(animal_dir):
        print(f"This directory exist:{animal_dir}, proceeding to image scraping.")
    else:
        # If the directory already exists, skip to the next animal
        if os.path.exists(animal_dir):
            print(f"This directory exist:{animal_dir}, skipping.")
            continue  
        
        # Create the search URL by appending the quoted (URL-safe) animal name to the base Wikipedia search URL  
        animal_search_url = f"{search_url}{quote(animal)}"  

        # Perform an HTTP GET request to the first search result page  
        for headers in headers_list:
            try:
                response = requests.get(animal_search_url, headers=headers, timeout=timeout)
                # If the request is successful, print a success message and set the flag
                if response.status_code == 200:
                    print(f"Successfully retrieved page for {animal} with headers {headers}.")
                    successful_retrieval = True
                    break  # Exit the loop as we have a successful retrieval
                else:
                    print(f"Failed to retrieve page for {animal} with headers {headers}. Status code: {response.status_code}")
            except (requests.exceptions.RequestException, socket.gaierror) as e:
                print(f"Failed to retrieve page for {animal} with headers {headers}. Error: {e}")

        # Check if a successful retrieval was made
        if not successful_retrieval:
            print(f"Failed to retrieve page for {animal} with all headers. Skipping to next animal.")
            continue

        # If the response contains the "no results" text, skip to the next animal
        if "There were no results matching the query in this site." in response.text:
            print(f"No results found for {animal}, skipping.")
            continue  

        # Parse the HTML content of the response using BeautifulSoup  
        soup = BeautifulSoup(response.content, 'html.parser')  

        # Check if there's a search result by looking for a div with the class 'mw-search-result-heading'  
        # If not found, skip to the next iteration of the loop  
        if not soup.find('div', class_='mw-search-result-heading'):    
            continue  

        # Extract the first search result link  
        first_result_link = soup.find('div', class_='mw-search-result-heading').find('a')['href']  

        # Construct the full URL of the first search result page  
        page_url = f"https://en.wikipedia.org{first_result_link}"  

        # Perform an HTTP GET request to the first search result page  
        page_response = requests.get(page_url)  

        # If the response status code is not 200 (OK), skip to the next iteration of the loop  
        if page_response.status_code != 200:    
            continue  

        # Initialize main_content as None
        main_content = None

        # Parse the HTML content of the page response  
        page_soup = BeautifulSoup(page_response.content, 'html.parser')  

        # Find the main content section of the page  
        main_content = page_soup.find('main', {'id': 'content'})  
        
        # Create a directory for the current animal in the base directory  
        animal_dir = os.path.join(base_dir, animal)        
        os.makedirs(animal_dir, exist_ok=True)  
        
        # Extract the URL of the page  
        url = page_response.url  
        
        # Extract the title of the page  
        title = main_content.find('h1', class_='firstHeading').text  
        
        # Join all paragraph texts in the main content to form the article text  
        article = ' '.join([p.text for p in main_content.find_all('p')])  
        
        # Save the URL, title, and article text to an Excel file in the animal's directory  
        save_to_excel(animal_dir, animal, [url, title, article])  
        
        tables = main_content.find_all('table', class_='infobox biota')  
        
        # Skip to the next animal if no tables are found  
        if not tables:  
            print(f"No tables found for {animal}, skipping.")  
        
        # Loop through each found table  
        for i, table in enumerate(tables):  
            # Parse the HTML table to a dataframe  
            df_table = pd.read_html(str(table))[0]  
            # Save the dataframe to an Excel file in the animal's directory  
            df_table.to_excel(create_unique_filename(animal_dir, f"{animal}_bio{i+1}", '.xlsx'))  


    animal_search_url = f"{search_url}{quote(animal)}"  

    # Perform an HTTP GET request to the first search result page  
    for headers in headers_list:
        try:
            response = requests.get(animal_search_url, headers=headers, timeout=timeout)
            # If the request is successful, print a success message and set the flag
            if response.status_code == 200:
                print(f"Successfully retrieved page for {animal} with headers {headers}.")
                successful_retrieval = True
                break  # Exit the loop as we have a successful retrieval
            else:
                print(f"Failed to retrieve page for {animal} with headers {headers}. Status code: {response.status_code}")
        except (requests.exceptions.RequestException, socket.gaierror) as e:
            print(f"Failed to retrieve page for {animal} with headers {headers}. Error: {e}")

    # Check if a successful retrieval was made
    if not successful_retrieval:
        print(f"Failed to retrieve page for {animal} with all headers. Skipping to next animal.")
        continue

    # If the response contains the "no results" text, skip to the next animal
    if "There were no results matching the query in this site." in response.text:
        print(f"No results found for {animal}, skipping.")
        continue  
        
    # Find all links in the main content that end with '.jpg' or '.png'  
    soup = BeautifulSoup(response.content, 'html.parser')  

    # Check if there's a search result by looking for a div with the class 'mw-search-result-heading'  
    # If not found, skip to the next iteration of the loop  
    if not soup.find('div', class_='mw-search-result-heading'):    
        continue  

    # Extract the first search result link  
    first_result_link = soup.find('div', class_='mw-search-result-heading').find('a')['href']  

    # Construct the full URL of the first search result page  
    page_url = f"https://en.wikipedia.org{first_result_link}"  

    # Perform an HTTP GET request to the first search result page  
    page_response = requests.get(page_url)  

    # If the response status code is not 200 (OK), skip to the next iteration of the loop  
    if page_response.status_code != 200:    
        continue  
    
    # Initialize main_content as None
    main_content = None

    # Parse the HTML content of the page response  
    page_soup = BeautifulSoup(page_response.content, 'html.parser')  

    # Find the main content section of the page  
    main_content = page_soup.find('main', {'id': 'content'})  
    if main_content is not None:
    # Your existing code that uses main_content
        images = main_content.find_all('a', href=True)  
        for img in images:  
            href = img['href']  
            if href.endswith('.jpg') or href.endswith('.png'):  
                # Construct the full image URL  
                img_url = urljoin("https://en.wikipedia.org", href)  
                img_response = requests.get(img_url)  
                # Extract the image extension
                _, img_extension = os.path.splitext(href)
                
                # If the image page response is not 200 (OK), skip to the next image  
                if img_response.status_code != 200:  
                    continue  
                
                # Parse the HTML content of the image page  
                img_soup = BeautifulSoup(img_response.content, 'html.parser')  
                img_link_div = img_soup.find('div', class_='fullImageLink')  
                
                # If the div containing the full image link is not found, skip to the next image  
                if img_link_div is None:  
                    continue  
                
                # Construct the full image link  
                img_link = urljoin("https://en.wikipedia.org", img_link_div.find('a')['href'])  
                try:
                    img_response = requests.get(img_url, timeout=timeout)
                except (requests.exceptions.RequestException, socket.gaierror) as e:
                    print(f"Failed to retrieve image for {animal}. Error: {e}")
                    continue            
                try:
                    img_response = requests.get(img_link, stream=True, timeout=timeout)
                except (requests.exceptions.RequestException, socket.gaierror) as e:
                    print(f"Failed to download image for {animal}. Error: {e}")
                    print(f"Exception type: {type(e)}")
                    continue
                
                # If the image is larger than 2MB, skip downloading it  
                if 'Content-Length' in img_response.headers and int(img_response.headers['Content-Length']) > 2 * 1024 * 1024:  ## feel free to change the size or just remove this condition
                    print(f"Image for {animal} is over 2MB, skipping.")  
                    continue  
                
                # Attempt to download the image to the animal's directory  
                try:  
                    wget.download(img_link, f'{animal_dir}/{animal}{img_extension}')  
                except (Exception, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, socket.gaierror) as e:  
                    # If downloading fails, print an error message  
                    print(f"Failed to download image for {animal}. Error: {e}")
                    print(f"Exception type: {type(e)}")
                    continue
    else:    
        print(f"Main content not found for {animal}, skipping.")
        continue        
        
# Print a completion message after all animals have been processed  
print("Scraping completed.")  


# %% [markdown]
# ### Remove Duplicated File ###

# %%
import os
import hashlib

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def remove_duplicates(directory):
    file_dict = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        print(f"Scanning directory: {dirpath}")
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_info = os.stat(file_path)
            file_hash = get_file_hash(file_path)
            file_size = file_info.st_size
            file_record = (file_size, file_hash)
            duplicate = file_dict.get(file_record, None)
            if duplicate:
                os.remove(file_path)
                print(f"Removed duplicate file: {file_path}")
            else:
                file_dict[file_record] = file_path

remove_duplicates("scrape")

# %%



