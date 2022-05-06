
# import wmi

# wmi_obj = wmi.WMI()
# wmi_sql = "select IPAddress,DefaultIPGateway from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
# wmi_out = wmi_obj.query( wmi_sql )

# for dev in wmi_out:
#     print "IPv4Address:", dev.IPAddress[0], "DefaultIPGateway:", dev.DefaultIPGateway[0]


# exit()
from scapy.all import ARP, Ether, srp, conf

target_ip = f"{conf.route.route('0.0.0.0')[2]}/24"
# IP Address for the destination
# create ARP packet
arp = ARP(pdst=target_ip)
# create the Ether broadcast packet
# ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
# stack them
packet = ether/arp

result = srp(packet, timeout=3, verbose=0)[0]

# a list of clients, we will fill this in the upcoming loop
clients = []

for sent, received in result:
    # for each response, append ip and mac address to `clients` list
    clients.append({'ip': received.psrc, 'mac': received.hwsrc})

# print clients
print("Available devices in the network:")
print("IP" + " "*18+"MAC")
for client in clients:
    print("{:16}    {}".format(client['ip'], client['mac']))