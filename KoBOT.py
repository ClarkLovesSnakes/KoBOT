import discord
from discord.channel import DMChannel
from discord.ext import commands
import asyncio
import random

#Globals and Constants
quirkLines = []
usedQuirks = []
dnd = False
playersToChars = {}
charsToNumbers = {}
charsToNumbers["Other"] = []

# Instantiate the bot, give it the command prefix
bot = discord.ext.commands.Bot(command_prefix = "!")

async def main():
    """main() driver function, takes no arguments, returns nothing. Instantiates global arrays, opens secret token file, runs bot based on this token."""

    global quirkLines
    global charsToNumbers

    # Open the quirk document, populate the global array, and close the document
    with open("Quirks.txt", "r", encoding = "utf-8") as quirks:
        quirkLines = quirks.readlines()

    # Open the characters document, populate the global array, and close the document
    with open("Characters.txt", "r", encoding = "utf-8") as characters:
        charLines = characters.readlines()
        for line in charLines:
            line = line.strip()
            char = line.split("|")
            try:
                luckyNums = char[1].split(" ")
            except IndexError:
                continue
            for i in range(len(luckyNums)):
                luckyNums[i] = int(luckyNums[i])
                    
            charsToNumbers[char[0]] = luckyNums

    # Get the token out of the secret token doc
    with open("Token.txt", "r", encoding="utf-8") as tokenDoc:
        TOKEN = tokenDoc.readline()

    # Run the bot
    await bot.start(TOKEN)
    return


@bot.command()
async def quit(ctx):
    """quit() takes no arguments, returns nothing, and simply closes the bot, as well as ending relevant processes"""

    await ctx.send("Logging Off!")
    await bot.close()
    loop.stop()
    return


@bot.command()
async def hello(ctx):
    """hello() takes no arguments, returns nothing. Greets the user when prompted"""
    await ctx.send("Greetings, human!")
    return


# The quirk function
def quirk(index = None):
    """quirk() takes one optional argument, an integer called index. Returns the quirk at that index, or a random one if no index is specified."""

    global quirkLines
    global usedQuirks

    # If no index is requested, select a random one
    if index is None:
        index = random.randint(0, 99)

    # Send the output
    return quirkLines[index]


# The dice-rolling function
def dice_roll(dice, id, modifier = None):
    """dice_roll() takes two arguments, dice and modifier. Dice is an integer, and  modifier is either None or an integer. It returns a dice roll result."""

    global dnd
    global playersToChars
    global charsToNumbers

    # Parse the integer value of dice and get the random roll, store that base value
    output = ""
    roll = random.randint(1, dice) # Generate the actual roll
    base = str(roll) 

    # Determine the modifier, and if it exists, add it to the output
    if modifier is None:
        output += base
    else:
        if modifier >= 0:
            output += (base + " + " + str(modifier))
        elif modifier <= -1:
            output += (base + " - " + str(modifier)[1:]) # strip the negative sign off of the modifier

        if not(dnd) and ((roll >= dice and modifier <= -1) or (roll <= 1 and modifier >= 1)):
            output += "\n" + base
        
        else:
            roll += modifier
            output += "\n" + str(roll)

    if not(dnd):
        
        base = int(base)

        # Determine if the roll was natural, and get the correct quirk and points if it is a crit
        isTwenty = dice == 20
        natural = (base == dice) or (base == 1)
        if roll >= dice:
            output += crit(natural, isTwenty)

        elif roll <= 1:
            output += fail(natural, isTwenty)

        elif (roll in charsToNumbers[playersToChars[id]] or base in charsToNumbers[playersToChars[id]]) and isTwenty:
            print("test")
            output += "\n***Lucky Number!***"
            output += ("\n" + quirk())

    return output


def crit(natural, isTwenty):
    """crit() takes one argument, a boolean called natural. It returns a quirk and points string"""

    output = "\n***Critical Success!***"
    if isTwenty:
        output += ("\n" + quirk())
        if natural:
            output += "You gained three **(3)** Positive Crit Points from a Natural Critical Success. Apply them as you wish or store them in your pool."
            return output
        output += "You gained two **(2)** Positive Crit Points. Apply them as you wish or store them in your pool."
    return output

def fail(natural, isTwenty):
    """fail() takes one argument, a boolean called natural. It returns a quirk and points string"""

    output = "\n***Critical Failure!***"
    if isTwenty:
        output += ("\n" + quirk())
        if natural:
            output += "You gained three **(3)** Negative Crit Points from a Natural Critical Failure. Unless otherwise instructed, please apply them now."
            return output
        output += "You gained two **(2)** Negative Crit Points. Unless otherwise instructed, please apply them now."
    return output


# The shortcut async rolling function for a plain d20
@bot.command(name = "r")
async def shortcut_roll(ctx):
    """r() takes no arguments and returns a dice roll integer, rolling a standard d20 with no modifiers"""
    await ctx.send(dice_roll(20, ctx.author.id))
    return


@bot.command(name="dnd")
async def toggleDnd(ctx):

    global dnd

    dnd = not dnd

    if(dnd):
        await bot.change_presence(activity = discord.Game(name = "Dungeons and Dragons"))
        await ctx.send("D&D mode turned on!")
        return

    await ctx.send("D&D mode turned off!")
    await bot.change_presence(activity = discord.Game(name = "Knaves of the Oblong Stool"))
    return



