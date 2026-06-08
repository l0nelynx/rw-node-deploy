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
2. Run the deployment:
   ```bash
   ansible-playbook -i inventory.ini deploy.yml
   ```

## License

BSD / MIT
