from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import subprocess
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

##########################################


def logon(url, browser, login, password):
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button"))
        )
    except:
        print("не вижу кнопки ВОЙТИ !!")

    login_block = '/html/body/div/main/div/section/article/div/form/div/div[3]/input[1]'
    password_block = '/html/body/div/main/div/section/article/div/form/div/div[3]/input[2]'

    browser.find_element(By.XPATH, login_block).send_keys(login)
    browser.find_element(By.XPATH, password_block).send_keys(password)
    browser.find_element(By.XPATH, '/html/body/div/main/div/section/article/div/form/div/div[3]/div[3]/button').click()
    sleep(1)
    page_source = browser.page_source
    if "Пароль неверный" in page_source:
        print('неверные пароль ! !')
        while browser.current_url != url:
            print("ЗАЛОГИНЬТЕСЬ УЖЕ !")
            sleep(5)
    if "Учетная запись не найдена" in page_source:
        print('неверный логин ! !')
        while browser.current_url != url:
            print("ЗАЛОГИНЬТЕСЬ УЖЕ !")
            sleep(15)
    if "Превышено количество одновременных сессий" in page_source:
        browser.find_element(By.XPATH,'/html/body/div/main/div/section/article/div/form/div/div[3]/div[1]/button').click()
        sleep(1)
        page_source = browser.page_source
    #print(page_source)
    if "Выберите вашу часовую зону" in page_source:
        browser.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div/div[2]/button').click()
        sleep(1)
        alert_obj = browser.switch_to.alert
        alert_obj.accept()

#######################################


def make_dir(dir: str, remove: bool = False, append: bool = True):
    """remove — пересоздавать ли папку, если она есть
    append — только если remove = False, оставлять ли папку без изменений, если она есть
    почти как os.makedirs('F:\\torrents\\bun', exist_ok=True) ,
    но может создавать копии папок если append  = False, возвращает path
    и / можно писать как угодно"""
    d = dir.replace(':\\', '://')
    d = d.replace('\\', '/')
    d = d.split('/')
    path = ''
    n = 0
    for p in d:
        if p == '':
            n = n + 1
            continue
        elif ':' in p:
            n = n + 1
            path = path + p + '//'
        else:
            name = d[n]
            path = path + name
            n = n + 1
            if n == len(d):
                if os.path.exists(path) and remove:
                    print('папка пересоздана ', path)
                    shutil.rmtree(path)
                    os.mkdir(path)
                elif os.path.exists(path) and remove == False:
                    if append:
                        print('папка ', path, ' существует')
                        return (path)
                    else:
                        i = 1
                        while os.path.exists(path):
                            path = dir + str(i)
                            i = i + 1
                        print('папка есть, выбрано имя ', path)
                        os.mkdir(path)
                else:
                    print('папки нет, создаем ', path)
                    os.mkdir(path)
            else:
                if not os.path.exists(path):
                    os.mkdir(path)
            if n < len(d):
                path = path + '//'
    return (path)
#####################################


def explore(path):
    """открывает папку"""
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])






