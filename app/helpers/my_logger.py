# my_logger.py
import os
import logging

log_file = None

def set_file(filename):
    global log_file
    log_file = filename
    if not os.path.exists(filename):
        with open(filename, 'w'):
            pass  # Create an empty file if it doesn't exist


def debug(message):
    log('debug', message)

def info(message):
    log('info', message)

def warning(message):
    log('warning', message)

def error(message):
    log('error', message)

def critical(message):
    log('critical', message)

def log(level, message):
    global log_file
    if log_file:
        with open(log_file, 'a') as f:
            log_entry = f"[{level.upper()}] {message}\n"
            f.write(log_entry)
    # Also log using the built-in logging module
    getattr(logging, level)(message)
