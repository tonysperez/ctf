# Description
Pronounced 'KOR-uh-log'  
This script ingests a log file for analysis for easy analysis via REGEX. 

## 0 - 1 Capture Group
If you spesify either no capture groups or 1 capture group, correlog can:
- Count both total and unique matches (especially useful if you use a capture group)
- Calculate averages
- Identify the most and least prevelant matches
- Count how many times each value appears

## 2 Capture Groups
The unique feature of correlog is that you can spesify 2
capture groups in your REGEX, and correlog will associate those
values together, almost allowing you to query the log like
a database.
- Count how many times a value is associated with another value
- Count how many unique values are associated with a value
- Identify the most and least prevelant values that are associated with another value
- Calculate averages of each capture group

# Input

Accepts any text, no spesific structure required. The beauty of REGEX is that so long as there is some structure of any kind, you can parse it.

# Arguments
-n \<x> : Print the top x results. Defaults to 10  
-b : Print the bottom results instead of the top  
-v : Print all results  
-g \<group 1> \<group 2, optional> : Spesifies the capture group indicies you want to process   
--csv \<outputfile> : Export the full output to a CSV

# Usage
Extract all users from the log. Show top 20 users, unique users, 
as well as how many times each user appears
```python
correlog.py logs.txt "user=(\w+)" -g 1 -n 20
```
Extract all status codes and show the least frequent status codes
```python
correlog.py logs.txt "status=(\d+)" -g 1 -b
```
Extract all the IPs and ports. Show which ports are associated
with which IPs. Show the most and least common IP:Port combinations
Show which IP has the most and least associated ports
```python
correlog.py logs.txt "(\d+\.\d+\.\d+\.\d+):(\d+)" -g 1 2
```
# Todo

- [ ] Document :)  
- [ ] Fix broken -v  
- [ ] Make REGEX multiline so you can correlate matches from diffrent lines. Ensure that this function is optionally enabled via argument as it will make REGEX creation harder  
- [ ] Make averages work for floats, not just ints  
- [ ] If a group is entirely ints / floats, add another output which sorts by matched value, not occurance count
- [ ] Make --csv confirm before overwriting a file  
