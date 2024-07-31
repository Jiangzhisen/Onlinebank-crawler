# !/usr/bin/python
# coding:utf-8

# Created by Zhisen Jiang on 2024/07/30.

import requests
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from time import sleep
import io


def taiwanBusinessBankCrawler(url, id_number, user_name, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=EN')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, timeout=300)

    driver.get(url)
    wait.until(EC.visibility_of_element_located((By.ID, "login")))
    driver.find_element(By.ID, "show_cusidn").send_keys(id_number)   
    driver.find_element(By.ID, "userName").send_keys(user_name)   
    driver.find_element(By.ID, "webpw").send_keys(password) 

    verify_code_element = driver.find_element(By.NAME, "kaptchaImage")
    verify_code_image = Image.open(io.BytesIO(verify_code_element.screenshot_as_png))
    # verify_code_image.show()

    code = input("Please input the verify code you saw: ")
    print(f"result: {code}")
    driver.find_element(By.ID, "capCode").send_keys(code)
    driver.find_element(By.ID, "login").click()

    wait.until(EC.visibility_of_element_located((By.ID, "balance_account_tw")))
    driver.find_element(By.ID, "balance_account_tw").click()
    wait.until(EC.visibility_of_element_located((By.ID, "actionBar")))
    options_block = driver.find_element(By.ID, "actionBar").find_elements(By.TAG_NAME, "option")
    options_block[1].click()  # Account Transaction History

    wait.until(EC.visibility_of_element_located((By.ID, "CMSUBMITNOW")))
    # driver.find_element(By.ID, "CMTODAY").click()   # Today's Transactions"
    driver.find_element(By.ID, "CMCURMON").click()   # This Month's Transactions
    driver.find_element(By.ID, "CMSUBMITNOW").click()
    wait.until(EC.visibility_of_element_located((By.ID, "DataTables_Table_0_wrapper")))
    transactions_table = driver.find_element(By.ID, "DataTables_Table_0_wrapper")

    # Get the image of transactions table
    total_height = driver.execute_script("return arguments[0].scrollHeight;", transactions_table)
    total_width = driver.execute_script("return arguments[0].scrollWidth;", transactions_table)
    driver.set_window_size(total_width + 100, total_height + 100)
    transactions_table_image = Image.open(io.BytesIO(transactions_table.screenshot_as_png))
    transactions_table_image.show()
    transactions_table_image_bytes_format = io.BytesIO(transactions_table.screenshot_as_png)
    sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_interval = soup.find("ul", {"class": "ttb-result-list"}).find_all("li")[1].find("p").get_text().strip()
    msg = f"\n\nSearch Interval: {search_interval}\n"

    return msg, transactions_table_image_bytes_format


def LineNotify(token, msg, image):
    headers = {
        "Authorization": "Bearer " + token
    }
    params = {
        "message": msg
    }
    image = {
        "imageFile": image
    }
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params, files=image)
    print(f"Response: {r.text}")

 

if __name__ == "__main__": 

    token = ""   # The token obtained from LINE Notify

    # Taiwan Business Bank
    url = "https://ebank.tbb.com.tw/nb3/login"   # The URL to be crawled
    id_number = ""   # Input your National ID No.
    user_name = ""   # Input your user name
    password = ""   # Input your password

    msg, image = taiwanBusinessBankCrawler(url, id_number, user_name, password);

    LineNotify(token, msg, image)
