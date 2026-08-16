import os
import json
import asyncio
import aiohttp
import smtplib
import subprocess
from email.message import EmailMessage
from telegram import Bot

# --- CONFIG FROM ENVIRONMENT VARIABLES ---
TOKEN = os.getenv('TELEGRAM_TOKEN', '8953861489:AAFcTbss72csyDG95qaA9e2CdvqRQSsR1t4')
CHAT_ID = os.getenv('CHAT_ID', '-1004428551744')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'thailandserver89977@gmail.com') 
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'ubaasgrskpmynmio')           
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', 'Gojoraghav74@gmail.com')      
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465 
DATA_FILE = "links.json"

def load_links():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return list(set(data))
        except Exception as e:
            print(f"Error loading JSON data: {e}")
    return []

def save_and_commit_links(links_list):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(links_list, f, indent=4)
        
        subprocess.run(["git", "config", "user.name", "GitHub Action Bot"], check=False)
        subprocess.run(["git", "config", "user.email", "bot@github.com"], check=False)
        subprocess.run(["git", "add", DATA_FILE], check=False)
        subprocess.run(["git", "commit", "-m", "Auto-remove active link from links.json"], check=False)
        subprocess.run(["git", "push"], check=False)
        print("links.json updated and committed to GitHub!")
    except Exception as e:
        print(f"Error committing JSON data: {e}")

def send_email_sync(subject, body):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

async def send_email_async(subject, body):
    await asyncio.to_thread(send_email_sync, subject, body)

async def check_url(session, url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
            return "Working" if response.status == 200 else "Not Working"
    except Exception:
        return "Not Working"

async def check_links_once(bot):
    monitored_links = load_links()
    if not monitored_links:
        print("No links in links.json to check.")
        return

    print(f"Checking {len(monitored_links)} links from links.json...")
    remaining_links = []
    updated = False

    async with aiohttp.ClientSession() as session:
        for link in monitored_links:
            status = await check_url(session, link)
            print(f"Link: {link} -> Status: {status}")

            if status == "Working":
                msg_tg = "🎉 <b>LINK IS NOW ACTIVE!</b>\n\n🔗 <b>Link:</b> " + str(link) + "\n📊 <b>Status:</b> Working ✅\n\n🛑 <i>Link automatically removed from GitHub links.json!</i>"
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=msg_tg, parse_mode="HTML")
                except Exception as e:
                    print(f"Failed to send Telegram alert: {e}")
                
                email_subject = "Success Alert: Link is ACTIVE!"
                email_body = "Link is now Active!\n\nLink: " + str(link) + "\nStatus: Working\n\nRemoved from monitoring list."
                await send_email_async(email_subject, email_body)

                updated = True
            else:
                remaining_links.append(link)

    if updated:
        save_and_commit_links(remaining_links)

async def main():
    bot = Bot(token=TOKEN)
    await check_links_once(bot)

if __name__ == "__main__":
    asyncio.run(main())
