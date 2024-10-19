import os
import subprocess
import shutil
from ftplib import FTP
from tqdm import tqdm

# FTP connection details
FTP_HOST = "ftp.yourdomain.com"  # Replace with your FTP host
FTP_USER = "your_ftp_user"  # Replace with your FTP username
FTP_PASS = "your_ftp_password"  # Replace with your FTP password
REMOTE_DIR = "/path/to/public_html"  # Remote path to public_html
LOCAL_PATH = "/path/to/your/local/file_or_directory"  # Local path to the build folder
CLONE_DIR = "/path/to/clone_project"  # Directory to clone the repository into

# GitLab repository details
GIT_REPO_URL = "http://gitlab.com/your-repo.git"  # Replace with your GitLab repo URL
GIT_USERNAME = "your-username"  # Your GitLab username
GIT_PASSWORD = "your-password"  # Your GitLab password

def progress_bar(file_size):
    """Initialize tqdm progress bar."""
    return tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading")

def upload_file(ftp, local_file, remote_file):
    """Upload a single file with progress."""
    file_size = os.path.getsize(local_file)
    with progress_bar(file_size) as progress:
        with open(local_file, 'rb') as f:
            def callback(block):
                progress.update(len(block))
            # Upload the file with progress callback
            ftp.storbinary(f'STOR {remote_file}', f, 1024, callback)

def upload_directory(ftp, local_dir, remote_dir):
    """Recursively upload a directory and its contents."""
    for root, dirs, files in os.walk(local_dir):
        relative_path = os.path.relpath(root, local_dir)
        remote_path = os.path.join(remote_dir, relative_path).replace("\\", "/")
        # Create remote directory if it doesn't exist
        try:
            ftp.mkd(remote_path)
        except Exception:
            pass  # Directory already exists or cannot be created
        for file in files:
            local_file = os.path.join(root, file)
            remote_file = os.path.join(remote_path, file).replace("\\", "/")
            upload_file(ftp, local_file, remote_file)

def ftp_transfer(local_path, remote_dir):
    """Upload the build folder via FTP."""
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(remote_dir)
        if os.path.isdir(local_path):
            upload_directory(ftp, local_path, remote_dir)
        else:
            print(f"Error: {local_path} is neither a file nor a directory.")
        ftp.quit()
        print("Upload completed successfully.")
    except Exception as e:
        print(f"Error during FTP transfer: {e}")

def clone_git_repo():
    """Clone the GitLab repository using credentials."""
    try:
        # Setup Git credential helper with username and password
        os.environ['GIT_ASKPASS'] = 'echo'
        os.environ['GIT_USERNAME'] = GIT_USERNAME
        os.environ['GIT_PASSWORD'] = GIT_PASSWORD
        git_command = [
            'git', 'clone', GIT_REPO_URL, CLONE_DIR
        ]
        print("Cloning GitLab repository...")
        subprocess.run(git_command, check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git clone: {e}")
        exit(1)

def run_npm_commands():
    """Run npm install and npm run build."""
    try:
        npm_path = r'C:\Program Files\nodejs\npm.cmd'
        # Run npm install
        print("Running npm install...")
        subprocess.run([npm_path, "install"], cwd=CLONE_DIR, check=True)
        print("npm install completed.")
        # Run npm run build
        print("Running npm run build...")
        subprocess.run([npm_path, "run", "build"], cwd=CLONE_DIR, check=True)
        print("npm run build completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error during npm command execution: {e}")
        exit(1)

def delete_clone_dir():
    """Delete the cloned directory if it exists."""
    if os.path.exists(CLONE_DIR):
        try:
            shutil.rmtree(CLONE_DIR)
            print(f"Deleted directory: {CLONE_DIR}")
        except Exception as e:
            print(f"Error deleting directory {CLONE_DIR}: {e}")
            exit(1)

if __name__ == "__main__":
    # Step 1: Delete the cloned directory if it exists
    delete_clone_dir()
    
    # Step 2: Clone the GitLab repository
    clone_git_repo()
    
    # Step 3: Run npm install and npm run build
    run_npm_commands()
    
    # Step 4: Upload the build folder via FTP
    ftp_transfer(LOCAL_PATH, REMOTE_DIR)