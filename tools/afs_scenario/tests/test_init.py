from pathlib import Path
from click.testing import CliRunner
from afs_scenario.main import main

def test_init():
    scenario_name = 'test_scenario'
    options = [
        'init',
        '-s', scenario_name,
        '-r', 'test_role',
        '--instance-name', 'test',
        '--num-instances', '1',
        '--os-name', 'test_os',
        '--groups', 'group_a,group_b',
        #'--force',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, options)
        assert result.exit_code == 0

        molecule = Path('molecule')
        scenario = molecule / scenario_name
        drivers = molecule / '__drivers__'
        molecule_yml = scenario / 'molecule.yml.j2'

        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert molecule_yml.is_file()

