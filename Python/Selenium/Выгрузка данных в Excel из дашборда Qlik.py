# загрузка библиотек
import os
import time
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import Month_today


# настройка браузера и настройка пути, где будут лежать загрузочные файлы
chrome_options = Options()
# download_directory = '\\\\pgk.rzd\\workgroups\\БД ЛП\\-ОТДЕЛ УЧЕТА-\\001 БД ЛПУ (S&М)\\08 Qlik\\01_ВО_и_ГО_пв-кр'
download_directory = "\\\\pgk.rzd\\workgroups\\БД ЛП\\ЛПА (отдел аналитической работы)\\001_ШАБЛОНЫ\\103 ЕВРАЗ автоматизация слайда\\Евраз автомат нов\\TRY"
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': download_directory,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})


# Указываем путь до папки с драйвером для хрома, вызываем метод ActionChains для автоматизации движения мыши и указываем путь до дашборда Qlik откуда берем данные
driver = webdriver.Chrome('\\\\pgk.rzd\\workgroups\\БД ЛП\\ЛПА (отдел аналитической работы)\\6. НАРАБОТКИ PYTHON\\Инструментарий Python\\Chromedriver\\chromedriver.exe', options=chrome_options)
actions = ActionChains(driver)
url = 'https://bi.pgk.ru/self/sense/app/5828858d-2ad8-4922-b63a-44cab6dd0db0/sheet/df2f7c91-bce7-44b7-9994-7bd765fb16e6/state/analysis'


# Функция, которая завершит выполнение программы через 2 минуты
Month_today.killer_low(driver)


# Перенаправляем страницу в переменной URL в драйвер хрома, расширяем окно браузера до максимального, ждем 1 секунду
driver.get(url)
driver.maximize_window()
time.sleep(1)

# При запуске Qlik срабатывает динамическая закладка на актуальный год, убираем год. Повторять пока не будет найден фильтр по году и не будет нажата кнопка закрытия, иначе ошибка.
# ________________________________________________Отжать год_______________________________
while True:
    try:
        klik_year = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[4]/div[1]/div/div/div[1]/div/div[2]")
        time.sleep(1)
        klik_year.click()
        print('Фильтр по году сброшен')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)


# _Найти дорогу отправления и назначения и ввести данные
# _________________DOR_OTPR__________________|
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[8]/div[1]/div/div[1]/article/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[1]/th[1]/div/div[2]/div")
        time.sleep(10)
        element.click()
        print('Находим фильтр Дорога отправления и нажимаем на него')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)

"""В строке ввода значений в фильтре Дорога отправления нажимаем левой кнопкой мыши для установки курсора, передаем текст ЗСБ, имитируем нажатие клавиши Enter"""
while True:
    try:
        element1 = driver.find_element_by_xpath("/html/body/div[10]/div/div/div/ng-transclude/div/div[3]/div/article/div[1]/div/div/div/div[1]/div/input")
        element1.click()
        print('Фильтр найден, отправлю в фильтр значение дороги')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(3)
element1.send_keys("ЗСБ")
time.sleep(3)
element1.send_keys(Keys.ENTER)
actions.perform()
time.sleep(1)


# Выставляем дороги по назначению аналогично предыдущим шагам|
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[8]/div[1]/div/div[1]/article/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[1]/th[2]/div/div[2]/div")
        time.sleep(1)
        element.click()
        print('Нашел фильтр Дороги по назначению')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)

"""открываем поле ввода в фильтре дорога назначения,отправляем выбранные дороги, имитируем нажатие кнопки Enter и применяем фильтр"""
while True:
    try:
        element1 = driver.find_element_by_xpath("/html/body/div[10]/div/div/div/ng-transclude/div/div[3]/div/article/div[1]/div/div/div/div[1]/div/input")
        element1.click()
        print('Ввел дороги назначения в фильтр')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(3)
element1.send_keys("ВСБ ДВС ЗАБ КРС")
time.sleep(3)
element1.send_keys(Keys.ENTER)
actions.perform()
time.sleep(1)


# Переходим на основной лист дашборда путем перещелкивания листов
while True:
    try:
        element_dop4 = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div/div[2]/button[1]")
        element_dop4.click()
        print('Нажал на кнопку перехода на другой лист')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(10)


