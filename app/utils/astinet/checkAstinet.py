def check_interface(connection, interface_name):
    try:
        command = f"display current-configuration interface {interface_name}"
        output = connection.send_command(command)

        if "Error: Wrong parameter found" in output:
            return "kosong", command, output
        else:
            return "ada", command, output

    except Exception as e:
        return "error", command, str(e)


def check_ip(connection, ip_address, vpn="Astinet_Mix"):
    try:
        command = f"display ip routing-table vpn-instance {vpn} {ip_address}"
        output = connection.send_command(command)

        if ip_address in output:
            return "ada", command, output
        else:
            return "kosong", command, output

    except Exception as e:
        return "error", command, str(e)
