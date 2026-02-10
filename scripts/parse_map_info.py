"""
A script for parsing MapInfo files and potentially writing some data to them.

Assumes it is run from the repository's root directory.
"""


from typing import NamedTuple
import glob
import struct
import json

map_info_files = glob.glob("Maps/ArchipelagoCampaign/*/ap_*.SC2Map/MapInfo", recursive=True)


def unpack_string(contents: bytes, offset: int) -> tuple[str, int]:
    parts = contents[offset:].split(b'\0', 1)
    return parts[0].decode('utf-8'), len(parts[0]) + (len(parts) > 1)


def prettyhex(num: int) -> str:
    if num < 0x10:
        return "0" + hex(num)[2:]
    return hex(num)[2:]


def printable_chr(num: int) -> str:
    if chr(num).isprintable():
        return chr(num)
    return '.'


class Player(NamedTuple):
    player_id: int
    control: int
    colour: int
    faction: str
    unknown: int
    start_point: int
    ai: int
    decal: str


class MapInfo(NamedTuple):
    map_version: int
    checksum: int
    width: int
    height: int
    small_preview_path: str
    large_preview_path: str
    fog_type: str
    tileset: str
    left: int
    bottom: int
    right: int
    top: int
    load_screen_path_offset: int
    load_screen_path_offset_end: int
    load_screen_fit_offset: int
    load_screen_path: str
    load_screen_race: str
    load_screen_fit: int
    data_flags_offset: int
    data_flags: int
    players: list[dict]


class Reader:
    def __init__(self, contents: bytes) -> None:
        self.offset = 0
        self.contents = contents
    def i32(self) -> int:
        result, = struct.unpack_from('<I', self.contents, self.offset)
        self.offset += 4
        return result
    def i16(self) -> int:
        result, = struct.unpack_from('<H', self.contents, self.offset)
        self.offset += 2
        return result
    def i8(self) -> int:
        result, = struct.unpack_from('<B', self.contents, self.offset)
        self.offset += 1
        return result
    def fmt(self, fmt: str, size: int) -> tuple:
        result = struct.unpack_from(fmt, self.contents, self.offset)
        self.offset += size
        return result
    def c4(self) -> str:
        result = b''.join(struct.unpack_from('cccc', self.contents, self.offset)).decode('utf-8')
        self.offset += 4
        return result
    def f32(self) -> float:
        struct.unpack_from('f', self.contents, self.offset)
        self.offset += 4
        return result
    def cstring(self) -> str:
        result, increment = unpack_string(self.contents, self.offset)
        self.offset += increment
        return result
    def nbytes(self, n: int) -> bytes:
        result = self.contents[self.offset:self.offset + n]
        self.offset += n
        return result


def parse_player(reader: Reader) -> Player:
    player_id = reader.i8()
    control = reader.i32()
    colour = reader.i32()
    faction = reader.cstring()
    unknown = reader.i32()
    start_point = reader.i32()
    ai = reader.i32()
    decal = reader.cstring()
    return Player(player_id, control, colour, faction, unknown, start_point, ai, decal)


