import logging
import os
from os.path import dirname

import datetime

import cv2


def tt(): return datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S_%f')


def tt_nextyear():
    now = datetime.datetime.now()
    next_year = now + datetime.timedelta(days=365)
    next_year = next_year.strftime('%Y-%m-%d %H-%M-%S')
    return next_year


def ttYMD(): return datetime.datetime.now().strftime('%Y-%m-%d')


class taLogClass(logging.Logger):
    """
       Class để cấu hình và ghi thông điệp log vào một file.

        >>> #cách dùng:
            from taLogClass import taLogClass
            logger = taLogClass(LogPosition='AllApp', logPath="path/to/your/log/file.log")
            logger.debug("This is a debug message - Đây là một thông báo gỡ lỗi")
            logger.info("This is an info message - Đây là một thông báo thông tin")
            logger.warning("This is a warning message - Đây là một thông điệp cảnh báo")
            logger.error("This is an error message - Đây là một thông báo lỗi")
            logger.critical("This is a critical message - Đây là một thông điệp quan trọng")

       Args:
           LogPosition (str): vị trí ghi dữ liệu, thường là file/project/chủ đề nào khai báo thì nhập tên file đó vào "AllApp".
           logPath (str): Đường dẫn đến file log. Mặc định là "AI_Data/Log/Project_Log.log".
       Attributes:
           handler (logging.FileHandler): Instance của FileHandler được tạo để ghi thông điệp log vào file.

       Methods:
           __init__(self, logPath="AI_Data/Log/Log.txt"): Hàm khởi tạo, tạo và cấu hình logger và FileHandler.

           mLog(self, level, mess): Ghi thông điệp log vào file với level và nội dung được truyền vào.
       """

    def __init__(self, LogPosition='AllApp', logPath="AI_Data/Log/Project_Log.log"):
        """
        Hàm khởi tạo của class. Tạo logger và FileHandler để ghi thông điệp log vào file.

        Args:
            LogPosition (str): vị trí ghi dữ liệu, thường là file/project/chủ đề nào khai báo thì nhập tên file đó vào "AllApp".
            logPath (str): Đường dẫn đến file log. Mặc định là "AI_Data/Log/Project_Log.log".
        """
        super().__init__(LogPosition)
        self.setLevel(logging.DEBUG)
        os.makedirs(dirname(logPath), exist_ok=True)
        # Tạo instance của FileHandler và thiết lập level cho nó
        logPath = logPath.replace('.log', f"_{ttYMD()}.log")
        self.handler = logging.FileHandler(logPath)
        self.handler.setLevel(logging.DEBUG)

        # Tạo định dạng cho các thông điệp log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

        # Thêm FileHandler vào logger
        self.addHandler(self.handler)

        # Ghi log message
        self.debug('Init taLogClass')

    def taDebug(self, mess):
        self.debug(mess)
        print(mess)

    def taLogImage(self, cv2img, username, IP="", filename=""):
        """
        Save image to AI_Data/ImagesLog/..., if filename=="" then save image's name as current datetime
        :param cv2img: CV2 array image
        :param username: Username
        :param IP: IP of this user
        :param filename: File name only or not provice
        :return: no return
        """
        imPath = f"AI_Data/ImagesLog/{username}_{IP}"
        os.makedirs(imPath, exist_ok=True)
        if filename == "":
            filename = tt()
        filename = f"{imPath}/{filename}.jpg"
        cv2.imwrite(filename, cv2img)
        self.taDebug(f"Lưu ảnh {filename} thành công!")
