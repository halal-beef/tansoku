import struct

from modules.logger import *
from Crypto.Cipher import AES

EPBL_KEY = bytes.fromhex("45F5A2F3F2E8C5C234DF481A3D6697FE30244C2F173DC773AC6BDD24087B638E")
EPBL_IV = bytes.fromhex("069F3C80DFBAC1AF5DF0C557712DFE38")

EPBL_LA = 0x02026000

PTR_ENCRYPTED_REGION_START = (0x02031D28 - EPBL_LA)
PTR_ENCRYPTED_REGION_END = (0x02031D50 - EPBL_LA)

def pre_process_epbl(file):
    cipher = AES.new(EPBL_KEY, AES.MODE_CBC, EPBL_IV)

    ENCRYPTED_REGION_START = (struct.unpack("<Q", file[PTR_ENCRYPTED_REGION_START:PTR_ENCRYPTED_REGION_START + 0x0008])[0] - EPBL_LA)
    ENCRYPTED_REGION_END = (struct.unpack("<Q", file[PTR_ENCRYPTED_REGION_END:PTR_ENCRYPTED_REGION_END + 0x0008])[0] - EPBL_LA)

    log(LogLevel.INFO, f"Encrypted region start: {hex(ENCRYPTED_REGION_START)}")
    log(LogLevel.INFO, f"Encrypted region end: {hex(ENCRYPTED_REGION_END)}")
    log(LogLevel.INFO, f"Encrypted region size: {hex(ENCRYPTED_REGION_END - ENCRYPTED_REGION_START)}")
    log(LogLevel.INFO, f"AES Key: {EPBL_KEY.hex()}")
    log(LogLevel.INFO, f"IV: {EPBL_IV.hex()}")

    log(LogLevel.INFO, "Decrypting epbl...")
    decrypted_block = cipher.decrypt(file[ENCRYPTED_REGION_START:ENCRYPTED_REGION_END])
    file[ENCRYPTED_REGION_START:ENCRYPTED_REGION_END] = decrypted_block
    log(LogLevel.SUCCESS, "Successfully decrypted epbl!")
