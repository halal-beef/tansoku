from postprocess.fwbl1 import post_process_fwbl1
from preprocess.epbl import pre_process_epbl
from postprocess.lk import post_process_lk

from patches.epbl.patches import EPBL_PATCHES
from patches.fwbl1.patches import FWBL1_PATCHES
from patches.lk.patches import LK_PATCHES

START = 0
END = 1
PREPROCESSING = 2
PATCHES = 3
POST_PROCESSING = 4

# Label: Start, End, Preprocessing, Patches, Post Processing
SBOOT_DATA = {
    "fwbl1": [0x0, 0x3000, None, FWBL1_PATCHES, post_process_fwbl1],
    "epbl": [0x3000, 0x16000, pre_process_epbl, EPBL_PATCHES, None],
    "bl2": [0x16000, 0x82000, None, None, None],
    "lk": [0xDB000, 0x35B000, None, LK_PATCHES, post_process_lk],
    "el3_mon": [0x35B000, 0x39B000, None, None, None],
}