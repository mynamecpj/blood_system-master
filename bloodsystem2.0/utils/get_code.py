import wmi#wmi依赖pywin32,python3.5以上版本安装pywin32需要手动安装
import hashlib
import binascii
import time
from pyDes import des, CBC, PAD_PKCS5

def des_encrypt(secret_key, s):
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)

def des_decrypt(secret_key, s):
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de

# secret_str = des_encrypt('12345678', 'I love YOU~')
# print(secret_str)
# clear_str = des_decrypt('12345678', secret_str)
# print(clear_str)

s = wmi.WMI()

#cpu 序列号
def get_CPU_info():
    cpu = []
    cp = s.Win32_Processor()
    for u in cp:
        cpu.append(
            {
                "Name": u.Name,
                "Serial Number": u.ProcessorId,
                "CoreNum": u.NumberOfCores
            }
        )
    return cpu

#硬盘序列号
def get_disk_info():
    disk = []
    for pd in s.Win32_DiskDrive():
        disk.append(
            {
                "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(), # 获取硬盘序列号，调用另外一个win32 API
                "ID": pd.deviceid,
                "Caption": pd.Caption,
                "size": str(int(float(pd.Size)/1024/1024/1024))+"G"
            }
        )
    return disk

#mac 地址（包括虚拟机的）
def get_network_info():
    network = []
    for nw in s.Win32_NetworkAdapterConfiguration ():  # IPEnabled=0
        if nw.MACAddress != None:
            network.append(
                {
                    "MAC": nw.MACAddress,  # 无线局域网适配器 WLAN 物理地址
                    "ip": nw.IPAddress
                }
            )
    return network

#主板序列号
def get_mainboard_info():
    mainboard=[]
    for board_id in s.Win32_BaseBoard ():
        mainboard.append(board_id.SerialNumber.strip().strip('.'))
    return mainboard

def get_base_code(now_time:str):
    id_cpu = get_CPU_info()[0]['Serial Number']
    id_disk = get_disk_info()[0]['Serial']
    id_mainboard = get_mainboard_info()[0]
    id = ''.join([id_cpu, id_mainboard, id_disk, now_time])

    return hashlib.md5(id.encode()).hexdigest()[:5]

def create_password_by_base_code(base_code):
    base_code = base_code + "scnu"
    password = hashlib.md5(base_code.encode()).hexdigest()
    return password[-5:]

def check_the_password(password, register_time:str):
    base_code = get_base_code(register_time)
    real_password = create_password_by_base_code(base_code)
    if real_password == password:
        return True
    else:
        return False

if __name__ == '__main__':

    while True:
        code = input("请输入注册码：")
        print(''.join(['您的激活码是：',create_password_by_base_code(code)]))