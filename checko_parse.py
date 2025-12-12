import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

df = pd.read_csv('ppap11.csv')

print(df.head())

driver = webdriver.Chrome()

import re

for index, row in df.iterrows():
    queries = [row['email'], row['phone'], row['name']]
    driver.get("https://checko.ru/")
    for query in queries:
        try:
            search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "query")))
            search_input.clear()
            search_input.send_keys(query)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            link_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-lg")))
            company_links = link_table.find_elements(By.CSS_SELECTOR, "a.link")
            if company_links:
                first_link = company_links[0]
                first_link.click()
                time.sleep(2)

                df.at[index, 'source'] = "checko"
                inn_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "copy-inn")))
                df.at[index, 'inn'] = inn_element.text.strip()

                try:
                    year_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.dropdown-toggle.link-pseudo")))
                    df.at[index, 'revenue_year'] = year_elem.text.strip()
                except Exception as e:
                    print(f"Ошибка при извлечении revenue_year")

                try:
                    rev_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "accounting-huge")))
                    rev_text = rev_elem.text.strip()
                    match = re.search(r'(\d+(?:,\d+)?)\s*(млрд|млн|тыс)?\s*руб\.?', rev_text)
                    if match:
                        num_str = match.group(1).replace(',', '.')
                        num = float(num_str)
                        unit = match.group(2)
                        if unit == 'млрд':
                            multiplier = 1000000000
                        elif unit == 'млн':
                            multiplier = 1000000
                        elif unit == 'тыс':
                            multiplier = 1000
                        else:
                            multiplier = 1
                        rev_num = int(num * multiplier)
                        df.at[index, 'revenue'] = rev_num
                    else:
                        df.at[index, 'revenue'] = None
                except Exception as e:
                    print(f"Ошибка при извлечении revenue")

                try:
                    okved_label = driver.find_element(By.XPATH, "//*[contains(text(), 'Вид деятельности')]")
                    okved_value = okved_label.find_element(By.XPATH, "following-sibling::*[1]")
                    df.at[index, 'okved_main'] = okved_value.text.strip()
                except Exception as e:
                    print(f"Ошибка при извлечении okved_main")

                try:
                    emp_label = driver.find_element(By.XPATH, "//*[contains(text(), 'Среднесписочная численность работников')]")
                    emp_value = emp_label.find_element(By.XPATH, "following-sibling::*[1]")
                    emp_text = emp_value.text.strip()
                    emp_num = ''.join(c for c in emp_text if c.isdigit())
                    df.at[index, 'employees'] = int(emp_num) if emp_num else None
                except Exception as e:
                    print(f"Ошибка при извлечении employees")

                print(str(index) + ' complete')
                break
        except Exception as e:
            print(f"Ошибка при обработке {query}")
            continue
try:
    driver.quit()
except:
    pass

df.dropna(subset="inn", inplace=True)
df.drop_duplicates(subset=['inn'], keep='first', inplace=True)
df.drop('link', axis=1, inplace=True)
companies = df[df['revenue'] >= 200000000]

companies.to_csv('companies.csv', index=False, encoding='utf-8')
print(companies)