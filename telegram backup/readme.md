# 🌟 Telegram Auto Backup Bot

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?color=00BFFF&size=24&center=true&vCenter=true&width=600&lines=Automated+Telegram+Backup;ZIP+Folders+%26+Large+Files;Ignore+Patterns+Support;Real-Time+Progress+Bar" />
</p>


## ✨ Features
- 🚀 Auto-detects new files & folders  
- 📤 Uploads everything to Telegram  
- 🎬 Video upload support (auto-zip if >50MB)  
- 🗂️ Full folder ZIP + upload  
- 🛑 `.backupignore` support  
- 📊 Modern progress bar (tqdm)  
- 🔔 Desktop notifications  
- 🔁 Skips already uploaded files  
- 🧹 Deletes files after successful backup  

---

## 📁 Folder Structure
```
Backup/
 ├── file1.txt
 ├── video.mp4
 ├── project/
 ├── .backupignore
 └── .uploaded_list.txt
telegram.py
```

---

## ⚙️ Configuration
Edit these parameters in `telegram.py`:

```
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
BACKUP_FOLDER = r"Backup"
```

---

## ▶️ How to Run
```
python telegram.py
```

The bot will automatically check for updates every 10 seconds.

---

## 📝 Example `.backupignore`
```
*.log
*.tmp
secret.txt
cache/
```

---

## 👤 Author
**Amit Kadam**  
GitHub: https://github.com/piyushkadam96k  
Telegram: @K9agentonduty  
Email: kadamamit462@gmail.com  

---
## ⭐ Support the Project
If this script helped you, give the repository a **star ⭐ on GitHub**!
