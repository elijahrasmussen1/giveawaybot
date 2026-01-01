const { Client, GatewayIntentBits, Collection, EmbedBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const config = require('./config.json');

// Create a new Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ]
});

// Initialize commands collection
client.commands = new Collection();

// Load commands from commands folder
const commandsPath = path.join(__dirname, 'commands');
if (fs.existsSync(commandsPath)) {
    const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

    for (const file of commandFiles) {
        const filePath = path.join(commandsPath, file);
        const command = require(filePath);
        
        if ('name' in command && 'execute' in command) {
            client.commands.set(command.name, command);
            console.log(`Loaded command: ${command.name}`);
        } else {
            console.log(`[WARNING] The command at ${filePath} is missing a required "name" or "execute" property.`);
        }
    }
}

// Store the target number for the guess game
let targetNumber = null;

// Bot ready event
client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
    console.log(`Bot is ready! Using prefix: ${config.prefix}`);
});

// Message handler
client.on('messageCreate', async message => {
    // Ignore messages from bots
    if (message.author.bot) return;

    // Check if message is a command
    if (message.content.startsWith(config.prefix)) {
        const args = message.content.slice(config.prefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        const command = client.commands.get(commandName);

        if (!command) return;

        try {
            await command.execute(message, args, client);
        } catch (error) {
            console.error(`Error executing command ${commandName}:`, error);
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Error')
                .setDescription('There was an error executing this command!')
                .setTimestamp();
            
            await message.reply({ embeds: [errorEmbed] });
        }
    }
    // Check for number guesses in the designated channel
    else if (message.channel.id === config.guessChannelId && targetNumber !== null) {
        const guess = parseInt(message.content.trim());
        
        // Check if the message is a valid number
        if (!isNaN(guess)) {
            // Check if the guess matches the target number
            if (guess === targetNumber) {
                const winnerEmbed = new EmbedBuilder()
                    .setColor('#00FF00')
                    .setTitle('🎉 WINNER! 🎉')
                    .setDescription(`${message.author} guessed the number! Ping an owner to obtain your prize!`)
                    .setTimestamp();
                
                await message.channel.send({ embeds: [winnerEmbed] });
                
                // Reset the target number after someone wins
                targetNumber = null;
            }
        }
    }
});

// Export for use in commands
module.exports = { targetNumber, setTargetNumber: (num) => { targetNumber = num; } };

// Login to Discord
client.login(process.env.DISCORD_TOKEN);
