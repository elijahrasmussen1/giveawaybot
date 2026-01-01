# Bot Usage Examples

## Setting Up the Guess the Number Game

### Step 1: Admin Sets the Number
An administrator uses the command with their chosen number:
```
&setnumber 42
```

**Bot Response (to admin):**
> ✅ **Number Set!**
> Target number has been set to: ||42||

**Bot Announcement (in game channel):**
> 🎮 **GUESS THE NUMBER ACTIVATED!** 🎮
> YOU MAY GUESS UNTIL SOMEBODY GETS IT RIGHT!
> Good luck!

### Step 2: Players Make Guesses
Players can guess by typing numbers in the designated channel:

```
Player1: 25
Player2: 50
Player3: 42
```

### Step 3: Winner Announced
When someone guesses correctly:

**Bot Announcement:**
> 🎉 **WINNER!** 🎉
> @Player3 guessed the number! Ping an owner to obtain your prize!

After a winner is announced, the game resets and admins need to use `&setnumber` again to start a new round.

## Permission Requirements

- **&setnumber**: Requires Administrator permission
- **Guessing**: Anyone can participate by typing numbers in the game channel

## Error Handling

### Invalid Number
```
&setnumber abc
```
**Bot Response:**
> ❌ **Invalid Number**
> Please provide a valid number!

### Missing Permission
```
&setnumber 100
```
(When used by non-admin)

**Bot Response:**
> ❌ **Permission Denied**
> You need Administrator permissions to use this command!

### Missing Number Argument
```
&setnumber
```
**Bot Response:**
> ⚠️ **Invalid Usage**
> Usage: &setnumber <number>

## Tips for Server Owners

1. **Designate a Game Channel**: Update `config.json` with the correct channel ID where you want the game to run
2. **Set Clear Rules**: Let your community know:
   - What prizes are available
   - How to claim prizes
   - Game frequency/schedule
3. **Test First**: Try the command in a private channel first to ensure everything works
4. **Monitor Activity**: Keep an eye on the game channel to prevent spam
5. **Have Fun**: Use this as a community engagement tool during events or special occasions

## Future Expansion Ideas

The modular command structure allows you to easily add:
- **Giveaway commands** for managing community giveaways
- **Game night scheduling** for organizing events
- **Leaderboards** to track winners
- **Multiple game channels** with different games
- **Custom prize tiers** based on difficulty
- **Hint system** for harder numbers
