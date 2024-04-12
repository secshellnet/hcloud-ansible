## Example configuration

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
