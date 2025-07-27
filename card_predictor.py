"""
Card prediction logic for Joker's Telegram Bot
Analyzes card combinations and makes predictions
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from config import VALID_CARD_COMBINATIONS, CARD_SYMBOLS, PREDICTION_MESSAGE

logger = logging.getLogger(__name__)

class CardPredictor:
    """Handles card prediction logic"""
    
    def __init__(self):
        self.predictions = {}  # Store predictions for verification
        self.processed_messages = set()  # Avoid duplicate processing
        self.sent_predictions = {}  # Store sent prediction messages for editing
        self.temporary_messages = {}  # Store temporary messages waiting for final edit
    
    def extract_game_number(self, message: str) -> Optional[int]:
        """Extract game number from message like #n744 or #N744"""
        pattern = r'#[nN](\d+)'
        match = re.search(pattern, message)
        if match:
            return int(match.group(1))
        return None
    
    def extract_cards_from_parentheses(self, message: str) -> List[str]:
        """Extract cards from first and second parentheses"""
        # Pattern to match content in parentheses
        pattern = r'\(([^)]+)\)'
        matches = re.findall(pattern, message)
        
        card_groups = []
        for match in matches[:2]:  # Only first two parentheses
            cards = self.extract_card_symbols(match)
            if cards:
                card_groups.extend(cards)
        
        return card_groups
    
    def extract_cards_from_first_parentheses(self, message: str) -> List[str]:
        """Extract cards only from first parentheses"""
        # Pattern to match content in parentheses
        pattern = r'\(([^)]+)\)'
        matches = re.findall(pattern, message)
        
        if matches:
            # Only process the first parentheses
            return self.extract_card_symbols(matches[0])
        
        return []
    
    def extract_card_symbols(self, text: str) -> List[str]:
        """Extract card symbols from text"""
        cards = []
        for symbol in CARD_SYMBOLS:
            # Count how many times this symbol appears
            count = text.count(symbol)
            # Add the symbol that many times
            cards.extend([symbol] * count)
        return cards
    
    def has_three_different_cards(self, cards: List[str]) -> bool:
        """Check if there are exactly 3 different card symbols"""
        unique_cards = list(set(cards))
        return len(unique_cards) == 3
    
    def is_temporary_message(self, message: str) -> bool:
        """Check if message contains temporary progress emojis"""
        temporary_emojis = ['⏰', '▶', '🕐', '➡️']
        return any(emoji in message for emoji in temporary_emojis)
    
    def is_final_message(self, message: str) -> bool:
        """Check if message contains final completion emojis"""
        final_emojis = ['✅', '🔰']
        return any(emoji in message for emoji in final_emojis)
    
    def get_card_combination(self, cards: List[str]) -> Optional[str]:
        """Get the combination of 3 different cards"""
        unique_cards = list(set(cards))
        if len(unique_cards) == 3:
            # Sort the cards for consistency
            combination = ''.join(sorted(unique_cards))
            logger.info(f"Card combination found: {combination} from cards: {unique_cards}")
            
            # Check if this combination matches any valid pattern
            for valid_combo in VALID_CARD_COMBINATIONS:
                if set(combination) == set(valid_combo):
                    logger.info(f"Valid combination matched: {valid_combo}")
                    return combination
            
            # If no exact match, but we have 3 different cards, it should be valid
            # All combinations of 3 different card symbols should be valid
            logger.info(f"No exact match found in VALID_CARD_COMBINATIONS, but accepting 3 different cards: {combination}")
            return combination
        return None
    
    def should_predict(self, message: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Determine if we should make a prediction based on message content
        Returns: (should_predict, game_number, card_combination)
        """
        # Extract game number
        game_number = self.extract_game_number(message)
        if not game_number:
            logger.debug(f"No game number found in message: {message[:50]}...")
            return False, None, None
        
        # Check if this is a temporary message (should wait for final edit)
        if self.is_temporary_message(message):
            logger.info(f"Game {game_number}: Temporary message detected, storing for later processing")
            self.temporary_messages[game_number] = message
            return False, None, None
        
        # Check if this is a final message for a previously temporary message
        if self.is_final_message(message) and game_number in self.temporary_messages:
            logger.info(f"Game {game_number}: Final message detected for previously temporary message")
            # Remove from temporary storage as it's now final
            del self.temporary_messages[game_number]
        
        # Extract cards from first and second parentheses separately
        pattern = r'\(([^)]+)\)'
        matches = re.findall(pattern, message)
        
        if len(matches) < 1:
            logger.debug(f"No parentheses found in message: {message[:50]}...")
            return False, None, None
        
        logger.info(f"Game {game_number}: Found {len(matches)} parentheses")
        
        # Check first parentheses
        if len(matches) >= 1:
            first_cards = self.extract_card_symbols(matches[0])
            logger.info(f"Game {game_number}: First parentheses '{matches[0]}' -> cards: {first_cards}")
            if self.has_three_different_cards(first_cards):
                combination = self.get_card_combination(first_cards)
                logger.info(f"Game {game_number}: Found 3 different cards in first parentheses: {combination}")
                if combination:
                    # Check if we already processed this message
                    message_hash = hash(message)
                    if message_hash not in self.processed_messages:
                        self.processed_messages.add(message_hash)
                        return True, game_number, combination
        
        # Check second parentheses
        if len(matches) >= 2:
            second_cards = self.extract_card_symbols(matches[1])
            logger.info(f"Game {game_number}: Second parentheses '{matches[1]}' -> cards: {second_cards}")
            if self.has_three_different_cards(second_cards):
                combination = self.get_card_combination(second_cards)
                logger.info(f"Game {game_number}: Found 3 different cards in second parentheses: {combination}")
                if combination:
                    # Check if we already processed this message
                    message_hash = hash(message)
                    if message_hash not in self.processed_messages:
                        self.processed_messages.add(message_hash)
                        return True, game_number, combination
        
        logger.debug(f"Game {game_number}: No valid prediction conditions met")
        return False, None, None
    
    def make_prediction(self, game_number: int, combination: str) -> str:
        """Make a prediction for the next game"""
        next_game = game_number + 1
        prediction_text = PREDICTION_MESSAGE.format(numero=next_game)
        
        # Store the prediction for later verification
        self.predictions[next_game] = {
            'combination': combination,
            'status': 'pending',
            'predicted_from': game_number,
            'verification_count': 0,
            'message_text': prediction_text
        }
        
        logger.info(f"Made prediction for game {next_game} based on combination {combination} from game {game_number}")
        return prediction_text
    
    def count_cards_in_first_parentheses(self, message: str) -> int:
        """Count the number of card symbols in first parentheses"""
        pattern = r'\(([^)]+)\)'
        matches = re.findall(pattern, message)
        
        if matches:
            # Count all card symbols in first parentheses
            first_content = matches[0]
            card_count = 0
            for symbol in CARD_SYMBOLS:
                card_count += first_content.count(symbol)
            return card_count
        
        return 0
    
    def has_any_three_cards_in_first_parentheses(self, message: str) -> bool:
        """Check if first parentheses contains any 3 cards (not necessarily different)"""
        return self.count_cards_in_first_parentheses(message) >= 3
    
    def verify_prediction(self, message: str) -> Optional[Dict]:
        """Verify if a prediction was correct"""
        game_number = self.extract_game_number(message)
        if not game_number:
            return None
        
        logger.info(f"Verifying prediction for message: {message[:100]}...")
        logger.info(f"Extracted game number: {game_number}")
        logger.info(f"Current predictions: {list(self.predictions.keys())}")
        
        # Check all pending predictions to see if this game matches any verification attempt
        for predicted_game, prediction in self.predictions.items():
            if prediction['status'] != 'pending':
                continue
                
            # Check if this game is within the verification range (predicted_game to predicted_game + 3)
            verification_offset = game_number - predicted_game
            logger.info(f"Checking prediction {predicted_game} vs game {game_number}, offset: {verification_offset}")
            
            if 0 <= verification_offset <= 3:
                # Check if message has success symbols (✅ or 🔰) which indicate completion
                has_success_symbol = '✅' in message or '🔰' in message
                card_count = self.count_cards_in_first_parentheses(message)
                logger.info(f"Game {game_number}: Found {card_count} cards in first parentheses, has success symbol (✅ or 🔰): {has_success_symbol}")
                logger.info(f"Verification offset: {verification_offset}, within range, checking success symbol...")
                
                if has_success_symbol and card_count >= 3:
                    # Found success symbol AND exactly 3 cards in first parentheses - update status based on offset
                    status_map = {0: '✅0️⃣', 1: '✅1️⃣', 2: '✅2️⃣', 3: '✅3️⃣'}
                    new_status = status_map[verification_offset]
                    
                    # Update the prediction message
                    updated_message = prediction['message_text'].replace('statut :⏳', f'statut :{new_status}')
                    
                    prediction['status'] = 'correct'
                    prediction['verification_count'] = verification_offset
                    prediction['final_message'] = updated_message
                    
                    logger.info(f"Prediction verified for game {predicted_game} at offset {verification_offset} - found ✅ symbol AND {card_count} cards in first parentheses")
                    return {
                        'type': 'update_message',
                        'predicted_game': predicted_game,
                        'new_message': updated_message,
                        'original_message': prediction['message_text']
                    }
                elif has_success_symbol and card_count < 3:
                    logger.info(f"Game {game_number}: Has success symbol but only {card_count} cards in first parentheses (need 3+) - verification not valid")
                    
                elif verification_offset == 3:
                    # Reached maximum verification attempts without success
                    updated_message = prediction['message_text'].replace('statut :⏳', 'statut :❌⭕')
                    
                    prediction['status'] = 'failed'
                    prediction['verification_count'] = 4
                    prediction['final_message'] = updated_message
                    
                    logger.info(f"Prediction failed for game {predicted_game} after 4 attempts")
                    return {
                        'type': 'update_message', 
                        'predicted_game': predicted_game,
                        'new_message': updated_message,
                        'original_message': prediction['message_text']
                    }
        
        return None
    
    def get_prediction_stats(self) -> Dict:
        """Get statistics about predictions"""
        total = len(self.predictions)
        correct = sum(1 for p in self.predictions.values() if p['status'] == 'correct')
        incorrect = sum(1 for p in self.predictions.values() if p['status'] == 'incorrect')
        failed = sum(1 for p in self.predictions.values() if p['status'] == 'failed')
        pending = sum(1 for p in self.predictions.values() if p['status'] == 'pending')
        
        return {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'failed': failed,
            'pending': pending,
            'accuracy': (correct / total * 100) if total > 0 else 0
        }

# Global instance
card_predictor = CardPredictor()