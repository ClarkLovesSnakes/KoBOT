import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import random


# Denote the existence of the bot, and also that commands will begin with "!"
bot = commands.Bot(command_prefix = "!") # I've been taught to not use global variables, but the decorators don't seem
# to like this being local and I don't see a reason to make it occur in every function. I suppose I could make
# everything a local function, but that seems silly. Some variables can be global. It won't hurt anything.


# This command says "Greetings, human!" when the user says "!hello"
@bot.command()
async def hello(ctx):
    ######
    #
    # This command says "Greetings, human!" when the user says "!hello". It has a docstring because of consistency.
    #
    ######

    await ctx.send("Greetings, human!")


#####
#
# The two following functions are the non-asynchronous backbones of...
# The quirk and dice-rolling systems
#
#####


# The quirk function
def quirk(index):
    ######
    #
    # This function is called by the Asynchronous !quirk function, and eventually returns a value to that function to
    # be printed by the bot This function takes in one argument, index, which can be None, an integer... or a string,
    # and returns a quirk from the google sheet list. If index = None, it is assigned a random integer from 1 to 100
    # and the Quirk of that number is returned. If it is a specific integer, the same occurs.
    #
    ######

    # Open and set up the quirk document
    quirks = open("Quirks.txt", "r")
    quirkLines = quirks.readlines()
    quirks.close()

    # Open and set up the Used Quirk document
    usedQuirks = open("UsedQuirks.txt", "r")
    usedLines = usedQuirks.readlines()
    usedQuirks.close()

    # Split the string on spaces
    usedLines = usedLines[0].split(" ")

    # Find the entries in the list that are empty strings and delete them in reverse order
    storedDeletingIndeces = []
    for i in range(len(usedLines)):
        if usedLines[i] == "":
            storedDeletingIndeces.append(i)

    storedDeletingIndeces = storedDeletingIndeces[::-1]
    for j in range(len(storedDeletingIndeces)):
        del usedLines[storedDeletingIndeces[j]]


    if index is None: # If index is None, generate a random integer between 1 and 100
        index = random.randint(1, 100)


        #Check that the quirk hasn't been seen recently
        while(str(index) in usedLines):
            index = random.randint(1, 100)

        # Add the index to the list of quirks that have been used
        usedLines.append(index)

        # If more than 20 quirks are on the list, delete the oldest entries until there are 20
        while(len(usedLines) > 20):
            del usedLines[0]

        #  Rewrite to the file so that the list is preserved between sessions.
        usedQuirks = open("UsedQuirks.txt", "w")
        for usedIndex in usedLines:
            usedQuirks.write(str(usedIndex))
            usedQuirks.write(" ")
        usedQuirks.close()

    index += -1 # Decrement the value by 1, because arrays start at 0
    output = quirkLines[index] # Get the proper quirk
    return output # return the quirk


