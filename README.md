# Secure Shell Networks: [Hetzner Cloud](https://www.hetzner.com/cloud) Ansible Inventory

This repository template provides a ansible inventory to manage cloud server in 
hetzner cloud (hcloud). It performes some basic linux hardening (unattended upgrades, 
ssh, fail2ban) and can be extended by roles or tasks to perform whatever you need.

## Getting started
1. Create a reporitory from this template repository and clone it:
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
   ansible-galaxy collection install hetzner.hcloud
   pip3 install -r requirements.txt
   ```
8. Use the ansible inventory:
   ```shell
   ansible-playbook playbook.yaml
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

### [ansible-role-sshd](https://github.com/secshellnet/ansible-role-sshd)

### [ansible-role-fail2ban](https://github.com/secshellnet/ansible-role-fail2ban)

### [ansible-role-nginx](https://github.com/secshellnet/ansible-role-nginx)

### [ansible-role-redis](https://github.com/geerlingguy/ansible-role-redis)

### [ansible-role-postgresql](https://github.com/geerlingguy/ansible-role-postgresql)
```yaml
# host_vars/<hostname>/vars.yaml
---
postgresql_databases:
  - name: nextcloud
    state: present

  # synapse requires lc_collate and lc_ctype to be set to C
  - name: synapse
    lc_collate: C
    lc_ctype: C
    state: present

postgresql_users_u:
  - name: nextcloud
    db: nextcloud
    state: present

  - name: synapse
    db: synapse
    state: present
```

```yaml
# host_vars/<hostname>/vault
---
postgresql_users_e:
  - name: nextcloud
    password: s3cr3t-p4ssw0rd

  - name: synapse
    password: s3cr3t-p4ssw0rd
```

- You can spawn a postgres shell using: `sudo -u postgres psql`.
- Use `\l` to list databases, `\du` to list users and `\dt` to list tables.
- Use `\c <database>` to connect to a database
- You can also connect using tcp (like any other application): 
  `psql -h 127.0.0.1 -U <user> <database>`

## TODO
- run OpenSCAP and check what could be improved (see openscap reports / fixes)
  ```shell
  # on ubuntu:
  sudo apt install libopenscap8
  scp -o "StrictHostKeyChecking=no" -i .keys/id_ecdsa \
    -r ~/OpenSCAP/policies worker@[2a01:4f9:c011:a617::1]:

  # on debian:
  sudo apt install openscap-scanner
  scp -o "StrictHostKeyChecking=no" -i .keys/id_ecdsa \
    -r ~/OpenSCAP/policies worker@[2a01:4f9:c011:a617::1]:

  # on rhel
  sudo dnf install -y openscap-scanner scap-security-guide

  oscap info /usr/share/xml/scap/ssg/content/ssg-debian11-ds.xml
  oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_standard \
    --results-arf arf.xml \
    --report report.html \
    /usr/share/xml/scap/ssg/content/ssg-fedora-ds.xml  # on debian/ubuntu policies/ssg-debian11-ds.xml
  sudo oscap xccdf \
    generate fix \
    --fetch-remote-resources \
    --fix-type ansible \
    --result-id "" \
    arf.xml > fixes.yml
  ```

### think about
- (iptables/firewalld) firewall rules and/or hcloud firewall rules -> integration of hcloud would be independent of distribution -> if we want to support distros like fedora in future it would be better for now
- auditd / rkhunter / AIDE / snort -> how to log it
- disable core dumps via soft / hard limits
- disable unused filesystems (cramfs, freevxfs, jffs2, hfs, hfsplus, udf, squashfs, dccp, rds, sctp, tips)
