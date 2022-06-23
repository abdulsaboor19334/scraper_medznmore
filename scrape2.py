import time
from numpy import size
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException, InvalidSessionIdException
import re
from selenium.webdriver.chrome.options import Options
import pandas as pd
from playsound import playsound

def tabiyat():
    driver = Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://tabiyat.pk/category/medicines")
    time.sleep(10)
    lis = driver.find_elements(
        By.XPATH, "//section[@class='ep-product-container']//a")
    parent = driver.window_handles[0]

    name_lis = pd.Series([])
    company_lis = pd.Series([])
    price_lis = pd.Series([])

    wait = WebDriverWait(driver, 20)
    waitShort = WebDriverWait(driver, 5)
    for x in lis:
        try:
            href = x.get_attribute('href')
        except StaleElementReferenceException:
            continue
        if re.search('^https://tabiyat.pk/category', href):
            driver.execute_script(f"window.open('{href}','_blank');")
            child = driver.window_handles[-1]
            driver.switch_to.window(child)
            try:
                button_loc = driver.find_element(
                    By.XPATH, "//svg[@class='MuiSvgIcon-root ep-bg-white']")
                button_con = driver.find_element(
                    By.XPATH, "//button[text()='Confirm Location']")
                if button_loc.is_displayed():
                    button_loc.click()
                    if button_con.is_displayed():
                        button_con.click()
            except NoSuchElementException:
                pass
            try:
                wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//div[@class='ep-card-body']")))
                all_cards = driver.find_elements(
                    By.XPATH, "//div[@class='ep-card-body']/a")
            except TimeoutException:
                continue
            for x in all_cards:
                name = pd.Series(x.find_element(
                    By.CLASS_NAME, "ep-product-title").get_attribute('innerText'))
                company = pd.Series(x.find_element(
                    By.CLASS_NAME, "ep-product-description").get_attribute('innerText'))
                price = pd.Series(x.find_element(
                    By.CLASS_NAME, "ep-price-discount").get_attribute('innerText'))
                name_lis = pd.concat([name, name_lis], ignore_index=True)
                company_lis = pd.concat(
                    [company, company_lis], ignore_index=True)
                price_lis = pd.concat([price, price_lis], ignore_index=True)
                print(name, '\t', company, '\t', price)
            driver.close()
            driver.switch_to.window(parent)
        df = pd.DataFrame(
            {'name': name_lis, 'price': price_lis, 'company': company_lis})
        df.to_csv('tabiyat.csv')


def ailaj():
    options = Options()
    options.add_argument("start-maximized")
    driver = Chrome(executable_path="C:\\Users\\Syed ahmad jalal\\Documents\\Python Scripts\\saboor\\chromedriver.exe",chrome_options=options)
    driver.get("https://ailaaj.com/collections")
    cards = driver.find_elements(
        By.XPATH, "//a[@class='collection-list__item-wrapper collection-list__item-wrapper--overlay']")
    wait = WebDriverWait(driver,10)
    ind = 0
    name_lis = pd.Series([])
    size_lis = pd.Series([])
    price_lis = pd.Series([])
    for card in cards:
        playsound('beep.mp3')
        try:
            href = card.get_attribute('href')
        except WebDriverException as err:
            ind += 1
            driver.save_screenshot(f'ss/{ind}{str(err)}.png')
            continue
        driver.execute_script(f"window.open('{href}','_blank');")
        if len(driver.window_handles) != 2:
            time.sleep(5)
        parent = driver.current_window_handle
        driver.switch_to.window(driver.window_handles[1])
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'product-item__info')))
            items = driver.find_elements(By.CLASS_NAME, 'product-item__info')
        except (TimeoutException , WebDriverException) as err:
            ind += 1
            driver.save_screenshot(f'ss/{ind}{str(err)}.png')
            driver.close()
            driver.switch_to.window(parent)
            continue
        for item in items:
            try:
                name_size = item.find_element(By.CLASS_NAME,'product-item__info-inner').get_attribute('innerText').split('\n')
                name = pd.Series(name_size[0])
                size = pd.Series(name_size[1].strip('Pack Size: '))
                price = pd.Series(item.find_element(By.CSS_SELECTOR,'div.product-item__price-list.price-list.test16').get_attribute('innerText'))
            except (WebDriverException ) as err:
                driver.save_screenshot(f'ss/{ind}{str(err)}.png')
                print(driver.window_handles)
                print(parent)
                continue
            name_lis = pd.concat([name, name_lis], ignore_index=True)
            size_lis = pd.concat([size, size_lis], ignore_index=True)
            price_lis = pd.concat([price, price_lis], ignore_index=True)
            print(name , '\n' , size ,'\n',price, '\n')
        driver.close()
        driver.switch_to.window(parent)
        df = pd.DataFrame(
        {'name': name_lis, 'price': price_lis, 'size':size_lis })
        df.to_csv('aailaj.csv')
# ailaj()
tabiyat()
