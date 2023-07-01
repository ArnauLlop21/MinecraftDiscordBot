import os
import discord
import asyncio
from discord.ext import commands
import subprocess
import time
from mcstatus import JavaServer
from datetime import datetime, timedelta
import tarfile
import re

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
server = JavaServer.lookup("localhost:25565")
isBusy = False
#habilitat = False
habilitat = True

backupPath = "/home/arnau/minecraftBackups"


usuaris = { "discordname0":"minecraftname0",
            "discordname1":"minecraftname1",
            "discordname2":"minecraftname2",
            "discordname3":"minecraftname3",
            }


#commandStart = "java -Xms2G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar /home/minecraft/minecraft/server.jar --nogui"

commandStart = "java -Xms2G -Xmx12G -jar /home/minecraft/minecraft/server.jar --nogui"

#def there_is_output(process):
    # Comprova si hi ha dades disponibles per llegir en l'standard output del procé    
 #   return select.select([process.stdout], [], [], 0.0)[0]


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.errors.MissingRole)):
        await ctx.send("You dont have sufficient privileges to do so. Please contact with admin")
    else:
        #Mes coses
        pass

"""
This method allows for the bot to be "disabled" for all non-admin users.
This means that even if the bot is online and working, users will not be able to use the commands.
Use !activate to toggle this. Will reset on restart
"""
@bot.before_invoke 
async def checkSiHabilitat(ctx):
    global habilitat
    if not habilitat and "Admin" not in [role.name for role in ctx.author.roles]:
        await ctx.send("Bot is disabled")
        raise commands.CommandError("Bot is disabled!")

@bot.command()
@commands.has_role("Admin")
async def activate(ctx, valor: bool):
    global habilitat
    habilitat = valor
    await ctx.send("Bot status has been updated")

@bot.command()
@commands.has_role("Turn off")
async def shutdown(ctx):
    try:
        subprocess.check_output('pgrep java', shell = True)
        minecraft_alive = True
    except subprocess.CalledProcessError:
        minecraft_alive = False

    if minecraft_alive:
        await ctx.send("Please, first of all stop the minecraft process... We do not want to regret this.")
        return
    await ctx.send("Shutting down...")
    os.system('shutdown -h now')

@bot.command()
@commands.has_role("Alive")
async def ping(ctx):
    try:
        subprocess.check_output('pgrep java', shell = True)
        minecraft_alive = True
    except subprocess.CalledProcessError:
        minecraft_alive = False
    if minecraft_alive:
        await ctx.send(f"Ping: {server.ping()}ms")
    else:
        await ctx.send("Cannot ping the server if there is no minecraft instanced")

@bot.command()
@commands.has_role("Message")
async def message(ctx, *, msg: str):
    global isBusy
    if isBusy == False:
        
        msg = f"User {ctx.author.name} said: " + msg
        try:
            subprocess.check_output("pgrep java", shell = True)
            minecraft_alive = True
        except subprocess.CalledProcessError:
            minecraft_alive = False
        if minecraft_alive:
            msg_lower = msg.lower()
            if "/" in msg_lower or "rm" in msg_lower or "sudo" in msg_lower:
                user = usuaris.get(ctx.author.name.lower())
                if user:
                    cmdBan = f'screen -S minecraftServer -X stuff "ban {user} Illegal message, you were warned^M"'
                    subprocess.run(cmdBan, shell=True)
                    await ctx.send(f"Illegal message. User {user} has been banned")
                
            else:
                cmd = f'screen -S minecraftServer -X stuff "say {msg}^M"'
                subprocess.run(cmd, shell=True)
                await ctx.send('Message sent to minecraft server')
        else:
            await ctx.send("Message could not be sent because there is no server being ran at the moment")
    else:
        await ctx.send("Server is busy :(")

@bot.command()
@commands.has_role("Admin")
async def ban(ctx, *, user):
    userMinecraft = usuaris.get(user.lower())
    if userMinecraft:
        cmdBan = f'screen -S minecraftServer -X stuff "ban {userMinecraft}^M"'
        subprocess.run(cmdBan, shell=True)
    await ctx.send(f"User {user} has been banned")

