import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import unquote

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

# URL of the Technopark A-Z company listing page
base_url = 'https://www.technopark.org/company-a-z-listing'

# List to store extracted data
data_list = []

def extract_company_name(soup):
    """Extracts company name from the soup."""
    company_name_element = soup.find('div', {'style': 'background-image:url(\'/resources/images/company/ico-company.png\');'})
    company_name = company_name_element.find_next('li').text.strip() if company_name_element else None
    # Remove 'company name' prefix and leading spaces
    company_name = company_name.replace('company name', '').strip() if company_name else None
    return company_name
def extract_company_email(soup):
    """Extracts company name from the soup."""
    company_email_element = soup.find('div', {'style': 'background-image:url(\'/resources/images/company/ico-phone.png\');'})
    company_email = company_email_element.find_next('li').text.strip() if company_email_element else None
    # Remove ' email' prefix and leading spaces
    company_email = company_email.replace('email ', '').strip() if company_name else None
    return company_email
def extract_company_website(soup):
    """Extracts company name from the soup."""
    company_website_element = soup.find('div', {'style': 'background-image:url(\'/resources/images/company/ico-mail.png\');'})
    company_website = company_website_element.find_next('li').text.strip() if company_website_element else None
    # Remove 'company website' prefix and leading spaces
    company_website = company_website.replace('website ', '').strip() if company_name else None
    return company_website

try:
    # Open the A-Z listing page
    driver.get(base_url)

    # Scroll to the bottom of the page to load more companies
    actions = ActionChains(driver)
    for _ in range(2):  # Adjust the range as needed
        actions.send_keys(Keys.END).perform()
        time.sleep(2)  # Adjust the sleep time as needed

    # Get the HTML content after scrolling
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract company links
    company_links = [a['href'] for a in soup.select('.cmpny-detail a[href^="/company/"]')]

    # Visit each company page and scrape details
    for company_link in company_links:
        # Construct the full company URL
        company_url = f'https://www.technopark.org{company_link}'
        # Open the company page in a new window
        driver.execute_script("window.open('', '_blank');")
        # Switch to the new window
        driver.switch_to.window(driver.window_handles[1])
        driver.get(company_url)
        time.sleep(2)  # Adjust the sleep time as needed

        # Get the HTML content of the company page
        company_page_source = driver.page_source
        company_soup = BeautifulSoup(company_page_source, 'html.parser')

        # Extract company name using the renamed method
        company_name = extract_company_name(company_soup)
        company_email = extract_company_email(company_soup)
        company_website = extract_company_website(company_soup)

        # Append the data to the list
        data = {
            "Company Name": company_name,
            "Company email": company_email,
            "Company website": company_website,
            "Tab URL": driver.current_url
        }
        data_list.append(data)

        # Close the current tab (window) to switch back to the original window
        driver.close()
        # Switch back to the original window
        driver.switch_to.window(driver.window_handles[0])

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()

# Convert data list to DataFrame
df = pd.DataFrame(data_list)
print(df)
# Save data to a CSV file
df.to_csv('technopark_company_details.csv', index=False)
