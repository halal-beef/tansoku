# TODO
# Extract stuff from current image, cut out footer, resign.

import os
import sys

from modules.logger import *

_TONASKET_DIR = os.path.join(os.path.dirname(__file__), "..", "tonasket")
sys.path.insert(0, os.path.abspath(_TONASKET_DIR))

from tonasket.sign_tool import *

import modules.shared_env

def sign_bl1(bl1_file, private_key_path, evt, machine_id, rp_count, stagetwo_tee_key, stagetwo_ree_key, model_id, hmac_path):
    signature_offset = 0x3000 - BL1_FOOTER_OFFSET + 1840

    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    public_key = private_key.public_key()
    padded_pub_key = generate_padded_pub_key(public_key)

    with open(hmac_path, 'rb') as f:
        hmac = f.read()
        f.close()

    log(LogLevel.INFO, "Creating minimal header")
    process_header(bl1_file, 0x3000)

    log(LogLevel.INFO, "Creating partial footer")
    create_partial_footer(bl1_file, evt, machine_id, rp_count, stagetwo_tee_key, stagetwo_ree_key, model_id, padded_pub_key, hmac)

    hash_data = bytes(bl1_file[:signature_offset])
    digest = hashlib.sha512(hash_data).digest()

    log(LogLevel.INFO, f"SHA-512 Digest: {digest.hex()}")

    signature = private_key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA512())))

    r, s = decode_dss_signature(signature)
    sig_blob = generate_padded_signature(r, s)

    log(LogLevel.INFO, "Inserting signature into footer")
    bl1_file[signature_offset:signature_offset + 512] = sig_blob

    log(LogLevel.INFO, "SHA-512 Hashing BL1")
    hash_data = bytes(bl1_file[BL1_HEADER_SIZE:0x3000])
    digest = hashlib.sha512(hash_data).digest()

    log(LogLevel.INFO, f"Final hash: {digest.hex()}")
    log(LogLevel.INFO, "Inserting hash into header")

    bl1_file[0x04:0x08] = struct.pack('<I', struct.unpack('<I', digest[:4])[0])

def post_process_fwbl1(file):
    log(LogLevel.INFO, "Extracting signer info...")

    targ_evt_bytes = file[0x3000 - BL1_SOC_INFO_OFFSET:0x3000 - BL1_SOC_INFO_OFFSET + 2]
    targ_evt = "".join(f"{b:x}" for b in targ_evt_bytes)
    machine_id = int.from_bytes(file[0x3000 - BL1_SOC_INFO_OFFSET + 2:0x3000 - BL1_SOC_INFO_OFFSET + 4], "little")

    rollback_count = int.from_bytes(file[0x3000 - BL1_FOOTER_OFFSET + 16:0x3000 - BL1_FOOTER_OFFSET + 20], "little")
    tee_key = file[0x3000 - BL1_FOOTER_OFFSET + 92:0x3000 - BL1_FOOTER_OFFSET + 616]
    ree_key = file[0x3000 - BL1_FOOTER_OFFSET + 616:0x3000 - BL1_FOOTER_OFFSET + 1140]

    model_id = int.from_bytes(file[0x3000 - BL1_FOOTER_OFFSET + 1268:0x3000 - BL1_FOOTER_OFFSET + 1272], "little")

    log(LogLevel.SUCCESS, "Extracted signer info!")
    print()

    log(LogLevel.INFO, f"Zeroise footer and header")
    file[0x3000 - BL1_FOOTER_OFFSET:0x3000] = b"\x00" * (0x3000 - (0x3000 - BL1_FOOTER_OFFSET))
    file[0:0x10] = b"\x00" * BL1_HEADER_SIZE
    print()

    log(LogLevel.INFO, f"Signer information:")
    log(LogLevel.INFO, f"EVT: {targ_evt}")
    log(LogLevel.INFO, f"Machine ID: 0x{machine_id:x}")
    log(LogLevel.INFO, f"Rollback Count: {rollback_count}")
    log(LogLevel.INFO, f"Model ID: 0x{model_id:x}")
    print()

    log(LogLevel.INFO, "Resigning fwbl1...")

    sign_bl1(file, modules.shared_env.key_file, targ_evt, machine_id, rollback_count, tee_key, ree_key, model_id, modules.shared_env.hmac_file)
    log(LogLevel.SUCCESS, "Successfully resigned fwbl1!")