# Находим элемент на странице и нажимаем на него правой кнопкой мыши
while True:
    try:
        element5 = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[6]/div[1]/div/div[1]/article/div[1]/div/div/div")
        actions = ActionChains(driver)
        actions.context_click(element5).perform()
        print('Нажимаю правой кнопкой мыши для вызова контекстного меню')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(10)

"""Нажимаю кнопку Загрузить как"""
while True:
    try:
        element6 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/ul/li[6]")
        element6.click()
        print('Нажал кнопку Загрузить как')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""Повторять пока не будет выполнено, поиск элемента <Данные> в контекстном меню Загрузить как"""
while True:
    try:
        element7 = driver.find_element_by_xpath("//span[@class='lui-list__text ng-binding' and @title='Data' and @tid='export']")
        element7.click()
        print('Нажал кнопку Загрузить данные-Данные')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(2)

"""Повторять пока не будет выполнено, поиск и нажатие на ссылку Click here to download your data file для старта выгрузки Excel-файла"""
while True:
    try:
        element8 = driver.find_element_by_link_text('Click here to download your data file.')
        element8.click()
        print('Старт загрузки Excel-файла')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(10)


# загружаем файл, потом находим самый последний загруженный файл и переименовываем его в папке.
"""инициализируем значение переменной из пути загрузки, который обозначен в начале и присваиваем фиксированное имя загруженного файла """
download_path = download_directory
filename = "QLIK все клиенты доля все ПВ на Восток.xlsx"


"""Получаем список файлов в директории загрузки,сортируем по дате последнего изменения, получаем самый последний файл"""
files = os.listdir(download_path)
sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)
latest_file = sorted_files[0]
downloaded_file_path = os.path.join(download_path, latest_file)

"""Формируем путь к загруженному файлу,переименовываем загруженный файл и выволдим сообщение об окончании работы блока """
renamed_file_path = os.path.join(download_path, filename)
os.replace(downloaded_file_path, renamed_file_path)
print('QLIK все клиенты доля все ПВ на Восток - COMPLETE','\n')
time.sleep(3)


# Начинаем загружать вторую таблицу по Евразу с добавлением дополнительного фильтра по ОХ:75т
# Через actions энтер засылается не туда, ввиду чего мы дополнительно добавляем переменную = находим поле ввода данных и туда нажимаем энтер
# Tut mi zakrivaem okoshechko zagruzki1
"""Повторять пока не сработает закрытие окна загрузки из предыдущего шага, закрытие происходит путем нажатия кнопки"""
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[9]/div/div/div[2]/div/div[3]/button")
        time.sleep(1)
        element.click()
        print('Закрываем окно загрузки')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(1)

"""Повторять пока не сработает выбор фильтра ОХ 75т. на листе, далее кликаем левой кнопкой мыши"""
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[11]/div[1]/div/div[1]/article/div[1]/div/div/qv-filterpane/div/div/div/article/div[1]/header/h1/a")
        time.sleep(1)
        element.click()
        print('Выбран фильтр ОХ')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)

"""В окно ввода фильтра ОХ вводим 75, затем применяем фильтр"""
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[11]/div[1]/div/div[1]/article/div[1]/div/div/qv-filterpane/div/div/div/article/div[1]/div/div/div/div[1]/div/input")
        time.sleep(1)
        element.click()
        element.send_keys('75')
        time.sleep(4)
        element500 = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[11]/div[1]/div/div[1]/article/div[1]/div/div/qv-filterpane/div/div/div/article/div[1]/div/div/div/div[2]/div[1]/div/ul/li[1]')
        element500.click()
        print('Применяем фильтр по ОХ на 75т')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)


"""Ищем элемент на листе Qlik и нажимаем правой кнопкой мыши для вызова контекстного меню"""
while True:
    try:
        element5 = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[6]/div[1]/div/div[1]/article/div[1]/div/div/div")
        actions = ActionChains(driver)
        actions.context_click(element5).perform()
        print('Нажал правой кнопкой мыши для вызова контекстного меню')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""В контекстном меню графика ищем кнопку "Загрузить как" и нажимаем на нее левой кнопкой мыши, цикл работает пока не нашли элемент"""
