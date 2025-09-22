# utils/astinet/modifyAst.py

def modify_astinet(connection, interface_name, bandwidth, astinet_type, pe_name="PE"):
    """
    Modify bandwidth dan QoS pada interface Astinet.

    Args:
        connection: Netmiko connection object
        interface_name (str): nama interface, contoh: GigabitEthernet3/0/1.100
        bandwidth (int): bandwidth dalam Mbps
        astinet_type (str): "Standard" | "SME" | "Lite"
        pe_name (str): nama PE (untuk output logging)

    Returns:
        str: hasil eksekusi siap tampil/copy di Streamlit
    """
    try:
        # 1. cek konfigurasi sebelum
        check_before = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 2. convert Mbps -> Kbps
        cir = bandwidth * 1024

        # 3. tentukan rasio inbound : outbound
        if astinet_type.lower() == "standard":
            cir_in = cir
            cir_out = cir
        elif astinet_type.lower() == "sme":
            cir_in = cir // 4
            cir_out = cir
        elif "lite" in astinet_type.lower():
            cir_in = cir // 2
            cir_out = cir
        else:
            cir_in = cir
            cir_out = cir 

        # 4. commands modify
        commands = [
            "sys",
            f"interface {interface_name}",
            f"bandwidth {bandwidth}",
            f"undo qos-profile i",
            f"undo qos-profile o",
            f"qos car cir {cir_in} pir {cir_in} i",   # inbound
            f"qos car cir {cir_out} pir {cir_out} o", # outbound
            "commit",
            "quit",
            "quit"
        ]

        # 5. kirim config
        result_config = connection.send_config_set(
            commands, enter_config_mode=False, cmd_verify=False
        )

        # 6. cek konfigurasi setelah
        check_after = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 7. gabungkan hasil output
        output = (
            f"\n{check_before}\n\n"
            f"### Eksekusi modify:\n{result_config}\n\n"
            f"{pe_name}\n"
            f"\n{check_after}"
        )

        return output

    except Exception as e:
        return f"Error saat modify Astinet: {str(e)}"
