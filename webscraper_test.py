import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

# URL of the Technopark A-Z company listing page
base_url = 'https://www.cyberparkkerala.org/companies-at-park'

# List to store extracted data
data_list = []

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
    company_links = [a['href'] for a in soup.select('.flt_rigt a[href^="https://www.cyberparkkerala.org/listings/"]')][:5]

    # Visit each company page and scrape details
    for company_link in company_links:
        # Open the company page in a new window
        driver.execute_script("window.open('', '_blank');")
        # Switch to the new window
        driver.switch_to.window(driver.window_handles[1])
        driver.get(company_link)
        time.sleep(2)  # Adjust the sleep time as needed

        # Get the URL of the current tab (window)
        current_tab_url = driver.current_url

        # Get the HTML content of the company page
        company_page_source = driver.page_source
        company_soup = BeautifulSoup(company_page_source, 'html.parser')

        # Extract relevant company details
        company_name_element = company_soup.find('div', class_='company-name')

        # Extract company name if available
        company_name = company_name_element.text.strip() if company_name_element else None

        # Append the data to the list
        data = {
            "Company Name": company_name,
            "Tab URL": current_tab_url
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
df.to_csv('cyberpark_companies.csv', index=False)