# Roughly following along view-source:
# (seems old and not very workable) https://repos.sc2mapster.com/sc2/sc2-map-analyzer/trunk/read.cpp
# https://github.com/ggtracker/sc2reader/blob/upstream/sc2reader/objects.py
def process_map_info(filename:str, contents: bytes):
    # Confirmed not in MapInfo:
    # * Suggested Players
    # * Game Minimap Image
    reader = Reader(contents)
    magic = reader.c4()
    assert magic == 'IpaM', (filename, magic)

    map_version = reader.i32()

    # unknown 2 words
    assert map_version >= 0x18
    checksum, unknown0 = reader.fmt('<II', 8)
    assert unknown0 == 0

    width, height = reader.fmt('<II', 8)

    small_preview_path = ''
    small_preview_type = reader.i32()

    if small_preview_type == 2:
        small_preview_path = reader.cstring()

    large_preview_path = ''
    large_preview_type = reader.i32()

    CUTOFF_VERSION = 34

    large_preview_path = reader.cstring()
    
    if map_version <= CUTOFF_VERSION:
        reader.offset += 8
    else:
        reader.offset += 9

    fog_type = reader.cstring()

    tileset = reader.cstring()

    left, bottom, right, top = reader.fmt('<IIII', 4*4)
    assert left < right
    assert bottom < top
    assert top <= height
    assert right <= width

    # some kind of base height value
    reader.offset += 4

    load_screen_type = reader.i32()
    # 0 = melee, 1 = custom
    assert load_screen_type == 1, f'load screen type {load_screen_type} != 1'

    load_screen_path_offset = reader.offset
    load_screen_path = reader.cstring()
    load_screen_path_offset_end = reader.offset

    load_screen_loadbar_type = reader.i16()
    if load_screen_loadbar_type == 0:
        load_screen_race = ''
    else:
        assert load_screen_loadbar_type == 4
        load_screen_race = reader.c4()
        assert load_screen_race in ('Terr', 'Prot', 'Zerg'), (filename, load_screen_race)

    load_screen_fit_offset = reader.offset
    load_screen_fit = reader.i32()

    load_text_position_type = reader.i32()

    load_text_offset_x, load_text_offset_y, load_text_size_x, load_text_size_y = reader.fmt('<IIII', 4*4)
    if map_version >= 39:
        load_screen_custom_layout_file = reader.cstring()
        load_screen_custom_layout_length = reader.i16()
        load_screen_custom_layout_template = reader.nbytes(load_screen_custom_layout_length)
        reader.offset += 2
    elif map_version == 38:
        reader.offset += 3

    data_flags_offset = reader.offset
    data_flags = reader.i32()
    # 0x21 means you don't need to press anything after loading to start
    # print(f"{hex(data_flags):>8} | v{map_version} | {filename}")

    unknown_int1 = reader.i32()  # Usually 1
    unknown_int2 = reader.i32()  # Usually 2
    # print(f"v{map_version} | {unknown_int} | {filename}")
    unknown_range = reader.nbytes(13)  # version >= 0x1f according to sc2reader
    # print(f"v{map_version} | {' '.join(prettyhex(x) for x in unknown_range)} | {filename}")
    # Measurements from last 'Zerg', 'Prot', 'Terr'
    # we are at: 3 * 16 + 1
    if map_version == 0x1f:
        # see prophecy missions
        # 5 * 16 + 5 to player race
        pass
    elif map_version in (0x20, 0x22):
        # see death from above
        # see back in the saddle
        # normally 5 * 16 + 9 to player race
        num_strings = reader.i32()
        mystery_strings = []
        for _ in range(num_strings):
            string1 = reader.cstring()
            reader.offset += 8

            # print(f"{filename}: {string1}")
            mystery_strings.append(string1)
    elif map_version == 38:
        # see forbidden weapon
        # normally 5 * 16 + 14

        # see steps of the rite
        # possible string at 3*16 + 8, controlled by int(1) immediately preceding it
        # See templar's return for an example of 3 strings/structs preceded by int(3)

        num_strings = reader.i32()
        mystery_strings = []
        for _ in range(num_strings):
            string1 = reader.cstring()
            reader.offset += 12
            mystery_strings.append(string1)

        # see into the void
        # 3 * 16 + 8 holds a short length for the string path to loading music
        load_music_string_len = reader.i16()
        assert load_music_string_len < 100
        load_music_file = reader.nbytes(load_music_string_len).decode('utf-8')
    elif map_version == 39:
        # see haven's fall
        # normally 6 * 16

        # string in Brothers in Arms at 3*16+10, immediately preceded by int(1)
        num_strings = reader.i32()
        mystery_strings = []
        for _ in range(num_strings):
            string1 = reader.cstring()
            reader.offset += 12
            mystery_strings.append(string1)

        # string in Amon's Fall at 3*16 + 12
        # interestingly, this is not a null-terminated string;
        # its length is controlled by a short immediately before
        load_music_string_len = reader.i16()
        assert load_music_string_len < 100
        load_music_file = reader.nbytes(load_music_string_len).decode('utf-8')
    else:
        assert False, "Unsupported map file version"

    num_players = reader.i32()
    players = []
    for _ in range(num_players):
        players.append(parse_player(reader))
    # The majority of the bytes remaining are always 0. Only Conviction and Sudden strike have non-zero bytes
    remaining = contents[reader.offset:]
    # if any(x for x in remaining if x != 0):
    #     print(f"v{map_version} | {''.join(prettyhex(x) for x in remaining)} | {filename}")

    return MapInfo(
        map_version,
        checksum,
        width,
        height,
        small_preview_path,
        large_preview_path,
        fog_type,
        tileset,
        left,
        bottom,
        right,
        top,
        load_screen_path_offset,
        load_screen_path_offset_end,
        load_screen_fit_offset,
        load_screen_path,
        load_screen_race,
        load_screen_fit,
        data_flags_offset,
        data_flags,
        [x._asdict() for x in players],
    )


