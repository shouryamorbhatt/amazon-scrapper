import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException
import pytesseract
from PIL import Image
import io
import time
import requests
import json
import psycopg2

# Set the path to the Tesseract OCR executable (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
tesseract_path = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Set the path to the Chrome WebDriver executable
webdriver_path = 'chromedriver.exe'

# Initialize Chrome WebDriver with headless options
chrome_options = ChromeOptions()
chrome_options.use_chromium = True
chrome_options.headless = True

# Create a new Chrome WebDriver instance
driver = webdriver.Chrome(service=ChromeService(executable_path=webdriver_path), options=chrome_options)

# Function to solve CAPTCHA using Tesseract OCR
def solve_captcha(captcha_image_element):
    captcha_image_src = captcha_image_element.get_attribute("src")
    print(captcha_image_src)
    response = requests.get(captcha_image_src)
    print(response)
    if response.status_code == 200:
        # Download the CAPTCHA image and process it with Tesseract OCR
        content = response.content
        image_content = io.BytesIO(content)
        captcha_image = Image.open(image_content)
        print(captcha_image)
        time.sleep(2)
        captcha_text = pytesseract.image_to_string(captcha_image, config='--psm 6')  # Use appropriate config
        return captcha_text
    else:
        return None

def try_captcha(driver):
    captcha_image_element = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]")
    captcha_text = solve_captcha(captcha_image_element)
    print(captcha_text)
    if captcha_text:
        # Enter the CAPTCHA text into the input field (modify the XPath as needed)
        captcha_input = driver.find_element(By.XPATH, "//input[@id='captchacharacters']")
        captcha_input.send_keys(captcha_text)

        # Submit the CAPTCHA form (modify the XPath as needed)
        captcha_form = driver.find_element(By.XPATH, "//form[@action='/errors/validateCaptcha']")
        captcha_form.submit()
        time.sleep(4)
        try_captcha(driver)

# Database connection parameters
db_params = {
    'dbname': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port'
}

# Connect to the PostgreSQL database
conn = psycopg2.connect(**db_params)

# Create a cursor
cursor = conn.cursor()

# Create a table to store the JSON data if it doesn't already exist
create_table_query = """
CREATE TABLE IF NOT EXISTS product_info (
    id SERIAL PRIMARY KEY,
    data JSON
);
"""
cursor.execute(create_table_query)

# Commit the table creation query
conn.commit()

urls = []
product_info_list = []

# Specify the JSON file path where you want to save the data
json_file_path = 'product_info.json'
# Timer start current time
with open('data.csv', 'r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)

    # Initialize variables to store the column indices
    asin_column_index = None
    country_column_index = None

    # Read the header row to find the column indices
    header = next(csvreader)
    for col_idx, col_name in enumerate(header):
        if col_name == "Asin":
            asin_column_index = col_idx
        elif col_name == "country":
            country_column_index = col_idx

    # Check if both columns were found
    if asin_column_index is not None and country_column_index is not None:
        # Loop through the rows
        for row in csvreader:
            asinCode = row[asin_column_index]
            countryCode = row[country_column_index]
            urls.append(f"https://www.amazon.{countryCode}/dp/{asinCode}")
    else:
        print("Columns 'Asin' and 'country' not found in the CSV file.")

# Function to extract product information
def extract_product_info(url):
    driver.get(url)

    # Check for a 404 error page by looking for the anchor tag with href="/dogsofamazon"
    try:
        title = driver.title
        if not "404" in title:
            driver.find_element(By.XPATH, "//a[@id='l' and @href='/dogsofamazon']")
            print(f"{url} not available (404 error)")
        elif "404" in title or "unavailable" in title:
            print(f"{url} not available (404 error)")
        return None
    except NoSuchElementException:
        pass

    # Solve CAPTCHA if present
    try:
        try_captcha(driver)
    except NoSuchElementException:
        time.sleep(2)
        pass

    try:
        product_title = driver.find_element(By.ID, "productTitle").text
        price = None
        try:
            product_price_list = driver.find_elements(By.XPATH, './/span[@class="a-offscreen"]')
            if product_price_list:
                price_text = product_price_list[0].get_attribute("innerHTML").strip()
                if price_text != "":
                    price = price_text
        except NoSuchElementException:
            price = driver.find_element(By.ID, "price").text
        product_image_url = driver.find_element(By.ID, "landingImage").get_attribute('src')
        product_details = driver.find_element(By.ID, "detailBulletsWrapper_feature_div").text
        return {
            'title': product_title,
            'image_url': product_image_url,
            'price': price,
            'details': product_details
        }
    except NoSuchElementException:
        print(f"Product information not found for {url}")
        return None

# Iterate through the URLs, extract product information, and write to the database
if len(urls) != 0:
    for url in urls:
        product_info = extract_product_info(url)
        if product_info:
            # Append JSON data to the list
            product_info_list.append(product_info)
            print(f"Working URL: {url}")
        # Add a delay between requests (e.g., 2 seconds)
        time.sleep(2)

# Convert the list of dictionaries to a JSON string
product_info_json = json.dumps(product_info_list, indent=4)

# Insert the JSON data into the database
insert_query = "INSERT INTO product_info (data) VALUES (%s);"
cursor.execute(insert_query, (product_info_json,))

# Adding the JSON file with the list of products scrapped
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(product_info_json)

# Commit the database transaction
conn.commit()

# Close the cursor and the database connection
cursor.close()
conn.close()

# Close the Chrome WebDriver
driver.quit()
