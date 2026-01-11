const { EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const fs = require('fs');
const path = require('path');
const config = require('../config.json');

const GIVEAWAYS_FILE = path.join(__dirname, '..', 'giveaways.json');
const MESSAGES_FILE = path.join(__dirname, '..', 'messages.json');

// Load or initialize giveaway data
function loadGiveaways() {
    try {
        if (fs.existsSync(GIVEAWAYS_FILE)) {
            const data = fs.readFileSync(GIVEAWAYS_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading giveaways data:', error);
    }
    return {};
}

function saveGiveaways(data) {
    try {
        fs.writeFileSync(GIVEAWAYS_FILE, JSON.stringify(data, null, 2));
    } catch (error) {
        console.error('Error saving giveaways data:', error);
    }
}

// Load message tracking data
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

// Parse duration string (e.g., "10 minutes", "5 hours", "2 days")
function parseDuration(durationStr) {
    const match = durationStr.match(/^(\d+)\s*(m|min|minute|minutes|h|hr|hour|hours|d|day|days)$/i);
    if (!match) return null;
    
    const value = parseInt(match[1]);
    const unit = match[2].toLowerCase();
    
    if (unit.startsWith('m')) {
        return value * 60 * 1000; // minutes to ms
    } else if (unit.startsWith('h')) {
        return value * 60 * 60 * 1000; // hours to ms
    } else if (unit.startsWith('d')) {
        return value * 24 * 60 * 60 * 1000; // days to ms
    }
    
    return null;
}

// Get user's invite count by checking Invite Tracker bot's response
async function getUserInvites(guild, userId) {
    // This would need to interact with Invite Tracker bot's API or slash command
    // For now, we'll return 0 as placeholder
    // In production, you'd need to use Invite Tracker's API or parse their response
    return 0;
}

// Check if user meets message requirements
function checkMessageRequirement(userId, requirement, period) {
    const messagesData = loadMessages();
    const userMessages = messagesData[userId] || [];
    
    if (userMessages.length === 0) return false;
    
    const now = new Date();
    let startTime;
    
    if (period === 'today') {
        startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    } else if (period === 'weekly') {
        startTime = new Date(now);
        startTime.setDate(now.getDate() - now.getDay());
        startTime.setHours(0, 0, 0, 0);
    } else if (period === 'monthly') {
        startTime = new Date(now.getFullYear(), now.getMonth(), 1);
    } else {
        return false;
    }
    
    let messageCount = 0;
    for (const timestampStr of userMessages) {
        try {
            const msgTime = new Date(timestampStr);
            if (msgTime >= startTime) {
                messageCount++;
            }
        } catch (error) {
            continue;
        }
    }
    
    return messageCount >= requirement;
}

// Get entry count based on roles
function getEntryCount(member) {
    const roles = config.roles;
    
    // Server Booster gets 4 entries and bypasses requirements
    if (member.roles.cache.has(roles.serverBooster)) {
        return { entries: 4, bypass: true };
    }
    
    // Shop Owner gets 3 entries
    if (member.roles.cache.has(roles.shopOwner)) {
        return { entries: 3, bypass: false };
    }
    
    // Level 5 gets 2 entries
    if (member.roles.cache.has(roles.level5)) {
        return { entries: 2, bypass: false };
    }
    
    // Member role gets 1 entry
    if (member.roles.cache.has(roles.member)) {
        return { entries: 1, bypass: false };
    }
    
    return { entries: 0, bypass: false };
}

module.exports = {
    name: 'gcreate',
    description: 'Create a new giveaway with interactive setup',
    execute: async (message, args, client) => {
        // Check if the user has administrator permissions
        if (!message.member.permissions.has(PermissionFlagsBits.Administrator)) {
            const noPermEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Permission Denied')
                .setDescription('You need Administrator permissions to create giveaways!')
                .setTimestamp();
            
            return message.reply({ embeds: [noPermEmbed] });
        }
        
        const filter = m => m.author.id === message.author.id;
        const giveawayData = {};
        
        try {
            // Question 1: Duration
            await message.channel.send('**Giveaway Setup - Question 1/5**\nEnter the duration (e.g., "10 minutes", "5 hours", "2 days"):');
            const durationMsg = await message.channel.awaitMessages({ filter, max: 1, time: 60000 });
            
            if (durationMsg.size === 0) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            
            const durationMs = parseDuration(durationMsg.first().content);
            
            if (!durationMs) {
                return message.channel.send('Invalid duration format. Giveaway creation cancelled.');
            }
            
            giveawayData.duration = durationMs;
            giveawayData.endsAt = Date.now() + durationMs;
            
            // Question 2: Number of Winners
            await message.channel.send('**Giveaway Setup - Question 2/5**\nEnter the number of winners:');
            const winnersMsg = await message.channel.awaitMessages({ filter, max: 1, time: 60000 });
            
            if (winnersMsg.size === 0) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            
            const winners = parseInt(winnersMsg.first().content);
            
            if (isNaN(winners) || winners < 1) {
                return message.channel.send('Invalid number of winners. Giveaway creation cancelled.');
            }
            
            giveawayData.winners = winners;
            
            // Question 3: Prize
            await message.channel.send('**Giveaway Setup - Question 3/5**\nEnter the prize:');
            const prizeMsg = await message.channel.awaitMessages({ filter, max: 1, time: 60000 });
            
            if (prizeMsg.size === 0) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            
            giveawayData.prize = prizeMsg.first().content;
            
            // Question 4: Invite Requirement
            await message.channel.send('**Giveaway Setup - Question 4/5 (Requirements)**\nEnter the invite requirement (or 0 for no requirement):');
            const inviteMsg = await message.channel.awaitMessages({ filter, max: 1, time: 60000 });
            
            if (inviteMsg.size === 0) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            
            const inviteReq = parseInt(inviteMsg.first().content);
            
            if (isNaN(inviteReq) || inviteReq < 0) {
                return message.channel.send('Invalid invite requirement. Giveaway creation cancelled.');
            }
            
            giveawayData.inviteRequirement = inviteReq;
            
            // Question 5: Message Requirement
            await message.channel.send('**Giveaway Setup - Question 5/5 (Requirements)**\nEnter the message requirement followed by period (e.g., "250 weekly", "100 today", "500 monthly") or "0" for no requirement:');
            const messageReqMsg = await message.channel.awaitMessages({ filter, max: 1, time: 60000 });
            
            if (messageReqMsg.size === 0) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            
            const messageReqContent = messageReqMsg.first().content.trim();
            
            if (messageReqContent === '0') {
                giveawayData.messageRequirement = 0;
                giveawayData.messagePeriod = null;
            } else {
                const msgMatch = messageReqContent.match(/^(\d+)\s+(today|weekly|monthly)$/i);
                if (!msgMatch) {
                    return message.channel.send('Invalid message requirement format. Use format like "250 weekly". Giveaway creation cancelled.');
                }
                giveawayData.messageRequirement = parseInt(msgMatch[1]);
                giveawayData.messagePeriod = msgMatch[2].toLowerCase();
            }
            
            // Generate giveaway ID
            const giveawayId = `giveaway_${Date.now()}`;
            
            // Create giveaway embed
            const giveawayEmbed = new EmbedBuilder()
                .setColor('#00FF00')
                .setTitle(`GIVEAWAY: ${giveawayData.prize}`)
                .setDescription('React with 🎉 to enter!')
                .addFields(
                    { name: 'Prize', value: giveawayData.prize, inline: false },
                    { name: 'Winners', value: `${giveawayData.winners}`, inline: true },
                    { name: 'Ends', value: `<t:${Math.floor(giveawayData.endsAt / 1000)}:R>`, inline: true }
                );
            
            // Add requirements to embed
            let requirementsText = '';
            if (giveawayData.inviteRequirement > 0) {
                requirementsText += `Invites: ${giveawayData.inviteRequirement}\n`;
            }
            if (giveawayData.messageRequirement > 0) {
                requirementsText += `Messages: ${giveawayData.messageRequirement} (${giveawayData.messagePeriod})\n`;
            }
            if (requirementsText) {
                giveawayEmbed.addFields({ name: 'Giveaway Requirements', value: requirementsText, inline: false });
            }
            
            giveawayEmbed.addFields(
                { name: 'Entry Bonuses', value: 'Member: 1 entry\nLevel 5: 2 entries\nShop Owner: 3 entries\nServer Booster: 4 entries (bypass requirements)', inline: false }
            );
            
            giveawayEmbed.setFooter({ text: `Giveaway ID: ${giveawayId}` })
                .setTimestamp(giveawayData.endsAt);
            
            // Send giveaway message
            const giveawayMsg = await message.channel.send({ embeds: [giveawayEmbed] });
            await giveawayMsg.react('🎉');
            
            // Save giveaway data
            const giveaways = loadGiveaways();
            giveaways[giveawayId] = {
                ...giveawayData,
                messageId: giveawayMsg.id,
                channelId: message.channel.id,
                guildId: message.guild.id,
                createdBy: message.author.id,
                participants: {},
                ended: false
            };
            saveGiveaways(giveaways);
            
            // Send confirmation to giveaway channel
            try {
                const giveawayChannel = await client.channels.fetch(config.giveawayChannelId);
                const confirmEmbed = new EmbedBuilder()
                    .setColor('#0099FF')
                    .setTitle('New Giveaway Created')
                    .setDescription(`A new giveaway has been created in <#${message.channel.id}>`)
                    .addFields(
                        { name: 'Giveaway ID', value: giveawayId, inline: false },
                        { name: 'Prize', value: giveawayData.prize, inline: false },
                        { name: 'Duration', value: `Ends <t:${Math.floor(giveawayData.endsAt / 1000)}:R>`, inline: false },
                        { name: 'Created By', value: `<@${message.author.id}>`, inline: false }
                    )
                    .setTimestamp();
                
                await giveawayChannel.send({ embeds: [confirmEmbed] });
            } catch (error) {
                console.error('Error sending to giveaway channel:', error);
            }
            
            // Setup timer to end giveaway
            setTimeout(async () => {
                await endGiveaway(client, giveawayId);
            }, giveawayData.duration);
            
            await message.channel.send('Giveaway created successfully!');
            
        } catch (error) {
            if (error.message && error.message.includes('time')) {
                return message.channel.send('Giveaway creation timed out. Please try again.');
            }
            console.error('Error creating giveaway:', error);
            return message.channel.send(`An error occurred while creating the giveaway: ${error.message || 'Unknown error'}`);
        }
    }
};

// Function to end giveaway and pick winners
async function endGiveaway(client, giveawayId) {
    const giveaways = loadGiveaways();
    const giveaway = giveaways[giveawayId];
    
    if (!giveaway || giveaway.ended) return;
    
    try {
        const channel = await client.channels.fetch(giveaway.channelId);
        const giveawayMsg = await channel.messages.fetch(giveaway.messageId);
        
        // Get reactions
        const reaction = giveawayMsg.reactions.cache.get('🎉');
        if (!reaction) {
            await channel.send('No one entered the giveaway!');
            giveaway.ended = true;
            saveGiveaways(giveaways);
            return;
        }
        
        const users = await reaction.users.fetch();
        const validEntries = [];
        
        // Process each user
        for (const [userId, user] of users) {
            if (user.bot) continue;
            
            try {
                const guild = await client.guilds.fetch(giveaway.guildId);
                const member = await guild.members.fetch(userId);
                
                const { entries, bypass } = getEntryCount(member);
                
                if (entries === 0) continue; // No valid roles
                
                // Check requirements (unless bypassed)
                let meetsRequirements = bypass;
                
                if (!bypass) {
                    let inviteMet = true;
                    let messageMet = true;
                    
                    if (giveaway.inviteRequirement > 0) {
                        const invites = await getUserInvites(guild, userId);
                        inviteMet = invites >= giveaway.inviteRequirement;
                    }
                    
                    if (giveaway.messageRequirement > 0) {
                        messageMet = checkMessageRequirement(userId, giveaway.messageRequirement, giveaway.messagePeriod);
                    }
                    
                    meetsRequirements = inviteMet && messageMet;
                }
                
                if (meetsRequirements) {
                    // Add entries for this user
                    for (let i = 0; i < entries; i++) {
                        validEntries.push(userId);
                    }
                }
            } catch (error) {
                console.error(`Error processing user ${userId}:`, error);
            }
        }
        
        if (validEntries.length === 0) {
            await channel.send('No valid entries for the giveaway!');
            giveaway.ended = true;
            saveGiveaways(giveaways);
            return;
        }
        
        // Pick winners
        const winners = [];
        const winnerIds = new Set();
        const maxWinners = Math.min(giveaway.winners, validEntries.length);
        
        while (winners.length < maxWinners) {
            const randomIndex = Math.floor(Math.random() * validEntries.length);
            const winnerId = validEntries[randomIndex];
            
            if (!winnerIds.has(winnerId)) {
                winners.push(winnerId);
                winnerIds.add(winnerId);
            }
        }
        
        // Announce winners
        const winnerMentions = winners.map(id => `<@${id}>`).join(', ');
        const winnerEmbed = new EmbedBuilder()
            .setColor('#FFD700')
            .setTitle('Giveaway Ended!')
            .setDescription(`**Prize:** ${giveaway.prize}\n\n**Winner(s):** ${winnerMentions}`)
            .setFooter({ text: `Giveaway ID: ${giveawayId}` })
            .setTimestamp();
        
        await channel.send({ embeds: [winnerEmbed] });
        
        // Update giveaway message
        const endedEmbed = new EmbedBuilder()
            .setColor('#FF0000')
            .setTitle(`GIVEAWAY ENDED: ${giveaway.prize}`)
            .setDescription('This giveaway has ended!')
            .addFields(
                { name: 'Winner(s)', value: winnerMentions, inline: false }
            )
            .setFooter({ text: `Giveaway ID: ${giveawayId}` })
            .setTimestamp();
        
        await giveawayMsg.edit({ embeds: [endedEmbed] });
        
        // Mark as ended
        giveaway.ended = true;
        giveaway.winners = winners;
        saveGiveaways(giveaways);
        
    } catch (error) {
        console.error('Error ending giveaway:', error);
    }
}

// Export the endGiveaway function so it can be used by greroll command
module.exports.endGiveaway = endGiveaway;
module.exports.getEntryCount = getEntryCount;
module.exports.checkMessageRequirement = checkMessageRequirement;
module.exports.getUserInvites = getUserInvites;
module.exports.loadGiveaways = loadGiveaways;
module.exports.saveGiveaways = saveGiveaways;