while True:
    try:
        element6 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/ul/li[6]")
        element6.click()
        print('Нажал кнопку <Загрузить как>')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""Повторять пока не будет выполнено, поиск элемента <Данные> в контекстном меню Загрузить как"""
while True:
    try:
        element7 = driver.find_element_by_xpath("//span[@class='lui-list__text ng-binding' and @title='Data' and @tid='export']")
        element7.click()
        print('Нажал кнопку Загрузить данные-Данные')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(2)

"""Повторять пока не будет выполнено, поиск и нажатие на ссылку Click here to download your data file для старта выгрузки Excel-файла"""
while True:
    try:
        element8 = driver.find_element_by_link_text('Click here to download your data file.')
        element8.click()
        print('Старт загрузки Excel-файла')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(10)


# загружаем файл, потом находим самый последний загруженный файл и переименовываем его в папке.
"""инициализируем значение переменной из пути загрузки, который обозначен в начале и присваиваем фиксированное имя загруженного файла """
download_path = download_directory
filename = "QLIK все клиенты доля 75т на Восток.xlsx"


"""Получаем список файлов в директории загрузки,сортируем по дате последнего изменения, получаем самый последний файл"""
files = os.listdir(download_path)
sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)
latest_file = sorted_files[0]
downloaded_file_path = os.path.join(download_path, latest_file)


"""Формируем путь к загруженному файлу,переименовываем загруженный файл и выволдим сообщение об окончании работы блока """
renamed_file_path = os.path.join(download_path, filename)
os.replace(downloaded_file_path, renamed_file_path)
print('QLIK все клиенты доля 75т на Восток - COMPLETE','\n')
time.sleep(3)


# Закрываем окно загрузки
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[9]/div/div/div[2]/div/div[3]/button")
        time.sleep(1)
        element.click()
        print('Закрыл окно загрузки')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(1)


# Идем на 2 слайда вперед
while True:
    try:
        element1 = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div/div[2]/button[2]")
        element1.click()
        time.sleep(3)
        element1.click()
        print('Перехожу на 2 листа вперед в Qlik')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(2)


"""Выбираем Евразхолдинг в грузополучателе"""
while True:
    try:
        element5 = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[12]/div[1]/div/div[1]/article/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[1]/th[1]/div/div/div")
        element5.click()
        print('Нашел фильтр грузополучателя на листе')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)


""" Нажимаем на поле ввода левой кнопкой мыши, отправляем Евразхолдинг и применяем фильтр путем имитирования нажатия Enter"""
while True:
    try:
        element56 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/div/div[3]/div/article/div[1]/div/div/div/div[1]/div/input")
        element56.click()
        print('Открыл окно ввода в фильтре')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(3)
element56.send_keys("*ЕВРАЗХОЛДИНГ*")
time.sleep(3)
element56.send_keys(Keys.ENTER)
time.sleep(3)

"""нажимаем на кнопку применить фильтр"""
while True:
    try:
        element56 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/div/div[2]/div/ul/li[5]/button")
        element56.click()
        print('Применил фильтр')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(3)

# Идем на 2 слайда назад
while True:
    try:
        element100 = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[2]/div/div[2]/button[1]")
        element100.click()
        time.sleep(3)
        element100.click()
        print('Нажал на переход на 2 слайда назад')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)


# Через actions энтер засылается не туда, ввиду чего мы дополнительно добавляем переменную = находим поле ввода данных и туда нажимаем энтер
while True:
    try:
        element5 = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[6]/div[1]/div/div[1]/article/div[1]/div/div/div")
        actions = ActionChains(driver)
        actions.context_click(element5).perform()
        print('Нашел элемент и нажал правой кнопкой мыши')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""В контекстном меню графика ищем кнопку "Загрузить как" и нажимаем на нее левой кнопкой мыши, цикл работает пока не нашли элемент"""
