from datetime import datetime
import locale
from datetime import timedelta
import threading
import time
import os


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

date = datetime.today()
today_month = date.strftime("%B")
vchera_dirt = date - timedelta(1)
pozavchera_dirt = date - timedelta(2)
pozavchera_month_text_dirt = pozavchera_dirt.strftime("%B")
vchera_month_text_dirt = vchera_dirt.strftime("%B")
segodnyaa = datetime.today()
year = segodnyaa.year
month = segodnyaa.month
mesjac2 = date.strftime("%m")
segodnja_plus_odin = date.day + 1
starii_mesjac_dirt = date - timedelta(segodnja_plus_odin)
starii_mesjac = starii_mesjac_dirt.strftime("%B")
starii_mesjac_dirt2 = starii_mesjac_dirt.replace(day=1) - timedelta(days=1)
starii_mesjac_dirt3 = starii_mesjac_dirt2.replace(day=1) - timedelta(days=1)
summ_3_last_month = starii_mesjac_dirt.day + starii_mesjac_dirt2.day + starii_mesjac_dirt3.day
three_month_ago = date - timedelta(summ_3_last_month)
one_month_ago_and_one_day = date - timedelta(starii_mesjac_dirt.day) - timedelta(1)

# грязные переменные для 4 утра
segodnja_plus_dva = date.day + 2
starii_mesjac_dirt_minus_den = date - timedelta(segodnja_plus_dva)
starii_mesjac_dirt_pozavchera = date - timedelta(segodnja_plus_dva)
starii_mesjac_minus_den = starii_mesjac_dirt_minus_den.strftime("%B")
starii_mesjac_pozavchera = starii_mesjac_dirt_pozavchera.strftime("%B")
vchera_dirt_minus_odin = date - timedelta(2)
vchera_month_text_dirt_minus_odin = vchera_dirt_minus_odin.strftime("%B")

#yesterday_month3 = yesterday_month2.strftime("%B")

#___________________В_ПОЛЬЗОВАНИЕ____________________
segodnya = segodnyaa.strftime("%Y-%m-%d")
segodnya_tochki = segodnyaa.strftime("%d.%m.%Y")
vchera_tochki = vchera_dirt.strftime("%d.%m.%Y")
mesjac_vchera = vchera_dirt.strftime("%m")
mesjac_vchera_text = vchera_dirt.strftime("%B")
pozavchera_tochki = pozavchera_dirt.strftime("%d.%m.%Y")
vchera = vchera_dirt.strftime("%d.%m.%Y")
vchera_tire = vchera_dirt.strftime("%Y-%m-%d")
mesjac = today_month[:3]
pozavchera_month_text = pozavchera_month_text_dirt[:3]
vchera_month_text = vchera_month_text_dirt[:3]       # в мае не работает конструкция, так как в клике указано мая, скрипт кидает май. vchera_month_text = vchera_month_text_dirt[:3]
def get_word():                                      # конструкция на май
    return "мая"
start_mesjac = ('01'+'.'+str(mesjac2)+'.'+str(year))
proshliy_mesjac_tochki = ('01'+'.'+str(mesjac_vchera)+'.'+str(year))
proshlii_mesjac = starii_mesjac[:3]
pozavchera_day = date.day -2
vchera_day = date.day -1
segodnya_day = date.day
zavtra_day = date.day +1
vchera_year = vchera_dirt.strftime("%Y")
# skorosti = vchera_month_text + '. ' + vchera_year

dict_months = {'Январь': 'янв', 'Февраль': 'февр', 'Март': 'мар', 'Апрель': 'апр', 'Май': 'мая', 'Июнь': 'июн', 'Июль': 'июл', 'Август': 'авг', 'Сентябрь': 'сент', 'Октябрь': 'окт', 'Ноябрь': 'нояб', 'Декабрь': 'дек'}
dict_months_values = dict_months.values()
vchera_month_text_small = dict_months_values.mapping[vchera_month_text_dirt]
skorosti = vchera_month_text_small + '. '+ vchera_year #в мае нужно убирать точку, так как в фильтре клика в мае ее нет. skorosti = vchera_month_text_small + '. '+ vchera_year

year_three_month_ago = three_month_ago.strftime("%Y")
year_one_month_and_day_ago = one_month_ago_and_one_day.strftime("%Y")

#Переменные для 4 утра
proshlii_mesjac_minus_den = starii_mesjac_minus_den[:3]
proshlii_mesjac_pozavchera = starii_mesjac_pozavchera[:3]
vchera_month_text_minus_den = vchera_month_text_dirt_minus_odin[:3]
mesjac_minus_odin = mesjac_vchera_text[:3]
pozavchera_day_minus_odin = date.day -3
mesjac_minus_odin_and_year_text = mesjac_vchera_text+'.'+vchera_year[2:]
mesjac_minus_mesjac_and_year_text = starii_mesjac_minus_den+'.'+ year_one_month_and_day_ago[2:]

print(mesjac_minus_mesjac_and_year_text)


#___________________________2___ФУНКЦИИ__ОБРУБАЮЩИЕ ВЫПОЛНЕНИЕ В ЗАВИСИМОСТИ ОТ ВРЕМЕНИ ВЫПОЛНЕНИЯ СКРИПТА____________
def killer_low(driver):
    # Функция, которая завершит выполнение программы через 6 минуты
    def timeout():
        time.sleep(360)  # Ждем 360 секунд (6 минуты)
        print("Прошло 6 минуты. Прерывание выполнения.")
        driver.quit()
        os._exit(0)  # Завершаем выполнение программы


    # Создаем таймер для завершения программы
    timer = threading.Thread(target=timeout)
    timer.daemon = True  # Устанавливаем поток как демон, чтобы он завершился, если главный поток завершится
    timer.start()

def killer_high(driver):
    # Функция, которая завершит выполнение программы через 2 минуты
    def timeout():
        time.sleep(720)  # Ждем 720 секунд (12 минут)
        print("Прошло 12 минут. Прерывание выполнения.")
        driver.quit()
        os._exit(0)  # Завершаем выполнение программы


    # Создаем таймер для завершения программы
    timer = threading.Thread(target=timeout)
    timer.start()

#_____________________________ПОКВАРТАЛЬНАЯ РАЗБИВКА_________________


month_to_quarter = {'янв': 'окт.-дек. ', 'фев': 'окт.-дек. ', 'мар': 'окт.-дек. ', 'апр': 'янв.-мар. ', 'май': 'янв.-мар. ', 'июн': 'янв.-мар. ',
                    'июл': 'апр.-июн. ', 'авг': 'апр.-июн. ', 'сен': 'апр.-июн. ', 'окт': 'июл.-сент. ', 'ноя': 'июл.-сент. ', 'дек': 'июл.-сент. '}

current_quarter = month_to_quarter.get(vchera_month_text.lower())

print(year_one_month_and_day_ago)
print(year_three_month_ago)

print('-----')
print(vchera_month_text)
print(vchera_year)
print(current_quarter+year_three_month_ago)