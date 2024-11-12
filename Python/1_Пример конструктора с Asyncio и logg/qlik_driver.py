from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
import os
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime
import time
import logging
from typing import Tuple, List


class ChromeQlikDriver(webdriver.Chrome):
    """Подкласс для работы с Qlik.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)


    def get_element_by_xpath(self, xpath: str, sleep: float = 0.5,
                             timeout: float = None) -> WebElement:
        """Поиск элемента по xpath.

        Аргументы:
        ----------
            xpath - xpath.
            sleep - задержка перед попыткой поиска элемента.
            timeout - таймаут.

        Возвращаемое значение:
        ----------------------
            Искомый элемент.
        """
        start_time = time.time()
        while True:
            if timeout and time.time() > (start_time + timeout):
                return None
            try:
                time.sleep(sleep)
                element = self.find_element(By.XPATH, xpath)
                self.logger.debug(f"get_element_by_xpath({xpath!r}) succeed")
                return element
            except NoSuchElementException:
                self.logger.warning(f"NoSuchElementException \"{xpath}\"")
                time.sleep(5)


    def click_element(self, element: WebElement, left: bool = True):
        """Клик по элементу.

        Аргументы:
        ----------
            element - элемент.
            left - левая кнопка, если True, правая - если False.
        """
        while True:
            try:
                if left:
                    element.click()
                else:
                    actions = ActionChains(self)
                    actions.context_click(element).perform()
                    actions.reset_actions()
                self.logger.debug(f"click_element({element}, {left}) succeed")
                break
            except ElementClickInterceptedException:
                self.logger.warning(
                    f"ElementClickIntercepredException \"{element}\"")
                time.sleep(5)


    def toggle_selections_list(self):
        """Нажатие кнопки открытия/закрытия окна выборок.
        """
        # xpath = "//span[@id='explore-selections-label']"
        xpath = "//button[@id='currentSelections.toggleGlobalSelections']"
        toggle_selection_menu_button = self.get_element_by_xpath(xpath)
        self.click_element(toggle_selection_menu_button)


    def open_selections_list(self):
        """Открытие окна выборок.

        Метод нужен для совместимости. Рекомендуется использовать
        toggle_selections_list.
        """
        self.toggle_selections_list()


    def close_selections_list(self):
        """Закрытие окна выборок.

        Метод нужен для совместимости. Рекомендуется использовать
        toggle_selections_list.
        """
        self.toggle_selections_list()


    def drop_all_selections(self):
        """Сброс всех фильтров.
         
        Работает только при открытом окне выборок.
        """
        # xpath = "//i[@class='lui-icon lui-icon--clear-selections']"
        xpath = "//button[@data-tid='current-selections-clear']"
        drop_selections_button = self.get_element_by_xpath(xpath)
        self.click_element(drop_selections_button)


    def drop_selection(self, field_name: str):
        """Сброс фильтра (только при открытом окне выборок).

        Аргументы:
        ----------
            field_name - наименование выборки.
        """
        xpath = (
            "//div[@ng-repeat='item in items' "
            f"and *//h1[@title='{field_name}']]"
            "//div[@title='Очистить выбор']"
        )
        drop_selection_button = self.get_element_by_xpath(xpath)
        self.click_element(drop_selection_button)

    @staticmethod
    def input_text(element: WebElement, text: str, sleep: float = 1):
        """Ввод текста.

        Аргументы:
        ----------
            element - элемент для ввода текста.
            text - текст.
            sleep - задержка после ввода текста.
        """
        element.clear()
        element.send_keys(text)
        element.send_keys(Keys.ENTER)
        time.sleep(sleep)


    def set_selection(self, field_name: str, filter_string: str):
        """Установить фильтр по выборке.

        Аргументы:
        ----------
            field_name - наименование выборки.
            filter_string - значение фильтрации.
        """
        # вводим наименование поля
        xpath = (
            "//input[@q-placeholder="
            "'GlobalSelections.FilterDimensionsAndFields']"
        )
        selection_search_input = self.get_element_by_xpath(xpath)
        self.input_text(selection_search_input, field_name)
        time.sleep(1)
        # нажимаем кнопку "Поиск"
        xpath = f"//h1[div[@text='{field_name}']]/a[@title='Поиск']"
        while True:
            try:
                selection_search_button = self.get_element_by_xpath(xpath)
                self.click_element(selection_search_button)
                break
            except StaleElementReferenceException as exp:
                self.logger.warning(
                    f"StaleElementReferenceException \"{xpath}\"")
                time.sleep(2)
        # вводим строку фильтра
        xpath = (
            "//div[@class='qv-listbox-search' and @aria-hidden='false']"
            "//input[@q-placeholder='Object.Listbox.Search']"
        )
        filter_input = self.get_element_by_xpath(xpath)
        self.input_text(filter_input, filter_string)


    def set_selections(self, selections=List[Tuple[str, str]]):    
        """Установить фильтры по выборкам. 

        Работает только при открытом окне выборок.
        
        Аргументы:
        ----------
            selections - список кортежей, состоящих из двух элементов:
            наименования выборки и значения фильтрации
        """
        for field_name, filter_string in selections:
            self.logger.debug(f"{field_name!r}, {filter_string!r}")
            self.set_selection(field_name, filter_string)


    def set_filter(self, selections=List[Tuple[str, str]],
                   drop_selections: bool = True):
        """Открыть окно выборок, сбросить все фильтры, установить новые
        фильтры по выборкам, закрыть окно выборок.

        Аргументы:
        ----------
            selections - список кортежей, состоящих из двух элементов:
            наименования выборки и значения фильтрации.
            drop_selections - сбрасываем все фильтры, если True
        """
        self.toggle_selections_list()
        if drop_selections:
            self.drop_all_selections()
        self.set_selections(selections)
        self.toggle_selections_list()


    def download_excel(self, table_name: str, index: int = 1):
        """Загрузка данных в Excel.

        Аргументы:
        ----------
            table_name - заголовок загружаемой таблицы.
            index - порядковый номер загружаемой таблицы (если заголовок
            не уникальный).
        """
        # взаимодействуем с меню экспорта данных
        # правый клик по объекту
        xpath = (
            f"(//h1[@title='{table_name}'])[{index}]"
            "//ancestor::div[@class='object-wrapper']"
        )
        table_wrapper = self.get_element_by_xpath(xpath)
        self.click_element(table_wrapper, left=False)
        # левый клик по кнопке "Загрузить как..."
        xpath = "//span[@tid='export-group']"
        download_menu_button = self.get_element_by_xpath(xpath)
        self.click_element(download_menu_button)
        # левый клик по кнопке "Данные"
        xpath = "//span[@tid='export']"
        download_button = self.get_element_by_xpath(xpath)
        self.click_element(download_button)
        # необязательная кнопка, диалог отображается только при загрузке
        # больших таблиц
        xpath = "//button[@tid='table-export']"
        table_download_button = self.get_element_by_xpath(xpath, timeout=3)
        if table_download_button:
            self.click_element(table_download_button)
        xpath = "//a[@class='export-url']"
        download_link = self.get_element_by_xpath(xpath)
        self.click_element(download_link)
        # ожидаем окончания загрузки
        time.sleep(10) 
        # закрываем окно после загрузки
        xpath = "//button[@q-translation='Common.Close']"
        close_dialog_button = self.get_element_by_xpath(xpath)
        self.click_element(close_dialog_button)


    def apply_bookmark(self, bookmark_name: str):
        """Применить закладку.

        Аргументы:
        ----------
            bookmark_name - наименование закладки.
        """
        xpath = f"//button[@title='Закладки']"
        bookmark_menu_button = self.get_element_by_xpath(xpath)
        self.click_element(bookmark_menu_button)
        xpath = f"//span[@text='{bookmark_name}']"
        bookmark_button = self.get_element_by_xpath(xpath)
        self.click_element(bookmark_button)


def rename_last_file(folder: str, filename: str):
    """Переименование файла в целевой папке.

    Аргументы:
    ----------
        folder - папка для загрузки.
        filename - новое имя файла.
    """
    key = lambda file: os.path.getmtime(os.path.join(folder, file))
    files = os.listdir(folder)
    sorted_files = sorted(files, key=key, reverse=True)
    last_filename = sorted_files[0]
    original_path = os.path.join(folder, last_filename)
    new_path = os.path.join(folder, filename)
    os.replace(original_path, new_path)
    time.sleep(1)


def get_dates(date: datetime | None = None) -> Tuple[datetime]:
    """Возвращает границы периодов для отчетной даты.

    Аргументы:
    ----------
        date - отчетная дата.

    Возвращаемое значение:
    ----------------------
        Кортеж из четырех элементов: начало периода в текущем месяце,
        конец отчетного периода в текущем месяце, начало периода в
        предыдущем месяце, конец отчетного периода в предыдущем месяце.
    """
    if not date:
        date = datetime.today()
    current_month_de = date
    current_month_db = current_month_de.replace(day=1)
    end_of_month = current_month_db + relativedelta(months=1, days=-1)
    previous_month_db = current_month_db - relativedelta(months=1)
    if current_month_de == end_of_month:
        previous_month_de = previous_month_db + relativedelta(months=1,
                                                              days=-1)
    else:
        previous_month_de = current_month_de - relativedelta(months=1)
    return (current_month_db, current_month_de,
            previous_month_db, previous_month_de)


def get_filter_string_for_qlik(date: datetime | None = None,
                               mode: str = "dates") -> str:
    """Возвращает строку для фильтрации в Qlik для отчетной даты.

    Аргументы:
    ----------
        date - отчетная дата.
        mode - режим работы: "dates" - полные даты, "years" - годы,
        "months" - месяцы, "months_with_years" - месяцы с годами.

    Возвращаемое значение:
    ----------------------
        Строка для фильтра.
    """
    (current_month_db, current_month_de,
     previous_month_db, previous_month_de) = get_dates(date)
    if mode == 'dates':
        filter_string = (
            f'(>={current_month_db.strftime("%d.%m.%Y")}'
            f'<={current_month_de.strftime("%d.%m.%Y")}|'
            f'>={previous_month_db.strftime("%d.%m.%Y")}'
            f'<={previous_month_de.strftime("%d.%m.%Y")})'
        )
    elif mode == 'months':
        months = {
            current_month_db.strftime("%B"),
            current_month_de.strftime("%B"),
            previous_month_db.strftime("%B"),
            previous_month_de.strftime("%B")
        }
        filter_string = f'({"|".join(list(months))})'
    elif mode == 'months_with_years':
        months = {
            current_month_db.strftime("%B.%y"),
            current_month_de.strftime("%B.%y"),
            previous_month_db.strftime("%B.%y"),
            previous_month_de.strftime("%B.%y")
        }
        filter_string = f'({"|".join(list(months))})'
    elif mode == 'years':
        years = {
            current_month_db.year,
            current_month_de.year,
            previous_month_db.year,
            previous_month_de.year
        }
        filter_string = f'({"|".join(list(map(str, years)))})'
    return filter_string
