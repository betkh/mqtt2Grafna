# Environment Setup Guide for Linux/Ubuntu

This guide covers the essential setup steps for running the MQTT2Grafana project on Linux/Ubuntu systems.

## Prerequisites

Before starting, ensure you have:

- Ubuntu 18.04+ or similar Linux distribution
- Python 3.7+ installed
- Docker and Docker Compose installed
- Git installed

## Python Environment Setup

### 1. Install pipx (Recommended Method)

On Linux systems, `pipenv` cannot be installed directly using `pip` like on macOS or Windows. We use `pipx` instead, which installs Python applications in isolated environments.

```bash
# Install pipx
sudo apt update
sudo apt install pipx

# Add pipx to your PATH
 pipx ensurepath

# Restart your terminal or reload shell configuration
source ~/.bashrc  # or source ~/.zshrc for zsh users
```

### 2. Install pipenv

```bash
# Install pipenv using pipx
pipx install pipenv

# Verify installation
pipenv --version
```

### 3. Python Version Management

#### Option A: Using pyenv (Recommended for Multiple Python Versions)

If you need to work with multiple Python versions:

```bash
# Install pyenv dependencies
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to shell configuration
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Restart terminal or reload
source ~/.bashrc

# Install and use Python 3.9+ (recommended)
pyenv install 3.9.18
pyenv global 3.9.18
```

#### Option B: Using System Python

If you see different versions when running these commands:

```bash
python3 --version
python --version
```

Install the `python-is-python3` package to create a symlink:

```bash
sudo apt install python-is-python3
```

This ensures that running `python` in the terminal invokes `python3`.

## Docker Setup

### 1. Install Docker

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Add user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## Project Setup

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd mqtt2Grafna

# Create environment file
cp config/env.example .env

# Install Python dependencies
pipenv install
```

### 2. Start Services

```bash
# Start all Docker services
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Verification

### Check Python Environment

```bash
# Verify pipenv is working
pipenv --version

# Check Python version in virtual environment
pipenv run python --version
```

### Check Docker Services

```bash
# List running containers
docker ps

# Check service logs
docker-compose logs
```

## Troubleshooting

### Common Issues

1. **Permission Denied with Docker**

   ```bash
   # Log out and back in after adding user to docker group
   # Or run: newgrp docker
   ```

2. **pipx not found**

   ```bash
   # Reload shell configuration
   source ~/.bashrc
   ```

3. **Python version conflicts**
   ```bash
   # Use pyenv to manage Python versions
   pyenv versions
   pyenv global 3.9.18
   ```

### Next Steps

After completing this setup:

1. Follow the main [README.md](../README.md) for running the application
2. Check [troubleshooting.md](troubleshooting.md) for common issues
3. Review [bestpractices.md](bestpractices.md) for Docker Compose best practices

## System Requirements

- **Minimum**: 2GB RAM, 10GB free disk space
- **Recommended**: 4GB RAM, 20GB free disk space
- **OS**: Ubuntu 18.04+, Debian 9+, or similar Linux distribution
