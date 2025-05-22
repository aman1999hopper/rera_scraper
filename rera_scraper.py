
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# This will be setup chrome webDriver 
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

# This code will be responsible to open RERA project listing page
driver.get("https://rera.odisha.gov.in/projects/project-list")
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "project-card")))

# It will get first 6 urls of the project cards
# You can change the number of projects to scrape by modifying the range
project_links = [
    card.find_element(By.LINK_TEXT, "View Details").get_attribute("href")
    for card in driver.find_elements(By.CLASS_NAME, "project-card")[:6]
]

# scrape each project's detail page
scraped_projects = []

for link in project_links:
    driver.get(link)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-overview")))
    time.sleep(2)

    try:
    
        reg_no = driver.find_element(By.XPATH, "//div[contains(text(),'RERA Regd. No')]/following-sibling::div").text.strip()
        name_of_project = driver.find_element(By.XPATH, "//div[contains(text(),'Project Name')]/following-sibling::div").text.strip()
        
        # Click on the "Promoter Details" tab
        driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]").click()
        time.sleep(2)

        promoter_name = driver.find_element(By.XPATH, "//div[contains(text(),'Company Name')]/following-sibling::div").text.strip()
        promoter_address = driver.find_element(By.XPATH, "//div[contains(text(),'Registered Office Address')]/following-sibling::div").text.strip()
        gst_no = driver.find_element(By.XPATH, "//div[contains(text(),'GST No')]/following-sibling::div").text.strip()

        scraped_projects.append({
            "RERA Regd. No": reg_no,
            "Project Name": name_of_project,
            "Promoter Name": promoter_name,
            "Promoter Address": promoter_address,
            "GST No": gst_no
        })

    except Exception as e:
        scraped_projects.append({
            "error": str(e),
            "link": link
        })

driver.quit()

# Save to JSON
with open("output_projects.json", "w", encoding="utf-8") as f:
    json.dump(scraped_projects, f, indent=4)

print(f"✅ Total projects scraped: {len(scraped_projects)}")
