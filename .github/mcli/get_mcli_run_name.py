# Copyright 2024 MosaicML CI-Testing authors
# SPDX-License-Identifier: Apache-2.0

"""Get run name for MCLI."""

import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='mcli-pytest', help='Base name of run')
    parser.add_argument('--git_branch', type=str, help='Git branch to check out')
    parser.add_argument('--git_commit', type=str, help='Git commit to check out. Overrides git_branch if specified')
    parser.add_argument('--pr_number', type=int, help='PR number to check out. Overrides git_branch/git_commit if specified')

    args = parser.parse_args()

    name = args.name
    if args.git_branch is not None and args.git_commit is None:
        name += f'-branch-{args.git_branch}'
    if args.git_commit is not None:
        name += f'-commit-{args.git_commit}'
    if args.pr_number is not None:
        name += f'-pr-{args.pr_number}'

    # Shorten name if too long
    if len(name) > 56:
        name = name[:56]

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'RUN_NAME={name}', file=fh)
