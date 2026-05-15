# 📝 Slate

A lightning-fast, native desktop note-taking app for Ubuntu. Features a sleek GUI with real-time auto-save, live search, and a distraction-free dual-pane interface—powered entirely by Python.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Ubuntu%20%7C%20Linux-orange?style=flat-square&logo=ubuntu)
![Dependencies](https://img.shields.io/badge/Dependencies-Tkinter-brightgreen?style=flat-square)

---

## ⚡ Why use Slate over default Ubuntu Editors?

If you use `Gedit`, `Nano`, or `GNOME Text Editor` for taking quick notes, you probably deal with scattered `.txt` files all over your Desktop. **Slate solves this.**

* **🚫 Zero File Management:** No more dealing with "Save As...", choosing folders, or cluttering your filesystem. All your notes are securely stored in a single, hidden background JSON database.
* **💾 True Auto-Save:** There is no "Save" button. Slate saves your work on every single keystroke. You can abruptly close the app or lose power, and your data will still be there.
* **🔍 Millisecond Live Search:** Instantly filter through hundreds of notes right from the sidebar. It checks both titles and note bodies in real-time.
* **🪟 Two-Pane Workflow:** A modern, Notion-like layout with a persistent sidebar. Switch between notes instantly without opening multiple overlapping windows.
* **🪶 Feather-light:** Unlike Electron-based apps (Obsidian, VS Code) that eat up RAM, Slate uses pure Python `tkinter`. It opens instantly and consumes almost zero system resources.

---

## 🛠️ Prerequisites

Slate is built on Python's standard GUI library. Make sure you have `tkinter` installed on your Ubuntu system:

```bash
sudo apt update
sudo apt install python3-tk
```

---

## 🚀 Installation & Usage

### 1. Download the App
Clone the repository and place it in a safe directory:

```bash
mkdir -p ~/SlateApp
git clone [https://github.com/YOUR_USERNAME/Slate.git](https://github.com/YOUR_USERNAME/Slate.git) ~/SlateApp
```

### 2. Make it Executable

```bash
chmod +x ~/SlateApp/Notepad.py
```

### Option A: Run from Terminal
If you just want to run the app quickly from your terminal without installing it into your system menu:

```bash
python3 ~/SlateApp/Notepad.py
```

### Option B: Use as a Native Desktop App (Recommended)
To make Slate feel like a real Ubuntu application (searchable in your App Menu/Launcher), create a `.desktop` shortcut:

1. Open a new desktop file in your terminal:

```bash
nano ~/.local/share/applications/Slate.desktop
```

2. Paste the following configuration (⚠️ **IMPORTANT:** Replace `YOUR_USERNAME` with your actual Ubuntu username):

```ini
[Desktop Entry]
Version=1.0
Name=Slate
Comment=Ultralight Desktop Notes App
Exec=/usr/bin/env python3 /home/YOUR_USERNAME/SlateApp/Notepad.py
Icon=/home/YOUR_USERNAME/SlateApp/icon.png
Terminal=false
Type=Application
Categories=Utility;TextEditor;
```

3. Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).
4. Press your `Super/Windows` key, search for **"Slate"**, and launch it directly from your desktop! Pin it to your dock for quick access.

---

## 🗄️ Where is my data saved?

Your data is completely private and stored locally on your machine. You can find your database file at:  
`~/.Slate_data.json`

You can easily back up this single file to Google Drive or a flash drive to keep all your notes safe.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
