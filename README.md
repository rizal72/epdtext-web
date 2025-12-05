# epdtext-web

> **⚠️ DEPRECATED - Project Merged**
>
> This project has been **merged into [paperGate](https://github.com/rizal72/paperGate)**.
>
> **paperGate** is a unified monorepo that combines:
> - `epdtext` - E-paper display daemon
> - `epdtext-web` - Web control interface
> - `epdtext-feed` - RSS feed reader
>
> **Benefits of paperGate:**
> - ✅ Single repository for complete system
> - ✅ Unified configuration (one file for everything)
> - ✅ Improved architecture and documentation
> - ✅ Active development and maintenance
>
> **Please migrate to:** https://github.com/rizal72/paperGate
>
> ---

A modern, secure Flask web application to remotely control [epdtext](https://github.com/tsbarnes/epdtext) e-paper displays on Raspberry Pi.

## Features

- **Modern Web Interface**: Clean, responsive design that works on desktop and mobile
- **Secure by Default**: HTTP Basic Authentication and input validation
- **Production Ready**: Gunicorn WSGI server with proper service management
- **Easy Screen Control**: Navigate, reload, and manage e-paper display screens
- **System Monitoring**: Real-time CPU temperature, network stats, and uptime
- **Optional HTTPS**: Simple setup with Caddy reverse proxy

## Screenshots

The interface features a modern card-based layout with:
- Quick navigation controls (Previous, Reload, Next)
- Hardware button simulation (KEY1-4)
- Screen management (Switch, Add, Remove screens)
- Live system information display

## Security Features

- HTTP Basic Authentication on all routes
- Input validation to prevent command injection
- Runs as non-root user with proper permissions
- Automatic message queue permission management
- Production-grade WSGI server (Gunicorn)

## Prerequisites

- Raspberry Pi with [epdtext](https://github.com/tsbarnes/epdtext) installed and running
- Python 3.7+
- Git and pip3

## Quick Installation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install git python3-pip
```

### 2. Clone Repository

```bash
git clone https://github.com/rizal72/epdtext-web.git /home/pi/epdtext-web
cd /home/pi/epdtext-web
```

### 3. Install Python Packages

```bash
sudo pip3 install -r requirements.txt
```

### 4. Configure Authentication

```bash
# Copy the example configuration
cp app.cfg.example app.cfg

# Edit with your preferred editor
nano app.cfg
```

Set your credentials in `app.cfg`:
```python
# Generate a random secret key
SECRET_KEY = b'your-random-secret-key-here'

# Set your login credentials
AUTH_USERNAME = 'admin'
AUTH_PASSWORD = 'your-secure-password'
```

Generate a secret key with:
```bash
python3 -c 'import os; print(os.urandom(16))'
```

### 5. Setup Secure Permissions

See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed instructions:

```bash
# Make permission script executable
chmod +x fix-queue-permissions.sh

# Install systemd drop-in for queue permissions
sudo mkdir -p /etc/systemd/system/epdtext.service.d
sudo cp epdtext.service.d-override.conf /etc/systemd/system/epdtext.service.d/override.conf

# Install and start service
sudo cp epdtext-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart epdtext
sudo systemctl enable epdtext-web
sudo systemctl start epdtext-web
```

### 6. Verify Installation

```bash
# Check service status
systemctl status epdtext-web

# Verify queue permissions
ls -l /dev/mqueue/epdtext_ipc

# Access the web interface
# http://your-pi-ip:5000
```

You'll be prompted for the username and password you configured in `app.cfg`.

## Optional: Enable HTTPS

For secure access via Tailscale or other networks, see [HTTPS_SETUP.md](HTTPS_SETUP.md):

```bash
chmod +x install-caddy.sh
sudo ./install-caddy.sh
```

## Usage

Once installed, access the web interface at `http://your-raspberry-pi-ip:5000`

### Screen Controls
- **Previous/Next**: Navigate between loaded screens
- **Reload**: Refresh the current screen
- **KEY1-4**: Simulate hardware button presses

### Screen Management
- **Switch Screen**: Change to a specific screen module
- **Add Screen**: Load a new screen module
- **Remove Screen**: Unload a screen module

### System Information
Monitor your Raspberry Pi's health:
- Operating system and model
- CPU temperature (color-coded)
- Network statistics
- Uptime and more

## Configuration

### app.cfg
Main configuration file (not tracked in git):
- `SECRET_KEY`: Flask session secret
- `AUTH_USERNAME`: Login username
- `AUTH_PASSWORD`: Login password

### system.py
System information settings:
- `NETWORK_INTERFACE`: Preferred network interface (default: `wlan0`)
  - Automatically detects active interface (eth0, wlan0, etc.) if configured interface not found
  - No configuration needed for most setups

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl -u epdtext-web -n 50

# Verify permissions
ls -l /dev/mqueue/epdtext_ipc
```

### Can't access message queue
See [SECURITY_SETUP.md](SECURITY_SETUP.md) for permission setup instructions.

### Service not starting on boot
```bash
sudo systemctl enable epdtext-web
sudo systemctl enable epdtext
```

## Development

### Running Locally
```bash
# Development mode
python3 app.py

# Production mode (local testing)
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

### Project Structure
```
epdtext-web/
├── app.py                          # Main Flask application
├── system.py                       # System information module
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   └── index.html                 # Main interface
├── static/
│   └── style.css                  # Modern CSS styling
├── requirements.txt               # Python dependencies
├── epdtext-web.service           # Systemd service file
├── fix-queue-permissions.sh      # Permission management script
└── app.cfg.example               # Configuration template
```

## Documentation

- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Detailed security configuration guide
- [HTTPS_SETUP.md](HTTPS_SETUP.md) - HTTPS setup with Caddy
- `app.cfg.example` - Configuration file template

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project maintains the original license from [tsbarnes/epdtext-web](https://github.com/tsbarnes/epdtext-web).

## Acknowledgments

- Original project by [tsbarnes](https://github.com/tsbarnes)
- Built for [epdtext](https://github.com/tsbarnes/epdtext)
- Modern UI improvements and security enhancements