class MapFlag:
    DISABLE_REPLAY_RECORDING = 0x1
    LOADING_SCREEN_WAIT_FOR_KEY = 0x2
    DISABLE_TRIGGER_PRELOADING = 0x4
    ENABLE_STORY_MODE_PRELOADING = 0x8
    USE_HORIZONTAL_FIELD_OF_VIEW = 0x10
    HIDE_ERRORS_DURING_TEST_DOCUMENT = 0x20
    DISABLE_OBSERVERS = 0x40
    # unknown = 0x80
    # unknown = 0x100
    STAGGER_PERIODIC_TRIGGER_EVENTS = 0x200
    # unknown = 0x400
    # unknown = 0x800
    HIDE_ERRORS_DURING_ONLINE_GAME = 0x1000
    SHOW_GAME_START_COOLDOWN = 0x2000
    ALL_UNITS_USE_BASE_HEIGHT = 0x4000
    DISABLE_VIEW_EVERYONE = 0x8000
    DISABLE_TAKE_COMMAND = 0x10000
    DISABLE_RECOVER_GAME = 0x20000


CHECKSUM_DIFFERENCE = {
    MapFlag.HIDE_ERRORS_DURING_TEST_DOCUMENT: -1,
}


def analyze_file(filename: str) -> dict:
    with open(filename, 'rb') as fp:
        contents = fp.read()
    map_info = process_map_info(filename, contents)
    return map_info._asdict()


def update_loading_screen_image(filename: str, new_bg: str) -> None:
    filename = f"Maps/ArchipelagoCampaign/{filename}"
    if not new_bg.lower().startswith("assets"):
        new_bg = f"Assets\\Textures\\{new_bg}"
    DESIRED_FIT = 1
    with open(filename, 'rb') as fp:
        contents = fp.read()
    map_info = process_map_info(filename, contents)
    if map_info.load_screen_path == new_bg and map_info.load_screen_fit == DESIRED_FIT:
        return
    
    path_offset = map_info.load_screen_path_offset

    # find the fit offset
    path_end_offset = map_info.load_screen_path_offset_end
    fit_offset = map_info.load_screen_fit_offset
    remaining_offset = fit_offset + 4

    new_contents = (
        contents[:path_offset]
        + new_bg.encode('utf-8') + b'\0'
        + contents[path_end_offset:fit_offset]
        + struct.pack('<I', DESIRED_FIT)
        + contents[remaining_offset:]
    )
    print(f"Writing {filename}")
    with open(filename, 'wb') as fp:
        fp.write(new_contents)


def set_map_info_flag(filename: str, flag: int, checksum_diff: int) -> None:
    with open(filename, 'rb') as fp:
        contents = fp.read()
    map_info = process_map_info(filename, contents)
    flags = map_info.data_flags
    if (flags & flag) == flag:
        return
    flags |= flag
    checksum = map_info.checksum + checksum_diff
    result_bytes = (
        contents[:8]
        + checksum.to_bytes(4, 'little')
        + contents[12:map_info.data_flags_offset]
        + flags.to_bytes(4, 'little')
        + contents[map_info.data_flags_offset+4:]
    )
    assert len(result_bytes) == len(contents)
    assert contents[map_info.data_flags_offset+4] == result_bytes[map_info.data_flags_offset+4]
    with open(filename, 'wb') as fp:
        fp.write(result_bytes)


def unset_map_info_flag(filename: str, flag: int, checksum_diff: int) -> None:
    with open(filename, 'rb') as fp:
        contents = fp.read()
    map_info = process_map_info(filename, contents)
    flags = map_info.data_flags
    if (flags & flag) == 0:
        return
    flags &= ~flag
    checksum = map_info.checksum - checksum_diff
    result_bytes = (
        contents[:8]
        + checksum.to_bytes(4, 'little')
        + contents[12:map_info.data_flags_offset]
        + flags.to_bytes(4, 'little')
        + contents[map_info.data_flags_offset+4:]
    )
    assert len(result_bytes) == len(contents)
    assert contents[map_info.data_flags_offset+4] == result_bytes[map_info.data_flags_offset+4]
    with open(filename, 'wb') as fp:
        fp.write(result_bytes)


def print_binary_file(filename: str, output_filename: str) -> None:
    with open(filename, 'rb') as fp:
        contents = fp.read()
    with open(output_filename, 'w') as fp:
        for offset in range(0, len(contents), 16):
            line = contents[offset:offset+16]
            fp.write(f'{hex(offset)[2:]:>4} | {" ".join(map(prettyhex, line))} | {" ".join(map(printable_chr, line))}\n')


if __name__ == '__main__':
    result = {}
    for file in map_info_files:
        set_map_info_flag(
            file,
            MapFlag.HIDE_ERRORS_DURING_TEST_DOCUMENT,
            CHECKSUM_DIFFERENCE[MapFlag.HIDE_ERRORS_DURING_TEST_DOCUMENT],
        )
    SUFFIX = '_updated'
    for file in map_info_files:
        map_result = analyze_file(file)
        result[file] = map_result
        print(f"v{map_result['map_version']} | {hex(map_result['data_flags']):>6} | {file}")
    with open("mapinfos.json", 'w') as fp:
        json.dump(result, fp, indent=2)


