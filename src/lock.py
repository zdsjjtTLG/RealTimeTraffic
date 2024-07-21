# -- coding: utf-8 --
# @Time    : 2024/7/21 11:08
# @Author  : TangKai
# @Team    : ZheChengData


# 尝试给文件加锁
def tryLock(locker, timeout = 3):
    try:
        locker.acquire(timeout)
        return True
    except Exception as e:
        return False


# 尝试获取文件锁
def tryUnLock(locker):
    try:
        locker.release()
        return True
    except Exception as e:
        return False