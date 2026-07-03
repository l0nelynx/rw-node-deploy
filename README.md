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

*   **Ansible** 2.15+
*   **Docker** and **Docker Compose V2** on the target host.
*   **Cloudflare** API Token and Zone ID for automated DNS and SSL management.

## Usage

1. Configure your inventory and variables in `hosts` or `group_vars`.
2. Install external Ansible roles:
   ```bash
   ansible-galaxy install -r requirements.yml -p roles/
   ```
3. Run the deployment:
   ```bash
   ansible-playbook -i inventory.ini deploy.yml
   ```

## Running individual tasks

### Firewall (block_asn)

Downloads ASN blacklists, applies nftables rules, restarts Docker:

```bash
ansible-playbook -i hosts deploy.yml --tags security,firewall
```

### WARP

Installs or updates WARP on hosts with `install_warp=true` in the inventory:

```bash
ansible-playbook -i hosts deploy.yml --tags warp
```

### Preview tasks without executing

```bash
ansible-playbook -i hosts deploy.yml --tags security,firewall --list-tasks
ansible-playbook -i hosts deploy.yml --tags warp --list-tasks
```

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
until Cloudflare accepts one. Only `key` is required — `used_on` and `still_valid`
are back-filled on each run (a rejected key is flagged `still_valid: false` and
skipped thereafter; `used_on` records the hosts a key succeeded on).

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

## License

BSD / MIT
