#!/bin/bash
set -e

echo "🚀 Deploying Lexio Backend..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential nginx certbot python3-certbot-nginx

# Create user and directories
sudo useradd -m -s /bin/bash lexio || true
sudo mkdir -p /opt/lexio/backend
sudo chown lexio:lexio /opt/lexio/backend

# Copy files (run this from project directory)
sudo cp -r * /opt/lexio/backend/
sudo chown -R lexio:lexio /opt/lexio/backend

# Set up virtual environment
sudo -u lexio python3.11 -m venv /opt/lexio/backend/venv
sudo -u lexio /opt/lexio/backend/venv/bin/pip install -r /opt/lexio/backend/requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/lexio-backend.service > /dev/null <<EOF
[Unit]
Description=Lexio Backend API
After=network.target

[Service]
Type=simple
User=lexio
WorkingDirectory=/opt/lexio/backend
Environment=PATH=/opt/lexio/backend/venv/bin
EnvironmentFile=/opt/lexio/backend/.env
ExecStart=/opt/lexio/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable lexio-backend
sudo systemctl start lexio-backend

# Configure Nginx
sudo tee /etc/nginx/sites-available/lexio-api > /dev/null <<'EOF'
server {
    listen 80;
    server_name api.lexio.co.za;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/lexio-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL with Let's Encrypt (uncomment when DNS is configured)
# sudo certbot --nginx -d api.lexio.co.za --non-interactive --agree-tos -m admin@quikle.co.za

echo "✅ Lexio Backend deployed successfully!"
echo "Health check: curl http://localhost:8000/health"
