def send_commands(connection, commands):
    """
    Menjalankan beberapa command di PE.
    Return gabungan output.
    """
    try:
        all_output = []
        for cmd in commands:
            out = connection.send_command(cmd)
            all_output.append(f"===== {cmd} =====\n{out}")
        return "\n\n".join(all_output)
    except Exception as e:
        raise Exception(f"Error saat menjalankan command: {e}")

def exit_pe(connection):
    """
    Keluar dari sesi PE (Huawei biasanya pakai 'quit').
    """
    try:
        output = connection.send_command_timing(
            "quit",
            strip_prompt=False,
            strip_command=False
        )
        return output
    except Exception as e:
        raise Exception(f"Gagal keluar dari PE: {e}")
