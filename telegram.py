import os
import shutil
import requests
import time
from tqdm import tqdm
from fnmatch import fnmatch
from concurrent.futures import ThreadPoolExecutor
from plyer import notification

# ---------------- CONFIG ----------------

BOT_TOKEN = ""
CHAT_ID = ""

BACKUP_FOLDER = r"Backup"
UPLOADED_LIST_FILE = os.path.join(BACKUP_FOLDER, ".uploaded_list.txt")
BACKUPIGNORE = os.path.join(BACKUP_FOLDER, ".backupignore")

# video formats
VIDEO_EXT = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"]

# telegram max size
MAX_BOT_SIZE = 49 * 1024 * 1024  # 49 MB safe limit

# ---------------- NOTIFICATION ----------------

def show_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=5
        )
    except:
        pass


# ---------------- IGNORE SYSTEM ----------------

def load_ignore_patterns():
    patterns = []
    if os.path.exists(BACKUPIGNORE):
        with open(BACKUPIGNORE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

IGNORE_PATTERNS = load_ignore_patterns()

def is_ignored(path):
    name = os.path.basename(path)
    for pattern in IGNORE_PATTERNS:
        if fnmatch(name, pattern) or fnmatch(path, pattern):
            return True
    return False


# ---------------- UPLOADED LIST ----------------

def load_uploaded_list():
    if not os.path.exists(UPLOADED_LIST_FILE):
        return set()
    with open(UPLOADED_LIST_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_uploaded_item(item_path):
    with open(UPLOADED_LIST_FILE, "a", encoding="utf-8") as f:
        f.write(item_path + "\n")


# ---------------- TELEGRAM SENDERS ----------------

def send_video(file_path):
    """Send video for <50MB"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"video": (file_name, f)},
            timeout=600
        )

    return response.status_code == 200


def send_file_with_progress(file_path):
    """Send any file as document"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        with tqdm(total=file_size, unit="B", unit_scale=True, desc=file_name) as bar:
            response = requests.post(
                url,
                data={"chat_id": CHAT_ID},
                files={"document": (file_name, f)},
                timeout=600
            )
            bar.update(file_size)

    return response.status_code == 200


# ---------------- ZIP FOLDER ----------------

def zip_and_upload_folder(folder_path, folder_name, uploaded_list):
    zip_name = folder_name + ".zip"
    zip_path = os.path.join(BACKUP_FOLDER, zip_name)

    if zip_name in uploaded_list:
        print(f"⏩ Already uploaded ZIP: {zip_name}")
        return False

    print(f"📦 Creating ZIP: {zip_name}")
    shutil.make_archive(os.path.join(BACKUP_FOLDER, folder_name), 'zip', folder_path)

    print(f"📤 Uploading ZIP: {zip_name}")
    if send_file_with_progress(zip_path):
        print(f"✔ Uploaded: {zip_name}")
        save_uploaded_item(zip_name)

        shutil.rmtree(folder_path)
        os.remove(zip_path)
        print(f"🗑 Deleted folder & ZIP: {folder_name}")
        return True
    else:
        print(f"❌ Failed: {zip_name}")
        return False


# ---------------- PROCESS FILE ----------------

def process_file(item, full_path, uploaded):
    if item in uploaded:
        print(f"⏩ Already uploaded: {item}")
        return False

    ext = os.path.splitext(item)[1].lower()
    file_size = os.path.getsize(full_path)

    # ---------------- Video handling ----------------
    if ext in VIDEO_EXT:
        if file_size <= MAX_BOT_SIZE:
            print(f"\n🎬 Uploading video: {item} (<49MB)")
            if send_video(full_path):
                print(f"✔ Uploaded video: {item}")
                save_uploaded_item(item)
                os.remove(full_path)
                return True
            else:
                print(f"❌ Failed video: {item}")
                return False
        else:
            # Too big -> ZIP it
            print(f"\n📦 Video too large → Zipping: {item}")
            zip_name = item + ".zip"
            zip_path = os.path.join(BACKUP_FOLDER, zip_name)

            # create zip
            shutil.make_archive(zip_path.replace(".zip", ""), 'zip',
                                os.path.dirname(full_path), item)

            print(f"🎬 Uploading zipped large video: {zip_name}")
            if send_file_with_progress(zip_path):
                print(f"✔ Uploaded ZIP video: {zip_name}")
                save_uploaded_item(zip_name)
                os.remove(full_path)
                os.remove(zip_path)
                return True
            else:
                print(f"❌ Failed ZIP video: {zip_name}")
                return False

    # ---------------- Normal file handling ----------------
    print(f"\n📤 Uploading: {item}")
    if send_file_with_progress(full_path):
        print(f"✔ Uploaded: {item}")
        save_uploaded_item(item)
        os.remove(full_path)
        return True
    else:
        print(f"❌ Failed: {item}")
        return False


# ---------------- PROCESS FOLDER ----------------

def process_folder(item, full_path, uploaded):
    before = len(uploaded)
    success = zip_and_upload_folder(full_path, item, uploaded)
    after = len(uploaded)
    return success or (after > before)


# ---------------- MAIN BACKUP ----------------

def backup():
    uploaded = load_uploaded_list()
    items = os.listdir(BACKUP_FOLDER)
    tasks = []
    upload_happened = False

    with ThreadPoolExecutor(max_workers=4) as executor:
        for item in items:

            if item in [".uploaded_list.txt", ".backupignore"]:
                continue

            if is_ignored(item):
                print(f"🚫 Ignored: {item}")
                continue

            full_path = os.path.join(BACKUP_FOLDER, item)

            if os.path.isfile(full_path):
                tasks.append(executor.submit(process_file, item, full_path, uploaded))

            elif os.path.isdir(full_path):
                tasks.append(executor.submit(process_folder, item, full_path, uploaded))

    for t in tasks:
        try:
            if t.result():
                upload_happened = True
        except:
            pass

    if upload_happened:
        show_notification("Backup Completed", "All new files were uploaded successfully!")

    print("\n🎉 Backup Completed!\n")


# ---------------- LOOP ----------------

while True:
    print("🔄 Checking for new files...")
    backup()
    print("⏳ Waiting 10 seconds...\n")
    time.sleep(10)
