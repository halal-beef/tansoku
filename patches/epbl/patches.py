# Label: [Original, Patched]

EPBL_PATCHES = {
    "Disable Self Decryption": ["39 00 00 94 00 06 81 D2 A0 18 A6 F2 00 10 1E D5 DF 3F 03 D5", "1F 20 03 D5"], # NOP
    "Pre-set decryption markers": ["00 00 00 00 00 00 00 00 45 42 52 45 00 00 00 00 6F A0", "53 55 43 43 00 00 00 00 45 42 52 45 00 00 00 00 00 00"], # Set values dumped from live run
    "Disable signature verification": ["FD 7B BC A9 FD 03 00 91 F5 5B 02 A9 16 14 40 F9 15 18 40 F9", "00 00 80 52 C0 03 5F D6"], # Force return 0
}
