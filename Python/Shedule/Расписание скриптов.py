
import schedule as sch
import time
import subprocess
import datetime

print('Запущено '+str(datetime.datetime.now().strftime('%d-%m-%y/%H:%M')))


def run_script(choose):
    # process = subprocess.Popen(['C:\\Program Files\\JetBrains\\alarm\\Scripts\\python.exe', choose])
    subprocess.Popen(['python', choose])


def run_script2(choose):
    subprocess.Popen(['C:\\Program Files\\JetBrains\\alarm\\Scripts\\python.exe', choose])
    #
    # if process.poll() is None:
    #     process.terminate()
    #     os.system("taskkill /IM chromedriver.exe /F")
    #     os.system("taskkill /IM chrome.exe /F")
    #     print(str(datetime.datetime.now()))

# _________Обновление данных для справки по погрузке на Восток и Евразу____________________________
# _________Директория обновленных данных: W:\БД ЛП\ЛПА (отдел аналитической работы)\001_ШАБЛОНЫ\103 ЕВРАЗ автоматизация слайда\Евраз автомат нов\TRY ________________

# Opisanie Dmitriy 6:30
sch.every().day.at('06:30').do(run_script, choose='SSP_AUTO.py')

# Opisanie Dmitriy 6:35
sch.every().day.at('06:35').do(run_script, choose='SSP_AUTO2.py')

# Opisanie Dmitriy 6:40
sch.every().day.at('06:40').do(run_script, choose='Loev_Dmitrii_ALL_PV_PLAN_VOSTOK.py')

# Opisanie Dmitriy 07:15
sch.every().day.at('07:15').do(run_script, choose='Loev_Dmitrii_dol9_pogruzki.py')

# Opisanie Dmitriy 07:25
sch.every().day.at('07:25').do(run_script, choose='Loev_Dmitrii_dol9_pogruzki_2.py')

# Opisanie Dmitriy 08:20
sch.every().day.at('08:20').do(run_script, choose='Loev_Dmitrii_ktk.py')


# _________Обновление приложения-презентации____________________________
# sch.every().day.at('08:00').do(run_script, choose ='pptx_ex.py')

# _________Обновление данных для ЛПА, _______________________________________________________________________
# _________Директория обновленных данных: W:\БД ЛП\ЛПА (отдел аналитической работы)\001_ШАБЛОНЫ\111 Автоматический расчёт эффекта рынка________________

# Opisanie Alexandra 03:00
sch.every().day.at('03:00').do(run_script, choose='AUKC_MARKT_EFFECT_PV.py')
# Opisanie Alexandra 03:10
sch.every().day.at('03:10').do(run_script2, choose='xlsx_test_PV.py')
# Opisanie Arina 03:20
sch.every().day.at('03:20').do(run_script, choose='AUKC_MARKT_EFFECT_KR.py')
# Opisanie Alexandra 03:30
sch.every().day.at('03:30').do(run_script2, choose='xlsx_test_KR.py')


# ____Обновление данных для ЛПА, _____________________________________________________________
# ____Директория обновленных данных: W:\БД ЛП\ЛПА (отдел аналитической работы)\6. НАРАБОТКИ PYTHON\Роботы\Coefficient_Prikrytia\downloaded_files________________
sch.every().day.at('08:40').do(run_script, choose='Download_Koef_Prikrytia.py')


# ____Обновление данных для ЛПА Слайд по ситуации на ДВС ______________________________________
# ____Директория обновленных данных: \\pgk.rzd\workgroups\БД ЛП\ЛПА (отдел аналитической работы)\6. НАРАБОТКИ PYTHON\Роботы\Slide_maker_dvs_uzli\slides_archive_new
sch.every().day.at('07:00').do(run_script, choose='Slide_maker_1_0.py')


# ____Обновление данных для ЛПА Слайд по выполнению погрузки КР на Восток ____
# ____Директория обновленных данных: \\БД ЛП\ЛПА (отдел аналитической работы)\6. НАРАБОТКИ PYTHON\Роботы\Slide_maker_KR_Vostok\slides_archive_new_
sch.every().day.at('07:05').do(run_script, choose='Slide_maker_KR_Vostok.py')


while True:
        sch.run_pending()
        time.sleep(1)


# _________Обновление 1 раз в месяц____________________________ПОКА ТЕСТИМ___
# if datetime.datetime.now().day == 13: # тот же самый во-го только с выбором даты по полю отчет дат сутки
#     sch.every().day.at('22:50').do(run_script, choose ='qlik_v2_eng_month.py')
# else:
#     pass
# if datetime.datetime.now().day == 13:  # тот же самый во-го только с выбором даты по полю отчет дат сутки
#     sch.every().day.at('22:00').do(run_script, choose='Cargo_part_Disp_LPU_2_Month.py')
# else:
#     pass
#
