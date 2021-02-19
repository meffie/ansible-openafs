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

import click
import yaml

from afs_scenario.util import NestedDict

def get_str(ctx, key, default):
    """
    Prompt for a string value.
    """
    try:
        value = ctx[key]
    except KeyError:
        prompt = key.replace('.', ' ').replace('_', ' ').capitalize()
        value = click.prompt(prompt, default=default)
    return value

def get_int(ctx, key, default):
    """
    Prompt for an int value.
    """
    try:
        value = ctx[key]
    except KeyError:
        prompt = key.replace('.', ' ').replace('_', ' ').capitalize()
        value = click.prompt(prompt, type=int, default=default)
    return value

def get_choice(ctx, key, choices, default=None):
    """
    Select a value from a list of choices.
    """
    try:
        value = ctx[key]
    except KeyError:
        prompt = key.replace('.', ' ').replace('_', ' ')
        prompt = ['Choose %s' % prompt]
        options = {}
        di = 1
        for i, c in enumerate(choices, 1):
            prompt.append('%d - %s' % (i, c))
            options[str(i)] = c
            if c == default:
                di = i
        prompt.append('')
        prompt = '\n'.join(prompt)
        choice = click.Choice(options.keys())
        selected = click.prompt(prompt, type=choice, show_choices=False, default=str(di))
        value = options[selected]
    return value

def get_driver_str(ctx, key, defaults):
    """
    Prompt for a driver string option.
    The default value depends on the driver name.
    """
    if ctx['driver.name'] == 'vagrant':
        default = defaults[0]
    elif ctx['driver.name'] == 'delegated':
        default = defaults[1]
    else:
        default = ''
    return get_str(ctx, key, default)

def get_delegated_option(ctx, key, default):
    """
    Prompt for a delegated driver string option.
    """
    if ctx['driver.name'] != 'delegated':
        return None # skip
    return get_str(ctx, key, default)

def get_connection(ctx, key, choices):
    """
    Prompt for the delegated connection option.
    """
    if ctx['driver.name'] != 'delegated':
        return None # skip
    if ctx['driver.options.host'] == 'localhost':
        default = 'local'
    else:
        default = 'ssh'
    return get_choice(ctx, key, choices, default)

def get_port(ctx, key, default):
    """
    Prompt for the delegated port option.
    """
    if ctx['driver.name'] != 'delegated':
        return None # skip
    if ctx['driver.options.connection'] != 'ssh':
        return None # skip
    return get_int(ctx, key, default)

def parse_options(ctx, param, values):
    """
    Parse the --option list.
    """
    try:
        options = []
        for value in values:
            k, v = value.split('=', 1)
            options.append((k, v))
        return options
    except ValueError:
        raise click.BadParameter('values must be in the form "<name>=<value>"')


@click.command()
@click.option('-l', '--list-keys', is_flag=True, help='List option keys and exit')
@click.option('-c', '--config', type=click.Path(), envvar='AFS_SCENARIO_CONFIG', help='Output file')
@click.option('-o', '--option', 'options', multiple=True, callback=parse_options, metavar='<key>=<value>',
              help='Options in the form <key>=<value>')
def configure(list_keys, config, options):
    """
    Create afs-scenario configuration.
    """
    keys = [
        ('driver.name', get_choice, ['vagrant', 'delegated']),
        ('driver.provider', get_driver_str, ['', 'libvirt']),
        ('driver.options.host', get_delegated_option, 'localhost'),
        ('driver.options.connection', get_connection, ['local', 'ssh']),
        ('driver.options.port', get_port, 22),
        ('driver.options.loglevel', get_delegated_option, 'info'),
        ('driver.options.python_interpreter', get_delegated_option, '/usr/bin/python3'),
        ('platforms.instance_prefix', get_str, ''),
        ('platforms.image_type', get_driver_str, ['box', 'template']),
        ('platforms.images.centos7.name', get_driver_str, ['generic/centos7', 'generic-centos-7']),
        ('platforms.images.centos8.name', get_driver_str, ['generic/centos8', 'generic-centos-8']),
        ('prepare.import_playbook', get_str, ''),
    ]

    if list_keys:
        for key, fn, args in keys:
            click.echo(key)
        return 0

    if not config:
        raise click.BadParameter('Specify --config or set AFS_SCENARIO_CONFIG env var.')

    ctx = NestedDict()
    for name, value in options:
        ctx[name] = value
    for key, fn, args in keys:
        value = fn(ctx, key, args)
        if value:
            ctx[key] = value

    with open(config, 'w') as fh:
        yaml.dump(ctx.d, fh, explicit_start=True)
        click.echo('Wrote: %s' % config)
