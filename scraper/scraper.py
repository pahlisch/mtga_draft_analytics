from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from datetime import date
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


download_path = '/home/lpahl/Downloads/'
current_date = date.today()
download_file_name = f"card-ratings-{current_date}.csv"
download_pathname = f"{download_path}{download_file_name}"
format_to_download = ["PremierDraft", "QuickDraft"]


driver = webdriver.Chrome()
driver.get("https://www.17lands.com/card_ratings")

extension_selector = driver.find_element(By.ID, "expansion")
extension_list = extension_selector.find_elements(By.CSS_SELECTOR, "*")

format_selector = driver.find_element(By.ID, "format")
format_list = format_selector.find_elements(By.CSS_SELECTOR, "*")

user_selector = driver.find_element(By.ID, "user-group")
user_list = user_selector.find_elements(By.CSS_SELECTOR, "*")

time.sleep(5)

df = pd.DataFrame()

for extension in extension_list:
    extension.click()

    for user in user_list:
        user.click()

        for format in format_list:
            if format.get_attribute("text") in format_to_download:
                format.click()
                export_dropdown = driver.find_element(By.CSS_SELECTOR, "div.divider.text")
                export_button = driver.find_element(By.CSS_SELECTOR, f"a[download='card-ratings-{current_date}.csv']")

                export_dropdown.click()
                export_button.click()

                extension_name = extension.get_attribute("text")
                user_group = user.get_attribute("text")
                format_name = format.get_attribute("text")

                file_name = f"{current_date}-{extension_name}-{user_group}-{format_name}.csv"
                new_pathname = f"{download_path}{file_name}"

                time.sleep(5)

                os.rename(download_pathname, new_pathname)

                temp_df = pd.read_csv(new_pathname)
                temp_df["user_group"] = user_group
                temp_df["format"] = format_name
                temp_df["extension_name"] = extension_name

                if len(df.index) == 0:
                    df = temp_df
                else:
                    df = pd.concat([df, temp_df])

        
        break
    break

df.to_csv("/home/lpahl/Documents/Projects/mtga_draft/mtga_draft_analytics/scraper/all_data.csv")
df.head()



    
    
    