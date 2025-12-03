# HTTPS Setup with Caddy

This guide explains how to enable HTTPS for epdtext-web using Caddy as a reverse proxy.

## Why Caddy?

- **Automatic HTTPS**: Caddy automatically obtains and renews SSL/TLS certificates
- **Simple configuration**: Minimal setup required
- **Tailscale integration**: Works seamlessly with Tailscale hostnames
- **Production-ready**: High performance reverse proxy

## Prerequisites

- epdtext-web running on port 5000
- Tailscale installed and connected
- Your Raspberry Pi accessible via Tailscale hostname (e.g., `pi4.tailnet-name.ts.net`)

## Quick Installation

### Option 1: Automated Script (Recommended)

```bash
cd /home/pi/epdtext-web
chmod +x install-caddy.sh
sudo ./install-caddy.sh
```

The script will:
1. Install Caddy from official repository
2. Auto-detect your Tailscale hostname
3. Configure Caddy with the provided Caddyfile
4. Enable and start the service
5. Show access URLs and useful commands

### Option 2: Manual Installation

#### 1. Install Caddy

```bash
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Add Caddy repository
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
    sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
    sudo tee /etc/apt/sources.list.d/caddy-stable.list

sudo apt update
sudo apt install caddy
```

#### 2. Get your Tailscale hostname

```bash
tailscale status
# Look for your hostname (e.g., pi4.tailnet-name.ts.net)
```

#### 3. Configure Caddy

```bash
# Backup existing config
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup

# Copy new config
sudo cp /home/pi/epdtext-web/Caddyfile /etc/caddy/Caddyfile

# Edit and replace {$TAILSCALE_HOSTNAME:localhost} with your actual hostname
sudo micro /etc/caddy/Caddyfile
```

#### 4. Create log directory

```bash
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy
```

#### 5. Start Caddy

```bash
sudo systemctl enable caddy
sudo systemctl restart caddy
sudo systemctl status caddy
```

## Accessing Your App

After installation:

- **Via Tailscale (HTTPS)**: `https://your-hostname.ts.net`
- **Local (HTTP)**: `http://localhost:5000` or `http://192.168.x.x:5000`

Both will prompt for HTTP Basic Auth credentials (from your `app.cfg`).

## How It Works

```
Internet/Tailscale
       ↓
   Caddy (port 443 HTTPS)
       ↓
 epdtext-web (port 5000 HTTP)
       ↓
   Message Queue
       ↓
   epdtext daemon
```

Caddy handles:
- SSL/TLS termination
- Certificate management
- Secure headers (HSTS, XSS protection, etc.)
- Reverse proxy to epdtext-web

## Certificate Management

### Using Tailscale Certificates (Alternative)

If you prefer to use Tailscale's built-in HTTPS certificates:

```bash
# Get certificate from Tailscale
tailscale cert your-hostname.ts.net

# Certificates will be in /root/.local/share/tailscale/certs/
```

Then modify Caddyfile:
```
your-hostname.ts.net {
    tls /root/.local/share/tailscale/certs/your-hostname.ts.net.crt \
        /root/.local/share/tailscale/certs/your-hostname.ts.net.key
    reverse_proxy localhost:5000
}
```

### Using Let's Encrypt (Public Internet)

If your Pi is exposed to the public internet (not just Tailscale), Caddy will automatically use Let's Encrypt. Just use your public domain in the Caddyfile.

## Monitoring and Logs

```bash
# Check Caddy status
sudo systemctl status caddy

# View Caddy system logs
sudo journalctl -u caddy -f

# View access logs
sudo tail -f /var/log/caddy/epdtext-web.log

# Test configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload configuration without downtime
sudo systemctl reload caddy
```

## Troubleshooting

### Caddy won't start

Check logs:
```bash
sudo journalctl -u caddy -n 50
```

Validate config:
```bash
sudo caddy validate --config /etc/caddy/Caddyfile
```

### Certificate errors

For Tailscale hostnames, Caddy uses Tailscale's built-in certificate system. Ensure:
- Tailscale is running: `tailscale status`
- Hostname is correct: Check your Tailscale admin console
- Caddy can access Tailscale: Caddy runs as the `caddy` user

### Can't access via HTTPS

1. Check if Caddy is listening:
   ```bash
   sudo ss -tlnp | grep :443
   ```

2. Test locally:
   ```bash
   curl -k https://localhost
   ```

3. Check firewall (if any):
   ```bash
   sudo iptables -L -n | grep 443
   ```

### Port conflicts

If port 443 is already in use:
```bash
sudo ss -tlnp | grep :443
# Kill the conflicting service or reconfigure it
```

## Security Features

With Caddy enabled, you get:

1. **Automatic HTTPS**: All traffic encrypted
2. **HTTP Basic Auth**: Still enforced by epdtext-web
3. **Security Headers**: HSTS, XSS protection, clickjacking prevention
4. **Modern TLS**: Only secure cipher suites enabled
5. **Automatic certificate renewal**: No manual intervention needed

## Uninstalling

To remove Caddy:

```bash
sudo systemctl stop caddy
sudo systemctl disable caddy
sudo apt remove caddy
sudo rm /etc/apt/sources.list.d/caddy-stable.list
sudo rm /usr/share/keyrings/caddy-stable-archive-keyring.gpg
```

Your epdtext-web will still be accessible on port 5000 without HTTPS.

## Additional Resources

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Tailscale HTTPS Guide](https://tailscale.com/kb/1153/enabling-https/)
- [Reverse Proxy Configuration](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
