import os
import subprocess
import time
import re
from datetime import datetime
from tkinter import Tk, Listbox, Button, Toplevel, messagebox, Label
import threading

#list of MAC addresses and time periods when those MAC addresses are allowed to use services
list_allowed_mac = {'a4:50:46:d5:3f:77': ['12:00', '18:05'],
                    'dc:6a:e7:13:e7:37': ['17:00', '19:00'],
                    'e0:b5:5f:6f:4b:77': ['13:00', '19:00']}

list_interest_device = {'a4:50:46:d5:3f:77': 'device0',
                        'dc:6a:e7:13:e7:37': 'device1'}

#disconnect the corresponding user
def disconnect_mac(client_mac):
    subprocess.run(["sudo", "hostapd_cli", "disassociate", client_mac])

#return a list of the current user connected to the AP
def get_connected_users(interface):
    try:
        result = subprocess.check_output(['sudo', 'hostapd_cli', '-i', interface, 'all_sta']).decode('utf-8')
        lines = result.split('\n')
        list_connected_clients =[]

        for line in lines:
            match = re.search(r"STAAddress=([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})", line)
            if match:
                mac_address = match.group(0)
                mac_address = mac_address[11:]
                list_connected_clients.append(mac_address)
        return list_connected_clients
    except Exception as e:
        print(e)
        return []

#return True if the current time is inside start_time and end_time
def check_time(start_time, end_time):
    current_time = datetime.now().time()
    start_time = datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.strptime(end_time, "%H:%M").time()

    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        return current_time >= start_time or current_time <=end_time


def start_access_point(interface, ssid, password, dns_port=5353):
    #clean up: kill any existing hostapd or dnsmasq processes in case it's running
    subprocess.run(["sudo", "pkill", "hostapd"])
    subprocess.run(["sudo", "pkill", "dnsmasq"])

    #enable IP forwarding
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"])

    #configure the wireless interface
    subprocess.run(["sudo", "ifconfig", interface, "up", "192.168.1.1", "netmask", "255.255.255.0"])

    #allowed devices by its mac
    with open("/tmp/hostapd.accept", "w") as allowed_mac_file:
        str_allowed_mac = ""
        for mac in list_allowed_mac:
            str_allowed_mac += mac
            str_allowed_mac += '\n'
        allowed_mac_file.write(str_allowed_mac)

    #start hostapd with the configuration
    hostapd_conf = f"""interface={interface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
wpa=2
wpa_passphrase={password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
macaddr_acl=1
accept_mac_file=/tmp/hostapd.accept"""

    with open("/tmp/hostapd.conf", "w") as conf_file:
        conf_file.write(hostapd_conf)

    subprocess.Popen(["sudo", "hostapd", "/tmp/hostapd.conf"])

    # Start dnsmasq to provide IP addresses to connected devices
    dnsmasq_conf = f"--interface={interface} --dhcp-range=192.168.1.2,192.168.1.100,12h --port={dns_port}"
    subprocess.Popen(["sudo", "dnsmasq"] + dnsmasq_conf.split())

    print(f"Access Point started with DNS port {dns_port}. Press Ctrl+C to stop.")

#simple monitor window using tkinter
class Monitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.connected_interest_users=[]
        self.start()

    def callback(self):
        self.root.quit()

    def show_interested_devices(self):
        top = Toplevel()
        top.title("Interested Devices")

        title_label = Label(top, text="List of Interested Devices")
        title_label.pack(padx=80, pady=10)

        listbox = Listbox(top, width=25)
        for mac_address, device_name in list_interest_device.items():
            listbox.insert('end', f"{device_name}: {mac_address}")

        listbox.pack(padx=80, pady=10)

    def notify_admin(self, msg):
        messagebox.showinfo("Notification", msg)

    def run(self):
        self.root = Tk()
        self.root.title("WiFi Monitor")


        my_label = Label(self.root, text="Current User connected to AP")
        my_label.grid(row=0, column=0, padx=10, pady=10)

        # Connected Devices Listbox
        connected_devices_listbox = Listbox(self.root)
        connected_devices_listbox.grid(row=1, column=0, padx=80, pady=10)

        interested_devices_button = Button(self.root, text="Interested Devices", command=self.show_interested_devices)
        interested_devices_button.grid(row=2, column=0, padx=10, pady=10)

        def update_connected_devices():
            # show list connected devices
            connected_devices_listbox.delete(0, 'end')  # Clear the existing list
            current_users = get_connected_users(interface)
            for i in self.connected_interest_users:
                if i not in current_users:
                    self.connected_interest_users.remove(i) #the device of interest has disconnect by itself
            for user in current_users:
                start_time = list_allowed_mac[user][0]
                end_time = list_allowed_mac[user][1]
                if not check_time(start_time, end_time):
                    disconnect_mac(user)
                else:
                    connected_devices_listbox.insert('end', user)
                    if user in list_interest_device and user not in self.connected_interest_users:
                        self.connected_interest_users.append(user)
                        self.notify_admin(f"new interested device connecting: {user}")
            # Schedule the function to run again after a delay
            self.root.after(1000, update_connected_devices)

        self.root.after(1000, update_connected_devices)
        self.root.mainloop()


if __name__ == "__main__":
    
    interface = "wlo1"
    SSID_AP = "MyAP"
    Password_AP = "123123123"
    dns_port=5353
    try:
        start_access_point(interface, SSID_AP, Password_AP, dns_port)
        monitor = Monitor()
        while True:
            pass

    except KeyboardInterrupt:
        # Cleanup and exit
        subprocess.run(["sudo", "pkill", "hostapd"])
        subprocess.run(["sudo", "pkill", "dnsmasq"])
        subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"])
        subprocess.run(["sudo", "ifconfig", interface, "down"])
        print("\nAccess Point stopped.")


