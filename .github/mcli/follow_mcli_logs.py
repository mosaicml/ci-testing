# Copyright 2024 MosaicML CI-Testing authors
# SPDX-License-Identifier: Apache-2.0

import argparse

from mcli import RunStatus, follow_run_logs, get_run, wait_for_run_status

"""Follow MCLI run logs."""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True, help='Name of run')
    args = parser.parse_args()

    run = get_run(args.name)

    # Wait until run starts before fetching logs
    run = wait_for_run_status(run, status='running')
    print('[GHA] Run started. Following logs...')

    # Print logs
    for line in follow_run_logs(run):
        print(line, end='')

    print('[GHA] Run completed. Waiting for run to finish...')
    run = wait_for_run_status(run, status=RunStatus.COMPLETED)

    # Fail if command exited with non-zero exit code or timed out (didn't reach COMPLETED)
    assert run.status == RunStatus.COMPLETED, f'Run {run.name} did not complete: {run.status} ({run.reason})'
