from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup
import requests
import datetime
import json
import pytz
import discord
import os
import keep_alive
from replit import db


def draw(price, change, date):
    image2 = Image.open("SLP Value.png")
    title_font = ImageFont.truetype('bunch/BUNCH-BONARIE.ttf', 125)
    change_font = ImageFont.truetype('bunch/BUNCH-BONARIE.ttf', 80)
    date_font = ImageFont.truetype('bunch/BUNCH-BONARIE.ttf', 20)

    if "-" in change:
        res = 222, 20, 23
    else:
        res = 64, 247, 54

    #display
    title_text = str(price)
    change_24hr = str(change)
    date = str(date)


    color_positive = 64, 247, 54

    #drawing
    image_editable = ImageDraw.Draw(image2)
    image_editable.text((180, 260), title_text, (199, 16, 25), font=title_font)
    image_editable.text((625, 300), change_24hr, (res), font=change_font)
    image_editable.text((260, 570), date, (199, 16, 25), font=date_font)

    #save
    image2.save("result.png")

#status tracker
def tracker(ronin):
    address = ronin.replace("ronin:", "0x")
    url = f"https://axie-infinity.p.rapidapi.com/get-update/{address}"

    querystring = {"id":address}

    headers = {
        'x-rapidapi-host': "axie-infinity.p.rapidapi.com",
        'x-rapidapi-key': "62f0693f84msh434a264440c1f5ep142316jsnb268e75e3e5b"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    message = f"""
    :axe:Profile Name: {data["leaderboard"]["name"]}
    
    :crossed_swords: MMR :crossed_swords:\t\t\t:trophy: RANK :trophy:
    \t\t{data["leaderboard"]["elo"]}\t\t\t\t\t\t{data["leaderboard"]["rank"]}  
    -------------------------------------------------------------------
    :heart:Total SLP : {data["slp"]["total"]}
    :heart_on_fire:Today     : {data["slp"]["todaySoFar"]}
    :heartbeat:Yesterday : {data["slp"]["yesterdaySLP"]}
    :heartpulse:Average   : {data["slp"]["average"]}
    
    """

    return message

def register_address(name, ronin_add):
  if name.lower() not in db.keys():
    db[name.lower()] = ronin_add
    result = "Registered"
  else:
    result = "Name or address was already used."
  return result

def show_address():
  keys = db.keys()
  stored = "LIST:\n"
  for index, char in enumerate(keys):
    stored += str(index)+" "+str(char)+" = " +str(db[char]+ "\n")
  return stored

def delete_address(name):
  del db[name]
  result = "Name deleted"
  return result

keep_alive.keep_alive()

client = discord.Client()

@client.event 
async def on_ready():
  print("Logged in as {0.user}".format(client))

@client.event
async def on_member_join(member):
  await member.channel.send(f"Welcome {member}")


#message detect
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith("$hello"):
    await message.channel.send("Hello Master!")
  
  if message.content.startswith("thank you bot"):
    await message.channel.send("You're welcome Master <3")
  
  if message.content.startswith("$help"):
    messages = """ 
    Utusan nyo ako mga master:
    Mamili lang kayo dito:

    $hello = Reply ako hello
    $register = Register ng name at address. EXAMPLE : $register kraken roninaddress542565622
    $show profiles = Makikita yung mga naka register na ronin addresses
    $delete = Mag delete ng account. EXAMPLE : $delete kraken
    $stats = Lalabas stats nyo sa game. EXAMPLE : $stats ronin:address15651512
    $status = Pangalan ng naka register na ronin address. EXAMPLE : $status kraken
    $updateslp = SLP price update.
    
    """
    await message.channel.send(messages)

  if message.content.startswith("$register"):
    reg = message.content.split("$register ",2)[1]
    print(reg)
    name = reg.split(" ")[0]
    address = reg.split(" ")[1]
    register_address(name, address)
    print(register_address)
    await message.channel.send(str(name)+": Masusunod Master!")

  if message.content.startswith("$show profiles"):
    res = show_address()
    await message.channel.send(res)

  if message.content.startswith("$delete"):
    deleted = message.content.split("$delete ",1)[1]
    delete_address(deleted)
    show = show_address()
    await message.channel.send("Deleted na po Master \n" + show)

  if message.content.startswith("$stats"):
    address = message.content.split("$stats ",1)[1]
    result_message = tracker(address)
    await message.channel.send(result_message)


  if message.content.startswith("$status"):
    stat = message.content.split("$status ",1)[1]
    val = db[stat]
    res_address = tracker(val)
    await message.channel.send(res_address)

  if message.content.startswith("$updateslp"):
    print("awake")
    #current date 
    date = datetime.datetime.now(tz=pytz.timezone("Australia/Perth"))
    format_date = date.strftime("%B %d %Y %I:%M %p")

    default_currency = "php"
    default_coin = "smooth-love-potion"

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={default_coin}&vs_currencies={default_currency}&include_24hr_change=true"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    capture_dict = soup.find("p").text
    capture = json.loads(capture_dict)
    value = round(float(capture["smooth-love-potion"]["php"]), 2)
    value_change = round(float(capture["smooth-love-potion"]["php_24h_change"]), 2)
    format_value = default_currency.upper() + " " + str(capture["smooth-love-potion"]["php"])

    draw(format_value, str(value_change), format_date)
    await message.channel.send(file=discord.File('result.png'))
  
 


secret = os.environ['token']
client.run(secret)

keep_alive.keep_alive()
