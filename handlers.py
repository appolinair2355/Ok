"""
Event handlers for the Telegram bot
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from config import (
    GREETING_MESSAGE, WELCOME_MESSAGE, HELP_MESSAGE, 
    ABOUT_MESSAGE, DEV_MESSAGE, MAX_MESSAGES_PER_MINUTE, RATE_LIMIT_WINDOW
)
from card_predictor import card_predictor

logger = logging.getLogger(__name__)

# Rate limiting storage
user_message_counts = defaultdict(list)

def is_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited"""
    now = datetime.now()
    user_messages = user_message_counts[user_id]

    # Remove old messages outside the window
    user_messages[:] = [msg_time for msg_time in user_messages 
                       if now - msg_time < timedelta(seconds=RATE_LIMIT_WINDOW)]

    # Check if user exceeded limit
    if len(user_messages) >= MAX_MESSAGES_PER_MINUTE:
        return True

    # Add current message time
    user_messages.append(now)
    return False

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when bot is added to a channel or group"""
    try:
        # Check if our bot was added
        if update.message and update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if member.id == context.bot.id:
                    chat = update.effective_chat
                    if chat:
                        logger.info(f"Bot added to {chat.type}: {chat.title} (ID: {chat.id})")

                        # Send greeting message
                        await context.bot.send_message(
                            chat_id=chat.id,
                            text=GREETING_MESSAGE
                        )

                        logger.info(f"Greeting sent to {chat.title}")
                    break

    except Exception as e:
        logger.error(f"Error in handle_new_chat_members: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    try:
        user = update.effective_user
        chat = update.effective_chat

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user and chat:
            logger.info(f"Start command from user {user.id} in chat {chat.id}")

        if update.message:
            await update.message.reply_text(WELCOME_MESSAGE)

    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    try:
        user = update.effective_user

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user:
            logger.info(f"Help command from user {user.id}")

        if update.message:
            await update.message.reply_text(HELP_MESSAGE)

    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command"""
    try:
        user = update.effective_user

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user:
            logger.info(f"About command from user {user.id}")

        if update.message:
            await update.message.reply_text(ABOUT_MESSAGE)

    except Exception as e:
        logger.error(f"Error in about_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def dev_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dev command"""
    try:
        user = update.effective_user

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user:
            logger.info(f"Dev command from user {user.id}")

        if update.message:
            await update.message.reply_text(DEV_MESSAGE)

    except Exception as e:
        logger.error(f"Error in dev_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages and card predictions"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        message = update.message

        # Rate limiting check for regular messages
        if user and is_rate_limited(user.id):
            return

        # Log the message
        if user and chat and message and message.text:
            logger.info(f"Message from user {user.id} in chat {chat.id}: {message.text[:50]}...")

            # Check for card prediction in group/channel messages
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                await process_card_message(update, context, message.text)

        # Only respond in private chats for regular messages
        if chat and message and chat.type == ChatType.PRIVATE:
            await message.reply_text(
                "🎭 Salut ! Je suis le bot de Joker.\n"
                "Utilisez /help pour voir mes commandes disponibles.\n\n"
                "Ajoutez-moi à un canal pour que je puisse saluer tout le monde ! 👋"
            )

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")

async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle edited messages for card predictions and verification"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        message = update.edited_message

        # Rate limiting check
        if user and is_rate_limited(user.id):
            return

        # Log the edited message
        if user and chat and message and message.text:
            logger.info(f"Edited message from user {user.id} in chat {chat.id}: {message.text[:50]}...")

            # Check for card prediction and verification in group/channel messages
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                # Process for both prediction and verification
                await process_card_message_for_verification(update, context, message.text)

    except Exception as e:
        logger.error(f"Error in handle_edited_message: {e}")

async def process_card_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> None:
    """Process message for card predictions"""
    try:
        # Check if we should make a prediction
        should_predict, game_number, combination = card_predictor.should_predict(message_text)

        if should_predict and game_number is not None and combination is not None:
            prediction = card_predictor.make_prediction(game_number, combination)
            next_game = game_number + 1  # The game we're predicting for
            logger.info(f"Making prediction: {prediction}")

            # Send prediction to the chat
            if update.effective_chat:
                sent_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=prediction
                )
                # Store the message information for potential later edits
                card_predictor.sent_predictions[next_game] = {
                    'chat_id': sent_message.chat_id,
                    'message_id': sent_message.message_id
                }
                logger.info(f"Stored prediction message for game {next_game}")

        # Check if this message verifies a previous prediction
        verification_result = card_predictor.verify_prediction(message_text)
        if verification_result and update.effective_chat:
            logger.info(f"Verification result: {verification_result}")

            if verification_result['type'] == 'update_message':
                # Edit the original prediction message instead of sending a new one
                predicted_game = verification_result['predicted_game']
                if predicted_game in card_predictor.sent_predictions:
                    message_info = card_predictor.sent_predictions[predicted_game]
                    try:
                        await context.bot.edit_message_text(
                            chat_id=message_info['chat_id'],
                            message_id=message_info['message_id'],
                            text=verification_result['new_message']
                        )
                    except Exception as e:
                        logger.error(f"Failed to edit message: {e}")
                        # Fallback: send new message if editing fails
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=verification_result['new_message']
                        )

    except Exception as e:
        logger.error(f"Error in process_card_message: {e}")

