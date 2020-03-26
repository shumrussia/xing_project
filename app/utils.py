from collections import OrderedDict
import os
import pandas as pd
import random
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


def parse_page(driver):
    iter_collected_data = OrderedDict({
    "Firma": [],
    "Ort": [],
    "Vorname": [],
    "Nachname": [],
    "Original-Positionsbezelchnung": [],
    "Xing": []
                } )
    # Считываем все анкеты на странице
    total_profiles = driver.find_elements_by_xpath("//a[contains(@class, 'search-card')]")
    # Подгоняем диапазон под селениум (элементы в селениуему индексируются не с нуля, а с единицы)
    anchor_iteration = len(total_profiles) + 1
    for i in range(1, anchor_iteration):
        # Хватаем анкету
        iter_profile_element = driver.find_element_by_xpath("//a[contains(@class, 'search-card')][{}]".format(i))
        # Хватаем подэлемент "титул"
        iter_title_element = iter_profile_element.find_element_by_xpath(".//div[contains(@class, 'MemberCard-style-title')]")
        text_title = iter_title_element.text
        iter_list_title = text_title.split()
        # Заполняем имя и фамилию
        iter_surname = iter_list_title.pop()    
        iter_name = ' '.join(iter_list_title)
        # Хватаем подэлемент "ссылка на профиль"
        iter_list_link = iter_profile_element.get_attribute('href').rsplit("/",1)
        iter_list_link.pop()
        # Заполняем ссылку
        iter_link = iter_list_link.pop() + "/cv"
        # Пробуем найти подэлемент "инфо о трудоустройстве", так как у некоторых анкет он отсутствует
        try:
            # Если инфо о трудоустройстве имеется, вытаскиваем должность
            iter_employment_element = iter_profile_element.find_element_by_xpath(".//div[contains(@class, 'MemberCard-style-occupationMdWrapper')]")
            employment_text = iter_employment_element.text
            iter_list = employment_text.split(",", 1)
            iter_position = iter_list[-1].strip().rstrip(",")
            # Вытаскиваем название компании
            iter_company_element = iter_profile_element.find_element_by_xpath(".//a[contains(@href, '/companies/go?name')]")
            iter_company = iter_company_element.text
        except NoSuchElementException:
            # Если инфо о трудоустройстве отсутствует, заполняем пустыми 
            employment_text = "Absent"
            iter_position = "unemployed"
            iter_company = "unemployed"
        # Пробуем найти город, потому что у некоторых анкет он отстутствует
        try:
            # Если нашли, заполняем город
            iter_city_element = driver.find_element_by_xpath("//a[contains(@class, 'search-card')][{}]/div[1]/div[2]/div[1]/span/strong".format(i))
            iter_city = iter_city_element.text.strip()
        except NoSuchElementException:
            # Если не нашли, заполняем страну
            iter_city = 'Deutschland'   
        iter_collected_data["Vorname"].append(iter_name)
        iter_collected_data["Nachname"].append(iter_surname)
        iter_collected_data["Original-Positionsbezelchnung"].append(iter_position)
        iter_collected_data["Firma"].append(iter_company)
        iter_collected_data["Xing"].append(iter_link)
        iter_collected_data["Ort"].append(iter_city)
    return iter_collected_data


def process_query(query, login, password):
    collected_data = OrderedDict({
    "Firma": [],
    "Ort": [],
    "Vorname": [],
    "Nachname": [],
    "Original-Positionsbezelchnung": [],
    "Xing": []
                } )

		# инициализируем движок Мозилла Файрфокс и переходим на сайт
    driver = webdriver.Firefox()
    driver.get("https://www.xing.com")
    # ждём рандомное время для прогрузки страницы
    time.sleep(random.uniform(0.3, 0.8))
    el_login = driver.find_element_by_xpath("//a[@href='https://login.xing.com']")
    el_login.click()
    # ждём рандомное время для прогрузки страницы
    time.sleep(random.uniform(0.5, 1.5))
    el_username = driver.find_element_by_xpath("//input[@name='username']")
    el_password = driver.find_element_by_xpath("//input[@name='password']")
    el_submit = driver.find_element_by_xpath("//button[@type='submit']")
    time.sleep(random.uniform(1.2, 2.4))
    el_username.send_keys(login)
    time.sleep(random.uniform(1.3, 2.5))
    el_password.send_keys(password)
    time.sleep(random.uniform(0.7, 1.8))
    el_submit.click()
    # ждём рандомное время для прогрузки страницы
    time.sleep(random.uniform(5,7.3))
    el_search_bar = driver.find_element_by_xpath("//input[@type='search']")
    el_search_bar.send_keys(query)
    el_search_button = driver.find_element_by_xpath("//button[@title='Suchen']")
    el_search_button.click()
    # ждём рандомное время для прогрузки страницы
    time.sleep(random.uniform(1.7, 3.4))
    el_members_list = driver.find_elements_by_xpath("//div[contains(@class,'MemberCard-style-title')]")
    # необходимое количество итераций на странице
    no_of_iterations = len(el_members_list)

    # Номер первой страницы результатов
    el_first_page = driver.find_element_by_xpath("//li[contains(@class, 'malt-pagination')]/span[1]")
    # Номер последней страницы результатов
    el_last_page = driver.find_element_by_xpath("//li[contains(@class, 'malt-pagination')]/span[2]")
    last_page = el_last_page.text
    # Количество скроллов по страницам
    no_of_scrolls = int(last_page) - 1

    for i in range(no_of_scrolls):
        el_scroll = driver.find_element_by_xpath("//ol[contains(@class, 'malt-pagination-Pagination')]/li[3]")
        el_scroll.click()
        time.sleep(random.uniform(2.3, 3.7))
        iter_result = parse_page(driver)

        for key in iter_result:
            collected_data[key].extend(iter_result[key])

    driver.quit()

    df = pd.DataFrame.from_dict(collected_data)

    file_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\test_list.xlsx')

    df.to_excel(file_path)

    return file_path




