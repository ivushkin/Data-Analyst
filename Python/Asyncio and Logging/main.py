import logging
import logging.config


logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


import schedule as sch
import time
import datetime
from tools.async_subprocess import exec_subprocess
import asyncio


def run_script(*args):
    logger.info("Инициация выполнения скрипта по расписанию")
    try:
        asyncio.run(exec_subprocess(*args))
    except Exception as e:
        logger.error(e)
    finally:
        logger.info("Выполнение скрипта по расписанию завершено")

# ЕВРАЗ доли
sch.every().day.at("07:20").do(run_script,
                    ["python", "scripts\\ЕВРАЗ_доли.py"], 600)
# Евраз доли_выгрузка отдела аналитики для слайда по Евразу по новой схеме
sch.every().day.at("07:25").do(run_script,
                    ["python", "scripts\\Слайд_Евраз_Доли.py"], 600)

# ЕВРАЗ выполнение плана
sch.every().day.at("07:25").do(run_script,
                    ["python", "scripts\\ЕВРАЗ_выполнение_плана.py"], 600)
# Евраз доли_выгрузка отдела аналитики для слайда по Евразу по новой схеме
sch.every().day.at("07:10").do(run_script,
                    ["python", "scripts\\Слайд_Евраз_ВыполнениеПлана.py"], 600)

# Изменение доли комм.
sch.every().day.at("22:05").do(run_script,
					["python", "scripts\\изменение_доли_комм.py", "1"], 600)
sch.every().day.at("04:25").do(run_script,
					["python", "scripts\\изменение_доли_комм.py", "2"], 600)



# Изменение доли ЖД
sch.every().day.at("22:10").do(run_script,
					["python", "scripts\\изменение_доли_ЖД.py", "1"], 600)
sch.every().day.at("04:30").do(run_script,
					["python", "scripts\\изменение_доли_ЖД.py", "2"], 600)

# ВО и ГО 22:15
sch.every().day.at("22:15").do(run_script,
					["python", "scripts\\ВО_ГО.py", "1"], 600)
sch.every().day.at("04:35").do(run_script,
					["python", "scripts\\ВО_ГО.py", "2"], 600)

# ДКД сегменты
sch.every().day.at("22:20").do(run_script,
					["python", "scripts\\ДКД_сегменты.py", "1"], 600)
sch.every().day.at("04:40").do(run_script,
					["python", "scripts\\ДКД_сегменты.py", "2"], 600)

# Детализация за текущий месяц
sch.every().day.at("22:25").do(run_script,
					["python", "scripts\\детализация_тек.py", "1"], 600)
sch.every().day.at("04:45").do(run_script,
					["python", "scripts\\детализация_тек.py", "2"], 600)

# Детализация за предыдущий месяц
sch.every().day.at("22:30").do(run_script,
					["python", "scripts\\детализация_пред.py", "1"], 600)
sch.every().day.at("04:50").do(run_script,
					["python", "scripts\\детализация_пред.py", "2"], 600)

# Погрузка с ОХ
sch.every().day.at("22:35").do(run_script,
					["python", "scripts\\погрузка_с_ОХ.py", "1"], 600)
sch.every().day.at("04:55").do(run_script,
					["python", "scripts\\погрузка_с_ОХ.py", "2"], 600)

# Погрузка за ЖД сутки
sch.every().day.at("22:40").do(run_script,
					["python", "scripts\\погрузка_ЖД.py", "1"], 600)
sch.every().day.at("05:00").do(run_script,
					["python", "scripts\\погрузка_ЖД.py", "2"], 600)

# Штрафы
# sch.every().day.at("12:00").do(run_script,
#					["python", "scripts\\штрафы_v2.py", "0"], 600)

try:
    logger.info("Шедулер запущен")
    while True:
        sch.run_pending()
        time.sleep(1)
finally:
    logger.info("Работа шедулера завершена")