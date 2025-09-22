def activate_astinet(
    connection,
    pe_name,
    portname,
    vlan,
    bandwidth,
    astinet_type,
    sid,
    description,
    ip_address
):
    """
    Aktivasi layanan Astinet baru di PE.

    Args:
        connection: Netmiko connection object
        pe_name (str): nama PE
        portname (str): contoh "GigabitEthernet3/0/1"
        vlan (int): VLAN ID
        bandwidth (int): bandwidth dalam Mbps
        astinet_type (str): "Standard" | "SME" | "Lite"
        sid (int): Service ID
        description (str): deskripsi layanan
        ip_address (str): IP address dengan mask

    Returns:
        tuple: (commands, result_config, output_after)
    """
    try:
        # convert Mbps -> Kbps
        cir = bandwidth * 1024

        # tentukan rasio inbound : outbound
        if astinet_type.lower() == "standard":
            cir_in = cir
            cir_out = cir
        elif astinet_type.lower() == "sme":
            cir_in = cir // 4   # inbound dibagi 4
            cir_out = cir       # outbound tetap
        elif "lite" in astinet_type.lower():
            cir_in = cir // 2   # inbound dibagi 2
            cir_out = cir       # outbound tetap
        else:
            cir_in = cir
            cir_out = cir

        # buat perintah konfigurasi
        commands = [
            "sys",
            f"int {portname}.{vlan}",
            f"vlan-type dot1q {vlan}",
            f"bandwidth {bandwidth}",
            f"description {sid} {astinet_type} {description}",
            "ip binding vpn-instance Astinet_Mix",
            f"ip address {ip_address}",
            "statistic enable",
            f"qos car cir {cir_in} pir {cir_in} i",   # inbound (dibagi sesuai tipe)
            f"qos car cir {cir_out} pir {cir_out} o", # outbound (full)
            "commit",
            "quit",
            "quit"
        ]

        # kirim konfigurasi
        result_config = connection.send_config_set(
            commands, enter_config_mode=False, cmd_verify=False
        )

        # cek hasil konfigurasi setelah aktifasi
        check_after = connection.send_command(
            f"display current-configuration interface {portname}.{vlan}"
        )

        output_after = f"{pe_name}\n\n{check_after}"

        return commands, result_config, output_after

    except Exception as e:
        return None, None, str(e)