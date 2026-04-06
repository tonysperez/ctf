# Description

This simple script converts wpa_supplicant information (SSID + PMK) to a Hashcat format (-m 12000) for cracking.

# Input
Expected wpa_supplicant format. Can be in most any format so long as ssid= and psk= are present:

```
network={ 
   ssid="homeWifi"
   psk=f65e61758b86994a9504928405289efe34eadf581ceff6bfe55b3ecba989f589
}
```

# Output 

An output file will be generated which has 1 line per input wpa_supplicant.

```
<ssid>:sha1:4096:<ssid, base64>:<psk, decoded from hex and encoded into base64>
```

# Usage
```python
wpa_supplicant_formatter.py <supplicant info> <output file>
```
