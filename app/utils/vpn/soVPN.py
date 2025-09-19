def suspend_vpn_interface(connection, pe_name, interface_name):
    """
    Suspend interface VPN dengan menambahkan (SUSPEND) di description dan shutdown interface.
    Return hasil sebelum, saat suspend, dan sesudah konfigurasi.
    """
    try:
        # 1. cek konfigurasi sebelum edit
        check_before = connection.send_command(f"show run int {interface_name}")

        # 2. ambil description lama
        old_desc = ""
        for line in check_before.splitlines():
            if line.strip().startswith("description"):
                old_desc = line.strip().replace("description", "", 1).strip()
                break

        # 3. bikin description baru dengan tambahan (SUSPEND)
        new_desc = f"description {old_desc} (SUSPEND)"

        # 4. command suspend
        commands = [
            "conf t",
            f"interface {interface_name}",
            new_desc,
            "shutdown",
            "commit",
            "end"
        ]

        # 5. kirim perintah
        result_config = connection.send_config_set(commands, enter_config_mode=False, cmd_verify=False)

        # 6. cek konfigurasi setelah update
        check_after = connection.send_command(f"show run int {interface_name}")

        return check_before, result_config, check_after

    except Exception as e:
        return None, None, str(e)
