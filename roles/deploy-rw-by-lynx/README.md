# deploy-rw-by-lynx

Deploys an nginx stream proxy and a Remnawave v3 node with Docker, DNS
reconciliation, a fully managed nftables ruleset, and optional Debian/Ubuntu WARP.

## Supported platforms

- Debian 12/13 and Ubuntu 22.04/24.04
- RHEL, Rocky Linux, and AlmaLinux 9

WARP is intentionally limited to Debian-family hosts because the external
`warp_native` role does not support EL.

## Required inventory values

`main_domain`, `sub_mask`, `sub_count`, `pp_map`, `rw_endpoint`, `rw_token`,
`rw_config_uuid`, `cf_token`, and `cf_zone_id`. `panel_control_port` defaults to
`2222`; `panel_control_ip` may be one IPv4/IPv6 address or a list.

## Important defaults

- `nginx_image: nginx:alpine`
- `remnanode_image: remnawave/node:latest`
- `custom_core_url`: URL custom Xray core; written as `CUSTOM_CORE_URL` to
  `/opt/remnanode/.env` before Remnanode is started
- `docker_pull_policy: always`
- `templates_repo_version: main`
- `fake_site_force_regenerate: false`
- `firewall_whitelist_path: "{{ playbook_dir }}/whitelist.nft"`
- `firewall_icmp_echo_rate: 10`, `firewall_icmp_echo_burst: 20`
- `firewall_bad_tcp_log_rate: 5`, `firewall_bad_tcp_log_burst: 10`
- `firewall_lock_timeout: 30`, `firewall_rollback_timeout: 120`
- `cf_api_base_url: https://api.cloudflare.com/client/v4`
- `public_ip_lookup_url: https://api.ipify.org`

The role leaves `make_certs.yml` unchanged. Remnanode secrets are written to
`/opt/remnanode/.env` with mode `0600`; API and WARP credentials are redacted from
Ansible output.

`force_reinstall` performs a controlled Remnanode secret rotation and container
recreate while synchronizing the already matching panel node. It is not a
"create another node" switch. The `dns`, `config`, and `nginx` tags include the
derived-address/subdomain work they need; run `repo` once before the first nginx
start so the Compose project and fake site exist.

The firewall drops malformed TCP flag combinations before ASN whitelist handling,
rate-limits only ICMP echo requests per source, and permits essential ICMP/ICMPv6
control traffic. Bad TCP logging is capped per minute; set
`firewall_bad_tcp_log_rate: 0` to keep counter/drop behaviour without journal logs.
Echo rate is measured per source and per second; both firewall timeouts are in
seconds.

Each firewall apply uses an isolated staging directory and a host lock. A transient
systemd timer restores the previous live and persisted rules if a fresh SSH
connection cannot be established after the Docker restart. A successful check
disarms the timer and removes all rollback artifacts.

Before that Docker restart, the role stops a running Remnanode and removes only
its `/dev/shm/tcp_*.socket` files. Other shared sockets are preserved, and a
previously running Remnanode is explicitly restored if Docker does not restart it.
