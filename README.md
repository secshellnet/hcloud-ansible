# Secure Shell Networks: [Hetzner Cloud](https://www.hetzner.com/cloud) Ansible Inventory

This repository template provides an ansible inventory to manage cloud server in 
hetzner cloud (hcloud). It performes some basic linux hardening (unattended upgrades, 
ssh, fail2ban, ...) and can be extended by roles or tasks to perform whatever you need.

## Getting started
1. Use this template to create your repository and clone it:
   ```shell
   git clone git@github.com:YOUR-USERNAME/hcloud-ansible.git
   ```
2. Create account on [hetzner.cloud](https://console.hetzner.cloud/) and create a new cloud project
3. Create an api token inside this cloud project
   ![Creating an api token in the hetzner cloud console](./img/hetzner-create-api-token.png)
4. Generate a new secret for the ansible vault file (you can use any password generated, store it in `.keys/all`)
   ```shell
   cat /dev/urandom | tr -dc A-Za-z0-9 | fold -w 20 | head -n 1 > .keys/all
   ```
5. Create a new ansible vault
   ```shell
   ansible-vault create group_vars/all/vault
   ```
   with the following content:
   ```yaml
   ---
   hcloud_api_token: "__YOUR_API_TOKEN__"
   worker_password: "__RANDOM_SECRET_PASSWORD__"
   ```
6. Extend the [`inventory.yaml`](./inventory.yaml), it should look for example like this:
   ```yaml
   ---
   all:
     hosts:
       server1:   # default settings if no configuration given
         server_type: cx11
         location: hel1
         image: ubuntu-22.04
         enable_ipv4: false
         enable_ipv6: true
       server2:
         server_type: cx21
         location: fsn1
         image: debian-12
         enable_ipv4: true
         enable_ipv6: true
   ```

7. Install the required ansible and python modules:
   ```shell
   pip3 install ansible ansible-lint passlib>=1.7.4
   ansible-galaxy collection install community.general ansible.posix hetzner.hcloud
   ansible-galaxy role install geerlingguy.postgresql geerlingguy.redis 
   ```
8. Use the ansible inventory:
   ```shell
   ansible-playbook playbook.yaml

   # you can also limit the playbook to one of your hosts
   ansible-playbook playbook.yaml --limit alpha

   # tags can be used to run only specific parts of a playbook
   ansible-playbook playbook.yaml --list-tasks
   ansible-playbook playbook.yaml --limit alpha --tags redis

   # to check wether the system picks up the correct variables you can run
   ansible-inventory --vars --graph

   # make sure to lint your inventory regulary
   ansible-lint
   ```
9. Create a backup of the [`.keys`](./keys/) directory. It contains the key to your vault 
   and the ssh key ansible uses to connect to the cloud servers. For security reasons this 
   directory is excluded from git operations (see [`.gitignore`](./.gitignore)), so by 
   default it will not be pushed to your git repository!

## What about GitOps?
I've tried integrating git ops, but there is one problem: the GitHub actions runner does 
not support ipv6... So you need an ipv4 address on each vm to use git ops for now.

Create the following github actions variables and secrets in your repository and make 
sure to commit and push both your `inventory.yaml` and `group_vars/all/vault` file:
- Variable: `ENABLE_GITOPS` to value `1`
- Secret: `SSH_KEY` to content of [`.keys/id_ecdsa`](./keys/id_ecdsa)
- Secret: `ANSIBLE_KEYS_ALL` to the content of [`.keys/all`](./keys/all)

## Structure

Even though the structure is self explaining here are some comments:
```shell
hcloud-ansible
├── .github                      # github actions workflows
│   └── workflows
│       └── gitops.yaml
├── .keys                        # ssh and ansible vault keys
│   ├── all                      # key for ansible vault for group_vars all
│   ├── id_ecdsa
│   └── id_ecdsa.pub
├── ansible.cfg
├── group_vars
│   └── all
│       ├── vars.yaml            # plaintext global variables
│       └── vault                # encrypted global variables (e. g. hetzner cloud api token)
├── inventory.yaml
├── playbook.yaml
├── roles
│   ├── ansible-role-fail2ban
│   ├── ansible-role-nginx       # our role to install nginx with acme.sh and cf dns integration
│   ├── ansible-role-postgresql  # role to install a postgresql database server
│   └── ansible-role-sshd
├── tasks
│   ├── auto-update.yaml
│   ├── create-worker-user.yaml
│   └── hetzner-cloud.yaml       # task to manage cloud servers and aquire information to connect
└── templates
    └── dnf-automatic.conf.j2
```

TODO explain seq chart

## [Examples](./docs/EXAMPLES.md)
