"""
Joker's Telegram Bot - Render.com Deployment Version
Main entry point for the bot application
"""
import logging
import os
import sys
from bot import TelegramBot

# Configure logging for Render.com
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console output for Render.com
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    try:
        # Check for required environment variables
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN environment variable is required")
            sys.exit(1)
        
        logger.info("Starting Joker's Telegram Bot (Render.com Version)...")
        
        # Create and start the bot
        bot = TelegramBot()
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
