const { EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const config = require('../config.json');
const state = require('../state.js');

module.exports = {
    name: 'setnumber',
    description: 'Sets the target number for the guess the number game (Admin only)',
    execute: async (message, args, client) => {
        // Check if the user has administrator permissions
        if (!message.member.permissions.has(PermissionFlagsBits.Administrator)) {
            const noPermEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Permission Denied')
                .setDescription('You need Administrator permissions to use this command!')
                .setTimestamp();
            
            return message.reply({ embeds: [noPermEmbed] });
        }

        // Check if a number was provided
        if (args.length === 0) {
            const usageEmbed = new EmbedBuilder()
                .setColor('#FFAA00')
                .setTitle('Invalid Usage')
                .setDescription(`Usage: ${config.prefix}setnumber <number>`)
                .setTimestamp();
            
            return message.reply({ embeds: [usageEmbed] });
        }

        const number = parseInt(args[0]);

        // Validate the number
        if (isNaN(number)) {
            const invalidEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Invalid Number')
                .setDescription('Please provide a valid number!')
                .setTimestamp();
            
            return message.reply({ embeds: [invalidEmbed] });
        }

        // Set the target number using the state module
        state.setTargetNumber(number);

        // Send confirmation to admin
        const confirmEmbed = new EmbedBuilder()
            .setColor('#00FF00')
            .setTitle('Number Set!')
            .setDescription(`Target number has been set to: ||${number}||`)
            .setTimestamp();
        
        await message.reply({ embeds: [confirmEmbed] });

        // Get the guess channel from cache or fetch it
        const guessChannel = client.channels.cache.get(config.guessChannelId) || 
                             await client.channels.fetch(config.guessChannelId).catch(() => null);
        
        if (guessChannel) {
            const activationEmbed = new EmbedBuilder()
                .setColor('#0099FF')
                .setTitle('🎮 GUESS THE NUMBER ACTIVATED! 🎮')
                .setDescription('YOU MAY GUESS UNTIL SOMEBODY GETS IT RIGHT!')
                .setFooter({ text: 'Good luck!' })
                .setTimestamp();
            
            await guessChannel.send({ embeds: [activationEmbed] });
        } else {
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Error')
                .setDescription('Could not find the guess channel. Please check the channel ID in config.json')
                .setTimestamp();
            
            await message.reply({ embeds: [errorEmbed] });
        }
    }
};
