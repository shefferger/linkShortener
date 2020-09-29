from datetime import datetime
from os import path, mkdir

num = 1
noPrint = False


def getName():
    global num
    timeNow = datetime.now()
    _path = 'logs/log-' + str(timeNow.day) + '-' + str(timeNow.month) + '-' + str(timeNow.year) + '-' + str(
        num) + '.txt'
    if path.exists(_path):
        num += 1
        _path = getName()
    return _path


def log(info):
    if not noPrint:
        print(info)
    timeNow = datetime.now()
    with open(fileName, 'a') as logFile:
        logFile.write('\n[' + str(timeNow) + ']\t' + str(info))


if not path.exists('logs'):
    mkdir('logs', 0o755)
fileName = getName()
