import re

def resume_astinet(connection, interface_name, pe_name):
    """
    Resume interface Astinet yang sebelumnya di-suspend.
    Menghapus teks 'suspend' dalam berbagai format dari description
    dan menjalankan 'undo shutdown'.
    Hasil dikembalikan dalam format siap copy.
    """
    try:
        # 1. cek konfigurasi sebelum resume
        check_before = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 2. ambil description lama
        old_desc = ""
        for line in check_before.splitlines():
            if line.strip().startswith("description"):
                old_desc = line.strip().replace("description", "", 1).strip()
                break

        # 3. hapus semua variasi suspend (case-insensitive, dengan/ tanpa kurung)
        clean_desc = re.sub(r"[\[\(\{]?\s*suspend\s*[\]\)\}]?", "", old_desc, flags=re.IGNORECASE).strip()

        # kalau masih ada kata suspend polos tanpa bracket
        clean_desc = re.sub(r"\bsuspend\b", "", clean_desc, flags=re.IGNORECASE).strip()

        # 4. bikin description baru
        new_desc = f"description {clean_desc}" if clean_desc else ""

        # 5. command resume
        commands = [
            "sys",
            f"interface {interface_name}",
        ]
        if new_desc:
            commands.append(new_desc)
        commands.extend([
            "undo shutdown",
            "commit",
            "quit",
            "quit"
        ])

        # 6. kirim perintah ke device
        result_config = connection.send_config_set(
            commands, enter_config_mode=False, cmd_verify=False
        )

        # 7. cek konfigurasi setelah resume
        check_after = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        # 8. gabungkan hasil biar siap copy
        output = f"""
PE: {pe_name}
Interface: {interface_name}

# Sebelum Resume:
{check_before}

# Config Result:
{result_config}

# Sesudah Resume:
{pe_name}
{check_after}
"""
        return output.strip()

    except Exception as e:
        return f"Error di {pe_name} - {str(e)}"
