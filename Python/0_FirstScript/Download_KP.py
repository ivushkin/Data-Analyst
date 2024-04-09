import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Опции для работы с сайтом
chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': "\\\\Папка\\buffer\\",
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True,
})
path = Service(executable_path='\\\\папка\\Сhromedriver_122\\chromedriver.exe')
driver = webdriver.Chrome(service=path, options=chrome_options)
driver.maximize_window()

# Опции для правого клика
action = ActionChains(driver)

# Формирование переменной с текущей датой
date_name = datetime.today()
date_format = date_name.strftime('%d.%m.%Y')


# Функция для скачивания и переименования файла
def download_naming(rps):

    # Определение названия скачанного файла в директории загрузки
    src = Path('//папка/buffer/')
    for file in src.iterdir():
        src_name = file.name

    # Копирование файла в Архив с присвоением названия файлу в виде даты
    src = Path('//папка/buffer/' + str(
            src_name))
    dest = Path('//папка/downloaded_files/' + str(
            rps) + str(date_format) + '.xlsx')
    dest.write_bytes(src.read_bytes())

    # Очистка папки загрузки
    src.unlink()



# Открытие браузера и навигация по сайту
driver.get("https://ссылка на дашборд")
time.sleep(10)

# Активация на таблицу с коэффициентом прикрытия (по умолчанию при открытии приложения в Qlik зажат фильтр по полувагонам)
# Навигация к необходимому блоку, активация контекстного меню и навигация по нему

# убираем ошибку появления 7 пунктов в контекстном пункте меню в клике путем перевода курсора на активную таблицу
step = driver.find_element("xpath",'/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[8]/div[1]/div/div[1]/article/div[1]/div/div/div/div[2]/div[1]/div/table/tbody/tr[8]/td[1]/div/div')
action.context_click(step).perform()
time.sleep(5)
# основной ход выгрузки
step = driver.find_element("xpath",'/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[8]/div[1]/div/div[1]/article/div[1]/div/div/div/div[2]/div[1]/div/table/tbody/tr[12]/td[14]')
action.context_click(step).perform()
time.sleep(5)
step = driver.find_element("xpath", '/html/body/div[9]/div/div/div/ng-transclude/ul/li[6]/span')
step.click()
time.sleep(5)
step = driver.find_element("xpath", '/html/body/div[9]/div/div/div/ng-transclude/ul/li[4]/span')
step.click()
time.sleep(5)

# Загрузка файла
step = driver.find_element("xpath", '/html/body/div[9]/div/div/div[2]/div[3]/button[2]')
step.click()
time.sleep(5)
step = driver.find_element("link text", 'Щелкните, чтобы загрузить файл с данными.')
step.click()
time.sleep(5)


#Загрузка файла по ПВ
download_naming('ПВ_')

# Закрытие загрузочного окна
step = driver.find_element("xpath", '/html/body/div[9]/div/div/div[2]/div/div[3]/button')
step.click()
time.sleep(5)

# Закрытие браузера
driver.quit()

