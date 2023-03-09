from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from datetime import date
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging as log
import sys
import json

root = log.getLogger()
root.setLevel(log.DEBUG)

handler = log.StreamHandler(sys.stdout)
handler.setLevel(log.DEBUG)
formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

download_path = '/home/lpahl/Documents/Projects/mtga_draft/mtga_draft_analytics/data/scraped_file/'

class Scraper():
    def __init__(self, download_path):
        self.download_path = download_path
        self.current_date = date.today()
        self.download_file_name = f"card-ratings-{self.current_date}.csv"
        self.download_pathname = f"{self.download_path}{self.download_file_name}"
        self.format_to_download = ["QuickDraft", "PremierDraft"]
        self.extension_to_download = []
        self.download_all = True
        self.user_group_to_download = ["All Users", "top", "middle", "bottom"]
        self.scraped_data = pd.DataFrame()
        self.already_downloaded = os.listdir(download_path)
        self.missing_data = []

    def set_format_to_download(self, format_to_download):
        self.format_to_download = format_to_download

    def set_download_all(self, download_all):
        self.download_all = download_all

    def set_extension_to_download(self, extension_to_download):
        self.extension_to_download = extension_to_download

    def set_user_group_to_download(self, user_group_to_download):
        self.user_group_to_download = user_group_to_download

    def initiate_driver_and_load_page(self):
        log.debug("initiate page")
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : download_path}
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get("https://www.17lands.com/card_ratings")

    def locate_selector(self):
        log.debug("locating selector")
        self.data_table = WebDriverWait(self.driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ui.celled.inverted.selectable.sortable.striped.unstackable.compact.table"))
            )

        self.extension_selector = self.driver.find_element(By.ID, "expansion")
        self.extension_list = self.extension_selector.find_elements(By.CSS_SELECTOR, "*")

        self.format_selector = self.driver.find_element(By.ID, "format")
        self.format_list = self.format_selector.find_elements(By.CSS_SELECTOR, "*")

        self.user_selector = self.driver.find_element(By.ID, "user-group")
        self.user_list = self.user_selector.find_elements(By.CSS_SELECTOR, "*")

    def is_warning_message_displayed(self):
        log.debug("wait time warning message")
        time.sleep(10)
        warning_text = None
        try:
            warning = self.driver.find_element(By.XPATH, '//*[@id="card_ratings_app"]/div/div[1]/div[6]/a[1]')
            warning_text = warning.text

        except:
            log.debug("no warning message found")
        
        if warning_text != None:
            log.debug("warning message found")
            return True
        
        else:
            return False
        
    def is_data_table_null(self):
        log.debug("data table check")
        try:
            log.debug("waiting for table to load")
            self.data_table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ui.celled.inverted.selectable.sortable.striped.unstackable.compact.table"))
                    )
        except:
            log.debug("data table is null")
            return True
        
        log.debug("data table wait 2")
        time.sleep(2)   
        self.first_cell = self.driver.find_element(By.XPATH, "//table/tbody/tr/td[4]")
        self.cell_value = self.first_cell.text
        if self.cell_value == '0':
            return True
        return False


    def locate_and_click_export(self):
        log.debug("locate export wait 10")
        time.sleep(10)

        self.export_dropdown = self.driver.find_element(By.CSS_SELECTOR, "div.divider.text")
        self.export_button = self.driver.find_element(By.CSS_SELECTOR, f"a[download='card-ratings-{self.current_date}.csv']")
        
        self.export_dropdown.click()
        self.export_button.click()

    def set_file_name(self, extension, user, format):
        log.debug("setting file name")
        self.extension_name = extension.get_attribute("text")
        self.user_group = user.get_attribute("text")
        self.format_name = format.get_attribute("text")

        self.file_name = f"{self.current_date}-{self.extension_name}-{self.user_group}-{self.format_name}.csv"
        self.new_pathname = f"{self.download_path}{self.file_name}"
        log.debug(f"file name is {self.file_name}")

    def rename_file(self):
        log.debug("renaming file wait 5")
        time.sleep(5)
        os.rename(self.download_pathname, self.new_pathname)

    def save_data(self, file_name):
        log.debug("saving data to csv")
        self.scraped_data.to_csv(f"{self.download_path}{file_name}")

    
    def add_data_to_scraped_data(self):
        log.debug("adding data to scraped data")
        temp_df = pd.read_csv(self.new_pathname)
        temp_df["user_group"] = self.user_group
        temp_df["format"] = self.format_name
        temp_df["extension_name"] = self.extension_name

        if len(self.scraped_data.index) == 0:
            self.scraped_data = temp_df
        else:
            self.scraped_data = pd.concat([self.scraped_data, temp_df])

    def log_missing_data(self):
        self.missing_data.append(
            {
            "extension": self.extension_name,
            "user_group": self.user_group,
            "format": self.format_name
            }
            )
    
    def check_missing_data(self):
        for dict in self.missing_data:
            if dict["extension"] == self.extension_name and dict["user_group"] == self.user_group and dict["format"] == self.format_name:
                return True
            
    def set_missing_data(self, file_path):
        with open(file_path) as f:
            self.missing_data = json.load(f)

    def dump_missing_data(self, file_path):
        with open(file_path, 'w') as f:
            self.missing_data = json.dump(f)

    def scrape(self):

        self.initiate_driver_and_load_page()
        self.locate_selector()

        for user in self.user_list:
            if user.get_attribute("text") in self.user_group_to_download:
                user.click()
            else:
                continue
            
            for format in self.format_list:
                if format.get_attribute("text") in self.format_to_download:
                    format.click()
                else:
                    continue

                for extension in self.extension_list:

                    self.set_file_name(extension, user, format)

                    if self.file_name in self.already_downloaded:
                        continue

                    if extension.get_attribute("text") in self.extension_to_download or self.download_all:
                        extension.click()

                        if self.is_warning_message_displayed() or self.is_data_table_null():
                            continue
                        else:
                            self.locate_and_click_export()
                            self.set_file_name(extension, user, format)
                            self.rename_file()
                            self.add_data_to_scraped_data()


scraper = Scraper(download_path)

scraper.scrape()

scraper.save_data("all_data.csv")


