#!/usr/bin/python

# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r'''
---
module: openafs_build

short_description: Build OpenAFS binaries from source

description:
  - Build OpenAFS server and client binaries from source code.

  - The source code must be already present in the I(projectdir) directory on
    the host.

  - The M(openafs_build) module will run the OpenAFS C(regen.sh) command, then
    run C(configure) with the given I(configure_options), and then run C(make)
    with the given I(target).  The C(regen.sh) execution is skipped when the
    C(configure) file already exists.  The C(configure) execution is skipped
    when the C(config.status) file already exists.

  - A complete set of build log files are written on the I(logdir) directory on
    the host for build troubleshooting.

  - Out-of-tree builds are supported by specifying a build directory with the
    I(builddir) option.

  - Before the build starts, C(git clean) is run in the I(projectdir) directory to
    remove all untracked files when I(clean) is true and a C(.git) directory is
    found in the C(projectdir). All of the files and directories are removed from
    the I(builddir) when I(clean) is true and an out-of-tree build is being
    done.

  - A check for a loadable kernel module is done after the build completes when
    the I(state) is C(kmodready).  Be sure the I(target) and
    I(configure_options) are set to build a kernel module when using the
    C(mkodready) state.

  - An installation file tree is created in the I(destdir) directory when the
    I(target) starts with C(install) or C(dest). The files in I(destdir) may be
    installed with the M(openafs_install) module.

  - See the C(openafs_devel) role for tasks to install required build tools and
    libraries on various platforms.

requirements:
  - tools and libraries required to build OpenAFS

options:
  state:
    description:
      - C(complete) Run regen.sh, configure, make
      - C(kmodready) After build is complete, also verify a kernel module was
        built for the current running kernel version. Be sure the target
        and configure options are set to build a client when this state is
        in use.
    type: str
    default: complete
    choices:
      - completed
      - kmodready

  projectdir:
    description:
      - The project directory.
      - Source files must have been previously checkout or copied to this path.
    required: true
    type: path

  builddir:
    description:
      - The path for out-of-tree builds.
    default: C(projectdir)
    type: path

  logdir:
    description:
      - The path to store build log files.
      - The logdir may be a subdirectory of the C(projectdir).
      - The logdir may not be a subdirectory of the C(builddir) when doing
        an out-of-tree build.
    type: path
    default: C(projectdir)/.ansible

  clean:
    description:
      - Run C(git clean) in the I(projectdir) when it contains a C(.git) directory.
      - Remove the I(builddir), if different than the I(projectdir).
      - A I(clean) build should be done if the source files in I(projectdir) or
        the I(configure_options) have been changed since the last time
        this module has been run.
      - Use the I(clean) option with caution!
    type: bool
    default: false

  version:
    description:
      - Version string to embed in built files.
      - The I(version) will be written to the C(.version) file, overwritting
        the current contents, if any.
    type: str

  make:
    description:
      - The C(make) program to be executed.
    type: path
    default: detect

  target:
    description:
      - The make target to be run.
    type: str

  jobs:
    description:
      - Number of parallel make processes.
      - Set this to 0 to disable parallel make.
    default: the number of CPUs on the system
    type: int

  manpages:
    description:
      - Generate the man-pages from POD files when running C(regen).
    default: true
    type: bool

  destdir:
    description:
      - The destination directory for C(install) and C(dest) targets and variants.
      - The tree staged in this directory may be installed with the M(openafs_install) module.
    default: I(projectdir)/packaging/dest
    type: path

  configure_options:
    description:
      - The C(configure) options, as a dictionary.
      - Provide only one of I(configure_options) or I(configure_options_str).
    type: dict

  configure_options_str:
    description:
      - The C(configure) arguments, as a string of command line options.
      - Provide only one of I(configure_options) or I(configure_options_str).
    type: dict

author:
  - Michael Meffie (@meffie)
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_build:
    projectdir: ~/src/openafs

