"""Repeat on the test bench: start a FlyScan scan, submit the workflow that selects
the next scan area to an ewoksjob worker, and write this area in the FlyScan configuration.

UNTESTED: requires the SOLEIL fs library and the FlyScan Tango devices.
Set EWOKS_CONFIG_URI to the ewoksjob configuration of the worker, for example scripts/config_redis.py.
"""

import argparse
import logging
import os

from ewoksjob.client import submit
from fs.client import proxy


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("flyscan_config", help="Name of the FlyScan configuration")
    parser.add_argument("pymca_config", help="PyMca configuration file")
    parser.add_argument("processed_dir", help="Directory for the results")
    parser.add_argument("--nscans", type=int, default=3, help="Number of scans")
    parser.add_argument(
        "--server", default="flyscan/core/server.1", help="FlyScan server device"
    )
    args = parser.parse_args()

    fss = proxy.FlyScanServerWrapper()
    fss._logger.setLevel(logging.CRITICAL)
    fss.relocate(args.server)
    fss._logger.setLevel(logging.INFO)

    for _ in range(args.nscans):
        fss.set_cfg(args.flyscan_config)
        fss.start(True)
        filename = list(fss.data_files_list())[-1]
        print("Scan saved in", filename)

        # The worker must see the files at the same paths
        basename = os.path.splitext(os.path.basename(filename))[0]
        processed_dir = os.path.abspath(args.processed_dir)
        # Parameters for the XIA channels 02 and 03, the counter miVtf1,
        # the PI actuators Tx and Tz, and 25 ms of real time per point
        inputs = [
            {"id": "convert", "name": "filename", "value": filename},
            {
                "id": "convert",
                "name": "output_filename",
                "value": f"{processed_dir}/{basename}_bliss.h5",
            },
            {
                "id": "sum",
                "name": "detector_names",
                "value": ["xmap1_det02", "xmap1_det03"],
            },
            {
                "id": "sum",
                "name": "detector_normalization_template",
                "value": "0.025*<instrument/{}/trigger_count_rate>"
                "/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)",
            },
            {
                "id": "sum",
                "name": "output_root_uri",
                "value": f"{processed_dir}/{basename}_xrf.h5::/1.1",
            },
            {
                "id": "fit",
                "name": "config",
                "value": os.path.abspath(args.pymca_config),
            },
            {"id": "fit", "name": "energy_name", "value": "energy"},
            {"id": "norm", "name": "counter_name", "value": "miVtf1"},
            {"id": "regrid", "name": "positioners", "value": ["Tx", "Tz"]},
            {"id": "select", "name": "signal", "value": "Ta_L"},
        ]
        future = submit(
            args=("xrfmap_flyscan_select_area",),
            kwargs={
                "inputs": inputs,
                "load_options": {"root_module": "ewokssoleildemo.workflows"},
            },
        )
        result = future.result()
        print("Next area", result)

        # The positions are in µm. The easy-config has x0 and y0 in mm.
        x0, y0, width, height = result["sample_area"]
        fss.reload_config(args.flyscan_config, False)
        easy_config = getattr(fss.cfgs, args.flyscan_config).easy_config
        easy_config.parameters.sample_area = [x0 / 1000, y0 / 1000, width, height]
        easy_config.parameters.pixel_size_in_um = result["pixel_size"]
        fss.save_config(args.flyscan_config, False)


if __name__ == "__main__":
    main()
