import time
import streamlit as st

def connect_vpn(conn, pe_name, username, password):
    """
    Melakukan koneksi ke PE lewat telnet dari router utama (sudah ada session 'connection').
    """
    try:
        # jalankan telnet ke PE
        output = conn.send_command_timing(
            f"telnet {pe_name}", strip_prompt=False, strip_command=False
        )

        st.write(output)

        # Jika telnet minta username
        if "sername" in output:  # cover "Username:" / "username:"
            output = conn.send_command_timing(username, strip_prompt=False, strip_command=False)
            st.write(output)

        # Jika minta password
        if "assword" in output:  # cover "Password:" / "password:" / "Please input the password:"
            output2 = conn.send_command_timing(password, strip_prompt=False, strip_command=False)
            st.write(output2)

        # Tunggu agar prompt stabil
        time.sleep(3)
        st.write("Sekarang prompt:", conn.find_prompt())

        # simpan status
        st.session_state["pe_connected"] = True

        return True, "Berhasil connect ke PE"

    except Exception as e:
        return False, f"Error: {e}"
