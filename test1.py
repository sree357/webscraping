import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

# Set up Chrome options with a random user agent and additional headers
chrome_options = Options()
chrome_options.add_argument(f'user-agent={UserAgent().random}')
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Added to avoid detection

# Set up the Chrome service with executable path
chrome_service = Service(executable_path=ChromeDriverManager().install())

# Initialize the webdriver with Chrome options and service
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

base_url = 'https://in.indeed.com/jobs?q=data+scientist&l=kerala&rbl=Kerala&jlid=b2ef2f03f7a1c2f3&fromage=14&vjk=66d6ede3b70b98e5'

data_list = []

try:
    for start in range(0, 150, 10):
        print(start)  # Assuming 9658 results, with 15 results per page
        url = f'{base_url}{start}'

        driver.get(url)

        # Wait for the page to load
        time.sleep(1)  # Add a delay

        # Simulate scrolling to load more job listings
        for _ in range(5):  # Scroll 5 times (you may adjust this based on your needs)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Add a delay to allow content to load

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract job details
        job_titles = [title.text for title in soup.find_all('span', {'title': True})]
        company_names = [company.text for company in soup.find_all('span', {'data-testid': 'company-name'})]
        job_locations = [loc.text for loc in soup.find_all('div', {'data-testid': 'text-location'})]
        salaries = [sal.text if sal.text else "Not specified" for sal in
                    soup.find_all('div', class_='metadata salary-snippet-container')]

        # Append the data to the list
        for i in range(len(job_titles)):
            data = {
                "index": start + i,
                "Job Title": job_titles[i] if i < len(job_titles) else None,
                "Company Name": company_names[i] if i < len(company_names) else None,
                "Job Location": job_locations[i] if i < len(job_locations) else None,
                "Salary": salaries[i] if i < len(salaries) else None
            }
            data_list.append(data)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

# Convert data list to DataFrame
df = pd.DataFrame(data_list)
print(df)
df.to_csv(r'C:\Users\Sree_Luminar\PycharmProjects\Job_scraping\jobs2_output.csv')
