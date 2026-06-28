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

## License

BSD / MIT
