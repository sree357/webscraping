import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent  # Make sure to install this library

def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def click_show_more_button(driver):
    try:
        show_more_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-test="load-more"]')))
        show_more_button.click()
        return True
    except:
        return False

def get_job_links(soup):
    return [link['href'] for link in soup.find_all('a', {'class': 'JobCard_trackingLink__zUSOo'})]

def get_company_names(employer_info):
    return [info.find('span', {'class': 'EmployerProfile_employerName__Xemli'}).text if info.find('span', {'class': 'EmployerProfile_employerName__Xemli'}) else "Not specified" for info in employer_info]

def get_job_titles(soup):
    return [title.text for title in soup.find_all('a', {'class': 'JobCard_seoLink__WdqHZ'})]

def get_job_locations(soup):
    return [loc.text if loc.text else "Not specified" for loc in soup.find_all('div', {'class': 'JobCard_location__N_iYE'})]

def get_salaries(soup):
    return [salary.text.strip() if salary.text else "Not specified" for salary in soup.find_all('div', {'class': 'JobCard_salaryEstimate___m9kY'})]

def get_job_descriptions(soup):
    return [desc.text.strip() if desc.text else "Not specified" for desc in soup.find_all('div', {'class': 'JobCard_jobDescriptionSnippet__HUIod'})]

def scrape_job_data(base_url, job_location, job_name, date_posted):
    chrome_options = Options()
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)
    data_list = []

    try:
        full_url = f'{base_url}?fromAge={date_posted}'
        driver.get(full_url)

        while click_show_more_button(driver):
            scroll_down(driver)
            time.sleep(2)  # Adjust sleep time based on your needs

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        job_links = get_job_links(soup)
        employer_info = soup.find_all('div', {'class': 'EmployerProfile_employerInfo__GaPbq'})
        company_names = get_company_names(employer_info)
        job_titles = get_job_titles(soup)
        job_locations = get_job_locations(soup)
        salaries = get_salaries(soup)
        job_descriptions = get_job_descriptions(soup)

        # Append the data to the list
        for i in range(len(job_titles)):
            job_link = urljoin(full_url, job_links[i])
            data = {
                "index": i,
                "Job Title": job_titles[i] if i < len(job_titles) else None,
                "Company Name": company_names[i] if i < len(company_names) else None,
                "Job Location": job_locations[i] if i < len(job_locations) else None,
                "Salary": salaries[i] if i < len(salaries) else None,
                "Job Description": job_descriptions[i] if i < len(job_descriptions) else None,
                "Job Link": job_link if i < len(job_links) else None,
                "Job Location Filter": job_location,
                "Job Name Filter": job_name,
                "Date Posted Filter": date_posted,
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add current timestamp
            }
            data_list.append(data)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return data_list

def save_to_csv(data_list, csv_path):
    df = pd.DataFrame(data_list)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    base_url = 'https://www.glassdoor.co.in/Job/kochi-india-data-science-jobs-SRCH_IL.0,11_IC2887994_KO12,24.htm'
    job_location_filter = 'Kochi'  # Set your desired job location
    job_name_filter = 'Data Scientist'  # Set your desired job name
    date_posted_filter = '7'  # Set your desired date posted filter (in days)
    scraped_data = scrape_job_data(base_url, job_location_filter, job_name_filter, date_posted_filter)

    # Specify a different path where you have write access
    csv_path = r'C:\Users\Sree_Luminar\PycharmProjects\Job_scraping\glassdoor.csv'
    save_to_csv(scraped_data, csv_path)
