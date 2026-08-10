# Remnanode Deployment Script

A lightweight and efficient deployment script for setting up **Remnanode**, **Nginx**, and **Steal Oneself** protection.

## Overview

This project automates the full stack deployment for a Remnawave node:
*   **Remnanode**: Automated installation, API registration, and container management.
*   **Nginx**: High-performance configuration with Proxy Protocol, SSL, and custom routing.
*   **Steal Oneself**: Automatic generation of a unique decoy (fake) website to enhance server stealth.

## Acknowledgments

This project utilizes the excellent work from the [node-templates](https://github.com/Mrvibecodic/node-templates) repository. We express our sincere gratitude and respect to **[Mrvibecodic](https://github.com/Mrvibecodic)** for providing the high-quality templates and tools used for generating the decoy sites.

## Requirements

*   **Ansible** 2.15+ and the collections in `requirements.yml`.
*   Supported targets: Debian 12/13, Ubuntu 22.04/24.04, and RHEL/Rocky/Alma 9.
*   Docker is installed and managed by the role from Docker's official repository.
*   **Cloudflare** API Token and Zone ID for automated DNS and SSL management.

## Usage

1. Configure your inventory and variables in `hosts` or `group_vars`.
2. Install external Ansible roles:
   ```bash
    ansible-galaxy install -r requirements.yml -p roles/
    ansible-galaxy collection install -r requirements.yml
   ```
3. Run the deployment:
   ```bash
   ansible-playbook -i inventory.ini deploy.yml
   ```

## Tags reference

The deployment is fully tagged, so you can run any subset with `--tags` (or exclude
parts with `--skip-tags`) instead of the whole playbook.

| Tag | Task file | What it does |
|-----|-----------|--------------|
| `warp` | *(play “Install WARP”)* | WireGuard/wgcf install, WARP+ key-pool application, handshake watchdog, and pool persistence. Affects only hosts with `install_warp=true`. |
| `docker` | `install_docker.yml` | Install Docker Engine + Compose v2; add the user to the `docker` group. |
| `repo` | `sync_repo.yml` | Install git/unzip, create the `/opt/nginx` tree, write the nginx `docker-compose.yml`, clone templates, and generate the unique decoy site. |
| `config` | `derive_config.yml`, `build_nginx_conf.yml` | Build nginx **configuration only**: public IP, subdomain list, `default.conf`, `nginx.conf` (no container restart). |
| `nginx` | `collect_pp_flags.yml`, `build_nginx_conf.yml`, `run_nginx.yml` | Everything under `config` **plus** (re)start the nginx container. |
| `sysctl` | `set_sysctl.yml` | Kernel tuning: BBR, buffer sizes, `tcp_fastopen`, optional IPv6 disable. |
| `dns` | `setup_cloudflare.yml` | Create Cloudflare A-records for the reality domain and all subdomains. |
| `certs` | `make_certs.yml` | Generate the self-signed wildcard TLS certificate. |
| `security`, `firewall` | `block_asn.yml` | nftables firewall: ASN blacklists, optional whitelist, IP-restricted panel port, Docker/monitoring rules, and persistence across reboots. Both tags select the same tasks. |
| `remnanode` | `install_remnanode.yml` | Install the remnanode container and register the node with the panel via API. |

> The bootstrap play (installs the SSH service key) is **untagged** and is therefore
> skipped whenever you filter with `--tags`. Fact gathering always runs.

### Examples

```bash
# Full deploy (all tags)
ansible-playbook -i hosts deploy.yml

# Only the firewall
ansible-playbook -i hosts deploy.yml --tags firewall

# Only WARP (hosts with install_warp=true)
ansible-playbook -i hosts deploy.yml --tags warp

# Rebuild nginx config AND restart the container
ansible-playbook -i hosts deploy.yml --tags nginx

# Rebuild nginx config WITHOUT restarting
ansible-playbook -i hosts deploy.yml --tags config

# Everything except cert regeneration
ansible-playbook -i hosts deploy.yml --skip-tags certs

# Preview what a tag would run (no changes)
ansible-playbook -i hosts deploy.yml --tags firewall --list-tasks
```

> `dns`, `config`, and `nginx` calculate their own derived values and can be run
> independently on an already bootstrapped host. The full deploy uses `serial: 1`
> and stops after the first critical failure.

### Firewall: restricting the panel control port

The node's control port (previously hardcoded to `2222`) is opened **only** for trusted
source IPs, via two inventory variables:

```ini
[all:vars]
panel_control_port=2222              # optional, defaults to 2222
panel_control_ip=1.2.3.4             # trusted IP, or a list: [1.2.3.4, 5.6.7.8]
```

If `panel_control_ip` is not set, the port stays closed (secure default). Port `22`
remains open for regular SSH.

## Local configuration files (gitignored)

These files live in the project root, are **not** committed, and are optional.

### `whitelist.nft` — firewall allow-list

If present, its `whitelist_v4` set is loaded before the ASN blacklists and accepted
first in the `prerouting` chain (whitelisted IPs bypass all blacklist drops). If the
file is absent, the firewall play runs normally with no whitelist. Format:

```
table inet filter {
    set whitelist_v4 {
        type ipv4_addr
        flags interval
        elements = { 77.37.128.0/17, 1.2.3.0/24 }
    }
}
```

### `warp_plus.json` — shared WARP+ key pool

A fallback pool of WARP+ license keys. For any host that isn't already WARP+
`unlimited` and has no working per-host `warp_plus` var, keys are tried in order
until Cloudflare accepts one. Only `key` is required — `used_on` is back-filled
after a confirmed successful activation. A failed update does not automatically
invalidate a key, because network and rate-limit failures are indistinguishable
from a bad key; set `still_valid: false` manually when appropriate.

```json
{
  "keys": [
    { "key": "XXXX-YYYY-ZZZZ", "used_on": [], "still_valid": true }
  ]
}
```

Per-host `warp_plus` (set in the inventory) is always tried first; the pool is the fallback.

## WARP watchdog

When `install_warp=true`, a systemd timer (`warp-watchdog.timer`) restarts the `warp`
interface whenever its WireGuard handshake goes stale. The check interval is controlled
by the `warp_watchdog` inventory variable (minutes, default `10`):

```ini
[all:vars]
warp_watchdog=5
```

WARP installation is supported only on Debian/Ubuntu. Setting `install_warp=true`
on an EL host fails before any WARP changes are made.

## Security and lifecycle

The bootstrap play uses SSH `accept-new` only for a host's first connection; all
later plays verify the stored host key. The service key is
`~/.ssh/id_ed25519_rw_deploy`, separate from the operator's master key.

Tokens and passwords may remain in the ignored local inventory by design, but they
are never printed by role tasks. Keep `hosts` and `warp_plus.json` private, rotate
any token that was previously committed or exposed, and use file permissions that
prevent other local users from reading them.

`nginx_image`, `remnanode_image`, `templates_repo_version`, and
`docker_pull_policy` default to `latest/main` behaviour. Each run may therefore
adopt upstream changes. Set them to an explicit tag or digest when reproducibility
is required.

The public deployment knobs are `panel_control_port`, `panel_control_ip`,
`force_reinstall`, `install_warp`, `warp_watchdog`, `warp_watchdog_enabled`,
`pp_map`, `sub_count`, the Cloudflare and Remnawave credentials,
`nginx_image`, `remnanode_image`, `docker_pull_policy`,
`templates_repo_version`, `fake_site_force_regenerate`,
`firewall_public_tcp_ports`, `firewall_public_udp_ports`,
`firewall_blacklist_urls`, and `firewall_whitelist_path`. `force_reinstall`
rotates the managed Remnanode secret, recreates its container, and PATCHes the
existing panel record; it never creates a duplicate record.

The firewall owns the complete target-host ruleset. Each `firewall` run validates a
candidate first, then deliberately executes `flush ruleset`, recreates the managed
`inet filter` table, and restarts Docker so its nftables/NAT chains are rebuilt. A
controller-local `whitelist.nft` can define `whitelist_v4` and optionally
`whitelist_v6` sets in `table inet filter`; it is compiled into that managed table.

## License

BSD / MIT