while True:
    try:
        element6 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/ul/li[6]")
        element6.click()
        print('Нажал кнопку <Загрузить как>')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""Повторять пока не будет выполнено, поиск элемента <Данные> в контекстном меню Загрузить как"""
while True:
    try:
        element7 = driver.find_element_by_xpath("//span[@class='lui-list__text ng-binding' and @title='Data' and @tid='export']")
        element7.click()
        print('Нажал кнопку Загрузить данные-Данные')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(2)

"""Повторять пока не будет выполнено, поиск и нажатие на ссылку Click here to download your data file для старта выгрузки Excel-файла"""
while True:
    try:
        element8 = driver.find_element_by_link_text('Click here to download your data file.')
        element8.click()
        print('Старт загрузки Excel-файла')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(10)

# загружаем файл, потом находим самый последний загруженный файл и переименовываем его в папке.
"""инициализируем значение переменной из пути загрузки, который обозначен в начале и присваиваем фиксированное имя загруженного файла """
download_path = download_directory
filename = "QLIK ЕВРАЗ доля 75т на Восток.xlsx"


"""Получаем список файлов в директории загрузки,сортируем по дате последнего изменения, получаем самый последний файл"""
files = os.listdir(download_path)
sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)
latest_file = sorted_files[0]
downloaded_file_path = os.path.join(download_path, latest_file)


"""Формируем путь к загруженному файлу,переименовываем загруженный файл и выволдим сообщение об окончании работы блока """
renamed_file_path = os.path.join(download_path, filename)
os.replace(downloaded_file_path, renamed_file_path)
print('QLIK ЕВРАЗ доля 75т на Восток - COMPLETE','\n')
time.sleep(3)


"""закрываем окно загрузки"""
while True:
    try:
        element = driver.find_element_by_xpath("/html/body/div[9]/div/div/div[2]/div/div[3]/button")
        time.sleep(1)
        element.click()
        print('Закрыл окно загрузки')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)
time.sleep(1)

"""Убираем фильтр с инновационного парка путем нажатия левой кнопкой мыши на кнопку закрытия"""
while True:
    try:
        element1 = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[4]/div[5]/div/div/div[1]/div/div[2]/button")
        element1.click()
        print('Сбросил фильтр по ОХ')
        time.sleep(1)
        break
    except NoSuchElementException or ElementClickInterceptedException:
        time.sleep(1)

# Начинаем выгружать данные
# Через actions энтер засылается не туда, ввиду чего мы дополнительно добавляем переменную = находим поле ввода данных и туда нажимаем энтер
while True:
    try:
        element5 = driver.find_element_by_xpath("/html/body/div[4]/div[4]/div/div[2]/div/div/div[3]/div/div/div[3]/div[2]/div[6]/div[1]/div/div[1]/article/div[1]/div/div/div")
        actions = ActionChains(driver)
        actions.context_click(element5).perform()
        print('Нажал правой кнопкой мыши по элементу')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)


"""В контекстном меню графика ищем кнопку "Загрузить как" и нажимаем на нее левой кнопкой мыши, цикл работает пока не нашли элемент"""
while True:
    try:
        element6 = driver.find_element_by_xpath("/html/body/div[9]/div/div/div/ng-transclude/ul/li[6]")
        element6.click()
        print('Нажал кнопку <Загрузить как>')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(1)

"""Повторять пока не будет выполнено, поиск элемента <Данные> в контекстном меню Загрузить как"""
while True:
    try:
        element7 = driver.find_element_by_xpath("//span[@class='lui-list__text ng-binding' and @title='Data' and @tid='export']")
        element7.click()
        print('Нажал кнопку Загрузить данные-Данные')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(2)

"""Повторять пока не будет выполнено, поиск и нажатие на ссылку Click here to download your data file для старта выгрузки Excel-файла"""
while True:
    try:
        element8 = driver.find_element_by_link_text('Click here to download your data file.')
        element8.click()
        print('Старт загрузки Excel-файла')
        time.sleep(1)
        break
    except NoSuchElementException:
        time.sleep(1)
time.sleep(10)


# загружаем файл, потом находим самый последний загруженный файл и переименовываем его в папке.
"""инициализируем значение переменной из пути загрузки, который обозначен в начале и присваиваем фиксированное имя загруженного файла """
download_path = download_directory
filename = "QLIK ЕВРАЗ доля все ПВ на Восток.xlsx"


"""Получаем список файлов в директории загрузки,сортируем по дате последнего изменения, получаем самый последний файл"""
files = os.listdir(download_path)
sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)
latest_file = sorted_files[0]
downloaded_file_path = os.path.join(download_path, latest_file)

"""Формируем путь к загруженному файлу,переименовываем загруженный файл и выволдим сообщение об окончании работы блока """
renamed_file_path = os.path.join(download_path, filename)
os.replace(downloaded_file_path, renamed_file_path)
print('QLIK ЕВРАЗ доля все ПВ на Восток - COMPLETE','\n')
time.sleep(3)


# Выключение драйвера и завершение скрипта.
driver.quit()
print('Loev_Dmitrii_dol9_pogruzki.py - COMPLETE','\n','___________________________________________________________','\n')
