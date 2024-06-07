# Загрузка используемых библиотек
import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import Month_today


# Вывод текущей даты, что зонировать один день от другого в логе
#print('\n','\033[32mСтарт нового дня\033[0m','Запущено '+str(datetime.now().strftime('%d-%m-%y/%H:%M')),'\n')


# Настройки загрузочных папок и папок сохранения, настройка браузера
chrome_options = Options()
download_directory = "\\\\pgk.rzd\\workgroups\\БД ЛП\\ЛПА (отдел аналитической работы)\\001_ШАБЛОНЫ\\103 ЕВРАЗ автоматизация слайда\\Евраз автомат нов\\TRY"
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': download_directory,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})


# Загрузка драйвера Хрома, присваивание перемменной на ссылку ССП, добавляем ожидание срабатывание драйвера
driver = webdriver.Chrome('\\\\pgk.rzd\\workgroups\\БД ЛП\\ЛПА (отдел аналитической работы)\\6. НАРАБОТКИ PYTHON\\Инструментарий Python\\Chromedriver\\chromedriver.exe', options=chrome_options)
url = "https://ssp.pgk.ru/auth/login"
wait = WebDriverWait(driver, 10)


# Инициализация переменных текущей даты
today = datetime.today()
yesterday = today - timedelta(days=1)
yesterday_format = yesterday.strftime('%d.%m.%Y')


# _______________МОМЕНТ__С__КОДИРОВКОЙ__________
data_log = open('\\\\pgk.rzd\\workgroups\\БД ЛП\\ЛПА (отдел аналитической работы)\\6. НАРАБОТКИ PYTHON\\Инструментарий Python\\data1.json', "r", encoding='utf-8-sig')
data_log1 = json.load(data_log)


# _______________________ДАННЫЕ____________________
login = data_log1["login"]
passw = data_log1["passw"]
url = data_log1["url"]
url2 = data_log1["url2"]


# Функция, которая завершит выполнение программы через 2 минуты
Month_today.killer_low(driver)


# Перенаправляем страницу в переменной URL в драйвер хрома, расширяем окно браузера до максимального, обновляем текущую страницу, ждем 15 секунд
driver.get(url)
driver.maximize_window()
driver.refresh()
time.sleep(15)


""" Ранее используемый код
# element = driver.find_element_by_id('mat-select-value-3')
# element.click()
# element1 = driver.find_element_by_xpath("//span[@class='mat-option-text' and contains(text(), 'ССП')]")
# element1.click()
"""


# Скрипт захода в ССП, ищем элементы на странице ССП и отправляем на стартовой страницу логин и пароль из файла, далее авторизовываемся в ССП
Login_selen = driver.find_element_by_xpath('/html/body/app-root/div/div/app-login/form/mat-form-field[1]/div/div[1]/div/input')
time.sleep(2)
Login_selen.click()
time.sleep(2)
Login_selen.send_keys(login)
Passw_selen = driver.find_element_by_xpath('/html/body/app-root/div/div/app-login/form/mat-form-field[2]/div/div[1]/div/input')
time.sleep(2)
Passw_selen.click()
time.sleep(2)
Passw_selen.send_keys(passw)
time.sleep(5)
Enter_selen = driver.find_element_by_xpath("/html/body/app-root/div/div/app-login/form/button")
Enter_selen.click()
time.sleep(10)
driver.refresh()
system_type = driver.find_element_by_xpath("(//a[contains(text(),'ССП')])[1]")
 #   ('/html/body/app-root/div/div/app-system/div[2]/a[1]')
system_type.click()
time.sleep(5)


# Скрипт выгрузки данных внутри ССП
"""Отправляем в драйвер хрома ссылку внутри ссп и ждем секунду """
driver.get(url2)
time.sleep(1)

"""Повторять пока не будет найден элемент на странице, как только найден - передать сочетание клавиш и выйти из цикла, иначе выдать ошибку """
while True:
    try:
        date_choose = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/mat-dialog-container/app-park-changes-params/form/div[2]/div/input').send_keys(Keys.CONTROL + 'a')
        print('Элемент найден')
        time.sleep(1)
        break
    except :NoSuchElementException


"""Найти элементы, результаты выгрузить в Excel, файл сохранить в папку указанную в начале, подождать 10 секунд после операции сохранения файла """
time.sleep(1)
date_choose1 = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/mat-dialog-container/app-park-changes-params/form/div[2]/div/input').send_keys(Keys.DELETE)
time.sleep(1)
data_choose2 = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/mat-dialog-container/app-park-changes-params/form/div[2]/div/input').send_keys(yesterday_format)
time.sleep(2)
date_turn = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/mat-dialog-container/app-park-changes-params/form/div[4]/button[2]')
date_turn.click()
time.sleep(10)
export_excel = driver.find_element_by_xpath('/html/body/app-root/mat-drawer-container/mat-drawer-content/div/app-ssp/app-park-changes/app-toolbar/div/div[1]/app-toolbar-button[3]/div')
export_excel.click()
time.sleep(10)
download_path = download_directory

""" Присваиваем название выгруженного файла """
filename = "Park_changes.xlsx"

""" Получаем список файлов в директории, куда отправили файл Excel """
files = os.listdir(download_path)

""" Сортируем список файлов в директории по времени изменения """
sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)
latest_file = sorted_files[0]

""" Создаем новый путь загрузки, где соединяем путь загрузки, куда ранее отправили Excel + последний загруженный файл """
downloaded_file_path = os.path.join(download_path, latest_file)

""" Создаем новый путь,где будет в итоге лежать актуальный файл Excel и ждем 3 секунды """
renamed_file_path = os.path.join(download_path, filename)
time.sleep(3)

""" Переименовываем каталог, где лежит выгруженный файл """
os.replace(downloaded_file_path, renamed_file_path)
time.sleep(3)
# Конец скрипта по работе с браузером


# Выключение драйвера и завершение скрипта.
driver.quit()
print('SSP_AUTO.py - COMPLETE','\n','___________________________________________________________','\n')
