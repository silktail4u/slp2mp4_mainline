# Logic for dolphin INIs
# https://github.com/dolphin-emu/fifoci/

import configparser
import contextlib
import pathlib

import slp2mp4.util as util


@contextlib.contextmanager
def make_ini_file(filename: pathlib.Path, contents: dict):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as ini_file:
        ini_parser = configparser.ConfigParser(
            allow_no_value=True, delimiters=("=",), strict=False
        )
        ini_parser.optionxform = lambda option: option
        for section, options in contents.items():
            ini_parser.add_section(section)
            for opt_name, opt_val in options.items():
                ini_parser.set(section, opt_name, opt_val)
        ini_parser.write(ini_file)
        ini_file.flush()
        yield filename, ini_file


@contextlib.contextmanager
def make_dolphin_file(userdir: pathlib.Path):
    # TODO: Try full screen / forced window size for Windows
    settings = {
        # Disables rumble, since it's annoying when rendering replays
        "Core": {
            "AdapterRumble0": "False",
            "AdapterRumble1": "False",
            "AdapterRumble2": "False",
            "AdapterRumble3": "False",
        },
        # Enables dumping frames
        "Movie": {
            "DumpFrames": "True",
            "DumpFramesSlient": "True",
        },
        # Enables dumping audio
        "DSP": {
            "DumpAudio": "True",
            "DumpAudioSilent": "True",
            "Backend": "ALSA",
        },
        "Display": {
            "RenderToMain": "True",
            "RenderWindowAutoSize": "True",
        },
    }
    filename = userdir.joinpath("squashfs-root","usr","bin","Sys","Config", "Dolphin.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name


@contextlib.contextmanager
def make_gfx_file(userdir: pathlib.Path, user_settings):
    # Could use Settings.DumpFramesAsImages, then detect all-black images
    settings = {
        "Settings": {
            "AspectRatio": "0",
            "InternalResolutionFrameDumps": "True",
        },
    }
    util.update_dict(settings, user_settings)
    filename = userdir.joinpath("squashfs-root","usr","bin","Sys","Config", "GFX.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name


@contextlib.contextmanager
def make_gal_file(userdir: pathlib.Path, user_settings):
    settings = {}
    util.update_dict(settings, user_settings)
    filename = userdir.joinpath("squashfs-root","usr","bin","Sys","GameSettings", "GAL.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name


@contextlib.contextmanager
def make_hotkeys_file(userdir: pathlib.Path):
    settings = {
        "Hotkeys1": {
            "Device": "/0/",
        }
    }
    filename = userdir.joinpath("squashfs-root","usr","bin","Sys","Config", "Hotkeys.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name


@contextlib.contextmanager
def make_gecko_file(userdir: pathlib.Path, user_gecko):
    settings = {"Gecko": {}}
    util.update_dict(settings, user_gecko)
    filename = userdir.joinpath("squashfs-root","usr","bin","Sys","GameSettings", "GALE01.ini")
    with make_ini_file(filename, settings) as (name, handle):
        yield name
