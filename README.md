# SC_proj

This githup repository program creates a wifi acces point based on a "Time of day" access control. Based on a list of MAC address and time periods when those MAC addresses are allowed to use services

It uses Python to run it.

You have to install in your system soft AP hostapd and dnsmasq to create the AP and give IP. You can install it by typing in the terminal:
$sudo apt-get install hostapd dnsmasq

After installation is done, simply run in your terminal:
$python3 main.py

It automatically runs all the services
(remember install library used of the python if you don't have it)

If the services cannot run. Try to disconnect your networkmanager.
$sudo nmcli networking off
