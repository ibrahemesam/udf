import netifaces as ni
import subprocess as sp
import socket
def get_private_ip(Iface=None):
	if not Iface:
		o = sp.check_output("route").decode().split('\n')[2]
		Iface = o[o.rfind(' ')+1:] # get current_used_interface
		if not Iface: return None
	ip = ni.ifaddresses(Iface)[ni.AF_INET][0]['addr']
	return ip

def get_free_port():
    for port in range(1025, 65535):  # check for all available ports
        try:
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new socket
            serv.bind(('0.0.0.0', port))  # bind socket with address
            serv.close()  # close connection
            return port
        except: continue
