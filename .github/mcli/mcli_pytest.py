# Copyright 2022 MosaicML CI-Testing authors
# SPDX-License-Identifier: Apache-2.0

"""Run pytest using MCLI."""

import argparse
import os

from mcli import RunConfig, create_run

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='mcli-pytest', help='Base name of run')
    parser.add_argument('--cluster', type=str, default='r1z4', help='Cluster to use')
    parser.add_argument('--gpu_type', type=str, default='a100_40gb', help='Type of GPU to use')
    parser.add_argument('--gpu_num', type=int, default=2, help='Number of GPUs to use')
    parser.add_argument('--image', type=str, default='mosaicml/pytorch:latest', help='Docker image to use')
    parser.add_argument('--git_branch', type=str, help='Git branch to check out')
    parser.add_argument('--git_commit', type=str, help='Git commit to check out. Overrides git_branch if specified')
    parser.add_argument('--git_repo', type=str, help='Git repo to check out')
    parser.add_argument('--git_ssh_clone', type=bool, default=False, help='Whether to use SSH to clone the repo')
    parser.add_argument('--pip_deps', type=str, help='Dependency group to install')
    parser.add_argument('--pip_package_name', type=str, default='', help='Name of pip package to install before running tests')
    parser.add_argument('--pr_number', type=int, help='PR number to check out. Overrides git_branch/git_commit if specified')
    parser.add_argument('--pytest_markers', type=str, help='Markers to pass to pytest')
    parser.add_argument('--pytest_command', type=str, help='Command to run pytest')
    parser.add_argument('--timeout', type=int, default=2700, help='Timeout for run (in seconds)')
    args = parser.parse_args()

    name = args.name
    git_integration = {
        'integration_type': 'git_repo',
        'git_repo': args.git_repo,
        'ssh_clone': str(args.git_ssh_clone),
    }
    if args.git_branch is not None and args.git_commit is None:
        name += f'-branch-{args.git_branch}'
        git_integration['git_branch'] = args.git_branch
    if args.git_commit is not None:
        name += f'-commit-{args.git_commit}'
        git_integration['git_commit'] = args.git_commit

    repo_name = args.git_repo.split('/')[-1]
    command = f'cd {repo_name}'

    # Checkout a specific PR if specified
    if args.pr_number is not None:
        name += f'-pr-{args.pr_number}'
        command += f'''

        git fetch origin pull/{args.pr_number}/head:pr_branch

        git checkout pr_branch

        '''

    # Shorten name if too long
    if len(name) > 56:
        name = name[:56]

    clear_tmp_path_flag = '-o tmp_path_retention_policy=none'
    command += f'''

    export COMPOSER_PACKAGE_NAME='{args.pip_package_name}'

    pip install uv

    uv pip install --system --no-build-isolation .{args.pip_deps}

    export COMMON_ARGS="-v --durations=20 -m '{args.pytest_markers}' {clear_tmp_path_flag}"
    '''

    if args.gpu_num == 1:
        command += f'''
        make test PYTEST='{args.pytest_command}' EXTRA_ARGS="$COMMON_ARGS --codeblocks"
        '''
    else:
        world_size = args.gpu_num
        command += f'''
        make test-dist PYTEST='{args.pytest_command}' EXTRA_ARGS="$COMMON_ARGS" WORLD_SIZE={world_size}
        '''

    command += '''
    python -m coverage combine

    python -m coverage report
    '''
    config = RunConfig(
        name=name,
        compute={
            'cluster': args.cluster,
            'gpu_type': args.gpu_type,
            'gpus': args.gpu_num
        },
        image=args.image,
        integrations=[git_integration],
        command=command,
        scheduling={'max_duration': args.timeout / 60 / 60},
        env_variables=[
            {
                'key': 'MOSAICML_PLATFORM',
                'value': 'False',
            },
            {
                'key': 'PYTHONUNBUFFERED',
                'value': '1',
            },
        ],
    )

    # Create run
    run = create_run(config, timeout=600)
    print(f'[GHA] Run created: {run.name}')

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'RUN_NAME={run.name}', file=fh)
