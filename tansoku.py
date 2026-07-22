import os

from modules.logger import *

from modules.sboot_data import *

import modules.shared_env

import subprocess
import datetime

import argparse

ver = subprocess.check_output(["git", "describe", "--always", "--dirty"]).decode().strip()

PATCH_DESC = 0
PATCH_PARAM = 1

PARAM_ORIGINAL = 0
PARAM_REPLACEMENT = 1

def main():
    start = datetime.datetime.now().replace(microsecond=0)

    parser = argparse.ArgumentParser(description="Build system")
    parser.add_argument('-i', '--input', type=str, help="Path to sboot.bin", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to output file", required=True)
    parser.add_argument("-k", "--key", type=str, help="Path to key file", required=True)
    parser.add_argument("-m", "--mac", type=str, help="Path to HMAC file", required=True)

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        log(LogLevel.ERROR, f"Input file not found: {args.input}")
        sys.exit(1)

    if not os.path.isfile(args.key):
        log(LogLevel.ERROR, f"Key file not found: {args.key}")
        sys.exit(1)

    if not os.path.isfile(args.mac):
        log(LogLevel.ERROR, f"HMAC file not found: {args.mac}")
        sys.exit(1)

    if args.input == args.output:
        log(LogLevel.ERROR, "Input and output file cannot be the same!")
        sys.exit(1)

    modules.shared_env.key_file = args.key
    modules.shared_env.hmac_file = args.mac

    log(LogLevel.NORMAL, r'''
         ,_         _,
         |\\.-"""-.//|
         \`         `/
        /    _   _    \
        |    a _ a    |
        '.=    Y    =.'
          >._  ^  _.<
         /   `````   \
         )           (
        ,(           ),
       / )   /   \   ( \
       ) (   )   (   ) (
       ( )   (   )   ( )
       )_(   )   (   )_(-.._
      (  )_  (._.)  _(  )_, `\
       ``(   )   (   )`` .' .'
          ```     ```   ( (`
                         '-'
                         ''')
    log(LogLevel.NORMAL, f"Tansoku build system ({ver})")
    log(LogLevel.NORMAL, f"Build started at {start}")
    print()

    log(LogLevel.INFO, f"Reading sboot.bin from {args.input}...")
    with open(args.input, 'rb') as f:
        sboot_data = bytearray(f.read())
        f.close()
    print()

    for image, params in SBOOT_DATA.items():
        if not params[PREPROCESSING] and not params[PATCHES] and not params[POST_PROCESSING]:
            log(LogLevel.WARN, f"{image} Has no patches nor any processing queued, skipping...")
            print()
            continue

        log(LogLevel.INFO, f"Starting operations on {image}...")

        log(LogLevel.INFO, f"Getting {image} area from sboot.bin...")
        target_area = sboot_data[params[START]:params[END]] 
        log(LogLevel.INFO, f"Extracted area 0x{params[START]:x}-0x{params[END]:x}")

        if params[PREPROCESSING]:
            log(LogLevel.INFO, f"Pre-processing {image}...")
            params[PREPROCESSING](target_area)
            print()

        if params[PATCHES]:
            log(LogLevel.INFO, f"Patching {image}...")
            for patch in params[PATCHES].items():
                log(LogLevel.INFO, f"Applying patch: {patch[PATCH_DESC]}...")
                orig_bytes = bytes.fromhex(patch[PATCH_PARAM][PARAM_ORIGINAL])
                repl_bytes = bytes.fromhex(patch[PATCH_PARAM][PARAM_REPLACEMENT])
                offset = target_area.find(orig_bytes)

                if offset == -1:
                    log(LogLevel.ERROR, f"Could not find pattern: {patch[PATCH_PARAM][PARAM_ORIGINAL]}")
                    log(LogLevel.ERROR, f"Abort!")
                    sys.exit(1)

                log(LogLevel.INFO, f"Found pattern: {patch[PATCH_PARAM][PARAM_ORIGINAL]} at offset 0x{offset:x}")
                log(LogLevel.INFO, f"Replacing with: {patch[PATCH_PARAM][PARAM_REPLACEMENT]}")

                target_area[offset:offset + len(repl_bytes)] = repl_bytes

                log(LogLevel.SUCCESS, "Patch applied successfully!")
                print()

        if params[POST_PROCESSING]:
            log(LogLevel.INFO, f"Post-processing {image}...")
            params[POST_PROCESSING](target_area)
            print()

        log(LogLevel.INFO, f"Inserting {image} into S-Boot image...")
        log(LogLevel.INFO, f"Writing to 0x{params[START]:x}-0x{params[END]:x}, size: 0x{len(target_area):x}")
        sboot_data[params[START]:params[END]] = target_area
        log(LogLevel.SUCCESS, f"Successfully inserted {image} into S-Boot image!")
        print()

    log(LogLevel.INFO, f"Writing output to {args.output}...")
    with open(args.output, 'wb') as f:
        f.write(sboot_data)
        f.close()
    log(LogLevel.SUCCESS, f"Successfully wrote output to {args.output}!")
    print()

    end = datetime.datetime.now().replace(microsecond=0)
    log(LogLevel.NORMAL, f"Build finished at {end} ({end - start} elapsed)")

if __name__ == "__main__":
    main()
