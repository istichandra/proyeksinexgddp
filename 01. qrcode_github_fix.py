import os
import pandas as pd
import qrcode
from github import Github

# --- CONFIGURATION: EDIT THESE VARIABLES --- #

# 1. GitHub Details
GITHUB_TOKEN = "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"      # Paste your GitHub Personal Access Token
REPO_NAME = "istichandra/proyeksinexgddp"      # The repository to upload to (e.g., "my-user/image-archive")
BRANCH_NAME = "main"                         # The default branch of your repo (usually "main" or "master")

# 2. Local File Paths
IMAGE_FOLDER = "E:/2025/python_2025/peta_proyeksi_nexgddp/images"                      # The local folder where your JPGs are stored
CSV_FILE_PATH = "E:/2025/python_2025/peta_proyeksi_nexgddp/list_produk_id_780_20250708.csv"             # The path to your CSV data file
QR_CODE_FOLDER = "nexgddp_qrcodes1"         # A folder to temporarily save QR codes before uploading

# --- END OF CONFIGURATION --- #


def create_qr_code_folder():
    """Creates the output folder for QR codes if it doesn't exist."""
    if not os.path.exists(QR_CODE_FOLDER):
        os.makedirs(QR_CODE_FOLDER)
        print(f"Created folder: {QR_CODE_FOLDER}")

def upload_to_github(repo, local_file_path, github_file_path, branch):
    """Uploads a single file to the specified GitHub repository."""
    print(f"Uploading {local_file_path} to GitHub at {github_file_path}...")
    try:
        with open(local_file_path, 'rb') as file:
            content = file.read()
        
        # Check if the file already exists to update it, otherwise create it
        try:
            contents = repo.get_contents(github_file_path, ref=branch)
            repo.update_file(contents.path, f"Updating {os.path.basename(github_file_path)}", content, contents.sha, branch=branch)
            print("...File updated successfully.")
        except Exception:
            repo.create_file(github_file_path, f"Creating {os.path.basename(github_file_path)}", content, branch=branch)
            print("...File created successfully.")
            
    except Exception as e:
        print(f"🚨 Error uploading {local_file_path}: {e}")

def main():
    """Main function to process images, generate QR codes with download links, and upload."""
    
    # 1. Setup
    create_qr_code_folder()
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        print(f"✅ Successfully connected to GitHub repository: {REPO_NAME}")
    except Exception as e:
        print(f"🚨 Could not connect to GitHub. Check your TOKEN and REPO_NAME. Error: {e}")
        return

    # 2. Load the data from CSV
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df.set_index('filename', inplace=True)
        print("✅ Successfully loaded data from CSV.")
    except FileNotFoundError:
        print(f"🚨 Error: The file '{CSV_FILE_PATH}' was not found.")
        return
    except KeyError:
        print(f"🚨 Error: The CSV must contain a column named 'filename'.")
        return

    # 3. Process each JPG in the image folder
    for jpg_filename in os.listdir(IMAGE_FOLDER):
        if jpg_filename.lower().endswith(".png"):
            base_name = os.path.splitext(jpg_filename)[0]
            local_jpg_path = os.path.join(IMAGE_FOLDER, jpg_filename)
            
            print(f"\n--- Processing: {jpg_filename} ---")

            # 4. Find matching data in the DataFrame
            try:
                image_info = df.loc[base_name]
            except KeyError:
                print(f"⚠️ Warning: No data found for '{base_name}' in {CSV_FILE_PATH}. Skipping.")
                continue

            # 5. UPLOAD THE ORIGINAL IMAGE FIRST
            github_image_path = f"images/{jpg_filename}"
            upload_to_github(repo, local_jpg_path, github_image_path, BRANCH_NAME)

            # 6. CONSTRUCT THE DIRECT DOWNLOAD URL
            # This uses the raw content URL format from GitHub.
            download_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH_NAME}/{github_image_path}"
            print(f"Generated download link: {download_url}")

            # 7. Combine metadata and the new download link for the QR code
            qr_data_string = (
                #f"ID: {image_info['filename']}\n"
                f"Nama Produk: {image_info['Nama']}\n"
                f"Periode Waktu: {image_info['Periode Waktu']}\n"
                f"Period Proyeksi: {image_info['Periode Proyeksi']}\n"
                f"Skenario: {image_info['Skenario']}\n"
                f"Keterangan: {image_info['Keterangan']}\n"
                f"Link: {download_url}"
            )
            print(f"Generating QR code with data:\n{qr_data_string}")

            # 8. Generate the QR code image
            qr_img = qrcode.make(qr_data_string)
            qr_code_filename = f"{base_name}.png"
            local_qr_code_path = os.path.join(QR_CODE_FOLDER, qr_code_filename)
            qr_img.save(local_qr_code_path)
            print(f"Saved QR code to {local_qr_code_path}")

            # 9. Upload the generated QR code to GitHub
            github_qr_path = f"qrcodes1/{qr_code_filename}"
            upload_to_github(repo, local_qr_code_path, github_qr_path, BRANCH_NAME)

    print("\n🎉 All files processed and uploaded successfully!")

if __name__ == "__main__":
    main()