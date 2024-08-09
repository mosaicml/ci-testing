# Copyright 2024 MosaicML CI-Testing authors
# SPDX-License-Identifier: Apache-2.0

import argparse

from mcli import RunStatus, get_run, stop_run, wait_for_run_status

"""Cancel an MCLI run."""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True, help='Name of run')
    args = parser.parse_args()

    run = get_run(args.name)

    print('[GHA] Stopping run.')
    stop_run(run)

    # Wait until run stops
    run = wait_for_run_status(run, status=RunStatus.STOPPED)
    print('[GHA] Run stopped.')
