import csv
from bs4 import BeautifulSoup
import requests

def scrape_job_links(url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        job_opening_links = []

        company_containers = soup.find_all('div', class_='my-list')

        for container in company_containers:
            company_name = container.find('h3', class_='company-name-hd').text.strip()
            job_opening_link = container.find('a', class_='btn-info')['href']

            job_opening_links.append({
                'Company Name': company_name,
                'Job Opening Link': job_opening_link
            })

        return job_opening_links

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def scrape_company_details(job_links):
    company_details_list = []

    for job_link in job_links:
        try:
            response = requests.get(job_link['Job Opening Link'], verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            company_name = soup.find('h5').text.strip()

            address_details = soup.find('div', class_='address_details')
            if address_details and address_details.find('p', recursive=False):
                address_lines = [line.strip() for line in address_details.find('p', recursive=False).get_text("\n", strip=True).split('\n') if line.strip()]
            else:
                address_lines = []

            company_email = soup.find('div', class_='company_email').get_text(strip=True).replace('Email:', '') if soup.find('div', class_='company_email') else ''
            company_phone = soup.find('div', class_='company_phone').get_text(strip=True).replace('Ph:', '') if soup.find('div', class_='company_phone') else ''

            company_details_list.append({
                'Company Name': company_name,
                'Company Email': company_email,
                'Company Phone': company_phone,
                'Address Lines': '\n'.join(address_lines)
            })

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while scraping details from {job_link['Job Opening Link']}: {e}")

    return company_details_list

def save_to_csv(company_details, csv_filename='company_details.csv'):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Company Name', 'Company Email', 'Company Phone', 'Address Lines']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for details in company_details:
            writer.writerow(details)

# Example usage
url = 'https://infopark.in/companies/company'
job_links = scrape_job_links(url)

if job_links:
    company_details = scrape_company_details(job_links)
    save_to_csv(company_details)

print("Company details saved to company_details.csv")
