# utils/astinet/modifyAst.py

def modify_astinet(connection, interface_name, bandwidth, astinet_type, pe_name="PE"):
    """
    Modify bandwidth dan QoS pada interface Astinet.

    Args:
        connection: Netmiko connection object
        interface_name (str): nama interface, contoh: GigabitEthernet3/0/1.100
        bandwidth (int): bandwidth dalam Mbps
        astinet_type (str): "Standard" | "SME" | "Lite (1/2)"
        pe_name (str): nama PE (untuk output logging)

    Returns:
        str: hasil eksekusi siap tampil/copy di Streamlit
    """
    try:
        # 1. cek konfigurasi sebelum
        check_before = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 2. tentukan ratio CIR:PIR
        cir = bandwidth * 1024  # convert Mbps -> Kbps
        if astinet_type.lower() == "standard":
            pir = cir  # 1:1
        elif astinet_type.lower() == "sme":
            pir = cir * 4  # 1:4
        elif "lite" in astinet_type.lower():
            pir = cir * 2  # 1:2
        else:
            pir = cir  # default fallback 1:1

        # 3. commands modify
        commands = [
            "sys",
            f"interface {interface_name}",
            f"bandwidth {bandwidth}",
            f"undo qos-profile i",
            f"undo qos-profile o",
            f"qos car cir {cir} pir {pir} i",
            f"qos car cir {cir} pir {pir} o",
            "commit",
            "quit",
            "quit"
        ]

        # 4. kirim config
        result_config = connection.send_config_set(
            commands, enter_config_mode=False, cmd_verify=False
        )

        # 5. cek konfigurasi setelah
        check_after = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 6. gabungkan hasil output
        output = (
            f"{pe_name}\n\n"
            f"### Konfigurasi sebelum:\n{check_before}\n\n"
            f"### Eksekusi modify:\n{result_config}\n\n"
            f"### Konfigurasi setelah:\n{check_after}"
        )

        return output

    except Exception as e:
        return f"Error saat modify Astinet: {str(e)}"
