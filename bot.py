"""
Main bot class for Joker's Telegram Bot
"""

import logging
import signal
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes
)
from telegram import Update
from config import BOT_TOKEN, PORT
# Import HEALTH_CHECK_ENABLED safely
try:
    from config import HEALTH_CHECK_ENABLED
except ImportError:
    # Fallback if import fails - detect deployment environment
    import os
    HEALTH_CHECK_ENABLED = bool(os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'))
from handlers import (
    handle_new_chat_members, start_command, help_command,
    about_command, dev_command, handle_message, handle_edited_message,
    stats_command, deploy_command, error_handler
)

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks on deployment platforms"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "bot": "jokers-telegram-bot"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

class TelegramBot:
    """Main Telegram Bot class"""
    
    def __init__(self):
        """Initialize the bot"""
        self.application = None
        self.health_server = None
        self.setup_bot()
        if HEALTH_CHECK_ENABLED:
            self.setup_health_server()
    
    def setup_health_server(self):
        """Setup HTTP health check server for deployment platforms"""
        try:
            self.health_server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
            health_thread = threading.Thread(target=self.health_server.serve_forever, daemon=True)
            health_thread.start()
            logger.info(f"Health check server started on port {PORT}")
        except Exception as e:
            logger.warning(f"Could not start health server: {e}")

    def start(self):
        """Start the bot using run_polling"""
        try:
            if not self.application:
                raise RuntimeError("Bot application not properly initialized")
                
            # Start health server if enabled
            if HEALTH_CHECK_ENABLED and not self.health_server:
                self.setup_health_server()
                
            # Get bot info and start
            logger.info("Starting Joker's Telegram Bot...")
            logger.info(f"Health check enabled: {HEALTH_CHECK_ENABLED}")
            logger.info(f"Port configured: {PORT}")
            
            self.application.run_polling(
                poll_interval=1.0,
                timeout=10,
                read_timeout=10,
                write_timeout=10,
                connect_timeout=10,
                pool_timeout=10,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    def setup_bot(self):
        """Setup the bot application and handlers"""
        try:
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", start_command))
            self.application.add_handler(CommandHandler("help", help_command))
            self.application.add_handler(CommandHandler("about", about_command))
            self.application.add_handler(CommandHandler("dev", dev_command))
            self.application.add_handler(CommandHandler("stats", stats_command))
            self.application.add_handler(CommandHandler("deploy", deploy_command))
            
            # Add message handlers
            self.application.add_handler(
                MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members)
            )
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            )
            
            # Add edited message handler
            self.application.add_handler(
                MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message)
            )
            
            # Add error handler
            self.application.add_error_handler(error_handler)
            
            logger.info("Bot handlers configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup bot: {e}")
            raise
    

