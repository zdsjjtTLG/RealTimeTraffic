# -- coding: utf-8 --
# @Time    : 2024/7/21 11:08
# @Author  : TangKai
# @Team    : ZheChengData

from multiprocessing import Lock


# 尝试给文件加锁
def tryLock(locker: Lock = None, timeout=3):
    try:
        locker.acquire(timeout)
        return True
    except Exception as e:
        print(repr(e))
        return False


# 尝试获取文件锁
def tryUnLock(locker: Lock = None):
    try:
        locker.release()
        return True
    except Exception as e:
        print(repr(e))
        return False
