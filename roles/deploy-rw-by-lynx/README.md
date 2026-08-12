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
