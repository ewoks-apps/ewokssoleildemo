"""Scenario A.2 on the test bench: FlyScan scan, XRF processing with ewoksjob,
selection of a new area, and repeat.

UNTESTED: requires the SOLEIL fs library and the FlyScan Tango devices.
Set EWOKS_CONFIG_URI to the configuration of the worker, for example scripts/config_redis.py.
"""

import argparse
import logging
import pathlib

import tango
from ewoksjob.client import submit
from fs.client import proxy

from ewokssoleildemo.apps.xrfmap import WORKFLOW_SELECT_AREA
from ewokssoleildemo.apps.xrfmap import XrfmapParameters
from ewokssoleildemo.apps.xrfmap import xrfmap_arguments

# The workflow gives the area in the units of the positioners: assumed to be um.
# The easy-config expects [x0_in_mm, y0_in_mm, width_in_um, height_in_um].
_POSITION_TO_MM = 1e-3


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("flyscan_config", help="Name of the FlyScan configuration")
    parser.add_argument("parameters", help="JSON file with the processing parameters")
    parser.add_argument("processed_dir", help="Directory for the results")
    parser.add_argument("--nscans", type=int, default=3, help="Number of scans")
    parser.add_argument(
        "--server", default="flyscan/core/server.1", help="FlyScan server device"
    )
    parser.add_argument(
        "--merger", default="flyscan/core/data-merger.1", help="DataMerger device"
    )
    args = parser.parse_args()

    parameters = XrfmapParameters.model_validate_json(
        pathlib.Path(args.parameters).read_text()
    )
    fss = proxy.FlyScanServerWrapper()
    fss._logger.setLevel(logging.CRITICAL)
    fss.relocate(args.server)
    fss._logger.setLevel(logging.INFO)
    merger = tango.DeviceProxy(args.merger)

    for _ in range(args.nscans):
        fss.set_cfg(args.flyscan_config)
        fss.start(True)
        filename = list(merger.outputNexusFiles)[-1]
        print("Scan saved in", filename)

        arguments = xrfmap_arguments(
            filename, args.processed_dir, parameters, select_area=True
        )
        future = submit(args=(WORKFLOW_SELECT_AREA,), kwargs=arguments)
        result = future.result()
        print("Next area", result)

        x0, z0, width, height = result["sample_area"]
        fss.reload_config(args.flyscan_config, False)
        easy_config = getattr(fss.cfgs, args.flyscan_config).easy_config
        easy_config.parameters.sample_area = [
            x0 * _POSITION_TO_MM,
            z0 * _POSITION_TO_MM,
            width,
            height,
        ]
        easy_config.parameters.pixel_size_in_um = result["pixel_size"]
        fss.save_config(args.flyscan_config, False)


if __name__ == "__main__":
    main()
