import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime

def extract_job_title(soup):
    return [title.text for title in soup.find_all('span', {'title': True})]

def extract_company_name(soup):
    return [company.text for company in soup.find_all('span', {'data-testid': 'company-name'})]

def extract_job_location(soup):
    return [loc.text for loc in soup.find_all('div', {'data-testid': 'text-location'})]

def extract_salaries(soup):
    return [sal.text if sal.text else "Not specified" for sal in soup.find_all('div', class_='metadata salary-snippet-container')]

def extract_job_links(soup):
    return [a['href'] for a in soup.find_all('a', {'class': 'jcs-JobTitle'}, href=True)]

def extract_job_type(soup):
    job_type_element = soup.find('div', class_='css-1p3gyjy e1xnxm2i0')
    return job_type_element.text if job_type_element else "Not specified"

def scrape_indeed_jobs(job_name, location, num_days, output_file):
    driver = webdriver.Chrome()
    base_url = f'https://in.indeed.com/jobs?q={job_name.replace(" ", "+")}&l={location.replace(" ", "+")}&fromage={num_days}&start='
    data_list = []

    try:
        start = 0
        while True:
            url = f'{base_url}{start}'
            print(f"Scraping page {url}")
            driver.get(url)
            time.sleep(1)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            job_titles = extract_job_title(soup)
            company_names = extract_company_name(soup)
            job_locations = extract_job_location(soup)
            salaries = extract_salaries(soup)
            job_links = extract_job_links(soup)
            job_types = [extract_job_type(soup) for _ in range(len(job_titles))]

            for i in range(len(job_titles)):
                data = {
                    "index": start + i,
                    "Job Title": job_titles[i] if i < len(job_titles) else None,
                    "Company Name": company_names[i] if i < len(company_names) else None,
                    "Job Location": job_locations[i] if i < len(job_locations) else None,
                    "Salary": salaries[i] if i < len(salaries) else "Not specified",
                    "Job Type": job_types[i] if i < len(job_types) else "Not specified",
                    "Job URL": f'https://in.indeed.com{job_links[i]}' if i < len(job_links) else None,
                    "Scraped Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                data_list.append(data)

            # Check if the "Next Page" button is present
            next_page_button = soup.find('a', {'data-testid': 'pagination-page-next'})
            if not next_page_button:
                print("No more pages. Exiting loop.")
                break

            # Increment by 10 for the next iteration
            start += 10

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    df = pd.DataFrame(data_list)
    print(df)

    output_file_path = f'indeed_jobs_{job_name.lower().replace(" ", "_")}_{location.lower().replace(" ", "_")}.csv'
    df.to_csv(output_file_path)
    print(f'Data saved to {output_file_path}')

# Example usage:
scrape_indeed_jobs(job_name='python', location='Kochi, Kerala', num_days=14, output_file='indeed_jobs')
