import pytz
import os
import sys
import threading
from datetime import datetime

from loguru import logger

pdt_tz = pytz.timezone('Asia/Kolkata')
thread_sink_ids = {}


def get_day_with_suffix(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f'{day}{suffix}'


now = datetime.now(pdt_tz)
day_with_suffix = get_day_with_suffix(now.day)
log_dir = 'logs'


def remove_default_logger() -> None:
    logger.remove()


def configure_master_logger() -> str:
    os.makedirs(log_dir, exist_ok=True)

    logger.add(sys.stdout,
               format='<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> '
                      '<cyan>[+{elapsed}]</cyan> '
                      '<magenta>({module}:{line})</magenta> '
                      '<level>{level} > {message}</level>',
               level='DEBUG')
    logger.add(f'{log_dir}/MAIN.log',
               format='[{time:YYYY-MM-DD HH:mm:ss}] '
                      '[+{elapsed}] '
                      '({module}:{line}) '
                      '{level} > {message}',
               level='TRACE',
               encoding='utf-8',
               rotation='1 day',
               retention='1 month',
               compression='gz')

    return os.path.abspath(log_dir)


def configure_thread_logger() -> str | None:
    thread_id = threading.get_ident()
    thread_name = threading.current_thread().name
    thread_log_folder = os.path.join(log_dir, thread_name)
    os.makedirs(thread_log_folder, exist_ok=True)

    if thread_id not in thread_sink_ids:
        logger.add(sys.stdout,
                   format='<green>[{time:HH:mm:ss}]</green> '
                          '<cyan>[+{elapsed}]</cyan> '
                          '[{thread.name}] '
                          '<magenta>({module}:{function}:{line})</magenta> '
                          '<level>{level} > {message}</level>',
                   level='DEBUG')
        sink_id = logger.add(os.path.join(thread_log_folder, 'DEVICE.log'),
                             filter=lambda record: record['thread'].id == thread_id,
                             format='[{time:YYYY-MM-DD HH:mm:ss}] '
                                    '[+{elapsed}] '
                                    '[{thread.name}] '
                                    '({module}:{function}:{line}) '
                                    '{level} > {message}',
                             level='TRACE',
                             encoding='utf-8',
                             rotation='1 day',
                             retention='1 month',
                             compression='gz')
        thread_sink_ids[thread_id] = sink_id

    return os.path.abspath(log_dir)
