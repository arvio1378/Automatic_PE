import streamlit as st

def command_vpn(conn, command_input: str):
    """
    Jalankan command ke PE yang sudah terkoneksi.
    Bisa multi-line command (dipisahkan newline).
    """
    try:
        cmds = [line.strip() for line in command_input.splitlines() if line.strip()]
        all_output = []
        for cmd in cmds:
            out = conn.send_command(cmd)
            all_output.append(f"===== {cmd} =====\n{out}")

        # gabungkan hasil
        final_output = "\n\n".join(all_output)
        return True, final_output
    except Exception as e:
        return False, f"Error: {e}"


def exit_vpn(conn):
    """
    Keluar dari session PE (Huawei pakai 'quit')
    """
    try:
        output = conn.send_command_timing("quit", strip_prompt=False, strip_command=False)
        # reset status
        st.session_state["pe_connected"] = False
        return True, output
    except Exception as e:
        return False, f"Error: {e}"
