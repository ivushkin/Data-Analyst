import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import threading
import os
import Month_today
from selenium.webdriver.support.ui import WebDriverWait


#1 Настройка и инициализация браузера
def browser_settings(zagruzka_path, driver_path,link):
    global download_directory
    download_directory = zagruzka_path
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })

    global driver
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    global actions
    actions = ActionChains(driver)
    driver.maximize_window()
    driver.get(link)



def zoom():
    driver.execute_script("document.body.style.zoom='35%'")
#_________________________________Переключение__ФРЕЙМА___________________
def frame_switch(name_frame):
    driver.switch_to.frame(name_frame)

def frame_parent():
    driver.switch_to.parent_frame()
    asde = driver.execute_script("return window.frameElement.getAttribute('name');")
    print(asde)

#Поиск и переключение фрейма
def find_iframe():
    frame_element = driver.find_element('css selector', 'iframe[id^="iframe4753"]')
    driver.switch_to.frame(frame_element)

#_________________________________Исходный код страницы___________________
def page_sources():
    print(driver.page_source)


    #2 Функция для поиска элемента и нажатия на него
def FindTouch_l(xput):
    while True:
        try:
            element = driver.find_element_by_xpath(xput)
            try:
                element.click()
                time.sleep(2)
                break
            except ElementClickInterceptedException:
                """вызываем код элемента xpath, который не может найти конструтор.
                """
                print('Не найден элемент', (xput))
            print('Элемент найден и клик произведен')
            time.sleep(1)
            break
        except:NoSuchElementException

#3 Функция для поиска элемента и нажатия на него правой кнопкой мыши
def FindTouch_r(xput_prav):
    while True:
        try:
            element_prav = driver.find_element_by_xpath(xput_prav)
            time.sleep(1)
            try:
                actions.context_click(element_prav).perform()
                time.sleep(1)
                break
            except ElementNotInteractableException:
                """вызываем код элемента xpath, который не может найти конструтор.
                """
                print('Ошибка в нажатии правой кнопкой мыши по элементу',(xput_prav))
            print('Нашёл элемент и нажал правую кнопку мыши')
            time.sleep(1)
            break
        except: NoSuchElementException
    time.sleep(5)

def FindTouch_delete(xput):
    while True:
        try:
            element = driver.find_element_by_xpath(xput)
            try:
                element.click()
                time.sleep(1)
                break
            except ElementClickInterceptedException:
                """вызываем код элемента xpath, который не может найти конструтор.
                """
                print('Я не кликнул по элементу',(xput))
            print('Элемент найден и клик произведен')
            time.sleep(1)
            break
        except :NoSuchElementException
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(Keys.DELETE)

def FindTouch_SendText(xput,tekst2):
    while True:
        try:
            element = driver.find_element_by_xpath(xput)
            try:
                element.click()
                time.sleep(1)
                break
            except ElementClickInterceptedException:
                """вызываем код элемента xpath, который не может найти конструтор.
                """
                print('Нет клика по элементу',(xput))
                time.sleep(1)
        except :NoSuchElementException
    element.send_keys(tekst2)

def new_link(link):
    driver.get(link)

def FindTouch_SendText_enter(xput,tekst2):
    while True:
        try:
            element = driver.find_element_by_xpath(xput)
            try:
                element.click()
                time.sleep(1)
                break
            except ElementClickInterceptedException:
                """вызываем код элемента xpath, который не может найти конструтор.
                """
                print('Нет клика по элементу',(xput))
                time.sleep(1)
        except :NoSuchElementException
    element.send_keys(tekst2)
    time.sleep(3)
    element.send_keys(Keys.ENTER)

def Page_down():
    ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(1)

def FindTouch_l_double(double_click):
    while True:
        try:
            element_double = driver.find_element_by_xpath(double_click)
            time.sleep(1)
            try:
                actions.double_click(element_double).perform()
                time.sleep(1)
                break
            except ElementNotInteractableException:
                print('не нажал правую кнопку мыши')
            print('Нашёл элемент и нажал правую кнопку мыши')
            time.sleep(1)
            break
        except : NoSuchElementException
    time.sleep(5)
#4___________________________2___ФУНКЦИИ__ОБРУБАЮЩИЕ ВЫПОЛНЕНИЕ В ЗАВИСИМОСТИ ОТ ВРЕМЕНИ ВЫПОЛНЕНИЯ СКРИПТА____________
#__________________ВАЖНО ВСТАВИТЬ ПОСЛЕ driver в скрипте дабы он сначала определился а потом передавался в функцию
def killer_low(vrem9):
    # Функция, которая завершит выполнение программы через 6 минуты
    def timeout():
        time.sleep(int(vrem9))  # Ждем 360 секунд (6 минуты)
        print('\n',"Прошло 6 минут. Скрипт не смог найти элемент и принудительно был закрыт.",'\n')
        driver.quit()
        os._exit(0)  # Завершаем выполнение программы


    # Создаем таймер для завершения программы
    timer = threading.Thread(target=timeout)
    timer.daemon = True  # Устанавливаем поток как демон, чтобы он завершился, если главный поток завершится
    timer.start()

def killer_high(vrem91):
    # Функция, которая завершит выполнение программы через 2 минуты
    def timeout():
        time.sleep(vrem91)  # Ждем 480 секунд (8 минуты)
        print("Прошло 8 минуты. Прерывание выполнения.")
        driver.quit()
        os._exit(0)  # Завершаем выполнение программы


    # Создаем таймер для завершения программы
    timer = threading.Thread(target=timeout)
    timer.start()

def scroll_down():
    driver.execute_script("window.scrollTo(0, -1250);")
    time.sleep(3)

# 5 Сохранение и переименование файла
def save_file(tekst):
    download_path = download_directory
    filename = tekst + '.xlsx'

    files = os.listdir(download_directory)
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_directory, x)), reverse=True)
    latest_file = sorted_files[0]

    downloaded_file_path = os.path.join(download_directory, latest_file)

    renamed_file_path = os.path.join(download_directory, filename)

    os.replace(downloaded_file_path, renamed_file_path)

# 6 Сохранение и переименование файла с ретроспективой
def save_file_retro(tekst):
    download_path = download_directory
    filename = str(Month_today.segodnya) + tekst + '.xlsx'

    files = os.listdir(download_directory)
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_directory, x)), reverse=True)
    latest_file = sorted_files[0]

    downloaded_file_path = os.path.join(download_directory, latest_file)

    renamed_file_path = os.path.join(download_directory, filename)

    os.replace(downloaded_file_path, renamed_file_path)


#6 Закрытие браузера
def okon4anie():
    driver.quit()
    print('Закрыл браузер')