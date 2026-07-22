# Label: [Original, Patched]
LK_PATCHES = {
    "Disable download verification": ["a0 02 00 34 60 00 80 52 34 05 00 b0 d5 0d 80 12", "15 00 00 14"],
    "Allow download even when OEM lock is enabled (1)": ["80 35 00 34 01 05 00 f0 e0 03 13 aa 21 c0 08 91 30 7d 01 94", "1f 20 03 d5"],
    "Allow download even when OEM lock is enabled (2)": ["a0 46 00 34 e1 03 13 aa 20 00 80 52 19 0b 00 94 41 63 29 91", "1f 20 03 d5"],
    "Allow download when KG State is Prenormal": ["80 3e f8 37 00 00 80 52", "1f 20 03 d5"],
    "Always allow OEM unlock": ["fd 7b bf a9 00 00 80 52 fd 03 00 91 bb ee ff 97 1f 04 00 71", "20 00 80 52 c0 03 5f d6"],
    "Allow custom binaries to boot under prenormal KG state": ["e0 06 f8 37 00 00 80 52 15 f4 ff 97 e0 02 00 35", "1f 20 03 d5"]
}