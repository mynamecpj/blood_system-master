# blood_software

### bugs：

1、搜索栏不能标记

2、根目录换了之后可能会报错



### 自动检测环境配置（openvino）

**windows：**

1. 下载安装包：https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit/download.html?operatingsystem=window&distributions=webdownload&version=2021.3%20(latest)&options=offline
   ![image-20210424121115495](https://red0orange.oss-cn-shenzhen.aliyuncs.com/markdown-img/image-20210424121115495.png)
2. 安装时安装路径自己选，都可以，其他选项全部默认即可，有警告也不用管。
3. 安装好后复制安装路径，在main.py中搜索openvino_install_path这个全局变量，把值改为自己安装路径即可，注意要把路径中所有反斜杠改为正斜杠

**ubuntu：**

1. 下载路径为：https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit/download.html?operatingsystem=linux&distributions=webdownload&version=2021.2&options=offline
2. 安装（同windows）
3. ubuntu下无法直接在程序运行时配置动态so库的搜索路径，因此必须要在程序运行前source openvino安装根目录下的bin/setupvars.sh，如果需要使用pycharm，需要先打开终端source完setupvars.sh文件后，直接在终端打开pycharm，然后pycharm就有了环境变量，即可直接运行、调试程序。

