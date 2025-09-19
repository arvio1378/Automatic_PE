# utils/astinet/newInstallAst.py
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
    try:
        # tentukan ratio QoS sesuai tipe
        if astinet_type.lower() == "standard":
            ratio = (1, 1)  # 1:1
        elif astinet_type.lower() == "sme":
            ratio = (1, 4)  # 1:4
        elif "lite" in astinet_type.lower():
            ratio = (1, 2)  # 1:2
        else:
            raise ValueError("Tipe Astinet tidak valid!")

        # hitung CIR & PIR (inbound, outbound)
        cir_in = bandwidth * 1024 * ratio[0]
        pir_in = bandwidth * 1024 * ratio[1]
        cir_out = bandwidth * 1024 * ratio[0]
        pir_out = bandwidth * 1024 * ratio[1]

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
            f"qos car cir {cir_in} pir {pir_in} i",
            f"qos car cir {cir_out} pir {pir_out} o",
            "commit",
            "quit",
            "quit"
        ]

        # kirim perintah ke device
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
