from pathlib import Path
from click.testing import CliRunner
from afs_scenario.main import main

def test_configure_interactive_defaults():
    input = ''
    expected_yaml = """\
---
driver:
  name: vagrant
platforms:
  image_type: box
  images:
    centos7:
      name: generic/centos7
    centos8:
      name: generic/centos8
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['configure', '-c', 'output.yml'], input=input)
        assert result.exception is None
        assert result.exit_code == 0
        output = Path('output.yml')
        assert output.is_file()
        assert output.read_text() == expected_yaml

def test_configure_interactive_delegated():
    input = '2\n\nfoo.example.com\n2\n\n\n\nm-\n\n\n\nmyplaybook.yml\n'
    expected_yaml = """\
---
driver:
  name: delegated
  options:
    connection: ssh
    host: foo.example.com
    loglevel: info
    port: 22
    python_interpreter: /usr/bin/python3
  provider: libvirt
platforms:
  image_type: template
  images:
    centos7:
      name: generic-centos-7
    centos8:
      name: generic-centos-8
  instance_prefix: m-
prepare:
  import_playbook: myplaybook.yml
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['configure', '-c', 'output.yml'], input=input)
        assert result.exception is None
        assert result.exit_code == 0
        output = Path('output.yml')
        assert output.is_file()
        assert output.read_text() == expected_yaml
