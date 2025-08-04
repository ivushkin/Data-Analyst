import asyncio
from asyncio.subprocess import Process
from asyncio import StreamReader, StreamWriter, Event
from asyncio import TimeoutError
from typing import List
import logging
import os


logger = logging.getLogger(__name__)
dirname = os.path.dirname(__file__)
tcp_script_path = os.path.join(dirname, "terminate_children_processes.ps1") 


async def exec_subprocess(program: List[str], timeout: float | None = None):
    """Создание подпроцесса.

    Поскольку процесс мог запустить дочерние процессы, то при
    возникновении исключения asyncio TimeoutError запускаем скрипт pwsh
    (terminate_children_processes.ps1) для их завершения. Скрипту
    передаем pid родительского процесса, и он рекурсивно находит все
    дочерние процессы и переходит в режим ожидания ввода от
    пользователя. Для продолжения работы скрипта достаточно просто
    нажать enter. Python взаимодействует со скриптом pwsh через потоки
    stdout и stdin. Сначала потребляем вывод, ожидаем промпт, после
    этого останавливаем родительский процесс, имитируем нажатие enter, и
    ждем завершения дочерних процессов. Порядок обработки stdin и
    stdout, а также завершение родительского процесса регулируется
    событиями asyncio.

    Аргументы:
        program: программа, которую требуется запустить.
        timeout: таймаут в секундах.
    """
    process: Process = await asyncio.create_subprocess_exec(*program)
    process_waiter = asyncio.wait_for(process.wait(), timeout=timeout)
    logger.info(f"start subprocess id {process.pid}")
    try:
        await process_waiter
        logger.info(f"succeeded subprocess id {process.pid}")
    except TimeoutError:
        logger.error(f"failed subprocess id {process.pid}, timeout error")
        writer_event = asyncio.Event()
        reader_event = asyncio.Event()
        termination_process = await create_termination_subprocess(process)
        reader = termination_process.stdout
        writer = termination_process.stdin
        await asyncio.gather(terminate(process, writer_event),
                             read(reader, reader_event),
                             write(writer, reader_event, writer_event),
                             termination_process.wait())


async def read(reader: StreamReader, reader_event: Event):
    """Чтение потока stdout.

    Аргументы:
        reader: поток stdout.
        reader_enent: событие asyncio, которое триггерится при получении
        промпта.
    """
    while line := await reader.read(1024):
        data = line.decode().rstrip()
        if data.endswith("press enter to continue:"):
            reader_event.set()
        elif data != "":
            logger.info(data)


async def write(writer: StreamWriter,
                reader_event: Event, writer_event: Event):
    """Запись в поток stdin.

    Аргументы:
        writer: поток stdin.
        reader_event: событие asyncio, которое сигнализирует об
        отображении промпта.
        writer_event: событие asyncio, которое триггерится после
        завершения ввода
    """
    await reader_event.wait()
    writer.write("\n".encode())
    await writer.drain()
    reader_event.clear()
    writer_event.set()


async def terminate(process: Process, writer_event: Event):
    """Завершение родительского процесса.

    Аргументы:
        process: родительский процесс.
        writer_event: событие asyncio, которое сигнализирует о
        завершении ввода.
    """
    await writer_event.wait()
    logger.info(f"terminating process {process.pid}")
    process.terminate()
    await process.wait()
    writer_event.clear()


async def create_termination_subprocess(process: Process) -> Process:
    """Создание подпроцесса для завершения дочерних процессов.

    Аргументы:
        process: процесс, дочерние процессы которого нужно завершить.

    Возвращаемые значения:
        Подпроцесс asyncio для завершения дочерних процессов.
    """
    pid = str(process.pid)
    # TODO прописать относительные ссылки нормально
    program = ["pwsh", "-File", tcp_script_path, pid]
    return await asyncio.create_subprocess_exec(*program,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE,
                                                stdin=asyncio.subprocess.PIPE)


async def main(program: List[str]):
    await exec_subprocess(program, 5)


if __name__ == "__main__":
    program = ["python", "test.py"]
    asyncio.run(main(program))