# The dice-rolling function
def dice_roll(dice, check, modifier = None):
    ######
    #
    # This function is called by the Asynchronous !roll function, and eventually returns values to that function to
    # be printed by the bot This function takes two arguments, dice, an positive integer, and modifier,
    # which defaults to None but can be an integer Rolls a dice between 1 and the value of dice. If dice is a 1 or
    # the highest possible value, it notes that there is a critical success or failure If there is a crit success or
    # crit fail, generate a quirk via quirk() store all relevant values as strings concatenated to output.
    # This is returned and spoken by the bot
    #
    ######

    # Convert dice to an int if it is not
    dice = int(dice)

    output = "" # Initialize the outputs as None
    roll = random.randint(1, dice) # Generate the actual roll

    base_roll = roll # Store the base value of the roll that won't be modified

    if modifier is None or int(modifier) == 0: # If there is no modifier
        output += str(roll) # Send out the dice

        if roll >= dice: # If the dice is the highest possible value
            output += "\nCritical Success!" # Send the words "Critical Success!" to an output
            if (dice == 20 or dice == 100) and not(check):
                output += ("\n" + quirk(None))  # Send a quirk to an output

                if (base_roll == dice):
                    output += "You gained three Positive Crit Points from a Natural Critical Success. Apply them as you wish or store them in your pool."
                else:
                    output += "You gained two Positive Crit Points. Apply them as you wish or store them in your pool." # Tells the player that they have gained positive crit points

        elif roll <= 1: # If the dice is a 1
            output += "\nCritical Failure!" # Send the words "Critical Failure!" to an output
            if (dice == 20 or dice == 100) and not(check):
                output += ("\n" + quirk(None))  # Send a quirk to an output

                if(base_roll == 1):
                    output += "You gained three Negative Crit Points from a Natural Critical Failure. Unless otherwise instructed, please apply them now."
                else:
                    output += "You gained two Negative Crit Points. Unless otherwise instructed, please apply them now." # Tells the player that they have gained two negative crit points

    elif int(modifier) >= 1: # If the modifier is 1 or above
        # Positive (plus) modifiers
        output += (str(roll) + " + " + str(modifier)) # Send the string of the roll plus the modifier to an output

        if roll <= 1: # If the dice is a 1
            output += ("\n" + str(roll)) # Send the unmodified dice roll to an output
            output += "\nCritical Failure!" # Send the words "Critical Failure!" to an output
            if (dice == 20 or dice == 100) and not(check):
                output += ("\n" + quirk(None))  # Send a quirk to an output

                if(base_roll == 1):
                    output += "You gained three Negative Crit Points from a Natural Critical Failure. Unless otherwise instructed, please apply them now."
                else:
                    output += "You gained two Negative Crit Points. Unless otherwise instructed, please apply them now." # Tells the player that they have gained two negative crit points

        else: # If the roll is above a 1
            roll = roll + int(modifier) # Add the modifier to the roll
            output += ("\n" + str(roll)) # Send the modified roll to an output

            if roll >= dice: # If the modified roll is equal to or above the greatest possible value
                output += "\nCritical Success!" # Send the words "Critical Success!" to an output
                if (dice == 20 or dice == 100) and not (check):
                    output += ("\n" + quirk(None))  # Send a quirk to an output

                    if (base_roll == dice):
                        output += "You gained three Positive Crit Points from a Natural Critical Success. Apply them as you wish or store them in your pool."
                    else:
                        output += "You gained two Positive Crit Points. Apply them as you wish or store them in your pool."  # Tells the player that they have gained positive crit points

    elif int(modifier) <= -1: # If the modifier is -1 or below
        # Negative (minus) modifiers
        output += str(roll) + " - " + str(modifier[1:]) # Send the string of the roll minus the absolute value
        # of the modifier to an output

        if roll >= dice: # If the roll is at or above the highest possible value
            output += ("\n"  + str(roll)) # Send the unmodified dice roll to an output
            output += "\nCritical Success!" # Send the words "Critical Success!" to an output
            if (dice == 20 or dice == 100) and not(check):
                output += ("\n" + quirk(None))  # Send a quirk to an output

                if (base_roll == dice):
                    output += "You gained three Positive Crit Points from a Natural Critical Success. Apply them as you wish or store them in your pool."
                else:
                    output += "You gained two Positive Crit Points. Apply them as you wish or store them in your pool." # Tells the player that they have gained positive crit points

        else: # If the roll is below the highest possible value
            roll = roll + int(modifier) # Add the modifier to the roll (subtract the modifier from the roll)
            output += ("\n" + str(roll)) # Send the modified roll to an output

            if roll <= 1: # If the roll is now at 1 or below
                output += "\nCritical Failure!" # Send the words "Critical Failure!" to an output
                if (dice == 20 or dice == 100) and not(check):
                    output += ("\n" + quirk(None))   # Send a quirk to an output

                    if (base_roll == 1):
                        output += "You gained three Negative Crit Points from a Natural Critical Failure. Unless otherwise instructed, please apply them now."
                    else:
                        output += "You gained two Negative Crit Points. Unless otherwise instructed, please apply them now."  # Tells the player that they have gained two negative crit points

    # Once all the necessary outputs have been changed (The others are still initialized as None), return them all to
    # the Asynchronous function
    return output


