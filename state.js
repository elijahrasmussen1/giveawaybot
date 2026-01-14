// Shared state management for the bot
let targetNumber = null;

module.exports = {
    getTargetNumber: () => targetNumber,
    setTargetNumber: (number) => {
        targetNumber = number;
    },
    clearTargetNumber: () => {
        targetNumber = null;
    }
};
