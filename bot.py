from telethon import TelegramClient, events
from download_from_url import download_file, get_size
from config import BOTTOKEN, APIID, APIHASH, DOWNLOADPATH, USERNAME
import os
import time
import datetime
import aiohttp
from hurry.filesize import size, si
import traceback

bot = TelegramClient('upbot', APIID, APIHASH).start(bot_token=BOTTOKEN)

def get_date_in_two_weeks():
    """
    get maximum date of storage for file
    :return: date in two weeks
    """
    today = datetime.datetime.today()
    date_in_two_weeks = today + datetime.timedelta(days=14)
    return date_in_two_weeks.date()

async def send_to_transfersh_async(file):
    
    size = os.path.getsize(file)
    size_of_file = get_size(size)
    final_date = get_date_in_two_weeks()
    file_name = os.path.basename(file)

    print("\nUploading file: {} (size of the file: {})".format(file_name, size_of_file))
    url = 'https://transfer.sh/'
    
    with open(file, 'rb') as f:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={str(file): f}) as response:
                    download_link =  await response.text()
                    
    print("Link to download file(will be saved till {}):\n{}".format(final_date, download_link))
    return download_link, final_date, size_of_file


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi! please send me any file url or file uploaded in Telegram and I will upload to Telegram as file or generate download link of that file. Also you can upload sent file to TransferSh / TmpNinja.')
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/up'))
async def up(event):
    if not os.path.isdir(DOWNLOADPATH):
        os.mkdir(DOWNLOADPATH)

    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("Downloading...")
        
        try:
            filename = os.path.join(DOWNLOADPATH, os.path.basename(url.text))
            file_path = await download_file(url.text, filename, ilk, start, bot)
        except Exception as e:
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()

        try:
            orta = await event.respond("Uploading to Telegram...")
            async def progress(current, total):
                sonuc = (current / total) * 100
                await orta.edit("Uploading to Telegram...\nStatus: %" + str(round(sonuc,2)) + "\nSize: " + str(size(current, system=si)) + "/" + str(size(total, system=si))) 

            dosya = await bot.upload_file(filename, progress_callback=progress)

            zaman = str(time.time() - start)
            await bot.send_file(event.chat.id, dosya, caption=f"{filename} uploaded in {zaman} seconds! By {USERNAME}")
        except Exception as e:
            traceback.print_exc()

            print(e)
            await event.respond(f"Uploading Failed\n\n**Error:** {e}")
        
        await orta.delete()

    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/transfersh'))
async def tsh(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi!\nSent any file or direct download url to get the transfer.sh download link')
    raise events.StopPropagation

def main():
    """Start the bot."""
    print("\nBot started..\n")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
