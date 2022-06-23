import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
import re
# writer = pd.ExcelWriter('compet.xlsx', engine='xlsxwriter')


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
    dataFrame.to_excel(writer, sheet_name='dawai')


def medicalstore():
    driver = webdriver.Chrome(
        '/home/saboor/Documents/programming/auto/chromedriver')
    driver.get('https://medicalstore.com.pk/')
    ignored_exceptions = (NoSuchElementException,
                          StaleElementReferenceException,)
    your_element = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions)\
        .until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'a')))
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
    dataFrame.to_excel(writer, sheet_name='medicalstore')


def dvago():
    driver = webdriver.Chrome(
        '/home/saboor/Documents/programming/auto/chromedriver')
    driver.get('https://dvago.pk/')
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

        # main code end
        driver.close()
        driver.switch_to.window(parent)
    dataFrame.to_excel(writer, sheet_name='dvago')

def tabiyat():
    driver = webdriver.Chrome('/home/saboor/Documents/programming/auto/scrape/chromedriver')
    driver.get('https://tabiyat.pk/category/medicines')
    section = driver.find_elements(By.XPATH,"//section[@class='ep-product-container']/div[@class='MuiContainer-root MuiContainer-maxWidthLg']/div")
    print(len(section))
    
    





start = time.time()
# dvago()
# dawai()
# medicalstore()
tabiyat()
end = time.time()
# writer.save()
print(end-start)