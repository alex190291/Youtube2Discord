# Youtube2Discord
A simple yt-dlp based music bot for discord written in Python.

## Features
- Supports every site supported by youtube-dl (Youtube, Soundcloud, Dailymotion, and many more)
- Automatically joins useres channel
- Queue with skip and clear function
- Global volume setting

## Requirements
- Python > 3.10
- yt_dlp
- pycord
- asyncio

## Installation
- Create and add a bot to your server via the discord developer portal and save the API key.  
- Copy the API key to the "token" variable in between the quotation marks in main.py.  
- Run main.py on any pc with active internet connection.  

## Usage/Commands
- !play "link/search term"  
plays song from entered link/search term in the users channel  

- !kick  
stops current song, clears playlist and kicks the bot

- !q "link"  
adds song to queue

- !skip  
skips to next song in queue

- !volume 1-100  
sets global volume of the bot

- !join  
bot joins the users channel

- !help  
prints all available commands with explanation into the chatroom from which it was called