async def process_card_message_for_verification(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> None:
    """Process message specifically for verification and final predictions (used for edited messages)"""
    try:
        # Check if this is a final message that should trigger a prediction
        should_predict, game_number, combination = card_predictor.should_predict(message_text)
        
        if should_predict and game_number is not None and combination is not None:
            prediction = card_predictor.make_prediction(game_number, combination)
            next_game = game_number + 1  # The game we're predicting for
            logger.info(f"Making prediction from edited message: {prediction}")

            # Send prediction to the chat
            if update.effective_chat:
                sent_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=prediction
                )
                # Store the message information for potential later edits
                card_predictor.sent_predictions[next_game] = {
                    'chat_id': sent_message.chat_id,
                    'message_id': sent_message.message_id
                }
                logger.info(f"Stored prediction message for game {next_game} from edited message")
        
        # Check for verification
        verification_result = card_predictor.verify_prediction(message_text)
        if verification_result and update.effective_chat:
            logger.info(f"Verification result from edited message: {verification_result}")

            if verification_result['type'] == 'update_message':
                # Edit the original prediction message instead of sending a new one
                predicted_game = verification_result['predicted_game']
                if predicted_game in card_predictor.sent_predictions:
                    message_info = card_predictor.sent_predictions[predicted_game]
                    try:
                        await context.bot.edit_message_text(
                            chat_id=message_info['chat_id'],
                            message_id=message_info['message_id'],
                            text=verification_result['new_message']
                        )
                    except Exception as e:
                        logger.error(f"Failed to edit message: {e}")
                        # Fallback: send new message if editing fails
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=verification_result['new_message']
                        )

    except Exception as e:
        logger.error(f"Error in process_card_message_for_verification: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command to show prediction statistics"""
    try:
        user = update.effective_user

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user:
            logger.info(f"Stats command from user {user.id}")

        # Get prediction statistics
        stats = card_predictor.get_prediction_stats()

        stats_message = f"""
📊 **Statistiques de Prédiction**

🎯 Total des prédictions: {stats['total']}
✅ Correctes: {stats['correct']}
❌ Incorrectes: {stats['incorrect']}
🚫 Échouées: {stats['failed']}
⌛ En attente: {stats['pending']}
📈 Précision: {stats['accuracy']:.1f}%

🎭 Bot de Joker - Développé par Kouamé
        """

        if update.message:
            await update.message.reply_text(stats_message)

    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def deploy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /deploy command to create deployment package"""
    try:
        user = update.effective_user
        chat = update.effective_chat

        # Rate limiting check
        if user and is_rate_limited(user.id):
            if update.message:
                await update.message.reply_text("⏰ Veuillez patienter avant d'envoyer une autre commande.")
            return

        if user:
            logger.info(f"Deploy command from user {user.id}")

        # Import deployment utilities
        from deployment_utils import DeploymentPackager
        
        # Send initial message
        if update.message:
            initial_msg = await update.message.reply_text("🚀 Création du package de déploiement en cours...")

        try:
            # Create deployment package
            packager = DeploymentPackager()
            zip_path = packager.create_deployment_package()
            package_info = packager.get_package_info()
            
            # Get file size for display
            import os
            file_size = os.path.getsize(zip_path) / 1024  # Size in KB
            
            deployment_message = f"""
📦 **Package de Déploiement Créé**

🎯 **Fichier:** `jokers_bot_deployment.zip`
📏 **Taille:** {file_size:.1f} KB
🐍 **Python:** {package_info['python_version']}
🤖 **Bot Version:** {package_info['telegram_bot_version']}
🚢 **Port:** {package_info['port']}

**📁 Fichiers inclus:**
{chr(10).join([f"• {file}" for file in package_info['files_included']])}

**🔧 Variables d'environnement requises:**
{chr(10).join([f"• {var}" for var in package_info['environment_variables']])}

**✨ Fonctionnalités:**
{chr(10).join([f"• {feature}" for feature in package_info['features']])}

**📋 Instructions de déploiement:**
1. Téléchargez le fichier ZIP ci-dessous
2. Créez un nouveau projet Python sur Replit
3. Extrayez tous les fichiers dans votre projet
4. Ajoutez BOT_TOKEN dans les Secrets Replit
5. Lancez avec `python main.py`

🎭 **Développé par Kouamé** - Version {package_info['version']}
            """

            # Send the deployment info message
            if chat:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=deployment_message
                )
                
                # Send the ZIP file as document
                with open(zip_path, 'rb') as zip_file:
                    await context.bot.send_document(
                        chat_id=chat.id,
                        document=zip_file,
                        filename="jokers_bot_deployment.zip",
                        caption="📦 Package de déploiement complet pour Replit\n🚀 Prêt à déployer sur le port 10000"
                    )
            
            # Clean up the temporary ZIP file
            os.remove(zip_path)
            logger.info(f"Deployment package sent successfully to user {user.id if user else 'unknown'}")

        except Exception as deploy_error:
            logger.error(f"Error creating deployment package: {deploy_error}")
            error_message = f"❌ Erreur lors de la création du package: {str(deploy_error)}"
            if update.message:
                await update.message.reply_text(error_message)

    except Exception as e:
        logger.error(f"Error in deploy_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")

    # Try to send error message to user if possible
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Une erreur inattendue s'est produite. L'équipe technique a été notifiée."
            )
        except Exception:
            pass  # If we can't send the error message, just log it