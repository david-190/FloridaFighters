import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

class SaveManager:
    SAVE_DIR = "saves"
    MAX_SAVE_SLOTS = 5  # Maximum number of save slots
    
    @classmethod
    def ensure_save_dir_exists(cls):
        """Create saves directory if it doesn't exist."""
        try:
            os.makedirs(cls.SAVE_DIR, exist_ok=True)
            print(f"Successfully created/verified save directory: {os.path.abspath(cls.SAVE_DIR)}")
            # Verify we can write to the directory
            test_file = os.path.join(cls.SAVE_DIR, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("Successfully verified write access to save directory")
        except Exception as e:
            print(f"Error creating/verifying save directory: {e}")
            # Try creating in a different location if needed
            cls.SAVE_DIR = os.path.join(os.path.expanduser('~'), 'aetherbound_saves')
            print(f"Trying alternative save location: {os.path.abspath(cls.SAVE_DIR)}")
            os.makedirs(cls.SAVE_DIR, exist_ok=True)
    
    @classmethod
    def get_save_path(cls, slot: int = 0) -> str:
        """Get the path to a save file for the given slot."""
        return os.path.join(cls.SAVE_DIR, f'save_{slot}.json')
        
    @classmethod
    def has_save(cls, slot: int = 0) -> bool:
        """Check if a save file exists for the given slot."""
        return os.path.exists(cls.get_save_path(slot))
    
    @classmethod
    def save_game(cls, game_state: Dict[str, Any], slot: int = 0) -> bool:
        """
        Save the game state to disk in the specified slot.
        Returns True if successful, False otherwise.
        """
        try:
            print(f"\n=== Starting save operation ===")
            print(f"Attempting to save to slot {slot}...")
            
            if slot < 0 or slot >= cls.MAX_SAVE_SLOTS:
                error_msg = f"Invalid save slot: {slot}"
                print(f"Error: {error_msg}")
                raise ValueError(error_msg)
            
            # Ensure save directory exists and is writable
            cls.ensure_save_dir_exists()
            
            # Add metadata
            game_state['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'version': 1,
                'slot': slot
            }
            
            save_path = cls.get_save_path(slot)
            abs_save_path = os.path.abspath(save_path)
            print(f"Saving to: {abs_save_path}")
            
            # Create a temporary file first
            temp_path = f"{save_path}.tmp"
            
            # Write to temporary file
            with open(temp_path, 'w') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            # Verify the temporary file was created
            if not os.path.exists(temp_path):
                print(f"Error: Failed to create temporary save file at {temp_path}")
                return False
                
            # If a save file already exists, back it up
            if os.path.exists(save_path):
                backup_path = f"{save_path}.bak"
                try:
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(save_path, backup_path)
                    print(f"Created backup of existing save at {backup_path}")
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
            
            # Rename temp file to final name
            os.rename(temp_path, save_path)
            
            # Final verification
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                print(f"Successfully saved {file_size} bytes to {abs_save_path}")
                print("=== Save completed successfully ===\n")
                return True
            else:
                print(f"Error: Save file not found after writing to {abs_save_path}")
                return False
                
        except json.JSONEncodeError as e:
            print(f"Error encoding game state to JSON: {e}")
            print(f"Problematic data: {game_state}")
            return False
            
        except Exception as e:
            import traceback
            print(f"Error saving game: {e}")
            print("Stack trace:")
            print(traceback.format_exc())
            print("=== Save failed ===\n")
            return False
    
    @classmethod
    def load_game(cls, slot: int = 0) -> Optional[Dict[str, Any]]:
        """
        Load game state from the specified save slot.
        Returns the game state dict if successful, None otherwise.
        """
        print(f"Attempting to load from slot {slot}...")  # Debug print
        save_path = cls.get_save_path(slot)
        print(f"Looking for save file at: {os.path.abspath(save_path)}")  # Debug print
        
        if not os.path.exists(save_path):
            print(f"No save file found at {save_path}")  # Debug print
            return None
            
        try:
            with open(save_path, 'r') as f:
                print(f"Successfully loaded save from {save_path}")  # Debug print
                return json.load(f)
        except Exception as e:
            import traceback
            print(f"Error loading game: {e}")
            print(traceback.format_exc())  # Print full traceback
            return None
    
    @classmethod
    def delete_save(cls, slot: int = 0) -> bool:
        """Delete the save file for the specified slot."""
        try:
            if cls.has_save(slot):
                os.remove(cls.get_save_path(slot))
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
            
    @classmethod
    def get_save_info(cls, slot: int) -> Optional[Dict[str, Any]]:
        """Get metadata about a save file without loading the entire save."""
        if not cls.has_save(slot):
            return None
            
        try:
            save_path = cls.get_save_path(slot)
            with open(save_path, 'r') as f:
                data = json.load(f)
                return {
                    'slot': slot,
                    'timestamp': data.get('metadata', {}).get('timestamp'),
                    'version': data.get('metadata', {}).get('version', 1),
                    'player_health': data.get('player_state', {}).get('health', 0),
                    'player_level': 1
                }
        except Exception as e:
            print(f"Error reading save info: {e}")
            return None
            
    @classmethod
    def list_saves(cls) -> List[Dict[str, Any]]:
        """Get information about all existing save files."""
        saves = []
        for slot in range(cls.MAX_SAVE_SLOTS):
            save_info = cls.get_save_info(slot)
            if save_info:
                saves.append(save_info)
        return saves