- name: Build OpenAFS server binaries for RHEL
  openafs_build:
    state: completed
    projectdir: ~/src/openafs
    clean: yes
    target: install_nolibafs
    destdir: packaging/dest
    configure_options:
      prefix: /usr
      bindir: /usr/bin
      libdir: /usr/lib64
      sbindir: /usr/sbin
      disable:
        - strip_binaries
        - kernel_module
      enable:
        - debug
        - redhat_buildsys
        - transarc_paths
      with:
        - krb5: /path/to/krb5.lib
      with_linux_kernel_packaging: true
      with_swig: true
  register: build_results
  when: ansible_os_family == 'RedHat'

- name: Build OpenAFS legacy distribution
  openafs_build:
    state: kmodready
    projectdir: ~/src/openafs
    clean: yes
    target: dest
    configure_options:
      enable:
        - debug
        - transarc_paths
        - kernel_module
      with:
        - linux_kernel_packaging

- name: Build OpenAFS with configure options as a string
  openafs_build:
    projectdir: /tmp/openafs/myfiles
    destdir: /tmp/openafs/mydest
    clean: yes
    target: install
    configure_options_str: "--enable-debug --enable-kernel-module"
'''

RETURN = r'''
msg:
  description: Informational message.
  returned: always
  type: string
  sample: Build completed

projectdir:
  description: Absolute path to the project directory.
  returned: always
  type: string
  sample: /home/tycobb/projects/myproject

builddir:
  description: Absolute path to the build directory
  returned: always
  type: string
  sample: /home/tycobb/projects/myproject

destdir:
  description: Absolute path to the installation files.
  returned: when C(destdir) is specified
  type: string
  sample: /home/tycobb/projects/myproject/packaging/dest

logdir:
  description: Absolute path to the log files. Maybe used for M(openafs_install).
  return: always
  type: string
  sample: /home/tycobb/projects/myproject/.ansible

logfiles:
  description: Log files written for troubleshooting
  returned: always
  type: list
  sample:
    - /tmp/logs/build.log
    - /tmp/logs/make.out
    - /tmp/logs/make.err

kmods:
  description: The list of kernel modules built, if any.
  returned: success
  type: list
  sample:
    - /home/tycobb/projects/myproject/src/libafs/MODLOAD-5.1.0-SP/openafs.ko
