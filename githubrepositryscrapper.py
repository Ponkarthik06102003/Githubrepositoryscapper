import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def extract_star_count(element):
    count = element.text.strip().replace('\n', '')
    if count.endswith('k'):
        count = float(count[:-1]) * 1000
    elif not count.isdigit():
        count = 0
    return int(count)

def get_forks_count(repo_link):
    driver = webdriver.Chrome()
    driver.get(repo_link)
    forks_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='repo-network-counter']")))
    forks_count = forks_element.text.strip() if forks_element else "0"
    driver.quit()

    if forks_count.endswith('k'):
        forks_count = float(forks_count[:-1]) * 1000
    elif not forks_count.isdigit():
        forks_count = 0
    else:
        forks_count = int(forks_count)

    return forks_count


def search_github_repositories(topic):
    # Prepare the GitHub search URL based on the provided topic
    url = f"https://github.com/search?q={topic}&type=Repositories"

    # Send a GET request to the GitHub search URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all repository cards
    repository_cards = soup.find_all("li", class_="repo-list-item")

    # Initialize lists to store repository information
    repositories = []

    # Extract information from each repository card
    for card in repository_cards:
        # Extract repository link
        link = card.find("a", class_="v-align-middle")
        repo_link = link["href"]

        # Extract repository name
        repo_name = link.text.strip()

        # Extract star count
        star_count = card.find('a', {'class': 'Link--muted'})
        star_count = extract_star_count(star_count)

        # Fetch forks count using Selenium
        forks_count = get_forks_count(f"https://github.com{repo_link}")

        # Extract last updated date
        updated_date = card.find("relative-time")
        last_updated = updated_date["datetime"].split("T")[0] if updated_date else ""

        # Extract languages
        lang_spans = card.find_all("span", itemprop="programmingLanguage")
        languages = ", ".join(lang.text.strip() for lang in lang_spans)

        # Add repository details to the list
        repositories.append((repo_link, repo_name, star_count, forks_count, last_updated, languages))

    # Sort repositories by star count in descending order
    repositories.sort(key=lambda x: x[2], reverse=True)

    # Create a DataFrame from the repositories list
    df = pd.DataFrame(repositories, columns=["Repository Link", "Name", "Star Count", "Forks Count", "Last Updated", "Languages"])

    # Convert the DataFrame to an Excel file
    excel_file = f"{topic}_repositories.xlsx"
    df.to_excel(excel_file, index=False)

    print(f"Excel file '{excel_file}' created successfully.")

# Example usage
topic_input = input("Enter a topic to search GitHub repositories: ")
search_github_repositories(topic_input)

