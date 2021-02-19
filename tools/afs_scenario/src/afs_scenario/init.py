# Copyright (c) 2020-2021 Sine Nomine Associates
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Create initial ansible-openafs scenario files."""

from pathlib import Path

import click
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.exceptions import UndefinedVariableInTemplate

def lookup_template(name):
    source = Path(__file__).resolve().parent
    path = source / 'cookiecutter' / name / 'cookiecutter.json'
    if not path.is_file():
        raise LookupError("Template '%s' not found in path '%s'." % (name, path.parent))
    return str(path.parent)

@click.command()
@click.option('-s', '--scenario-name', default='default', help='Scenario name (default: "default")')
@click.option('-r', '--role-name', default='', help='Role name (default: "")')
@click.option('--instance-name', default='server', help='Instance base name (default: "server")')
@click.option('--num-instances', type=int, default=1, help='Number of instances (default: 1)')
@click.option('--os-name', default='centos8', help='OS name (default: "centos8")')
@click.option('--groups', default='', help='Comma separated list of group names (default: "")')
@click.option('--cell', default='example.com', help='Cell name (default: "example.com")')
@click.option('--install-method', default='managed', help='Install method (default: "managed")')
@click.option('--module-install-method', default='dkms', help='Kernel module install method (default: "dkms")')
@click.option('-f', '--force', is_flag=True, help='Overwrite existing files')
def init(**kwargs):
    """
    Create initial scenario templates.
    """
    force = kwargs.pop('force')
    context = kwargs
    molecule_path = Path('./molecule').resolve()
    drivers_path = molecule_path / '__drivers__'

    # Create the molecule directory and common driver files.
    if not drivers_path.is_dir() or force:
        cookiecutter(
            lookup_template('drivers'),
            output_dir=str(molecule_path.parent),
            no_input=True,
            overwrite_if_exists=force)
        click.echo('Initialized: %s/' % (drivers_path))

    # Create scenario files under the existing molecule directory.
    try:
        cookiecutter(
            lookup_template('scenario'),
            output_dir=str(molecule_path),
            no_input=True,
            overwrite_if_exists=force,
            extra_context=context)
        click.echo('Initialized: %s/' % (molecule_path / kwargs['scenario_name']))
        return 0
    except OutputDirExistsException as e:
        click.echo(e, err=True)
        return 1
    except UndefinedVariableInTemplate as e:
        click.echo(e, err=True)
        return 1
