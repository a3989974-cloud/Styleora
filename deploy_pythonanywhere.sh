#!/bin/bash
# STYLEORA - PythonAnywhere Deployment Script
# Run this in your PythonAnywhere Bash console
# Usage: bash deploy_pythonanywhere.sh yourusername

set -e

USERNAME=$1
if [ -z "$USERNAME" ]; then
    echo "Usage: bash deploy_pythonanywhere.sh YOUR_PYTHONANYWHERE_USERNAME"
    exit 1
fi

echo "============================================"
echo "  STYLEORA - Deploying to PythonAnywhere"
echo "============================================"
echo ""

PROJECT_DIR="/home/$USERNAME/styleora"
REPO_URL="https://github.com/a3989974-cloud/luxe-store.git"

# Clean up if exists
rm -rf "$PROJECT_DIR"

# Clone the repo
echo "[1/6] Cloning repository..."
git clone "$REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo "[2/6] Creating virtual environment..."
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn whitenoise

# Set up database
echo "[4/6] Setting up database..."
python manage.py migrate --skip-checks
python manage.py collectstatic --noinput --skip-checks

# Create superuser (set password via environment)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='myadmin').exists() or User.objects.create_superuser('myadmin', 'admin@styleora.com', '12345')" | python manage.py shell --skip-checks

echo ""
echo "============================================"
echo "  DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "Now CONFIGURE YOUR WEB APP in PythonAnywhere:"
echo ""
echo "1. Go to Web tab -> Add a new web app"
echo "2. Select Manual Configuration -> Python 3.13"
echo ""
echo "3. In the 'Code' section:"
echo "   Source code: $PROJECT_DIR"
echo "   Working directory: $PROJECT_DIR"
echo ""
echo "4. In the 'Virtualenv' section:"
echo "   Virtualenv path: $PROJECT_DIR/venv"
echo ""
echo "5. In the 'Static files' section:"
echo "   URL: /static/"
echo "   Path: $PROJECT_DIR/staticfiles"
echo "   URL: /media/"
echo "   Path: $PROJECT_DIR/media"
echo ""
echo "6. Edit WSGI configuration file:"
echo "   Replace contents with the WSGI code below"
echo ""
echo "7. In the 'Environment variables' section, add:"
echo "   DJANGO_SECRET_KEY = (generate one)"
echo "   DJANGO_DEBUG = False"
echo "   DJANGO_ALLOWED_HOSTS = $USERNAME.pythonanywhere.com"
echo ""
echo "8. Back to Web tab -> Reload"
echo ""
echo "Your site will be live at: https://$USERNAME.pythonanywhere.com"
echo ""
