import sys
import platform
import os
from PyQt5 import QtCore
# init openvino
system_type = platform.system()
if system_type == "Linux":
    print("若要使用openvino，请自行source openvino安装根目录下的bin/setupvars.sh后再运行程序!")
else:
    openvino_install_path = "C:/Program Files (x86)/Intel/openvino_2021"  # TODO 这里每台电脑安装完后需要改为自己的openvino安装路径
    sys.path.append(os.path.join(openvino_install_path, "python", "python" + sys.version[:3]))
    os.environ["Path"] += ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "python", "python" + sys.version[:3]) + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "opencv", "bin") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "ngraph", "lib") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "inference_engine", "external", "tbb", "bin") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "inference_engine", "bin", "intel64", "Release") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "inference_engine", "external", "hddl", "bin") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "inference_engine", "external", "omp", "lib") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "inference_engine", "external", "gna", "lib") + ";"
    os.environ["Path"] += os.path.join(openvino_install_path, "deployment_tools", "model_optimizer") + ";"

import logging
from PyQt5.QtWidgets import QApplication
from Mainwindow import Mainwindow

logger = logging.getLogger("root")
logger.setLevel(level=logging.DEBUG)
console_handle = logging.StreamHandler()
console_handle.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 构建一个mainWindow
    mainWindow = Mainwindow()
    #QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    if mainWindow.register():
        mainWindow.showMaximized_and_iocn()
        mainWindow.recovery()
        logger.info("mainWindow初始化完成。")
        mainWindow.show()
        sys.exit(app.exec_())
    else:
        pass