@bot.command()
@commands.has_role("Admin")
async def pardon(ctx, *, user):
    userMinecraft = usuaris.get(user.lower())
    if userMinecraft:
        cmdPardon = f'screen -S minecraftServer -X stuff "pardon {userMinecraft}^M"'
        subprocess.run(cmdPardon, shell=True) 
    await ctx.send(f"User {user} has been forgiven!")

"""
@bot.command()
@commands.has_role("Command")
async def command(ctx, *, command):
    global isBusy
    if isBusy == False:
        try:
            subprocess.check_output("pgrep java", shell = True)
            minecraft_alive = True
        except subprocess.CalledProcessError:
            minecraft_alive = False
        if minecraft_alive:
            await ctx.send(command)
            screen_command = f'screen -S minecraftServer -p 0 -X stuff "{command}^M"'
            subprocess.run(shlex.split(screen_command))
            await ctx.send(f"Operacio executada {command}")
        else:
            await ctx.send("El server no està encés")
    else:
        await ctx.send("El server està ocupat amb tasques síncrones")
"""

@bot.command(name='alive')
@commands.has_role("Alive")
async def alive(ctx):
        try:
            process = subprocess.run(['pgrep', '-x', 'java'], stdout=subprocess.PIPE)
            if process.stdout:
                await ctx.send('Minecraft server **is** being ran')
            else:
                await ctx.send('Minecraft server **is not** being ran')
        except Exception as e:
            await ctx.send('There was an error validating the server\'s status ' + str(e))

@bot.command()
@commands.has_role("ip")
async def ip(ctx):
    await ctx.send("This server has been set up after a **dynamic IP** system so to save money")
    await ctx.send("So to use this server please use **server.hopto.org** on your minecraft launcher")


@bot.command()
@commands.has_role("ip")
async def sayHi(ctx, name):
    #print("Saludo")
    await ctx.send(f'Hi, {name}')

@bot.command()
@commands.has_role("stop")
async def stop(ctx):
    global isBusy
    try:
        subprocess.check_output("pgrep java", shell = True)
        minecraft_alive = True
    except subprocess.CalledProcessError:
        minecraft_alive = False
    if minecraft_alive:
        await ctx.send("Server is currently being executed")
    else:
        await ctx.send("Server could not be stopped because is not being executed")
        return
    if "ForceStop" not in [role.name for role in ctx.author.roles]:
        await ctx.send("ForceStop is not on your roles")
        await ctx.send("You can only stop the process when there are no players connected")
        status = server.status()
        time.sleep(0.2)
        jugadors_connectats = status.players.online
        if jugadors_connectats > 0:
            #await ctx.send(f"No es pot aturar el servidor, hi ha jugadors connectats: {last_line}")
            #query = server.query()
            #jugadors_connectats = ", ".join(query.players.names)
            await ctx.send("If you want to be able to stop the server when players are connected, please contact administration")
            #await ctx.send(f"Els jugadors que estan connectats son: {jugadors_connectats}")
#            query = server.query()
#            await ctx.send(f"El servidor te els jugadors seguents: {', '.join(query.players.names)}")
            return

    if isBusy == False:
        await ctx.send("Stopping petition has been registered")
        isBusy = True
        comandaStop = "screen -S minecraftServer -p 0 -X stuff 'stop^M'"
        resultStop = subprocess.run(comandaStop, shell=True)
        await ctx.send("Stopping server")
        # Esperem a que comenci a escriure
        #time.sleep(10)
        # wait asyncio.sleep(2)
        # S'espera 20 segons per assegurar que el server s'hagi aturat be
        #time.sleep(20)
        count = 0
        printFlag = False
        with subprocess.Popen(['tail', '-f', '/home/minecraft/minecraft/logs/latest.log'], stdout=subprocess.PIPE) as process:
            while os.system('pgrep java') == 0:
                #retCode = os.system("pgrep java")
                #await ctx.send(retCode)
                if count < 10:
                    line = process.stdout.readline().decode('utf-8')
                    if "Stopping" in line:
                        printFlag = True
                    if printFlag is True:
                        await ctx.send(line) 
                    if printFlag is False and count == 10:
                        await ctx.send("We're struggling to stop the server")
                    
                count += 1
                if count%10000 == 0:
                    await ctx.send("Maybe we are having some serious problem... Contact adminstration if this persists")
        await ctx.send("\n\nServer correctly stopped. Use **!shutdown** if you have the necessary permissions")
        isBusy = False
    else:
        await ctx.send("Bot is busy, try again later")

