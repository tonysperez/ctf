# CTF Workbench

A personal collection of scripts, utilities, and resources which I created for CTFs.

## Disclaimer
Programs contained within this repository are intended only for ethical and legal use. I am not responsible for how you use these programs.

## Structure

These scripts are grouped by use case:
- **`password_cracking/`** - Hash cracking, wordlists, formatting
  - **`combinator+`** - Combines 2-3 wordlists like Hashcat's combinator attack mode
  - **`wordlists/`** - Wordlists, typically used for password cracking and enumeration
    - **`verbs.txt`** - List of English verbs
    - **`adjectives.txt`** - List of English adjectives
    - **`nouns.txt`** - List of English  nouns
- **`log_analysis/`** - Parsing and searching logs
  - **`correlog`** - Find total and uniqie matches, correlate multiple fields
- **`network_analysis/`** - Parsing network traffic
- **`misc/`** - Scripts that don’t fit into the above categories

## Goals

- Keep CTF work version-controlled and easy to find
- Maintain a clean library of reusable tools
- Promote small, focused, and readable utilities

## Usage

Most programs here can be run directly with Python but will require arguments. Refer to the program's docstring for details.

## Note
- This repository is a living toolkit and evolves as I complete challenges
- Most of these programs are not as efficient or well-written as they could be. Should you find a program that you want to improve, PRs are welcome!
- These programs are in various states of working-ness. Refer to a programs header for its status
- These programs may be changed, refactored, reorganized, or retired over time
