#!/usr/bin/env python3
"""
Setup script for the Patient Management System (PMS) project.
This script helps with initial project setup and environment configuration.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    if run_command("python -m venv venv", "Creating virtual environment"):
        print("✅ Virtual environment created")
        print("📝 To activate the virtual environment:")
        print("   - Windows: venv\\Scripts\\activate")
        print("   - Unix/MacOS: source venv/bin/activate")
        return True
    return False


def install_dependencies():
    """Install project dependencies."""
    if not run_command("pip install -r requirement.txt", "Installing dependencies"):
        return False
    
    # Check if python-decouple is installed
    try:
        import decouple
        print("✅ python-decouple installed successfully")
    except ImportError:
        print("❌ python-decouple installation failed")
        return False
    
    return True


def setup_environment():
    """Set up environment variables."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔄 Creating .env file...")
    if run_command("python manage.py setup_env", "Setting up environment variables"):
        print("✅ Environment variables configured")
        print("📝 Please edit .env file with your actual configuration values")
        return True
    return False


def setup_database():
    """Set up database."""
    print("🔄 Setting up database...")
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        return False
    
    print("✅ Database setup completed")
    return True


def create_superuser():
    """Create superuser account."""
    print("🔄 Creating superuser account...")
    print("📝 You will be prompted to enter username, email, and password")
    
    try:
        subprocess.run(["python", "manage.py", "createsuperuser"], check=True)
        print("✅ Superuser account created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create superuser account")
        return False


def main():
    """Main setup function."""
    print("🚀 Patient Management System (PMS) Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Set up virtual environment
    setup_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Set up environment variables
    if not setup_environment():
        print("❌ Setup failed at environment configuration")
        sys.exit(1)
    
    # Set up database
    if not setup_database():
        print("❌ Setup failed at database setup")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate your virtual environment:")
    print("   - Windows: venv\\Scripts\\activate")
    print("   - Unix/MacOS: source venv/bin/activate")
    print("2. Edit .env file with your actual configuration values")
    print("3. Start the development server: python manage.py runserver")
    print("4. Access the API documentation: http://localhost:8000/api/docs/")
    print("5. Access the admin panel: http://localhost:8000/admin/")


if __name__ == "__main__":
    main()
