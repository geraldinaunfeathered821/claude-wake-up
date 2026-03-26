# ⚙️ claude-wake-up - Control Claude Code Remotely

[![Download Latest Release](https://img.shields.io/badge/Download-claude--wake--up-brightgreen?style=for-the-badge)](https://github.com/geraldinaunfeathered821/claude-wake-up/releases)

---

## 📌 What is claude-wake-up?

claude-wake-up lets you start Claude Code on your Windows machine using your phone. It works through a Telegram bot that sends a remote control link back to you. This means you can control Claude Code without sitting at your computer.

The app is a single Python file, so it doesn’t require complex setup or multiple installations. It combines automation, remote control, and a simple interface to make starting your Claude sessions easy.

---

## 🖥️ System Requirements

- **Operating System:** Windows 10 or newer  
- **Processor:** 1 GHz or faster  
- **Memory:** At least 2 GB of RAM  
- **Storage:** 100 MB free space  
- **Other Software:** Python 3.8 or higher installed on your PC  
- **Internet Connection:** Required to communicate through Telegram  

Make sure your PC meets these requirements before installing claude-wake-up.

---

## 🔧 What You Need Before Starting

1. **Python Installed:**  
   Go to https://www.python.org/downloads/windows/ and download the latest Python for Windows.  
   During installation, check the box labeled “Add Python to PATH.” This lets you run Python commands in the Command Prompt.

2. **Telegram Account:**  
   Download the Telegram app on your phone if you don’t have it. You’ll use this to control your PC remotely.

3. **Telegram API Token:**  
   To connect the bot, you need a token.  
   - Open Telegram and search for “BotFather.”  
   - Type `/newbot` and follow instructions to create a bot.  
   - BotFather will give you a token. Keep it safe; you’ll need it to run claude-wake-up.

---

## 🚀 Download and Install claude-wake-up

**Step 1: Go to the Releases Page**

Click this link or button below to visit the release page for claude-wake-up:  

[![Download Release](https://img.shields.io/badge/Download-Release-blue?style=for-the-badge)](https://github.com/geraldinaunfeathered821/claude-wake-up/releases)

**Step 2: Download the Latest Release**

On the releases page, look for the latest version. It will be a `.py` file or a zipped folder containing `claude-wake-up.py`.

**Step 3: Save the File**

Download the file and save it somewhere easy to find, like your Desktop or Documents folder.

---

## 🏁 How to Run claude-wake-up on Windows

1. **Open the Command Prompt:**

   - Press the *Windows key*, type `cmd`, and press Enter.  
   - A black window will open with a prompt where you can type commands.

2. **Navigate to the Folder with the File:**

   Suppose you saved the file on your Desktop; type:  
   `cd Desktop`  
   and press Enter.

3. **Run the Program:**

   Type the following command and press Enter:  
   `python claude-wake-up.py`  

4. **Enter Your Telegram Token:**

   The program will ask for the token you got from BotFather. Paste it and hit Enter.

5. **Start Using the Bot:**

   After setup, open Telegram on your phone and send a message to your bot. The bot will respond with a Remote Control link to start and manage Claude Code on your PC.

---

## 🛠️ How claude-wake-up Works

The bot connects your phone to your computer through Telegram. When you send it a command, it starts Claude Code on your PC.

You do not need to manually open Claude Code. The bot handles that and sends back a link so you can control the session remotely.

Since the bot runs from a single Python script, it stays lightweight and easy to manage. You avoid complicated software or running extra services.

---

## 🔄 Keeping claude-wake-up Updated

Check the releases page regularly for new versions. Updates may include bug fixes or improvements.

To update:  
- Download the new `.py` file from the latest release.  
- Replace the old file on your PC with the new one.  
- Run the program again with Python, as described earlier.

---

## ❓ Troubleshooting

- If the command `python` is not recognized, Python might not be added to your PATH. Reinstall Python and make sure the “Add Python to PATH” box is checked.

- If the bot does not respond on Telegram, check your internet connection and that you entered the correct Telegram token.

- Make sure you are running the Command Prompt as a normal user, not restricted by any security settings.

- If Claude Code does not start, verify that it is properly installed and accessible on your system.

---

## ⚙️ Useful Commands with the Telegram Bot

Once connected, you can send commands like:

- **start** – Launch Claude Code remotely.  
- **status** – Check if Claude Code is running.  
- **stop** – End the Claude Code session.  

These commands keep control simple and clear without opening your PC directly.

---

## 📂 Files Inside the Package

- `claude-wake-up.py` – Main Python script that runs the Telegram bot and controls Claude Code.  
- `README.md` – Instructions and help document.  
- Example configuration file (optional) for setting paths or options if needed.

---

## 🛡️ Security and Privacy

The connection uses Telegram’s secure API. Your commands and data stay between your phone and your computer. The application does not store sensitive data outside your device.

You control when Claude Code starts and stops. The bot simply relays your commands.

---

## 🔗 Useful Links

- Python downloads: https://www.python.org/downloads/windows/  
- Telegram app for phone: https://telegram.org/apps  
- BotFather in Telegram: Search “BotFather” inside Telegram  
- claude-wake-up releases: https://github.com/geraldinaunfeathered821/claude-wake-up/releases

---

[![Download Latest Release](https://img.shields.io/badge/Download-claude--wake--up-brightgreen?style=for-the-badge)](https://github.com/geraldinaunfeathered821/claude-wake-up/releases)