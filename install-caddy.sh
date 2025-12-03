#!/bin/bash
# Install and configure Caddy for epdtext-web HTTPS support

set -e

echo "=== Installing Caddy Web Server ==="

# Install dependencies
echo "Installing dependencies..."
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Add Caddy repository
echo "Adding Caddy repository..."
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# Install Caddy
echo "Installing Caddy..."
sudo apt update
sudo apt install -y caddy

# Get Tailscale hostname
echo ""
echo "=== Configuration ==="
TAILSCALE_HOSTNAME=$(tailscale status --json 2>/dev/null | grep -o '"HostName":"[^"]*"' | cut -d'"' -f4 | head -n1)

if [ -z "$TAILSCALE_HOSTNAME" ]; then
    echo "Warning: Could not auto-detect Tailscale hostname"
    echo "Please enter your Tailscale hostname (e.g., pi4.tailnet-name.ts.net):"
    read TAILSCALE_HOSTNAME
fi

echo "Using hostname: $TAILSCALE_HOSTNAME"

# Backup existing Caddyfile if present
if [ -f /etc/caddy/Caddyfile ]; then
    echo "Backing up existing Caddyfile..."
    sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup.$(date +%s)
fi

# Install new Caddyfile
echo "Installing Caddyfile..."
sudo cp /home/pi/epdtext-web/Caddyfile /etc/caddy/Caddyfile

# Set the hostname in the Caddyfile
sudo sed -i "s/{\$TAILSCALE_HOSTNAME:localhost}/$TAILSCALE_HOSTNAME/" /etc/caddy/Caddyfile

# Create log directory
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy

# Enable and start Caddy
echo "Starting Caddy..."
sudo systemctl enable caddy
sudo systemctl restart caddy

# Wait a moment for Caddy to start
sleep 2

# Check status
echo ""
echo "=== Caddy Status ==="
sudo systemctl status caddy --no-pager || true

echo ""
echo "=== Installation Complete ==="
echo "Caddy is now running and providing HTTPS for epdtext-web"
echo ""
echo "Access your app at:"
echo "  HTTPS: https://$TAILSCALE_HOSTNAME"
echo "  HTTP (local): http://localhost:5000"
echo ""
echo "Check logs with:"
echo "  sudo journalctl -u caddy -f"
echo "  sudo tail -f /var/log/caddy/epdtext-web.log"
echo ""
echo "Test the connection:"
echo "  curl -k https://$TAILSCALE_HOSTNAME"
