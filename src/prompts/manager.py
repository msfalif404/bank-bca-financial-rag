from pathlib import Path

class PromptManager:
    """
    Manager class to handle prompt templates easily.
    Load prompts from the text files in the prompts directory.
    """
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # Set default directory to where this file is located
            self.prompts_dir = Path(__file__).parent / "templates"
        else:
            self.prompts_dir = Path(prompts_dir)
            
    def get_prompt(self, filename: str) -> str:
        """Reads and returns the content of a prompt text file."""
        prompt_path = self.prompts_dir / filename
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at: {prompt_path}")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
            
    @property
    def extraction_prompt(self) -> str:
        """Returns the main extraction prompt for the Vision model."""
        return self.get_prompt("extraction_prompt.txt")

    @property
    def audit_prompt(self) -> str:
        """Returns the prompt used for auditing GenAI extraction vs Actual data."""
        return self.get_prompt("audit_prompt.txt")

    @property
    def intent_classifier_prompt(self) -> str:
        """Returns the prompt for classifying user intent into graph routes."""
        return self.get_prompt("intent_classifier_prompt.txt")
        
    @property
    def data_search_prompt(self) -> str:
        """Returns the instruction prompt for the specialized data search agent."""
        return self.get_prompt("data_search_prompt.txt")
        
    @property
    def insights_prompt(self) -> str:
        """Returns the instruction prompt for the specialized financial insight agent."""
        return self.get_prompt("insights_prompt.txt")

# Create a singleton instance for direct import
prompt_manager = PromptManager()
