# Security Setup Guide

This guide explains how to set up epdtext-web with proper security permissions.

## Problem

By default, the `epdtext` service creates the `/dev/mqueue/epdtext_ipc` message queue with root-only permissions (600). This prevents the `epdtext-web` service from accessing it when running as the `pi` user.

## Solution

The solution uses a systemd drop-in file that automatically fixes queue permissions after `epdtext` starts, allowing the `pi` user to access it securely.

## Installation Steps

### 1. Make the permission fix script executable

```bash
chmod +x /home/pi/epdtext-web/fix-queue-permissions.sh
```

### 2. Create systemd drop-in directory for epdtext service

```bash
sudo mkdir -p /etc/systemd/system/epdtext.service.d
```

### 3. Install the drop-in configuration

```bash
sudo cp /home/pi/epdtext-web/epdtext.service.d-override.conf \
       /etc/systemd/system/epdtext.service.d/override.conf
```

### 4. Update epdtext-web service file

```bash
sudo cp /home/pi/epdtext-web/epdtext-web.service /etc/systemd/system/
```

### 5. Reload systemd and restart services

```bash
sudo systemctl daemon-reload
sudo systemctl restart epdtext
sudo systemctl restart epdtext-web
```

### 6. Verify everything is working

```bash
# Check epdtext service
systemctl status epdtext

# Check epdtext-web service
systemctl status epdtext-web

# Check queue permissions (should show: -rw-rw---- pi pi)
ls -l /dev/mqueue/epdtext_ipc

# Test the web interface
curl -u username:password http://localhost:5000
```

## How It Works

1. The `epdtext` service starts and creates `/dev/mqueue/epdtext_ipc` with root:root 600 permissions
2. Systemd executes `ExecStartPost=/home/pi/epdtext-web/fix-queue-permissions.sh`
3. The script waits for the queue to appear, then:
   - Changes permissions to 660 (owner+group read/write)
   - Changes group to `pi`
4. Now the `pi` user can access the queue through group membership
5. The `epdtext-web` service can successfully connect to the message queue

## Security Benefits

- **epdtext-web runs as `pi` user** (not root)
- **Queue permissions are 660** (not world-readable 666)
- **Only pi group members** can access the queue
- **HTTP Basic Auth** protects all web routes
- **Input validation** prevents command injection
- **Gunicorn WSGI server** instead of Flask dev server

## Troubleshooting

### Queue permissions reset after reboot

This is expected. The drop-in configuration ensures permissions are fixed automatically when `epdtext` starts.

### epdtext-web can't connect to queue

Check the permissions:
```bash
ls -l /dev/mqueue/epdtext_ipc
```

Should show: `-rw-rw---- 1 root pi`

If not, manually restart epdtext:
```bash
sudo systemctl restart epdtext
```

### Script not executing

Check if the script is executable:
```bash
ls -l /home/pi/epdtext-web/fix-queue-permissions.sh
```

Should show: `-rwxr-xr-x`

Check systemd logs:
```bash
journalctl -u epdtext -n 20
```
