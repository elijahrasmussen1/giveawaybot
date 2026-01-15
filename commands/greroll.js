const { EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const { loadGiveaways, saveGiveaways, getEntryCount, checkMessageRequirement, getUserInvites } = require('./gcreate');

module.exports = {
    name: 'greroll',
    description: 'Reroll a giveaway to pick new winner(s)',
    execute: async (message, args, client) => {
        // Check if the user has administrator permissions
        if (!message.member.permissions.has(PermissionFlagsBits.Administrator)) {
            const noPermEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Permission Denied')
                .setDescription('You need Administrator permissions to reroll giveaways!')
                .setTimestamp();
            
            return message.reply({ embeds: [noPermEmbed] });
        }
        
        // Check if giveaway ID was provided
        if (args.length === 0) {
            const usageEmbed = new EmbedBuilder()
                .setColor('#FFAA00')
                .setTitle('Invalid Usage')
                .setDescription('Usage: -greroll <giveaway_id>\n\nYou can find the giveaway ID in the footer of the giveaway message.')
                .setTimestamp();
            
            return message.reply({ embeds: [usageEmbed] });
        }
        
        const giveawayId = args[0];
        const giveaways = loadGiveaways();
        const giveaway = giveaways[giveawayId];
        
        if (!giveaway) {
            const notFoundEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Giveaway Not Found')
                .setDescription(`No giveaway found with ID: ${giveawayId}`)
                .setTimestamp();
            
            return message.reply({ embeds: [notFoundEmbed] });
        }
        
        if (!giveaway.ended) {
            const notEndedEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Giveaway Not Ended')
                .setDescription('You can only reroll giveaways that have already ended!')
                .setTimestamp();
            
            return message.reply({ embeds: [notEndedEmbed] });
        }
        
        try {
            const channel = await client.channels.fetch(giveaway.channelId);
            const giveawayMsg = await channel.messages.fetch(giveaway.messageId);
            
            // Get reactions
            const reaction = giveawayMsg.reactions.cache.get('🎉');
            if (!reaction) {
                await message.reply('No one entered the giveaway!');
                return;
            }
            
            const users = await reaction.users.fetch();
            const validEntries = [];
            const previousWinners = new Set(giveaway.winners || []);
            
            // Process each user (excluding previous winners)
            for (const [userId, user] of users) {
                if (user.bot || previousWinners.has(userId)) continue;
                
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
                await message.reply('No valid entries remaining for reroll!');
                return;
            }
            
            // Pick new winners
            const newWinners = [];
            const winnerIds = new Set();
            const maxWinners = Math.min(giveaway.winners, validEntries.length);
            
            while (newWinners.length < maxWinners) {
                const randomIndex = Math.floor(Math.random() * validEntries.length);
                const winnerId = validEntries[randomIndex];
                
                if (!winnerIds.has(winnerId)) {
                    newWinners.push(winnerId);
                    winnerIds.add(winnerId);
                }
            }
            
            // Announce new winners
            const winnerMentions = newWinners.map(id => `<@${id}>`).join(', ');
            const rerollEmbed = new EmbedBuilder()
                .setColor('#FFD700')
                .setTitle('Giveaway Rerolled!')
                .setDescription(`**Prize:** ${giveaway.prize}\n\n**New Winner(s):** ${winnerMentions}`)
                .setFooter({ text: `Giveaway ID: ${giveawayId}` })
                .setTimestamp();
            
            await channel.send({ embeds: [rerollEmbed] });
            
            // Update stored winners
            giveaway.winners = newWinners;
            saveGiveaways(giveaways);
            
            await message.reply('Giveaway rerolled successfully!');
            
        } catch (error) {
            console.error('Error rerolling giveaway:', error);
            const errorEmbed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle('Error')
                .setDescription('An error occurred while rerolling the giveaway.')
                .setTimestamp();
            
            await message.reply({ embeds: [errorEmbed] });
        }
    }
};
