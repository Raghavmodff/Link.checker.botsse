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
        print("✅ links.json updated and committed to GitHub!")
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
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

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
        print("ℹ️ No links in links.json to check.")
        return

    print(f"🔎 Checking {len(monitored_links)} links from links.json...")
    remaining_links = []
    updated = False

    async with aiohttp.ClientSession() as session:
        for link in monitored_links:
            status = await check_url(session, link)
            print(f"Link: {link} -> Status: {status}")

            if status == "Working":
                msg_tg = (
                    "🎉 <b>LINK IS NOW ACTIVE!</b>\n\n"
                    f"🔗 <b>Link:</b> {link}\n"
                    "📊 <b>Status:</b> Working ✅\n\n"
                    "🛑 <i>Link automatically removed from GitHub links.json!</i>"
                )
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=msg_tg, parse_mode="HTML")
                except Exception as e:
                    print(f"Failed to send Telegram alert: {e}")
                
                email_subject = "Success Alert: Link is ACTIVE!"
                email_body = f"Link is now Active!\n\nLink: {link}\nStatus: Working\n\nRemoved from monitoring list."
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
    await check_links_once(app.bot)

if __name__ == "__main__":
    asyncio.run(main())
m        msg = f"🎉 <b>Link is ALREADY ACTIVE!</b>\n\n🔗 <b>Link:</b> {link}\n📊 <b>Status:</b> {current_status}\n\n🛑 <i>No need to monitor. Email alert sent instantly!</i>"
        try:
            await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)
            email_subject = "Success Alert: Link is ACTIVE!"
            email_body = f"The link you added is already Active!\n\nLink: {link}\nStatus: {current_status}"
            asyncio.create_task(send_email_async(email_subject, email_body))
        except Exception as e:
            print(f"Reply Error: {e}")
            
    else:
        monitored_links.add(link)
        save_links(monitored_links)
        status_track[link] = current_status
        msg = f"⏳ <b>Link Added to Monitoring!</b>\n\n🔗 <b>Link:</b> {link}\n📊 <b>Initial Status:</b> {current_status}\n\n<i>Bot will silently check this link and alert/email you ONLY when it becomes ACTIVE.</i>"
        try:
            await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)
        except Exception as e:
            print(f"Reply Error: {e}")

async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Link to do! Example:\n/remove https://example.com")
        return
    
    link = context.args[0].strip()
    monitored_links = load_links()

    if link in monitored_links:
        monitored_links.remove(link)
        save_links(monitored_links)
        status_track.pop(link, None)
        await update.message.reply_text("🗑️ Link monitoring se hata diya gaya hai!")
    else:
        await update.message.reply_text("❌ Yeh link monitoring list me nahi hai!")

async def list_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    monitored_links = load_links()
    if not monitored_links:
        await update.message.reply_text("📂 Abhi koi link monitor nahi ho raha hai. /add se add karo!")
        return

    msg = "📋 <b>Monitored Links List:</b>\n\n"
    for idx, link in enumerate(list(monitored_links), 1):
        status = status_track.get(link, "Not Working ❌")
        msg += f"{idx}. {link}\n📊 Status: {status}\n\n"
    
    try:
        await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"List Error: {e}")

async def monitor_loop(app):
    while True:
        monitored_links = load_links()
        if monitored_links:
            async with aiohttp.ClientSession() as session:
                for link in list(monitored_links.copy()):
                    current_status = await check_url(session, link)
                    old_status = status_track.get(link, "Unknown")

                    if current_status == "Working ✅" and old_status != "Working ✅":
                        msg_tg = f"🎉 <b>LINK IS NOW ACTIVE!</b>\n\n🔗 <b>Link:</b> {link}\n📊 <b>Status:</b> {current_status}\n\n🛑 <i>Task Done! Link removed from monitoring.</i>"
                        try:
                            await app.bot.send_message(chat_id=CHAT_ID, text=msg_tg, parse_mode="HTML")
                        except Exception as e:
                            print(f"Failed to send Telegram alert: {e}")
                        
                        email_subject = f"Success Alert: Link is ACTIVE!"
                        email_body = f"Link is now Active!\n\nLink: {link}\nStatus: {current_status}\n\nMonitoring stopped for this specific link."
                        asyncio.create_task(send_email_async(email_subject, email_body))

                        monitored_links.remove(link)
                        save_links(monitored_links)
                        status_track.pop(link, None)
                    else:
                        status_track[link] = current_status

        await asyncio.sleep(3)

async def post_init(application):
    asyncio.create_task(run_web_server())
    asyncio.create_task(monitor_loop(application))

if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add_link))
    app.add_handler(CommandHandler("check", add_link))
    app.add_handler(CommandHandler("remove", remove_link))
    app.add_handler(CommandHandler("list", list_links))

    print("🚀 Bot Started Successfully!")
    
    try:
        app.run_polling(drop_pending_updates=True)
    except (Conflict, NetworkError) as e:
        print(f"⚠️ Polling Issue: {e}")
