import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import myfunctions
import configparser
import os.path
import datetime
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
from gui_login_form import return_id

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")
y = ['y', 'yes', 'д', 'да', 'ага']

au = return_id()
login = au[0]
password = au[1]
#########


def xml_parser(url_xml):
    xml_file = urllib.request.urlopen(url_xml)
    root_node = ET.parse(xml_file).getroot()
    restrict_type = root_node.find(
        ".//restrict_records/restrict_record/restrictions_encumbrances_data/restriction_encumbrance_type/value").text
    name = root_node.find(
        ".//restrict_records/restrict_record/right_holders/right_holder/legal_entity/entity/resident/name").text
    return restrict_type, name


path_complete = myfunctions.make_dir('проверенные')
path_well_done = myfunctions.make_dir('готовые')
if os.listdir(path_well_done):
    a = input(f'[ВНИМАНИЕ !] папка {path_well_done} не пуста, очистить ?: ')
    if a.lower() in y:
        shutil.rmtree(path_well_done)
        path_well_done = myfunctions.make_dir('готовые')

now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
ext = 'json'
ext_ = 'xlsx'
fname_j = f'{now}.{ext}'
fname_ex = f'{now}.{ext_}'

url = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration'

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

browser = webdriver.Chrome(options=options, executable_path=settings['path']['executable_path'])

count = len(open('numbers.txt').readlines())
numbers = open('numbers.txt')
p = 0
browser.get(url)
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button"))
    )
except:
    print("не вижу кнопки ВОЙТИ !!")
if "ВОЙТИ" in browser.page_source:
    print("страница логина")
    myfunctions.logon(url, browser, login, password)
    sleep(1)

if browser.current_url != url:
    print(browser.current_url)
    print("Что-то пошло не так ((")
    # browser.get(url)
    sleep(5)
    if browser.current_url != url:
        print(browser.current_url)
        print("Походу не работает сайт ((")
        sys.exit()
    elif "ВОЙТИ" in browser.page_source:
        print("страница логина")
        myfunctions.logon(url, browser, login, password)
for number in numbers:
    number = number.replace('\n', '')
    number = number.replace(' ', '')
    preurl = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration/details/'
    posturl = '/docs'
    url = f'{preurl}{number}{posturl}'
    print(url)
    browser.get(url)
    browser.refresh()
    ##################

    try:
        element = WebDriverWait(browser, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "*[class^='link selected-item']"))
        )
    except:
        print("не вижу номера обращения на странице !!")
        if '502 Bad Gateway' in browser.page_source:
            browser.refresh()
    obr = (browser.find_element(By.CSS_SELECTOR, "*[class^='link selected-item']").text).rsplit('№', 2)
    obr = obr[1]
    print(obr)
    #   проверка загрузки нужной страницы текущего обращения
    if obr != number:
        print('не та страница !!')
        browser.quit()
    row = browser.find_elements(By.CLASS_NAME, 'row-data')
    n = 0
    to_json = {}
    v = 0
    for r in row[::-1]:  # перебор с конца
        if r.text == 'Выписка из реестра.xml':
            n += 1
            v += 1
            link_xml = r.find_element(By.CLASS_NAME, 'col-icon').find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(link_xml)


            def take_data_from_xml(i=1):
                try:
                    d = xml_parser(link_xml)
                    return d
                except:
                    i += 1
                    print(f'не удалось загрузить xml,или нужных ключей нет в xml, попытка {i}')
                    sleep(0.5)
                    if i < 3:
                        return take_data_from_xml(i)


            data = take_data_from_xml()

            print(data)
            if data:
                to_json_ = {
                    n: {'Ограничение': data[0], 'заёмодатель': data[1]}}
            else:
                to_json_ = {
                    n: {'Ограничение': 'не найдено', 'заёмодатель': 'не найден'}}
            to_json.update(to_json_)
    if not v:
        to_json_ = {
            n: {'Ограничение': 'отсутствует', 'заёмодатель': 'отсутствует'}}
        to_json.update(to_json_)
        print(f'номер {number} не содержит выписок')

    data_number = {number: to_json}

    # записываем в файл
    ext = 'json'
    fname = f'{path_well_done}\\{number}.{ext}'

    with open(fname, 'w') as f:
        f.write(json.dumps(data_number, indent=2, ensure_ascii=False))

    # записываем номер пакета в файл
    ext = 'txt'
    fname_ = f'{path_complete}\\{now}.{ext}'
    with open(fname_, 'a+') as f:
        f.write(number + '\n')

    p = p + 1
    print(f'[INFO] отработано {p} ({round(p / count * 100, 2)} %) обращений из {count}, осталось {count - p}')

browser.quit()


def do_merge(path_in, path_out, outfile, outfile_):
    merged = {}
    if not os.path.exists(path_in):
        print('папки ', path_in, ' не существует')
        print('Введите название path_in')
        path_in = str(input())
    for infile in os.listdir(path_in):
        if '.json' in infile:
            print(infile)
            with open(f'{path_in}\\{infile}', 'r') as f:
                datas = json.load(f)
                merged.update(datas)

    if not os.path.exists(path_out):
        print('папки ', path_out, ' не существует')
        print('Введите название path_out')
        path_out = str(input())
    print(path_out)
    df = pd.DataFrame()
    for i in merged:
        for n in merged[i]:
            df = df.append(
                {'номер обращения': i, 'Ограничение': merged[i][n]['Ограничение'],
                 'заёмодатель': merged[i][n]['заёмодатель']},
                ignore_index=True)
    df = df.drop_duplicates()  # удаляем дубли
    # df = df[(df.заёмодатель != 'не найден') & (df['номер обращения'].nunique())]
    df.to_excel(f'{path_out}\\{outfile}', index=False)
    with open(f'{path_out}\\{outfile_}', 'w') as meg_file:
        json.dump(merged, meg_file, indent=2, ensure_ascii=False)
        # json.dump(merged, meg_file, indent=2)


do_merge(path_well_done, path_well_done, fname_ex, fname_j)  # объединяем в один файл
input('Всё завершено удачно, нажмите ENTER для выхода')  # чтоб не закрывалась консоль
myfunctions.explore(path_well_done)