'''

import glob
import logging
import os
import platform
import pprint
import re
import shlex
import shutil
from multiprocessing import cpu_count
from ansible.module_utils.basic import AnsibleModule


class FileError(Exception):
    pass

def copy_tree(src, dst):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :returns: a list of files/symlinks created
    """
    outputs = []
    if not os.path.isdir(src):
        raise FileError("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except os.error:
        raise FileError("error listing files in '%s'" % src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            os.symlink(link_dest, dst_name)
            outputs.append(dst_name)
        elif os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name))
        else:
            shutil.copy2(src_name, dst_name)
            outputs.append(dst_name)
    return outputs

def abspath(base, rel):
    """ Get absolute path name relative to a base directory. """
    prev = os.getcwd()
    os.chdir(base)
    path = os.path.abspath(rel)
    os.chdir(prev)
    return path

def tail(s, n=256):
    """ Get the last n chars of a string. """
    if len(s) <= n:
        return s
    else:
        return s[-n:]

def run_command(name, command, cwd, module, logger, logdir, results):
    """Run a command and log the stdout and stderr.

    :arg command: command argument list
    :arg cwd: current directory to run the command
    :arg module: the ansible module object
    :arg logger: the logger object
    :arg logdir: where to place stdout and stderr logs
    :arg results: the module results dictionary
    """
    logger.info('Running: cd %s; %s' % (cwd, ' '.join(command)))
    rc, out, err = module.run_command(command, cwd=cwd)
    logfile_out = os.path.join(logdir, '%s.out' % name)
    with open(logfile_out, 'w') as f:
        f.write(out)
        results['changed'] = True
        results['logfiles'].append(logfile_out)
    logfile_err = os.path.join(logdir, '%s.err' % name)
    with open(logfile_err, 'w') as f:
        f.write(err)
        results['changed'] = True
        results['logfiles'].append(logfile_err)
    if rc != 0:
        logger.error('%s failed; rc=%d' % (name, rc))
        module.fail_json(
            msg='%s command failed. See log files %s and %s' % \
                (name, logfile_out, logfile_err),
            rc=rc,
            stdout=tail(out),
            stderr=tail(err),
        )

def _od2a(options, prefix=None):
    args = []
    for k, v in options.items():
        if prefix:
            args.append(_o2a(k, v, prefix=prefix))
        elif k in ('enable', 'disable', 'with', 'without'):
            if isinstance(v, dict):
                args.extend(_od2a(v, prefix=k))
            elif isinstance(v, list):
                args.extend(_ol2a(v, prefix=k))
            else:
                args.append(_o2a(v, prefix=k))
        else:
            args.append(_o2a(k, v))
    return args

def _ol2a(options, prefix=None):
    args = []
    for v in options:
        if isinstance(v, dict):
            args.extend(_od2a(v, prefix=prefix))
        else:
            args.append(_o2a(v, prefix=prefix))
    return args

def _o2a(name, value=None, prefix=None):
    if prefix:
        name = '%s-%s' % (prefix, name)
    if not value:
        arg = '--%s' % name
    elif isinstance(value, (dict, list)):
        raise ValueError('Unexpected dict or list: %s' % name)
    elif value is True:
        arg = '--%s' % (name)
    else:
        arg = '--%s=%s' % (name, value)
    return arg

def options_to_args(options):
    """ Convert option dictionary to a list of command line arguments.

    Special handling for the enable, disable, with, without keys. Treat
    these keys (at just the top-level) as a tree of options so we can make
    the yaml look nicer.
    """
    args = []
    if isinstance(options, dict):
        args.extend(_od2a(options))
    elif isinstance(options, list):
        args.extend(_ol2a(options))
    else:
        args.append(_o2a(options))
    return args

def configured_sysname(builddir):
    """ Get the afs sysname from the results of configure.

    :arg builddir: the location of the configure log
    :returns: the afs sysname value or None if not found
    """
    config_log = os.path.join(builddir, 'config.log')
    with open(config_log) as f:
        for line in f.readlines():
            m = re.match(r"AFS_SYSNAME='([^']*)'", line)
            if m:
                return m.group(1)
    return None

def main():
    logger = logging.getLogger(__name__)
    results = dict(
        changed=False,
        ansible_facts = {},
        msg='',
        projectdir=None,
        logfiles=[],
        kmods=[],
    )
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['completed', 'kmodready'], default='completed'),
            projectdir=dict(type='path', required=True),
            builddir=dict(type='path'),
            logdir=dict(type='path'),
            clean=dict(type='bool', default=False),
            version=dict(type='str'),
            make=dict(type='path'),
            target=dict(type='str'),
            jobs=dict(type='int', default=cpu_count()),
            manpages=dict(type='bool', default=True),
            destdir=dict(type='path'),
            configure_options=dict(type='dict'),
            configure_options_str=dict(type='str'), # alternative
        ),
        mutually_exclusive=[['configure_options', 'configure_options_str']],
        supports_check_mode=False,
    )

    state = module.params['state']
    projectdir = module.params['projectdir']
    builddir = module.params['builddir']
    logdir = module.params['logdir']
    clean = module.params['clean']
    version = module.params['version']
    make = module.params['make']
    target = module.params['target']
    jobs = module.params['jobs']
    manpages = module.params['manpages']
    destdir = module.params['destdir']
    configure_options = module.params['configure_options']
    configure_options_str = module.params['configure_options']

    if not (os.path.exists(projectdir) and os.path.isdir(projectdir)):
        module.fail_json(msg='projectdir directory not found: %s' % projectdir)
    results['projectdir'] = os.path.abspath(projectdir)

    #
    # Setup logging
    #
    if not logdir:
        logdir = os.path.join(projectdir, '.ansible')
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
        results['changed'] = True

    if logdir and os.path.isdir(logdir):
        results['logdir'] = logdir
        results['ansible_facts']['afs_build_logdir'] = logdir
        build_log = os.path.join(logdir, 'build.log')
        logging.basicConfig(
            level=logging.INFO,
            filename=build_log,
            format='%(asctime)s %(levelname)s %(message)s',
        )
        results['logfiles'].append(build_log)

    logger.info('Starting build')
    logger.debug('Parameters: %s' % pprint.pformat(module.params))

    #
    # Setup paths.
    #
    if builddir:
        builddir = abspath(projectdir, builddir)
    else:
        builddir = projectdir
    results['builddir'] = builddir
    logger.debug("builddir='%s'", builddir)

    gitdir = os.path.abspath(os.path.join(projectdir, '.git'))
    if not (os.path.exists(gitdir) and os.path.isdir(gitdir)):
        gitdir = None
    logger.debug("gitdir='%s'.", gitdir)

    #
    # Don't bother doing a build on a unchanged, clean git repo.
    #
    git_sha1 = None
    git_sha1_file = os.path.join(logdir, 'git_sha1')
    destdir_file = os.path.join(logdir, 'destdir')
    if gitdir:
        git = [module.get_bin_path('git', required=True), 'diff-files', '--quiet']
        rc, out, err = module.run_command(git, cwd=projectdir)
        if rc != 0:
            logger.info('git repo is dirty')
        else:
            git = [module.get_bin_path('git', required=True), 'show-ref', '--hash', 'HEAD']
            rc, out, err = module.run_command(git, cwd=projectdir)
            if rc == 0:
                git_sha1 = out.splitlines()[0]
                logger.info('Current sha1 %s', git_sha1)
                results['git_sha1'] = git_sha1

    if git_sha1 and os.path.exists(git_sha1_file):
        with open(git_sha1_file) as f:
            last_sha1 = f.read().rstrip()
        logger.info('Last sha1 %s', last_sha1)
        if git_sha1 == last_sha1:
            # Retrieve our last destdir for the install task.
            with open(destdir_file) as f:
                last_destdir = f.read().rstrip()
            results['destdir'] = last_destdir
            results['ansible_facts']['afs_build_destdir'] = last_destdir
            logger.info('Skipping build; no changes since last build.')
            results['msg'] = 'Build skipped; no changes since last build.'
            module.exit_json(**results)

    #
    # Cleanup previous build.
    #
    if not clean:
        logger.info('Skipping clean; clean is disabled.')
    else:
        if gitdir:
            clean_command = [
                module.get_bin_path('git', required=True), 'clean',
                '-f', '-d', '-x', '--exclude=.ansible'
            ]
            run_command('clean', clean_command, projectdir, module, logger, logdir, results)
        if builddir != projectdir and os.path.exists(builddir):
            if builddir == '/':
                module.fail_json(msg='Refusing to remove "/" builddir!')
            logger.info('Removing old build directory %s' % builddir)
            shutil.rmtree(builddir)

    #
    # Setup build directory. (This must be done after the clean step.)
    #
    if not os.path.isdir(builddir):
        logger.info('Creating build directory %s' % builddir)
        os.makedirs(builddir)
    if destdir:
        destdir = abspath(builddir, destdir) # makefiles need the full path
        results['destdir'] = destdir
        results['ansible_facts']['afs_build_destdir'] = destdir

    #
    # Set the version string, if supplied.
    #
    if version:
        version_file = os.path.join(projectdir, '.version')
        logger.info('Writing version %s to file %s' % (version, version_file))
        with open(version_file, 'w') as f:
            f.write(version)

    #
    # Run autoconf
    #
    if os.path.exists(os.path.join(projectdir, 'configure')):
        logger.info('Skipping regen; found %s' % os.path.join(projectdir, 'configure'))
    else:
        regen_command = [os.path.join(projectdir, 'regen.sh')]
        if not manpages:
            regen_command.append('-q')
        run_command('regen', regen_command, projectdir, module, logger, logdir, results)

    #
    # Run configure
    #
    if os.path.exists(os.path.join(builddir, 'config.status')):
        logger.info('Skipping configure; found %s' % os.path.join(builddir, 'config.status'))
    else:
        configure_command = [os.path.join(projectdir, 'configure')]
        if configure_options:
            args = options_to_args(configure_options)
        elif configure_options_str:
            args = shlex.split(configure_options_str)
        else:
            args = []
        configure_command.extend(args)
        run_command('configure', configure_command, builddir, module, logger, logdir, results)

    #
    # Run make
    #
    if not make:
        make = module.get_bin_path('make', required=True)
    make_command = [make]
    if jobs > 0:
        make_command.extend(['-j', '%d' % jobs])
    if target:
        make_command.append(target)
    if destdir and not target.startswith('dest'):
        make_command.append('DESTDIR=%s' % destdir)
    run_command('make', make_command, builddir, module, logger, logdir, results)

    #
    # `make` may silently fail to build a kernel module for the running kernel
    # version (or any version). Let's fail early instead of finding out later
    # when we try to start the cache manager.
    #
    kmod_pattern = os.path.join(builddir, 'src', 'libafs', 'MODLOAD-*', '*afs.ko')
    results['kmods'] = glob.glob(kmod_pattern)
    if state == 'kmodready':
        logger.info('Checking for kernel module for %s.' % platform.release())
        modloads = []
        for kmod in results['kmods']:
            pattern = r'/MODLOAD-%s-[A-Z]*/(lib|open)afs\.ko$' % platform.release()
            m = re.search(pattern, kmod)
            if m:
                modloads.append(kmod)
        logger.info('Modules found: %s' % ' '.join(modloads))
        if not modloads:
            results['msg'] = 'Loadable kernel module not found for %s' % platform.release()
            logger.error(results['msg'])
            module.fail_json(**results)

    #
    # Copy the transarc-style distribution tree into a DESTDIR file tree
    # for installation. Put root.server and root.client files into the
    # root directory.
    #
    if destdir and target in ('dest', 'dest_nolibafs', 'dest_only_libafs'):
        logger.info('Copying transarc-style distribution files to %s' % destdir)
        sysname = configured_sysname(builddir)
        if not sysname:
            module.fail_json(msg='Unable to get destdir; sysname not found.')
        dest = os.path.join(builddir, sysname, 'dest')
        if not os.path.isdir(dest):
            module.fail_json(msg='Missing dest directory: %s' % dest)
        for d in ('bin', 'etc', 'include', 'lib', 'man'):
            src = os.path.join(dest, d)
            dst = os.path.join(destdir, d)
            if os.path.isdir(src):
                logger.debug('copy_tree("%s", "%s")' % (src, dst))
                copy_tree(src, dst)
                results['changed'] = True
        for d in ('root.server', 'root.client'):
            src = os.path.join(dest, d)
            dst = destdir
            if os.path.isdir(src):
                logger.debug('copy_tree("%s", "%s")' % (src, dst))
                copy_tree(src, dst)
                results['changed'] = True

    #
    # Copy security key utilities to a standard location.
    #
    if destdir and target in ('install', 'install_nolibafs', 'dest', 'dest_nolibafs'):
        logger.info('Copying security key utilities to %s' % destdir)
        for p in ('asetkey', 'akeyconvert'):
            src = os.path.join(builddir, 'src', 'aklog', p)
            dst = os.path.join(destdir, 'usr', 'sbin')
            if os.path.isfile(src):
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                logger.debug('shutil.copy2("%s", "%s")' % (src, dst))
                shutil.copy2(src, dst)
                results['changed'] = True

    #
    # Save git sha1 for next time.
    #
    if git_sha1:
        with open(git_sha1_file, 'w') as f:
            logger.info("Writing '%s' to file '%s'.", git_sha1, git_sha1_file)
            f.write("%s\n" % git_sha1)
        with open(destdir_file, 'w') as f:
            logger.info("Writing '%s' to file '%s'.", destdir, destdir_file)
            f.write("%s\n" % destdir)

    logger.debug('Results: %s' % pprint.pformat(results))
    results['msg'] = 'Build completed'
    logger.info(results['msg'])

    module.exit_json(**results)

if __name__ == '__main__':
    main()

