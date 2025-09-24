# Commonizes the batching / concatenating of slippi files
#
# This renders by "set," which will be slightly slower on average than rendering
# all videos then concat-ing when the set is finished, but has a few upsides:
#
#   1. Reduces memory usage
#   2. Simplifies implementation

import concurrent.futures
import dataclasses
import enum

import pathlib
import tempfile

import slp2mp4.ffmpeg as ffmpeg
import slp2mp4.video as video
from slp2mp4.output import Output


def render_and_concat(executor: concurrent.futures.Executor, conf: dict, output: Output):
    futures = {i: executor.submit(render, conf, i) for i in output.inputs}
    concurrent.futures.wait(futures.values())
    tmp_paths = [futures[i].result() for i in output.inputs]
    concat(conf, output.output, tmp_paths)

def render(conf: dict, slp_path: pathlib.Path):
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp_path = pathlib.Path(tmp.name)
    video.render(conf, slp_path, tmp_path)
    tmp.close()
    return tmp_path

def concat(conf: dict, output_path: pathlib.Path, renders: list[pathlib.Path]):
    Ffmpeg = ffmpeg.FfmpegRunner(conf)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Ffmpeg.concat_videos(renders, output_path)
    for render in renders:
        render.unlink()

def run(conf: dict, outputs: list[Output]):
    num_procs = conf["runtime"]["parallel"]
    with concurrent.futures.ProcessPoolExecutor(num_procs) as executor:
        for output in outputs:
            render_and_concat(executor, conf, output)
