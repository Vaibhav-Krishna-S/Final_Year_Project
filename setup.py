"""
Setup script for Student Engagement Analysis Tool
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return False

def setup_backend():
    """Setup backend dependencies and database"""
    print("Setting up backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Initialize database
    try:
        from database.connection import db_manager
        db_manager.init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {str(e)}")
        return False
    
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print("\nSetting up frontend...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("✗ Frontend directory not found")
        return False
    
    os.chdir(frontend_path)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        os.chdir("..")
        return False
    
    os.chdir("..")
    return True

def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✓ Created .env file from template")
            print("⚠ Please update .env file with your actual configuration values")
            return True
        except Exception as e:
            print(f"✗ Failed to create .env file: {str(e)}")
            return False
    
    return True

def check_system_requirements():
    """Check system requirements"""
    print("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Check if pip is available
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        print("✓ pip is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ pip is not available")
        return False
    
    # Check if Node.js is available (optional for frontend)
    try:
        result = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
        print(f"✓ Node.js {result.stdout.strip()} detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Node.js not found - frontend setup will be skipped")
        return "partial"

def main():
    """Main setup function"""
    print("=" * 60)
    print("Student Engagement Analysis Tool - Setup")
    print("=" * 60)
    
    # Check system requirements
    req_check = check_system_requirements()
    if req_check is False:
        print("\n✗ System requirements not met. Please install required software.")
        return False
    
    # Create environment file
    create_env_file()
    
    # Setup backend
    if not setup_backend():
        print("\n✗ Backend setup failed")
        return False
    
    # Setup frontend (if Node.js is available)
    if req_check is True:
        if not setup_frontend():
            print("\n⚠ Frontend setup failed, but backend is ready")
    
    print("\n" + "=" * 60)
    print("Setup completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Start the backend: python backend/main.py")
    if req_check is True:
        print("3. Start the frontend: cd frontend && npm start")
    print("4. Start the dashboard: python dashboard/app.py")
    print("\nFor more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)