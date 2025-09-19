import time

def connect_astinet(connection, pe_name, pe_password):
    """
    Melakukan SSH ke PE dari host yang sudah terhubung.
    Return prompt PE jika sukses.
    """
    try:
        # Kirim perintah ssh
        output = connection.send_command_timing(
            f"ssh {pe_name}",
            strip_prompt=False,
            strip_command=False
        )

        # Jika diminta password
        if "assword" in output:  
            output = connection.send_command_timing(
                pe_password,
                strip_prompt=False,
                strip_command=False
            )

        # Tunggu prompt stabil
        time.sleep(2)
        prompt = connection.find_prompt()
        return prompt, output
    except Exception as e:
        raise Exception(f"Gagal masuk ke PE {pe_name}: {e}")
