# Description

This script preforms the same function as the hashcat Combinator mode. Given 2 or 3 wordlists as input, it will combine every line to every other line (in order) in the wordlists to generate an output wordlist.

I wrote this script because I needed to crack a password where the known format was 3 pieces long, with the last piece being a number. My preffered tool for hash cracking hashcat can either do a combinator of two wordlists, or a mask. Not both. So I created this tool to pre-combinate my wordlists, so Hashcat could just do the mask

# Input

Expects wordlists which have one word per line

# Output

Example output:

```
first1second1third1
first1second1third2
first1second1third3
first1second2third1
first1second2third2
etc, etc
```

# Usage

Usage: 
```python
combinator+.py <wordlist1> <wordlist2> <wordlist3, optional> <output>
```

