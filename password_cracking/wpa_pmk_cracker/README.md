**NOTICE**: This is an inefficient way of doing this. Instead of using this script, use wpa_supplicant_formatter.py to format your wpa_supplicant information for cracking with Hashcat. This program does work,  but is orders of magnitude slower. This is mostly for fun, but also because I didn't realize Hashcat could crack it until I had already written this...

# Description

This script can attack a WPA/WPA2 Pairwise Master Key (PMK) given both it's associated SSID and a wordlist.

This is not the typical way to attack a WiFi password. This method attacks the PMK, which is how wpa_supplicant stores a WiFi password on a device.

Some refrences on this topic:  
https://asecuritysite.com/hash/ssid_hm  
https://www.researchgate.net/figure/WPA-PSK-hash-key-cracking-using-password-and-SSID-and-multiply-hashing-function_fig2_261356151

# Arguments

-w : Number of workers. Generally 1 / CPU core works well  
-b : Batch size to feed the workers. The higher the number, the lower the overhead but higher memory usage

# Usage

Crack the PMKs in wpa_supplicant.txt using the worklist rockyou.txt using 8 workers and a batch size of 5000
```python
wpa_pmk_cracker.py ./wpa_supplicant.txt ./rockyou.txt -w 8 -b 5000
```
# Input

Expected wpa_supplicant format. Can be in most any format so long as ssid= and psk= are present.

```
network={ 
   ssid="homeWifi"
   psk=f65e61758b86994a9504928405289efe34eadf581ceff6bfe55b3ecba989f589
}
```