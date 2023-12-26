import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome()

base_url = 'https://in.indeed.com/jobs?q=python+developer&l=Kochi&start='

data_list = []

try:
    for start in range(0, 50, 10):
        print(start)  # Assuming 9658 results, with 15 results per page
        url = f'{base_url}{start}'

        driver.get(url)

        # Wait for the page to load
        time.sleep(1)

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

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
df.to_csv(r'C:\Users\Sree_Luminar\PycharmProjects\Job_scraping\indeed.csv')