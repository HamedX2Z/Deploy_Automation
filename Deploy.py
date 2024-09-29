import os
from ftplib import FTP
from tqdm import tqdm

# FTP connection details
FTP_HOST = "ftp.yourdomain.com"  # Replace with your FTP host
FTP_USER = "your_ftp_user"        # Replace with your FTP username
FTP_PASS = "your_ftp_password"    # Replace with your FTP password
REMOTE_DIR = "/path/to/public_html"  # Remote path to public_html
LOCAL_PATH = "/path/to/your/local/file_or_directory"  # Local path to file or directory

def progress_bar(file_size):
    # Initialize tqdm progress bar
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
    try:
        # Connect to FTP server
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(remote_dir)

        # Check if the local path is a file or a directory
        if os.path.isfile(local_path):
            # It's a file, upload directly
            file_name = os.path.basename(local_path)
            remote_file = os.path.join(remote_dir, file_name).replace("\\", "/")
            upload_file(ftp, local_path, remote_file)

        elif os.path.isdir(local_path):
            # It's a directory, upload recursively
            upload_directory(ftp, local_path, remote_dir)

        else:
            print(f"Error: {local_path} is neither a file nor a directory.")
        
        ftp.quit()
        print("Upload completed successfully.")

    except Exception as e:
        print(f"Error during FTP transfer: {e}")

if __name__ == "__main__":
    ftp_transfer(LOCAL_PATH, REMOTE_DIR)