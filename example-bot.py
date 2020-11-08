import discord
import requests
import json
from urllib import parse
from discord.ext import commands

bot_token = "????????????????????????????????????????" // 토큰 번호는 공개하지 않음.
lol_key = "RGAPI-665c20b7-c7a0-4d9c-9f60-b5e858504086"

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("We have logged at {0.user}".format(bot))


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("헬로우")


@bot.command(name="hey")
async def search(ctx, *, summoner_name):
    # Summoner
    enc_summoner_name = parse.quote(summoner_name)
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{enc_summoner_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": lol_key
    }
    res = requests.get(url=url, headers=headers)
    res_obj = json.loads(res.text)

    name = res_obj["name"]
    level = res_obj["summonerLevel"]
    profile_icon_id = res_obj["profileIconId"]

    profile_icon_name = f"{profile_icon_id}.png"
    profile_icon_file = discord.File(f"profileicon/{profile_icon_name}")

    # League info
    summoner_id = res_obj["id"]
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    res = requests.get(url=url, headers=headers)
    res_obj = json.loads(res.text)

    for obj in res_obj:
        if obj["queueType"] == "RANKED_SOLO_5x5":
            tier = obj["tier"]
            rank = obj["rank"]
            league_points = obj["leaguePoints"]
            wins = obj["wins"]
            losses = obj["losses"]
            winrate = wins / (wins + losses) * 100
            if "miniSeries" in obj:
                progress = obj["miniSeries"]["progress"]
                progress_desc = f"\n승급전: "
                for prog in progress:
                    if prog == 'W':
                        progress_desc += 'O'
                    elif prog == 'L':
                        progress_desc += 'X'
                    else:
                        progress_desc += '-'
            else:
                progress_desc = ""

    tier_icon_name = f"Emblem_{tier}.png"
    tier_icon_file = discord.File(f"ranked-emblems/{tier_icon_name}")

    # Build embed
    embed = discord.Embed(
        title=f"{tier} {rank} - {league_points}점",
        description=f"{wins+losses}전 {wins}승 {losses}패 ({winrate:.2f}%){progress_desc}",
        color=0x0062ff
    )
    embed.set_author(
        name=f"{summoner_name} (Lv. {level})",
        icon_url=f"attachment://{profile_icon_name}")
    embed.set_thumbnail(
        url=f"attachment://{tier_icon_name}"
    )
    await ctx.send(files=[profile_icon_file, tier_icon_file], embed=embed)
bot.run(bot_token)
