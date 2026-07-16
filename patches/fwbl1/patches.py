# Label: [Original, Patched]

FWBL1_PATCHES = {
    "Disable EPBL signature verification": ["EB 03 05 2A E8 03 04 AA E9 03 03 2A EA 03 02 AA EC 03 00 2A", "00 00 80 52 C0 03 5F D6"], # Force return 0
    "Disable Anti RollBack checks": ["FF 83 00 D1 F3 7B 01 A9", "20 00 80 52 C0 03 5F D6"] # Force return 1
}
