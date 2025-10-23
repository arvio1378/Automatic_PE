import pandas as pd
import streamlit as st
from utils.connDevice import connect_to_device
from utils.astinet.connectAst import connect_astinet
from utils.astinet.commandAst import send_commands, exit_pe
from utils.astinet.doAst import disconnect_astinet
from utils.astinet.moAst import modify_astinet
from utils.astinet.soAst import suspend_astinet
from utils.astinet.roAst import resume_astinet
from utils.astinet.aoAst import activate_astinet
from utils.astinet.checkAstinet import check_interface, check_ip
from utils.vpn.connectVPN import connect_vpn
from utils.vpn.commandVPN import command_vpn, exit_vpn
from utils.vpn.doVPN import disconnect_vpn_interface
from utils.vpn.soVPN import suspend_vpn_interface

# Load CSS dari file
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Konfigurasi Halaman
st.set_page_config(
    page_title="Otomatic PE",
    page_icon="🤖",
    layout="wide"
)

# Navigasi Sidebar
st.sidebar.title("Navigation")
pages = st.sidebar.selectbox("Menu : ", ["Astinet", "VPN"])

# Page Astinet
if pages == "Astinet":
    st.title("Astinet")
    # Hubungkan ke hostname
    st.write("### Hostname Login")
    host = st.text_input("Host", "10.60.190.15", key="host_ip")
    username = st.text_input("Username", key="host_user")
    password = st.text_input("Password", type="password", key="host_pass")

    if st.button("Connect"):
        try:
            connection = connect_to_device(host, username, password)
            st.session_state["connection"] = connection
            st.success(f"Login ke {host} sukses: {connection.find_prompt()}")
        except Exception as e:
            st.error(str(e))
    
    # Masuk ke PE
    if "connection" in st.session_state:
        st.write("### PE Input")
        pe_ast = pd.read_csv("./data/astinet.csv")["nama"].tolist()
        st.selectbox("Pilih opsi", pe_ast, key="pe_name_ast")
        pe_password = st.text_input("Password", type="password", key="pe_pass_ast")

        if st.button("PE connect"):
            conn = st.session_state["connection"]
            try:
                selected_ast = st.session_state["pe_name_ast"]
                prompt_ast, output_ast = connect_astinet(conn, selected_ast, pe_password)
                st.session_state["pe_connected"] = True
                st.success(f"Sukses masuk ke {selected_ast}, prompt: {prompt_ast}")
                st.text_area("Output", output_ast, height=200)
            except Exception as e:
                st.error(str(e))
        
        # Command di PE
        if st.session_state.get("pe_connected", False):
            st.subheader("PE Command")
            if "command_input_ast" not in st.session_state:
                st.session_state["command_input_ast"] = "dis cur int "
            
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("display"):
                    st.session_state["command_input_ast"] = "dis cur int "
            
            with col2:
                if st.button("Cek SID"):
                    st.session_state["command_input_ast"] = "dis int desc | in"
            
            with col3:
                if st.button("cek IP"):
                    st.session_state["command_input_ast"] = "dis ip routing-table vpn-instance Astinet_Mix "

            command_ast = st.text_area(
                "Command",
                key="command_input_ast"
            )

            # Button command
            if st.button("Run Command"):
                try:
                    cmds = [line.strip() for line in command_ast.splitlines() if line.strip()]
                    conn = st.session_state["connection"]
                    final_output = send_commands(conn, cmds)
                    st.write("### Hasil eksekusi:")
                    st.code(final_output, language=None)
                except Exception as e:
                    st.error(str(e))

            # Exit PE
            if st.button("Exit PE"):
                try:
                    conn = st.session_state["connection"]
                    output = exit_pe(conn)
                    st.code(output, language=None)

                    st.session_state["pe_connected"] = False
                    st.success("Berhasil keluar dari PE")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            
            # Seleksi task Astinet
            if "active_tab_ast" not in st.session_state:
                st.session_state.active_tab_ast = "Disconnect"
            # pilihan task astinet
            tabs_ast = ["Disconnect", "Modify", "Suspend", "Activate", "Resume"]
            selected_tab_ast = st.radio("Pilih Tab", tabs_ast, index=tabs_ast.index(st.session_state.active_tab_ast), horizontal=True)

            # update session state kalau pindah tab
            if selected_tab_ast != st.session_state.active_tab_ast:
                st.session_state.active_tab_ast = selected_tab_ast
            
            # Disconnect Astinet
            if st.session_state.active_tab_ast == "Disconnect":
                if st.session_state.get("pe_connected", False):
                    st.subheader("Disconnect")
                    interface_ast_do = st.text_input("Interface Astinet", key="interface_ast_do")
                    if st.button("Disconnect Astinet"):
                        try:
                            conn = st.session_state["connection"]
                            pe_name = st.session_state.get("pe_name_ast", "PE")
                            out_before, out_do, out_after = disconnect_astinet(conn, pe_name, interface_ast_do)
                            st.write("### Konfigurasi sebelum:")
                            st.code(out_before, language=None)
                            st.write("### Eksekusi undo interface:")
                            st.code(out_do, language=None)
                            st.write("### Konfigurasi setelah:")
                            st.code(out_after, language=None)
                        except Exception as e:
                            st.error(str(e))
                            
            # Modify Astinet
            elif st.session_state.active_tab_ast == "Modify":
                if st.session_state.get("pe_connected", False):
                    st.subheader("Modify Astinet")
                    # Input data modify astinet
                    interface_name = st.text_input("Interface", key="modify_interface")
                    bandwidth = st.number_input("Bandwidth (Mbps)", min_value = 1, step = 1, format="%d", key="modify_bandwidth")
                    astinet_type = st.selectbox("Astinet Type", ["Standard", "SME", "Lite (1/2)"], key="modify_type")

                    if st.button("Modify Astinet"):
                        connection = st.session_state["connection"]
                        pe_name = st.session_state.get("pe_name_ast", "PE")
                        output = modify_astinet(connection, interface_name, bandwidth, astinet_type, pe_name)
                        st.code(output, language=None)
            
            # Suspend Astinet
            elif st.session_state.active_tab_ast == "Suspend":
                st.subheader("Suspend")
                interface_ast_so = st.text_input("Interface Astinet", key="interface_ast_so")
                if st.button("Suspend Astinet"):
                    try:
                        connection = st.session_state["connection"]
                        pe_name = st.session_state.get("pe_name_ast", "PE")
                        output = suspend_astinet(connection, interface_ast_so, pe_name)
                        st.code(output, language=None)
                    except Exception as e:
                        st.error(f"Gagal suspend: {str(e)}")

            # New Install Astinet
            elif st.session_state.active_tab_ast == "Activate":
                st.subheader("New Install")

                # Cek interface Astinet
                interface_ast_ao = st.text_input("Input interface", key="interface_ast_ao")
                if st.button("Check Interface", key="check_interface"):
                    conn = st.session_state["connection"]
                    status, cmd, output = check_interface(conn, interface_ast_ao)
                    if status == "kosong":
                        st.success(f"Interface {interface_ast_ao} kosong !!")
                    elif status == "ada":
                        st.warning(f"Interface {interface_ast_ao} sudah terpakai !!")
                    else:
                        st.error(f"Error: {output}")
                    st.code(cmd)
                    st.code(output)

                # Cek IP Astinet
                ip_ao = st.text_input("Input IP", key="ip_ao")
                if st.button("Check IP", key="check_ip"):
                    conn = st.session_state["connection"]
                    status, cmd, output = check_ip(conn, ip_ao)

                    if status == "kosong":
                        st.success(f"IP {ip_ao} kosong !!")
                    elif status == "ada":
                        st.warning(f"IP {ip_ao} sudah digunakan !!")
                    else:
                        st.error(f"Error: {output}")

                    st.code(cmd)
                    st.code(output)

                # Input data untuk activate astinet
                portname_ast_ao = st.text_input("Portname (GigabitEthernet3/0/1)", key="portname_ast_ao")
                vlan_ast_ao = st.text_input("VLAN", key="vlan_ast_ao")
                bandwith_ast_ao = st.number_input("Bandwith", key="bandwith_ast_ao")
                astinet_type_ao = st.selectbox(
                    "Astinet Type",
                    ("Standard", "SME", "Lite (1/2)"),
                    key="astinet_type_ao"
                )
                sid_ast_ao = st.number_input("SID", key="sid_ast_ao")
                desc_ast_ao = st.text_input("Description", key="desc_ast_ao")
                ip_ast_ao = st.text_input("IP", key="ip_ast_ao")
                if st.button("Activate Astinet"):
                    connection = st.session_state["connection"]
                    pe_name = st.session_state.get("pe_ast", "PE")
                    try:
                        commands, result, after = activate_astinet(
                            connection,
                            pe_name,
                            portname_ast_ao,
                            vlan_ast_ao,
                            bandwith_ast_ao,
                            astinet_type_ao,
                            sid_ast_ao,
                            desc_ast_ao,
                            ip_ast_ao
                        )

                        if commands is None:
                            st.error(f"Error: {after}")
                        else:
                            st.code("\n".join(commands), language="bash")
                            st.write("### Hasil eksekusi:")
                            st.code(result, language=None)
                            st.write("### Konfigurasi setelah:")
                            st.code(after, language=None)

                    except Exception as e:
                        st.error(str(e))

            # Resume Astinet
            elif st.session_state.active_tab_ast == "Resume":
                st.subheader("Resume")
                interface_ast_ro = st.text_input("Interface Astinet", key="interface_ast_ro")
                
                if st.button("Resume Astinet"):
                    try:
                        connection = st.session_state["connection"]
                        pe_name = st.session_state.get("pe_name_ast", "PE")
                        output = resume_astinet(connection, interface_ast_ro, pe_name)
                        st.code(output, language=None)
                    except Exception as e:
                        st.error(f"Gagal resume: {str(e)}")
                
