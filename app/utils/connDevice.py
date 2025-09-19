from netmiko import ConnectHandler

def connect_to_device(host, username, password, device_type="huawei"):
    """
    Membuat koneksi ke perangkat menggunakan Netmiko.
    Return connection object jika sukses, raise Exception jika gagal.
    """
    device = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }
    try:
        connection = ConnectHandler(**device)
        return connection
    except Exception as e:
        raise Exception(f"Gagal konek ke {host}: {e}")
