const { Client, GatewayIntentBits, Collection, EmbedBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const config = require('./config.json');
const state = require('./state.js');

// Message tracking
const MESSAGES_FILE = path.join(__dirname, 'messages.json');

function loadMessages() {
    try {
        if (fs.existsSync(MESSAGES_FILE)) {
            const data = fs.readFileSync(MESSAGES_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading messages data:', error);
    }
    return {};
}

function saveMessages(data) {
    try {
        fs.writeFileSync(MESSAGES_FILE, JSON.stringify(data, null, 2));
    } catch (error) {
        console.error('Error saving messages data:', error);
    }
}

let messagesData = loadMessages();

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

// Bot ready event
client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
    console.log('Bot is ready!');
});

// Message handler
client.on('messageCreate', async message => {
    // Ignore messages from bots
    if (message.author.bot) return;

    // Track message for statistics
    const userId = message.author.id;
    const timestamp = new Date().toISOString();
    
    if (!messagesData[userId]) {
        messagesData[userId] = [];
    }
    
    messagesData[userId].push(timestamp);
    saveMessages(messagesData);

    // Check if message is a command
    if (message.content.startsWith(config.prefix)) {
        const args = message.content.slice(config.prefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        const command = client.commands.get(commandName) || client.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));

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
    else if (message.channel.id === config.guessChannelId && state.getTargetNumber() !== null) {
        const guess = parseInt(message.content.trim());
        
        // Check if the message is a valid number
        if (!isNaN(guess)) {
            // Check if the guess matches the target number
            if (guess === state.getTargetNumber()) {
                const winnerEmbed = new EmbedBuilder()
                    .setColor('#00FF00')
                    .setTitle('🎉 WINNER! 🎉')
                    .setDescription(`${message.author} guessed the number! Ping an owner to obtain your prize!`)
                    .setTimestamp();
                
                await message.channel.send({ embeds: [winnerEmbed] });
                
                // Reset the target number after someone wins
                state.clearTargetNumber();
            }
        }
    }
});

// Login to Discord
client.login(process.env.DISCORD_TOKEN);
