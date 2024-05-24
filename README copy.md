# wikipedia-scraper-from-csv
 
Initial data from  : https://datacatalog.worldbank.org/search?q=&start=1&sort=last_updated_date%20desc

TLDR; Code goes through a csv list, iterate over each line of the first column and search wikipedia, use the first page, download base article text, url, table and in a nested but removable loop, the images. 

### Web Scraping Documentation for Animal Data Extraction  
   
This Python script is designed to scrape detailed information about animals from Wikipedia. The primary functionalities include searching for animal names, extracting relevant text and image data, and organizing this information into structured Excel files. Each animal's data is stored in dedicated directories to keep the data organized and accessible.  
   
#### Libraries Used:  
- **os**: For interacting with the operating system to handle file and directory operations.  
- **requests**: To perform HTTP requests to retrieve web pages.  
- **pandas**: For handling data structures and operations for manipulating numerical tables and time series.  
- **BeautifulSoup (bs4)**: For parsing HTML and XML documents, crucial for web scraping to extract data from web pages.  
- **openpyxl**: To create and work with Excel files (.xlsx), allowing data storage in a widely used format.  
- **urllib.parse (quote, urljoin)**: For URL manipulation, ensuring that URLs are correctly formatted and combined.  
- **lxml**: As a parsing library used with BeautifulSoup to parse pages more efficiently.  
- **PIL (Image)**: To handle image files, which is part of the Python Imaging Library.  
- **io (BytesIO)**: To handle binary streams used in image processing.  
- **wget**: For downloading files from the web.  
- **socket**: To handle socket-level operations, useful for handling network errors.  
- **requests.exceptions**: To catch exceptions specifically raised by the requests library during HTTP requests.  
- **itertools**: For creating and using iterators to efficiently loop through data such as headers.  
- **warnings**: To suppress warnings that can clutter output.  
   
#### Workflow:  
   
1. **Disable Warnings**: Suppression of warnings to make the output cleaner.  
   
2. **Data Initialization**:  
   - **Animal List**: The script starts by reading a CSV file (`data/all_animal_list.csv`) that contains a list of animal names. This list is used to drive the searches on Wikipedia.  
   
3. **Directory and Filename Management**:  
   - **Unique Filenames**: A function (`create_unique_filename`) ensures that each saved file has a unique name by appending a counter to filenames if a file with the intended name already exists.  
   - **Excel Saving**: Another function (`save_to_excel`) manages the creation and saving of Excel files containing the scraped data.  
   
4. **Web Scraping**:  
   - **User Agent Cycling**: To avoid being blocked by Wikipedia due to multiple requests, the script cycles through different user agents. This is accomplished using a list of user agents and the `itertools.cycle` method.  
   - **Page Retrieval**: For each animal, the script constructs a search URL, sends requests to Wikipedia, and handles possible HTTP errors and exceptions.  
   - **Content Parsing**: If a valid page is found, the script uses BeautifulSoup to parse the HTML content. It specifically looks for main content areas, titles, and paragraphs to extract textual information.  
   - **Data Organization**: Each animal's data (URL, title, article text) is then saved into an Excel file within a directory named after the animal.  
   
5. **Image Scraping**:  
   - **Separate Process**: Images are scraped separately from text to allow easy modification or removal of this functionality. This is practical in scenarios where only textual data is needed.  
   - **Image Extraction**: The script checks for image links within the main content, verifies their formats (`.jpg` or `.png`), and downloads them if they meet size criteria. Images are saved in the same directory as the animal's textual data.  
   
6. **Duplicate File Handling**:  
   - After scraping, a function (`remove_duplicates`) scans the directories for duplicate files based on their content hash and removes them to optimize storage.  
   
#### Reasons for Separate Scraping of Images and Text:  
- **Flexibility**: Users might require only textual data or only images. Separating these functionalities makes the script versatile and adaptable to different needs.  
- **Performance**: Image downloading can significantly slow down the scraping process, especially for high-resolution images. Users can choose to skip image downloading for faster execution.  
- **Error Handling**: Image URLs might lead to broken links or content that isn't accessible. Isolating image scraping makes error handling more straightforward and prevents issues in one part from affecting the whole scraping process.  
   
#### Site Scraped:  
- **Wikipedia**: The script specifically targets Wikipedia for gathering comprehensive and reliable information about animals. Wikipedia's structured format and extensive content make it an ideal source for automated data extraction.  
   
This documentation provides a detailed overview of the script's functionality, its components, and the rationale behind its design choices. It is intended to help users understand, utilize, and potentially modify the script according to their needs.