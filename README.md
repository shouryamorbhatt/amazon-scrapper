# Amazon Web Scraping with Selenium and Tesseract OCR

This Python script allows you to scrape product information from Amazon product pages using Selenium WebDriver and solve CAPTCHAs using Tesseract OCR. The scraped data is then saved to a JSON file or a PostgreSQL database.

## Prerequisites

Before running the script, make sure you have the following installed:

- [Python](https://www.python.org/) (version 3.x)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Chrome WebDriver](https://sites.google.com/chromium.org/driver/) (ensure it matches your Chrome browser version)
- [PostgreSQL](https://www.postgresql.org/) (if you intend to use the database storage option)

You'll also need to install the required Python packages listed in the `requirements.txt` file.

## Installation

1. Clone this repository to your local machine:


git clone https://github.com/yourusername/Amazon-Web-Scraping.git
# Navigate to the project directory:

```bash
cd Amazon-Web-Scraping
```
# Install the required Python packages:
```bash
pip install -r requirements.txt
```

# Configuration
1. WebDriver and Tesseract Configuration
Before running the script, configure the path to your Tesseract OCR executable and Chrome WebDriver in the script:

```python
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
webdriver_path = 'chromedriver.exe'
```

# Make sure the paths point to the correct locations on your system.

2. Database Configuration (Optional)
If you plan to save scraped data to a PostgreSQL database, modify the database connection details in the script:

```python
db_config = {
    'host': 'localhost',
    'database': 'yourdatabase',
    'user': 'youruser',
    'password': 'yourpassword'
}
```
Replace 'yourdatabase', 'youruser', and 'yourpassword' with your actual PostgreSQL database information.

Usage
1. Scraping to JSON
Create a CSV file named data.csv with the following format:

```csv
Asin,country
B07XYZABC1,com
B08UVWXYZ2,ca
```
Replace the sample ASIN and country values with the products you want to scrape.

Run the script to scrape and save data to a JSON file:

#Ensure you have PostgreSQL installed and a database created.

```bash
python amazon_scraper.py
```
The scraped product data will be saved to a JSON file named product_info.json.
The scraped product data will also be stored in the specified PostgreSQL database.

# License
This project is licensed under the MIT License - see the LICENSE file for details.
