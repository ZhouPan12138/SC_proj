# SC_proj

This githup repository program creates a wifi acces point based on a "Time of day" access control. Based on a list of MAC address and time periods when those MAC addresses are allowed to use services

It uses Python to run it.

You have to install in your system soft AP hostapd and dnsmasq to create the AP and give IP. You can install it by typing in the terminal:

```bash
$sudo apt-get install hostapd dnsmasq
```

After installation is done, in the code, change the interface name to one you want to use as the AP. You can modify SSID and Password. 
```python
if __name__ == "__main__":
    interface = "wlo1"
    SSID_AP = "MyAP"
    Password_AP = "123123123"
```

Then, simply run in your terminal:
```bash
$python3 main.py
```

It automatically runs all the services
(remember install library used of the python if you don't have it)

If the services cannot run. Try to disconnect your networkmanager.
```bash
$sudo nmcli networking off
```

Github repo: [https://github.com/ZhouPan12138/SC_proj](https://github.com/ZhouPan12138/SC_proj)

Video demo link: [https://www.youtube.com/watch?v=UbctQKdAOA8](https://www.youtube.com/watch?v=UbctQKdAOA8)
