import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime

import discord

from discord.ext.commands import Bot


BLACKLIST_PATH = "blacklist.json"
IGNORE_PATH = "blacklistignore.json"
CHECKPOINT_PATH = "lastmsg.txt"
CHANNEL_ID = 710922894871625759
TOKEN = ""

bot = Bot(command_prefix="$", description="Tauri Blacklist Bot")


BlacklistType = Dict[str, List[Optional[str]]]


@dataclass
class Name:
    name: str = None
    is_guild: bool = False
    reason: str = None
    is_wildcard: bool = False # Unused atm


def check_blacklist(blacklist: BlacklistType) -> None:
    if (
        not isinstance(ignore, dict) 
        and not all(k in ignore for k in ["players", "guilds"])
    ):
        raise json.JSONDecodeError # a little too cheeky maybe


ignore = []
try:
    with open(IGNORE_PATH, "r", encoding="utf-8") as f:
        ignore = json.load(f)
        check_blacklist(ignore)
except FileNotFoundError:
    print(
        f"Unable to load '{IGNORE_PATH}', file does not exist. "
        "Proceeding with empty ignore list."
    )
except json.JSONDecodeError:
    print(f"Unable to parse '{IGNORE_PATH}', file is damaged or malformed.")
    


def load_blacklist() -> BlacklistType:
    _blacklist = {
        "players": [], 
        "guilds": []
    }
    try:
        with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
            blacklist = json.load(f)
            check_blacklist(blacklist)
            return blacklist  
    except FileNotFoundError:
        return _blacklist
    except json.JSONDecodeError:
        print(f"Unable to parse '{BLACKLIST_PATH}', file is damaged or malformed.")


def save_blacklist(blacklist: List[str]) -> None:
    try:
        bl = json.dumps(blacklist, indent=4)
    except:
        print("Unable to serialize blacklist.") # TODO: log
        exit(1)
    
    with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
        f.write(bl)


def save_message_checkpoint(message: discord.Message) -> None:
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        f.write(message.created_at.isoformat())


def load_message_checkpoint() -> Optional[datetime]:
    path = Path(CHECKPOINT_PATH)
    if not path.exists():
        print("No message checkpoint found. Fetching all messages!")
        # None is default arg of param `after` of TextChannel.history(), so this is fine
        return None 
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        return datetime.fromisoformat(f.read())


async def parse_message(message: discord.Message) -> Optional[Name]:
    n = Name() # kinda awful c-style declaration but avoids duplicate code
    content = message.content

    # Skip comments
    if content.startswith("#"):
        return
    
    if content.lower().startswith("guild: "):
        _, guild = content.split("guild: ")
        n.name = guild
        n.is_guild = True
    else:      
        name, *reason = message.content.split(" ")
        n.name = name.capitalize() # all player names are capitalized
    
    if n.name and n.name.isalpha():
        if "*" in content:
            n.is_wildcard = True # not used when serializing to json (yet)
        return n
    # TODO: Save reason (if it exists)
    #       Save if wildcard


async def generate_blacklist() -> None:
    """This function is a little too long. Could be broken up."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        raise discord.DiscordException(
            "Unable to find the blacklist channel! "
            "Make sure the bot can see the channel."
        )
    
    checkpoint = load_message_checkpoint()
    blacklist = load_blacklist()

    async for message in channel.history(limit=None, 
                                         after=checkpoint, 
                                         oldest_first=True):
        # Fail silently if parse fails (yeah, that's bad)
        try:
            name = await parse_message(message)
            if name:
                if name.is_guild:
                    if (
                        name.name not in ignore["guilds"]
                        and name.name not in blacklist["guilds"]
                    ):
                        blacklist["guilds"].append(name.name)
                else:
                    if (
                        name.name not in ignore["players"]
                        and name.name not in blacklist["players"]
                    ):
                        blacklist["players"].append(name.name)
        except:
            pass
    
    if not blacklist:
        raise ValueError(
            "Could not find any messages! "
            "Make sure the bot can read message history."
        )
    try:
        save_message_checkpoint(message)
    except UnboundLocalError:
        pass # if iterator is never entered (due to no new messages since last checkpoint), 
             # there will be no variable named "message"
        
    save_blacklist(blacklist)

    
@bot.listen()
async def on_ready() -> None:
    try:
        await generate_blacklist()
    finally:
        exit(1)


def run():
    bot.run(TOKEN or os.environ.get("TBLBOTKEY"))