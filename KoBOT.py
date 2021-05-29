import discord
from discord.ext import commands
import asyncio
import random

#Globals and Constants
MAX_QUIRKS = 20
quirkLines = []
usedQuirks = []
dnd = False
playersToChars = {}
charsToNumbers = {}

# Instantiate the bot, give it the command prefix
bot = discord.ext.commands.Bot(command_prefix = "!")

async def main():
    """main() driver function, takes no arguments, returns nothing. Instantiates global arrays, opens secret token file, runs bot based on this token."""

    global quirkLines

    # Open the quirk document, populate the global array, and close the document
    with open("Quirks.txt", "r", encoding = "utf-8") as quirks:
        quirkLines = quirks.readlines()

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

        '''#Check that the quirk hasn't been seen recently
        while(str(index) in usedQuirks):
            index = random.randint(0, 99)

        # Add the index to the list of quirks that have been used
        usedQuirks.append(index)

        # If more than the maximum quirks are on the list, delete the oldest entries until it is at the maximum
        while(len(usedQuirks) > MAX_QUIRKS):
            del usedQuirks[0]'''

    # Send the output
    return quirkLines[index]


# The dice-rolling function
def dice_roll(dice, id, modifier = None):
    """dice_roll() takes two argumetns, dice and modifier. Dice is an integer, and  modifier is either None or an integer. It returns a dice roll result."""

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

        # Determine if the roll was natural, and get the correct quirk and points if it is a crit
        natural = (int(base) == dice) or (int(base) == 1)
        if roll >= dice:
            output += crit(natural)

        elif roll <= 1:
            output += fail(natural)

        elif roll in charsToNumbers[playersToChars[id]] or int(base) in charsToNumbers[playersToChars[id]]:
            output += "\n***Lucky Number!***"
            output += ("\n" + quirk())

    return output


def crit(natural):
    """crit() takes one argument, a boolean called natural. It returns a quirk and points string"""

    output = "\n***Critical Success!***"
    output += ("\n" + quirk())
    if natural:
        output += "You gained three **(3)** Positive Crit Points from a Natural Critical Success. Apply them as you wish or store them in your pool."
        return output
    output += "You gained two **(2)** Positive Crit Points. Apply them as you wish or store them in your pool."
    return output

def fail(natural):
    """fail() takes one argument, a boolean called natural. It returns a quirk and points string"""

    output = "\n***Critical Failure!***"
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
    await ctx.send(dice_roll(20))
    return


@bot.command(name="dnd")
async def toggleDnd(ctx):

    global dnd

    dnd = not dnd

    if(dnd):
        await ctx.send("D&D mode turned on!")
        return

    await ctx.send("D&D mode turned off!")
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


@bot.command(name = "select")
async def selectChar(ctx, character):

    global playersToChars
    global charstoNumbers

    if character not in charsToNumbers:
        await ctx.send("The character " + character + " does not exist. Consider creating them.")
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
     
    # TO-DO:
    # Make this ints only, make this be at least one, make them > 1, < 20
    luckyNums = []
    for i in range(len(args)):
        luckyNums.append(int(args[i]))

    charsToNumbers[character] = luckyNums

    return
    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.send("That command does not exist. Please try again.")
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
