Playbooks
=========

The OpenAFS Ansible collection provides a set of playbooks which can be run
directly with ``ansible-playbook`` or imported into your custom playbooks with
the ``ansible.builtin.import_playbook`` module.

To run a playbook from the installed collection:

.. code-block:: console

    $ ansible-playbook openafs_contrib.openafs.<playbook> [options]

where ``<playbook>`` is the name of the playbook without the ``.yaml``
extension.  For playbooks that manage remote hosts, you will likely need to
specify an inventory file using the ``-i`` option.  The `--extra (-e)`` option
can be specified one or more times to override variable default values. See the
playbook ``vars`` section and the roles documentation for more information
about the supported variables.

Development Playbooks
---------------------

These playbooks are designed to be run on the directly on the local machine.
They are generally used for development and testing.

``local_devel.yaml``
   Install development tools on the local machine.

``local_cell.yaml``
   Install and setup Kerberos and OpenAFS clients and servers on the local
   machine to create a simple test realm and cell. This sets up a fully functional
   but non-distributed OpenAFS environment for local testing.

Deployment Playbooks
--------------------

These playbooks require an inventory file specifying the target systems to be
managed by Ansible.

``deploy_realm.yaml``
   Deploy a Kerberos server on a managed node defined in your inventory.
   This playbook also creates principals and keytabs for the AFS service,
   an admin user, and a regular user.

``deploy_cell.yaml``
   Deploy OpenAFS clients and servers on one or more managed nodes and ensure
   the cell has been created. This includes configuring the clients and servers
   and creating the top level volumes. This playbook assumes the Kerberos realm
   is already present and keytabs are available for the AFS service key, an admin
   user, and one regular user.


This is an example inventory file for the deployment playbooks. It shows the
required groups and some important host variables.

.. code-block:: yaml

    all:
      hosts:
        db1:
          ansible_host: 192.168.136.227
        db2:
          ansible_host: 192.168.136.65
        db3:
          ansible_host: 192.168.136.196
        fs1:
          ansible_host: 192.168.136.100
        fs2:
          ansible_host: 192.168.136.27
        fs3:
          ansible_host: 192.168.136.38
        ws1:
          ansible_host: 192.168.136.198
        ws2:
          ansible_host: 192.168.136.22
        ws3:
          ansible_host: 192.168.136.78
      vars:
        afs_install_method: managed
        afs_module_install_method: kmod
        afs_cell: example.com
        afs_realm: EXAMPLE.COM
        afs_user: alice
        afs_admin: admin
        afs_csdb:
          cell: example.com
          desc: Example cell
          hosts:
            - ip: 192.168.136.184
              name: db1
              clone: false
            - ip: 192.168.136.163
              name: db2
              clone: false
            - ip: 192.168.136.61
              name: db3
              clone: false
    afs_kdcs:
      hosts:
        db1:
    afs_databases:
      hosts:
        db1:
        db2:
        db3:
    afs_fileservers:
      hosts:
        fs1:
        fs2:
        fs3:
      vars:
        afs_pseudo_partitions:
          - a
          - b
          - c
    afs_admin_client:
      hosts:
        ws1:
    afs_clients:
      hosts:
        ws1:
        ws2:
        ws3:
