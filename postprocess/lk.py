import os

import subprocess

from modules.logger import *

import modules.shared_env

LK_LA = 0xE8000000
EXCEPTION_LOOP_CHECK = 0
INJECTION_POINT = 0
EARLY_INIT_CALLER = 0

def extract_printable_strings(data, min_len = 4):
    strings = []
    current = []

    for byte in data:
        if 0x20 <= byte <= 0x7E:
            current.append(chr(byte))
            continue

        if len(current) >= min_len:
            strings.append("".join(current))

        current = []

    if len(current) >= min_len:
        strings.append("".join(current))

    return strings

def encode_bl(frm, to):
    off = to - frm
    return ((0x94000000 | ((off >> 2) & 0x03FFFFFF)) & 0xFFFFFFFF).to_bytes(4, "little")

def nop(instructions):
    return b"\x1F\x20\x03\xD5" * instructions

def build_lk_payload(firmware_version):
    global INJECTION_POINT
    global EXCEPTION_LOOP_CHECK
    global EARLY_INIT_CALLER

    log(LogLevel.INFO, "Cleaning payload folder...")

    out = subprocess.check_output(["make", "-C", "tansoku-lk", "mrproper"]).decode().strip()

    for line in out.splitlines():
        log(LogLevel.INFO, line)

    print()

    log(LogLevel.INFO, f"Checking if device model is supported...")
    if os.path.exists(f"tansoku-lk/configs/{modules.shared_env.selected_model['model']}"):
        log(LogLevel.SUCCESS, f"Device model {modules.shared_env.selected_model['model']} is supported.")
    else:
        log(LogLevel.ERROR, f"Device model {modules.shared_env.selected_model['model']} is not supported yet.")
        sys.exit(1)

    print()

    log(LogLevel.INFO, f"Checking if firmware version {firmware_version} is supported...")
    if os.path.exists(f"tansoku-lk/configs/{modules.shared_env.selected_model['model']}/{firmware_version}_defconfig"):
        log(LogLevel.SUCCESS, f"Firmware version {firmware_version} is supported.")
    else:
        log(LogLevel.ERROR, f"Firmware version {firmware_version} is not supported yet.")
        sys.exit(1)

    print()

    log(LogLevel.INFO, f"Get injection point base and exception loop check base for firmware {firmware_version} via config...")
    log(LogLevel.INFO, f"Reading config")
    firmware_config_path = f"tansoku-lk/configs/{modules.shared_env.selected_model['model']}/{firmware_version}_defconfig"
    with open(firmware_config_path, "r") as f:
        for line in f:
            if line.startswith("CONFIG_INJECTION_BASE="):
                INJECTION_POINT = int(line.split("=")[1], 16) - LK_LA
                log(LogLevel.INFO, f"Found injection point base: 0x{INJECTION_POINT:x}")
            elif line.startswith("CONFIG_EXCEPTION_LOOP_CHECK_BASE="):
                EXCEPTION_LOOP_CHECK = int(line.split("=")[1], 16) - LK_LA
                log(LogLevel.INFO, f"Found exception loop check base: 0x{EXCEPTION_LOOP_CHECK:x}")
            elif line.startswith("CONFIG_PLATFORM_EARLY_INIT_CALLER_BASE="):
                EARLY_INIT_CALLER = int(line.split("=")[1], 16) - LK_LA
                log(LogLevel.INFO, f"Found early init caller base: 0x{EARLY_INIT_CALLER:x}")

    if INJECTION_POINT == 0 or EXCEPTION_LOOP_CHECK == 0 or EARLY_INIT_CALLER == 0:
        log(LogLevel.ERROR, f"Failed to find one or more required base addresses for firmware {firmware_version} via config.")
        sys.exit(1)

    log(LogLevel.SUCCESS, f"Found injection point base and exception loop check base for firmware {firmware_version} via config.")
    print()

    log(LogLevel.INFO, f"Making config for firmware {firmware_version}...")

    out = subprocess.check_output(["make", "-C", "tansoku-lk", f"DEVICE_MODEL={modules.shared_env.selected_model['model']}", f"{firmware_version}_defconfig"]).decode().strip()

    for line in out.splitlines():
        log(LogLevel.INFO, line)

    print()

    log(LogLevel.INFO, f"Building LK payload for firmware {firmware_version}...")

    # TODO Get system cores and use that for -j
    out = subprocess.check_output(["make", "-C", "tansoku-lk", "-j4"]).decode().strip()

    for line in out.splitlines():
        if line == "Payload built successfully!":
            log(LogLevel.SUCCESS, line)
        else:
            log(LogLevel.INFO, line)

def auto_detect_firmware_version(file):
    log(LogLevel.INFO, "Auto-detecting firmware version...")

    log(LogLevel.INFO, f"BL1 Model ID has indicated this device is a {modules.shared_env.selected_model['name']} (SM-{modules.shared_env.selected_model['model']})")

    log(LogLevel.INFO, f"Searching LK strings for {modules.shared_env.selected_model['model']}...")

    lk_strings = extract_printable_strings(file, 13)
    model_matches = [s for s in lk_strings if modules.shared_env.selected_model['model'] in s]

    if not model_matches:
        log(LogLevel.ERROR, "No matching model strings found in LK.")
        sys.exit(1)

    print()
    log(LogLevel.INFO, f"Firmware version: {model_matches[0]}")

    log(LogLevel.SUCCESS, "Auto-detected firmware version!")

    return model_matches[0]

def post_process_lk(file):
    firmware_version = auto_detect_firmware_version(file)
    print()

    build_lk_payload(firmware_version)
    print()

    log(LogLevel.INFO, "Reading tansoku lk payload...")
    with open("tansoku-lk/payload.bin", "rb") as f:
        payload = f.read()
        f.close()

    log(LogLevel.INFO, f"Payload size: {len(payload)} bytes")
    log(LogLevel.INFO, f"Injecting payload at 0x{INJECTION_POINT:x}...")

    file[INJECTION_POINT:INJECTION_POINT + len(payload)] = payload

    log(LogLevel.INFO, "Patching early init caller jump to payload setup...")
    file[EARLY_INIT_CALLER:EARLY_INIT_CALLER + 4] = encode_bl(EARLY_INIT_CALLER, INJECTION_POINT)

    log(LogLevel.SUCCESS, "Patched LK!")