#####
#
# The two following functions are Asynchronous functions called by discord commands beginning with a !
#
#####

# The shortcut async rolling function for a plain d20
@bot.command(name = "r")
async def shortcut_roll(ctx, dice = "", c = ""):
    #####
    #
    # Works exactly like parse_roll below it, but only for a non-modified d20
    #
    #####

    check = False
    if c == "c":
        check = True

    output= dice_roll(20, check)  # The results of
    # dice_roll() are set to these variables
    await ctx.send(output)  # The bot will speak the item


# The async rolling function
@bot.command(name = "roll")
async def parse_roll(ctx, dice, modifier = None, c = ""):
    ######
    #
    # The !roll command rolls a specified number of dice of a given number of faces, and can have a modifier added to
    # or subtracted from all of them !roll takes three arguments, the required ctx, dice, which is an intenger,
    # which is an integer or a string formatted as "#d#" or "#D#" where # is any integer (2d20, 3D8, d12, D6, etc),
    # and modifier, an int or default None The command will parse dice to determine how many dice are required to be
    # rolled (The first # in "#d#" or "#D#"), and then will, that many times, roll a dice of the given value. This
    # invokes the dice_roll() synchronous function and returns between 1 and 4 output variables, based on the
    # function of dice_roll(), and these are then spoken by the bot
    #
    ######

    if dice.lower() == "confusion":
        z = random.randint(1,10)
        if z == 10:
            await ctx.send("KoBOT hurt itself in its confusion")
            return
        else:
            await ctx.send("AAAAAAAAAAHHHHHHHHHHH!!!!")

    # See if the roll is classed as a check. If it is, set check to True
    check = False
    if modifier == "c":
        check = True
        modifier = None
    elif c == "c":
        check = True


    if modifier is not None:
        try:
            int(modifier)

        except ValueError:
            await ctx.send("Modifier must be some integer. Please enter a valid modifier.")
            return


    # Create a variable to store which character in the dice string has the "d" or the "D". This will be assigned in the
    # upcoming for loop, but will need to be referenced outside of it, so we create it here in this function.
    locationOfD = 0


    if "d" in dice or "D" in dice: # If there is a d or D in the dice string
        for dChar in range(len(dice)): # Go through all the characters in the dice string
            if dice[dChar] == "d" or dice[dChar] == "D": # Find which specific character is the d or D.
                # The characters before it will all be numbers and will refer to the number of dice to be rolled
                # The characters after it will all be numbers and will refer to the number of faces on the dice
                # to be rolled

                # set the value of dChar to locationOfD, so that the value can be used elsewhere
                locationOfD = dChar

                break # Break the loop, as only one d or D should be in the string
        # END FOR dChar

        if dice[0:locationOfD] == "": # If there is no value before the d or D (That is, !roll d20)
            output = dice_roll(int(dice[locationOfD+1:]), check, modifier) # The results of
            # dice_roll() are set to these variables # The output variables are put in a list
            await ctx.send(output) # The bot will speak the item

        else: # If there is a value before the d or D (That is, !roll Xd20)
            numberOfRolls = int(dice[0:locationOfD]) # Set the number of dice to be rolled as an integer
            for roll in range(numberOfRolls): # For that number of iterations
                output = dice_roll(int(dice[locationOfD + 1:]), check, modifier) # The results of
                # dice_roll() are set to these variables
                await ctx.send(output) # The bot will speak the item
            # END FOR roll

    else: # If there is no d or D in the string
        output = dice_roll(int(dice), check, modifier) # The results of dice_roll() are set to
        # these variables
        await ctx.send(output) # The bot will speak the item


# The async quirk command
@bot.command(name = "quirk")
async def find_quirk(ctx, index = None):
    ######
    #
    # Asynchronous method to take an argument via discord and send it through
    # to the Synchronous quirk command
    #
    ######

    if index is not None: # If the index is not set to None
        index = int(index) # Turn the index into an int
    output = quirk(index) # Set the output to the quirk of the index number or None
    await ctx.send(output) # The bot will speak the quirk


