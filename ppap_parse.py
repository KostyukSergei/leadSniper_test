from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)
segment_urls = [["BTL","https://www.alladvertising.ru/top/btl/"], ["FULL_CYCLE","https://www.alladvertising.ru/top/full-service/"], ["COMM_GROUP","https://www.alladvertising.ru/top/event-management/"],
        ["SOUVENIR","https://www.alladvertising.ru/top/gifts/"], ["COMM_GROUP","https://www.alladvertising.ru/top/merchandising/"], ["COMM_GROUP","https://www.alladvertising.ru/top/branding/"]]
companies = []

for url in segment_urls:
    try:
        driver.get(url[1])
        rate_elements = WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rate20")))
        for element in rate_elements:
            links = element.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "/info/" in href:
                    companies.append({"link": href, "segment_tag": url[0]})
        
    except Exception as e:
        print(f"An error occurred: {e}")

companies = list({d["link"]: d for d in companies}.values())
print(len(companies))
print(companies)

for com in companies:
    try:
        driver.get(com["link"])
        com["name"] = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'h1_700b'))).text.strip()
        com["region"] = driver.find_element(By.CLASS_NAME, "h1_300").text.split(',')[1].strip()
        phone_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:']")
        com["phone"] = phone_elements[0].text if phone_elements else "N/A"
        body_text = driver.find_element(By.TAG_NAME, "body").text
        emails = re.findall(r'E-mail: ([\w\.-]+@[\w\.-]+)', body_text)
        com["email"] = emails[0] if emails else "N/A"
        com["description"] = driver.find_element(By.CLASS_NAME, "preview").text.strip()
        sites = re.findall(r'Сайт: ([\S]+)', body_text)
        com["site"] = sites[0] if sites else "N/A"
        rating_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/top100/"]')
        com["rating_ref"] = "https://www.alladvertising.ru/top100/" if rating_elements else "N/A"
        print(com)
    except Exception as e:
        print(f"An error occurred: {e}")

print(companies)

try:
    driver.quit()
except:
    pass

df = pd.DataFrame(companies)
df.to_csv('ppap11.csv', index=False, encoding='utf-8')