from os.path import isfile
from sqlite3 import connect
from config.config import BUILD_PATH, DB_PATH

cxn = connect(DB_PATH)
cur = cxn.cursor()


# def with_commit(func):
#     def inner(*args, **kwargs):
#         func(*args, **kwargs)
#         commit()
#
#     return inner


# @with_commit
def build():
    pass
    # if isfile(BUILD_PATH):
    #     scriptexec(BUILD_PATH)