# The async multiquirk command
@bot.command(name = "multiquirk")
async def multiquirk(ctx, number):
    ######
    #
    # Asynchronous method to take an argument from discord and call the
    # Synchronous quirk command that number of times
    #
    ######

    for i in range(int(number)):
        output = quirk(None)
        await ctx.send(output)

@bot.command(name = "nonbinary")
async def nonbinary(ctx):

    await ctx.send("Valid.")


# The async gen command
@bot.command(name = "gen")
async def generate(ctx, type):
    ######
    #
    # Asynchronous method to take an argument from the user to generate a random idea of that type, based on an extensive
    # list of options
    #
    ######

    if type == "insanity":
        verbs = open("InsanityVerbs.txt", "r")
        verbLines = verbs.readlines()
        verbs.close()

        nouns = open("InsanityNouns.txt", "r")
        nounLines = nouns.readlines()
        nouns.close()

        index1 = random.randint(0, (len(verbLines)-1))
        index2 = random.randint(0, (len(nounLines)-1))


        await ctx.send(verbLines[index1].strip() + " " + nounLines[index2])



# The async info command
@bot.command(name = "info")
async def info(ctx, index = None):
    ######
    #
    # Asynchronous method to take an argument via discord and send it through
    # to the Synchronous quirk command
    #
    ######

    if index is None: # If the index is not set to None
        await ctx.send("Welcome to KotOS Bot, or KoBOT for short.\nKoBOT helps with all of your KotOS Needs. It can roll dice, using !roll, roll exactly one d20 without modifiers with !r, find single quirks with !quirk, find multiple quirks with !multiquirk, generate various random ideas with !gen, say \"Hello\" with !hello, and, of course, give help with !info.\nTo see specific information about these commands, use !info <command> (i.e. !info roll). Happy Knaving.")

    elif index == "roll":
        await ctx.send("!roll takes one or two or three arguments. The first is the size and number of the dice you are rolling, such as 20, d4, or 9d6. The second is an optional modifier added or subtracted to the final value. !roll d20 4 rolls a d20 and adds 4 to the result, !roll 4d6 -2 rolls 4 d6 and subtracts two from each result. The third is the check flag. If you enter \"c\" the roll will be read as a check, so it will not generate quirks or crit points.")

    elif index == "quirk":
        await ctx.send("!quirk takes one optional argument. If it has no argument, it displays a random quirk from the list. If you give it a numerical argument (1-100) it returns that quirk specifically.")

    elif index == "multiquirk":
        await ctx.send("!multiquirk takes one argument. This argument should be a number. The bot will then say that number of random quirks.")

    elif index == "gen":
        await ctx.send("!gen takes one argument, the name of the thing you want to generate, and then generates one for you. We'll include a full list of what you can generate eventually.")

    elif index == "r":
        await ctx.send("!r works like !roll, except it only rolls one 20-sided die with no modifiers. It can be flagged to be a check, though.")

    elif index == "hello":
        await ctx.send("!hello prompts the bot to reply \"Greetings Human!\"")

    else:
        await ctx.send("That command does not exist. Please try again.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("That command does not exist. Please try again.")

# Speak when online
@bot.event
async def on_ready():
    ######
    #
    # Startup command
    #
    ######
    await bot.change_presence(activity = discord.Game(name = "Knaves of the Oblong Stool")) # Change the game being
    # played to "Knaves of the Oblong Stool"
    print("Bot is logged in as {0.user}".format(bot)) # Print to the console that the user is logged in as KotOS Bot
    print("All systems are online. Awaiting orders.") # Print that everything is working




######
#
# The main() function, which does a few important pieces.
#
######


# Main function, to initialize all the important bits and run the bot on_ready()
def main():
    ######
    #
    # main() which initializes a few variables and runs the bot. Not much else.
    #
    ######

    # Get the token out of the secret token doc
    tokenDoc = open("Token.txt", "r")
    token = tokenDoc.readline()
    
    tokenDoc.close()

    # Run the bot
    bot.run(token)


# Run the main() function
main()