# Page VPN
elif pages == "VPN":
    st.title("VPN")
    # Hubungkan ke hostname
    st.write("### Hostname Login")
    host = st.text_input("Host", "10.60.190.15", key="host_ip")
    username = st.text_input("Username", key="host_user")
    password = st.text_input("Password", type="password", key="host_pass")

    if st.button("Connect"):
        try:
            connection = connect_to_device(host, username, password)
            st.session_state["connection"] = connection
            st.success(f"Login ke {host} sukses: {connection.find_prompt()}")
        except Exception as e:
            st.error(str(e))
        
    # Masuk ke PE
    if "connection" in st.session_state:
        st.write("### PE Input")
        pe_vpn = pd.read_csv("./data/vpn.csv")["nama"].tolist()
        st.selectbox("Pilih opsi", pe_vpn, key="pe_name_vpn")
        user_vpn = st.text_input("Username", key="pe_user_vpn")
        pass_PE = st.text_input("Password", type="password", key="pe_pass_vpn")

        if st.button("PE connect"):
            conn = st.session_state["connection"]
            selected_vpn = st.session_state["pe_name_vpn"]
            prompt_vpn, output_vpn = connect_astinet(conn, selected_vpn, pass_PE)
            success, message = connect_vpn(conn, selected_vpn, user_vpn, pass_PE)

            if success:
                st.success(message)
            else:
                st.error(message)
        
        # Command di PE
        if st.session_state.get("pe_connected", False):
            st.subheader("PE Command")
            if "command_input_vpn" not in st.session_state:
                st.session_state["command_input_vpn"] = "show run int "
            
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("display"):
                    st.session_state["command_input_vpn"] = "show run int "
            
            with col2:
                if st.button("Cek SID"):
                    st.session_state["command_input_vpn"] = "sh int desc | in"
            
            with col3:
                if st.button("cek IP"):
                    st.session_state["command_input_vpn"] = "sh route vrf "

            command_vpn = st.text_area(
                "Command",
                key="command_input_vpn"
            )

            # Button command
            if st.button("Run Command"):
                try:
                    cmds = [line.strip() for line in command_vpn.splitlines() if line.strip()]
                    conn = st.session_state["connection"]
                    final_output = send_commands(conn, cmds)
                    st.write("### Hasil eksekusi:")
                    st.code(final_output, language=None)
                except Exception as e:
                    st.error(str(e))

            if st.button("Exit PE"):
                conn = st.session_state["connection"]
                success, output = exit_vpn(conn)

                if success:
                    st.write(output)
                    st.success("Berhasil keluar dari PE")
                    st.rerun()
                else:
                    st.error(output)

            # Seleksi task Astinet
            if "active_tab_vpn" not in st.session_state:
                st.session_state.active_tab_vpn = "Disconnect"
            tabs_vpn = ["Disconnect", "Modify", "Suspend", "Activate", "Resume"]
            selected_tab_vpn = st.radio("Pilih Tab", tabs_vpn, index=tabs_vpn.index(st.session_state.active_tab_vpn), horizontal=True)

            # update session state kalau pindah tab
            if selected_tab_vpn != st.session_state.active_tab_vpn:
                st.session_state.active_tab_vpn = selected_tab_vpn

            # Disconnect VPN
            if st.session_state.active_tab_vpn == "Disconnect":
                st.subheader("Disconnect")
                interface_vpn_do = st.text_input("Interface VPN", key="interface_vpn_do")

                if st.button("Disconnect VPN"):
                    try:
                        connection = st.session_state["connection"]
                        pe_name = st.session_state.get("pe_name_vpn", "PE")
                        out_before, out_do, out_after = disconnect_vpn_interface(connection, pe_name, interface_vpn_do)
                        st.write("### Konfigurasi sebelum:")
                        st.code(out_before, language=None)
                        st.write("### Eksekusi disconnect:")
                        st.code(out_do, language=None)
                        st.write("### Konfigurasi setelah:")
                        st.code(pe_name, language=None)
                        st.code(out_after, language=None)
                    except Exception as e:
                        st.error(str(e))
            # Modify VPN
            elif st.session_state.active_tab_vpn == "Modify":
                st.subheader("Modify")
            # Suspend VPN
            elif st.session_state.active_tab_vpn == "Suspend":
                st.subheader("Suspend")
                interface_vpn_so = st.text_input("Interface VPN", key="interface_vpn_so")
                if st.button("Suspend VPN"):
                    connection = st.session_state["connection"]
                    pe_name = st.session_state.get("pe_name_vpn", "PE")
                    check_before, result_config, check_after = suspend_vpn_interface(connection, pe_name, interface_vpn_so)
                    if check_before is None:
                        st.error(f"Error: {check_after}")
                    else:
                        st.write("### Konfigurasi sebelum:")
                        st.code(check_before, language=None)
                        st.write("### Eksekusi suspend:")
                        st.code(result_config, language=None)
                        st.write("### Konfigurasi setelah:")
                        st.code(pe_name, language=None)
                        st.code(check_after, language=None)