def disconnect_astinet(connection, pe_name, interface_name):
    """
    Disconnect (undo) interface tertentu di PE.
    Return hasil sebelum, saat, dan sesudah konfigurasi.
    """
    try:
        # 1. cek sebelum config
        check_before = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )
        output_before = f"{pe_name}\n{check_before}"

        # 2. jalankan config undo
        commands = [
            "sys",
            f"undo interface {interface_name}",
            "commit",
            "quit"
        ]
        disconnect_out = connection.send_config_set(commands, enter_config_mode=False)

        # 3. cek setelah config
        check_after = connection.send_command(
            f"display current-configuration interface {interface_name}"
        )

        return output_before, disconnect_out, check_after
    except Exception as e:
        raise Exception(f"Error disconnect {interface_name}: {e}")