@bot.command()
@commands.has_role("Start")
async def start(ctx):
    global isBusy
    try:
        subprocess.check_output("pgrep java", shell = True)
        minecraft_alive = True
    except subprocess.CalledProcessError:
        minecraft_alive = False
    if minecraft_alive:
        await ctx.send("There is already a server process running")
    else:
        if isBusy == False:
            isBusy = True
            # Inicia el servidor de Minecraft.
            #await ctx.send("Canviant el directori")
    
            await ctx.send(f'Server has been started by: {ctx.author.name}!')
            comanda = f"cd /home/minecraft/minecraft ; screen -S minecraftServer -dm /usr/bin/{commandStart}"
            result = subprocess.run(comanda, shell=True)
            #await ctx.send(f'El returncode es {result}')
            time.sleep(10)
            await ctx.send('Minecraft server has been instanced')
            isBusy = False
        else:
            await ctx.send("Bot is busy, please try again later")

@bot.command()
@commands.has_role("Backup")
async def backup(ctx):
    global isBusy
    await ctx.send(f"User {ctx.author.name} asked for a backup")
    member = ctx.author
    name = str(member.name)
    name = re.sub('[^A-Za-z0-9]+', '', name)

    admin_role = False
    if "Admin" in [role.name for role in member.roles]:
        admin_role = True
    if os.path.exists("/tmp/lastMinecraftBackup"):
        last_backup_time = datetime.fromtimestamp(os.path.getmtime("/tmp/lastMinecraftBackup"))
        if datetime.now() - last_backup_time < timedelta(hours=24) and not admin_role:
            await ctx.send("You cannot backup more than once every 24 hours if you're not an admin")
            return
    try:
        subprocess.check_output("pgrep java", shell = True)
        minecraft_alive = True
    except subprocess.CalledProcessError:
        minecraft_alive = False
    print(f"Minecraft_alive és {minecraft_alive}")
    if minecraft_alive:
        await ctx.send("Minecraft is being ran")
        await ctx.send("Please, so to assure data coherence... Stop the server first")
        return
    if isBusy:
        await ctx.send("Bot is busy, try again later")
        return
    else:
        isBusy = True
    # Copia de seguretat
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backupFilename = f"/home/arnau/backup/{timestamp_str}_{name}.tar.gz"
    print(f"BackupFile és: {backupFilename}")
    await ctx.send(f"S'ha començat a realitzar un backup. {backupFilename}")
    with tarfile.open(backupFilename, "w:gz") as tar:
        tar.add("/home/minecraft/minecraft", arcname=os.path.basename("/home/minecraft/minecraft"))
    print("Tar being ran")
    await ctx.send("Backup created, sending to external server")
    
    subprocess.run(["scp",backupFilename, f"arnau@192.168.1.128:{backupFilename}"])
    os.remove(backupFilename)

    await ctx.send(f"{member.name} has created a backup.")
    with open("/tmp/lastMinecraftBackup", "w") as f:
            f.write(f"Copia de seguretat realitzada per {member.name} a {datetime.now()}")
    isBusy = False


@bot.event
async def on_ready():
    print(f'Has iniciat sessióm a {bot.user}')
# Reemplaç'your-token' amb el token del teu bot de Discord
bot.run('Token')

