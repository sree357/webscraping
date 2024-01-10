from bs4 import BeautifulSoup
import requests

url = 'https://infopark.in/companies/company'

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

    # Print or use the job opening links as needed
    for job_opening_link in job_opening_links:
        print(job_opening_link)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
