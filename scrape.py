import time
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
from bs4 import BeautifulSoup
import requests
import os
def load_driver(url:str) -> Chrome:
    cwd = os.getcwd()
    name = 'chromedriver'
    abs_path = os.path.join(cwd,name)
    options = Options()
    options.add_argument("start-maximized")
    driver = Chrome(abs_path,chrome_options=options)
    driver.get(url)
    return driver


def dawai():
    dataFrame = pd.DataFrame({
        'name': [],
        'type': [],
        'sku': [],
        'price_orignal': [],
        'price_retail': []
    })
    index = 0
    response = requests.get('https://dawaai.pk/')
    soup = BeautifulSoup(response.content, 'html.parser')
    nav = soup.find(
        'div', {'class': 'column col-8 main-nav', 'style': 'padding-left: 0px'})
    a_tags = nav.find_all('a', {'itemprop': 'url'})
    links = []
    for tag in a_tags:
        if tag.get('href') not in links:
            links.append(tag.get('href'))
    for link in links:
        playsound('beep.mp3')
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.find_all('div', {'class': 'card'})
        for card in cards:
            try:
                name = card.find('h2').text
                p = card.find_all('p')
                type = p[0].text
                sku = p[1].text
                price = card.find('h4').text
                discounts_vs_retail = re.split('Rs\s*|Rs\.', price)
                result = [x.strip() for x in discounts_vs_retail if x != '']
                if '' in result:
                    result.remove('')
                try:
                    num1 = int(result[1].strip('.'))
                    num2 = int(result[0].strip('.'))
                    index += 1
                    df = pd.DataFrame({'name': name, 'type': type, 'sku': sku,
                                      'price_orignal': num1, 'price_retail': num2}, index=[index])
                    dataFrame = pd.concat([df, dataFrame])
                except ValueError:
                    num1_raw = result[1].strip('.')
                    num2_raw = result[0].strip('.')
                    num1_split = re.split(',', num1_raw)
                    num2_split = re.split(',', num2_raw)
                    try:
                        num1 = int(''.join(num1_split))
                        num2 = int(''.join(num2_split))
                    except ValueError:
                        num1 = int(float(''.join(num1_split)))
                        num2 = int(float(''.join(num2_split)))
                    index += 1
                    df = pd.DataFrame({'name': name, 'type': type, 'sku': sku,
                                      'price_orignal': num1, 'price_retail': num2}, index=[index])
                    dataFrame = pd.concat([df, dataFrame])

            except AttributeError:
                pass
            except IndexError:
                pass
    print('writing to excel...')
    dataFrame.to_csv('csv/dawai.csv')


def medicalstore():
    driver = load_driver('https://medicalstore.com.pk/')
    ignored_exceptions = (NoSuchElementException,
                          StaleElementReferenceException,)
    your_element = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions)\
        .until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    elements = driver.find_elements(by=By.TAG_NAME, value='a')
    body = driver.find_element(by=By.TAG_NAME, value='body')
    parent = driver.current_window_handle
    index = 0
    dataFrame = pd.DataFrame({
        'name': [],
        'type': [],
        'brand': [],
        'price': []
    })
    for element in elements:
        playsound('beep.mp3')
        try:
            href = element.get_attribute('href')
            if href != None and re.search(r'https://medicalstore\.com\.pk/product-category/.*', href):
                driver.execute_script(f"window.open('{href}','_blank')")
                driver.switch_to.window(driver.window_handles[1])
                try:
                    products = driver.find_element(
                        by=By.CLASS_NAME, value="products")
                except:
                    continue
                productlist = products.find_elements(
                    by=By.CLASS_NAME, value="gtm4wp_productdata")
                for pr in productlist:
                    try:
                        name = pr.get_attribute('data-gtm4wp_product_name')
                    except WebDriverException:
                        name = 'Not Found'

                    try:
                        type = pr.get_attribute('data-gtm4wp_product_cat')
                    except WebDriverException:
                        type = 'Not Found'

                    try:
                        brand = pr.get_attribute('data-gtm4wp_product_brand')
                    except WebDriverException:
                        brand = 'Not Found'
                    try:
                        price = pr.get_attribute('data-gtm4wp_product_price')
                    except:
                        price = 'Not Found'
                    index += 1
                    df = pd.DataFrame(
                        {'name': name, 'type': type, 'brand': brand, 'price': price}, index=[index])
                    dataFrame = pd.concat([df, dataFrame])
                driver.close()
                driver.switch_to.window(parent)
        except:
            continue
    dataFrame.to_csv('csv/medicalstore.csv')

def dvago():
    driver = load_driver('https://dvago.pk/')
    nav_ul = driver.find_element(By.CLASS_NAME, 'navmenu')
    nav_a = nav_ul.find_elements(By.TAG_NAME, 'a')
    parent = driver.current_window_handle
    dataFrame = pd.DataFrame({
        'name': [],
        'title': [],
        'qauntity': [],
        'price': []
    })
    index = 0
    for a in nav_a:
        playsound('beep.mp3')
        link = a.get_attribute('href')
        driver.execute_script(f"window.open('{link}','_blank')")
        driver.switch_to.window(driver.window_handles[1])
        # main code
        elemens = driver.find_elements(By.CLASS_NAME, 'productitem')
        for element in elemens:
            price = element.find_element(By.CLASS_NAME, 'money').text
            title = element.find_element(
                By.CLASS_NAME, 'productitem--title').text
            try:
                name = re.search('[a-zA-Z\s\-&]*', title).group(0)
            except AttributeError:
                name = 'N/A'
            try:
                qtty = re.search(r'\d.*', title).group(0)
            except AttributeError:
                qtty = 'N/A'
            if price != '':
                index += 1
                df = pd.DataFrame({
                    'name': name,
                    'title': title,
                    'qauntity': qtty,
                    'price': price
                }, index=[index])
                dataFrame = pd.concat([dataFrame, df])
        driver.close()
        driver.switch_to.window(parent)
        dataFrame.to_csv('csv/dvago.csv')

def tabiyat():
    driver = Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://tabiyat.pk/category/medicines")
    driver = load_driver('https://tabiyat.pk/category/medicines')
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
        playsound('beep.mp3')
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
        df.to_csv('csv/tabiyat.csv')

def ailaj():
    driver = load_driver('https://ailaaj.com/collections')
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
        df.to_csv('csv/aailaj.csv')

start = time.time()
dvago()
# dawai()
# medicalstore()
# tabiyat()
# ailaj()
end = time.time()
print(end-start)