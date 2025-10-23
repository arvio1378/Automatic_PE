def suspend_astinet(connection, interface_name, pe_name):
    """
    Suspend interface Astinet dengan menambahkan (SUSPEND) di description
    dan melakukan shutdown. Hasil dikembalikan dalam format siap copy.
    """
    try:
        # cek config sebelum edit
        check_before = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # ambil description lama
        old_desc = ""
        for line in check_before.splitlines():
            if line.strip().startswith("description"):
                old_desc = line.strip().replace("description", "", 1).strip()
                break

        # fallback kalau kosong
        old_desc = old_desc if old_desc else interface_name

        # bikin description baru, hindari double (SUSPEND)
        if "(SUSPEND)" not in old_desc:
            new_desc = f"description {old_desc} (SUSPEND)"
        else:
            new_desc = f"description {old_desc}"

        # command suspend
        commands = [
            "sys",
            f"interface {interface_name}",
            new_desc,
            "shutdown",
            "commit",
            "quit",
            "quit"
        ]

        # kirim perintah
        result_config = connection.send_config_set(commands, enter_config_mode=False)

        # cek config setelah update
        check_after = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # gabungkan hasil biar sekali copy langsung jelas
        output = f"""
{check_before}\n
{result_config}\n
{pe_name}
{check_after}
        """
        return output.strip()

    except Exception as e:
        return f"Error di {pe_name} - {str(e)}"
