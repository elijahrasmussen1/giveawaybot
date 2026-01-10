const { EmbedBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');

const MESSAGES_FILE = path.join(__dirname, '..', 'messages.json');

// Load or initialize message tracking data
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

module.exports = {
    name: 'm',
    description: 'Shows message count statistics for a user',
    aliases: ['messages'],
    execute: async (message, args, client) => {
        // Get the target member
        let member = message.mentions.members.first() || message.member;
        
        // If args provided but no mention, try to get by ID
        if (args.length > 0 && !message.mentions.members.first()) {
            try {
                member = await message.guild.members.fetch(args[0]);
            } catch (error) {
                // Invalid ID, default to message author
                member = message.member;
            }
        }
        
        const userId = member.user.id;
        
        // Load message data
        const messagesData = loadMessages();
        const userMessages = messagesData[userId] || [];
        
        if (userMessages.length === 0) {
            const noDataEmbed = new EmbedBuilder()
                .setColor('#0099FF')
                .setTitle('📊 Message Statistics')
                .setDescription(`No messages tracked for ${member} yet.`)
                .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
                .setTimestamp();
            
            return message.channel.send({ embeds: [noDataEmbed] });
        }
        
        // Calculate time periods
        const now = new Date();
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() - now.getDay());
        weekStart.setHours(0, 0, 0, 0);
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
        
        // Count messages in each period
        let messagesToday = 0;
        let messagesWeek = 0;
        let messagesMonth = 0;
        const messagesAllTime = userMessages.length;
        
        for (const timestampStr of userMessages) {
            try {
                const msgTime = new Date(timestampStr);
                
                if (msgTime >= todayStart) {
                    messagesToday++;
                }
                if (msgTime >= weekStart) {
                    messagesWeek++;
                }
                if (msgTime >= monthStart) {
                    messagesMonth++;
                }
            } catch (error) {
                // Skip invalid timestamps
                continue;
            }
        }
        
        // Create embed
        const embed = new EmbedBuilder()
            .setColor('#0099FF')
            .setTitle('📊 Message Statistics')
            .setDescription(`Activity stats for ${member}`)
            .addFields(
                { name: '📅 Today', value: `**${messagesToday.toLocaleString()}** messages`, inline: true },
                { name: '📆 This Week', value: `**${messagesWeek.toLocaleString()}** messages`, inline: true },
                { name: '📊 This Month', value: `**${messagesMonth.toLocaleString()}** messages`, inline: true },
                { name: '🌟 All Time', value: `**${messagesAllTime.toLocaleString()}** messages`, inline: true }
            )
            .setThumbnail(member.user.displayAvatarURL({ dynamic: true }))
            .setFooter({ 
                text: `Requested by ${message.author.tag}`, 
                iconURL: message.author.displayAvatarURL({ dynamic: true })
            })
            .setTimestamp();
        
        await message.channel.send({ embeds: [embed] });
    }
};