# The async rolling function
@bot.command(name = "roll")
async def parse_roll(ctx, dice, modifier = None):
    """roll() takes two arguments, a string dice and a string modifier, both with specifics formats, and return nothing. Parses the dice string, and gets the values for a dice roll with that modifier """

    # If the modifier exists, it must be an integer
    if modifier is not None:
        try:
            modifier = int(modifier)
        except ValueError:
            await ctx.send("Modifier must be some integer. Please enter a valid modifier.")
            return

    # Assume a negative location to start
    locationOfD = -1

    # Find the d or D if relevant
    for i in range(len(dice)):
        if dice[i] in ["d", "D"]:
            locationOfD = i
            break

    try:
        final = int(dice[locationOfD + 1:])
        if final <= 0:
            raise ValueError
    except ValueError:
        await ctx.send("Dice to be rolled must be a positive integer.")
        return

    # If there is no d or no number before the D, roll that number
    if dice[0:locationOfD] == "" or locationOfD == -1:
       await ctx.send(dice_roll(int(dice[locationOfD + 1:]), ctx.author.id, modifier))

    # If there is a number in front of the D, roll that many Dice
    else: # If there is a value before the d or D (That is, !roll Xd20)

        try:
            numberOfRolls = int(dice[0:locationOfD])
            if numberOfRolls <= 0:
                raise ValueError
        except ValueError:
            await ctx.send("Number of dice to be rolled must be a positive integer.")
            return

        for _ in range(numberOfRolls):
            await ctx.send(dice_roll(int(dice[locationOfD + 1:]), ctx.author.id, modifier)) 

    return

# The async quirk command
@bot.command(name = "quirk")
async def find_quirk(ctx, index = None):
    """find_quirk() takes one optional argument, index. It uses the index, or a random one if not used, to call quirk(), and returns a quirk."""

    if index is not None:
        try:
            index = int(index)
            if index < 0:
                raise ValueError
        except ValueError:
            await ctx.send("Quirk Index must be some positive integer. Please enter a valid index.")
            return

    output = quirk(index) 
    await ctx.send(output) 
    return


# The async multiquirk command
@bot.command(name = "multiquirk")
async def multiquirk(ctx, number):
    """multiquirk() takes one argument, number, and returns a number of quirks."""

    try:
        number = int(number)
        if number <= 0:
            raise ValueError
    except ValueError:
        await ctx.send("Multiquirk Number must be some positive integer. Please enter a valid number.")
        return
    else:
        for _ in range(number):
            output = quirk(None)
            await ctx.send(output)
            
        return


@bot.command(name = "join")
async def joinPlayer(ctx):
    # Players must join the game to play
    playersToChars[ctx.author.id] = "Other"
    await ctx.send(ctx.author.name + " has joined the game!")
    return


@bot.command(name = "select")
async def selectChar(ctx, character):

    global playersToChars
    global charstoNumbers

    if character != "Other":

        if character not in charsToNumbers:
            await ctx.send("The character " + character + " does not exist. Consider creating them.")
            return

        for player in playersToChars:
            if playersToChars[player] == character:
                await ctx.send("The character " + character + " is already being played!")
                return

    if ctx.author.id in playersToChars:
        await ctx.send(str(ctx.author.name) + " is no longer playing " + playersToChars[ctx.author.id])

    playersToChars[ctx.author.id] = character

    await ctx.send(str(ctx.author.name) + " is now playing " + character)
    return

@bot.command(name = "create")
async def createChar(ctx, character, *args):

    global charsToNumbers

    if character in charsToNumbers:
        await ctx.send("The character " + character + " already exists.")
        return
     
    luckyNums = []
    try:
        if(len(args)) < 1:
            raise IndexError
        for i in range(len(args)):
            luckyNums.append(int(args[i]))
            if luckyNums[i] >= 20 or luckyNums[i] <= 1:
                raise ValueError
    except IndexError:
        await ctx.send("Character " + character + " must have at least one lucky number.")
        return
    except ValueError:
        await ctx.send("Character " + character + "'s lucky numbers must be integers greater than 1 but less than 20.")
        return

    charsToNumbers[character] = luckyNums

    with open("Characters.txt", "a") as chars:
        chars.write(character)
        chars.write("|")
        for n in luckyNums:
            chars.write(str(n))
            chars.write(" ")
        chars.write("\n")

    await ctx.send("Character " + character + " has been created with Lucky Numbers " + str(luckyNums))
    return
    

@bot.command(name = "query")
async def query(ctx):
    global playersToChars

    await ctx.send(ctx.message.author.name + " is playing " + playersToChars[ctx.message.author.id])
    return

@bot.command(name = "delete")
async def delete(ctx, character):
    global playersToChars
    global charsToNumbers

    if(character == "Other"):
        await ctx.send("You cannot Delete \"Other.\" They are too powerful!")
        return

    for key in playersToChars:
        if playersToChars[key] == character:
            playersToChars[key] = "Other"
            break

    del charsToNumbers[character]

    with open("Characters.txt", "w") as chars:
        for char in charsToNumbers:
            chars.write(char)
            chars.write(" ")
            for n in charsToNumbers[char]:
                chars.write(str(n))
                chars.write(" ")
            chars.write("\n")
    
    await ctx.send(character + " has been deleted!")
    return


@bot.command(name = "list")
async def list(ctx):
    global playersToChars
    global charsToNumbers

    await ctx.send("List of current characters:\n")
    for character in charsToNumbers:
        if character != "Other":
            await ctx.send(character)

    return


# Speak when online
@bot.event
async def on_ready():
    # Startup
    await bot.change_presence(activity = discord.Game(name = "Knaves of the Oblong Stool")) # Change the game being played to "Knaves of the Oblong Stool"
    print("Bot is logged in as {0.user}".format(bot)) # Print to the console that the user is logged in as KotOS Bot
    print("All systems are online. Awaiting orders.") # Print that everything is working
    return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
