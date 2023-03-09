from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from datetime import date
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


download_path = '/home/lpahl/Documents/Projects/mtga_draft/mtga_draft_analytics/data/scraped_file/'
current_date = date.today()
download_file_name = f"card-ratings-{current_date}.csv"
download_pathname = f"{download_path}{download_file_name}"
format_to_download = ["QuickDraft", "PremierDraft"]
extension_to_download = []
download_all = True
user_group_to_download = ["All Users", "top", "middle", "bottom", ""]

chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_path}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)



driver.get("https://www.17lands.com/card_ratings")

data_table = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".ui.celled.inverted.selectable.sortable.striped.unstackable.compact.table"))
        )

extension_selector = driver.find_element(By.ID, "expansion")
extension_list = extension_selector.find_elements(By.CSS_SELECTOR, "*")

format_selector = driver.find_element(By.ID, "format")
format_list = format_selector.find_elements(By.CSS_SELECTOR, "*")

user_selector = driver.find_element(By.ID, "user-group")
user_list = user_selector.find_elements(By.CSS_SELECTOR, "*")


df = pd.DataFrame()


for user in user_list:
    if user.get_attribute("text") in user_group_to_download:
        user.click()
    else:
        continue

    for format in format_list:
        if format.get_attribute("text") in format_to_download:
            format.click()
        else:
            continue

        for extension in extension_list:
            if extension.get_attribute("text") in extension_to_download or download_all:
                extension.click()
                time.sleep(10)

                warning_text = None

                try:
                    
                    warning = driver.find_element(By.XPATH, '//*[@id="card_ratings_app"]/div/div[1]/div[6]/a[1]')
                    warning_text = warning.text

                except:
                    print("warning message not found")
                
                if warning_text != None:
                    continue

                else:

                    export_dropdown = driver.find_element(By.CSS_SELECTOR, "div.divider.text")
                    export_button = driver.find_element(By.CSS_SELECTOR, f"a[download='card-ratings-{current_date}.csv']")

                    try:
                        data_table = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".ui.celled.inverted.selectable.sortable.striped.unstackable.compact.table"))
                                )
                        
                    except:

                        continue

                    time.sleep(2)
                    first_cell = driver.find_element(By.XPATH, "//table/tbody/tr/td[4]")
                
                    cell_value = first_cell.text
                
                    if cell_value == '0':
                        continue

                    time.sleep(5)
                    
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
            else:
                continue

df.to_csv("/home/lpahl/Documents/Projects/mtga_draft/mtga_draft_analytics/data/all_data.csv")
df.head()



    
    
    