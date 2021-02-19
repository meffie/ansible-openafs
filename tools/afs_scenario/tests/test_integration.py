from pathlib import Path
from click.testing import CliRunner
from afs_scenario.main import main
import yaml

def test_integration_default():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        assert result.exit_code == 0
        assert Path('molecule/default/molecule.yml.j2').is_file()

        result = runner.invoke(main, ['render', '-r', '-d', 'molecule'])
        assert result.exit_code == 0
        assert Path('molecule/default/molecule.yml').is_file()

def test_integration_with_data():
    configure_args = [
        'configure',
        '-c', 'data.yml',
        '-o', 'driver.name=delegated',
        '-o', 'driver.provider=libvirt',
        '-o', 'driver.option.host=localhost',
        '-o', 'driver.option.loglevel=info',
        '-o', 'driver.option.python_interpreter=/usr/bin/python3',
        '-o', 'platforms.instance_prefix=m-',
        '-o', 'platforms.images.centos7.name=generic-centos-7',
        '-o', 'platforms.images.centos8.name=generic-centos-8',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        assert result.exception is None
        assert result.exit_code == 0
        assert Path('molecule/default/molecule.yml.j2').is_file()

        result = runner.invoke(main, configure_args)
        assert result.exception is None
        assert result.exit_code == 0
        assert Path('data.yml').is_file()

        result = runner.invoke(main, ['render', '-r', '-d', 'molecule', '-c', 'data.yml'])
        assert result.exception is None
        assert result.exit_code == 0

        assert Path('molecule/default/molecule.yml').is_file()
        molecule = yaml.safe_load(Path('molecule/default/molecule.yml').read_text())
        assert molecule['driver']['name'] == 'delegated'
        assert molecule['driver']['provider']['name'] == 'libvirt'
        assert molecule['platforms'][0]['name'] == 'm-server-01'
        assert molecule['platforms'][0]['template'] == 'generic-centos-8'
