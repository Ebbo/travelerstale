import openai
import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_story(self, prompt: str, current_context: str = "", gm_role: str = "") -> Dict[str, str]:
        """Generate story content using OpenAI API"""
        
        # Build system prompt with custom GM role if provided
        base_prompt = """
        You are a skilled Game Master for a collaborative fantasy adventure game. Your role is to:
        
        1. Create engaging, immersive story content
        2. Respond to player actions with logical consequences
        3. Maintain narrative flow and consistency
        4. Create opportunities for all players to participate
        5. Balance challenge and fun
        6. Describe scenes vividly but concisely
        
        Guidelines:
        - Keep responses between 100-300 words
        - End with a clear situation requiring player decision/action
        - Maintain consistent tone and world-building
        - Include sensory details (sights, sounds, smells)
        - Create meaningful choices and consequences
        - Indicate if the scene is: adventure, combat, dialog, or exploration
        - NEVER include meta text like "Scene:", "Dialog:", "Decision:", or player names as labels
        - Focus on immersive storytelling without breaking the fourth wall
        
        Return your response as a story that advances the narrative based on the prompt.
        """
        
        if gm_role and gm_role.strip():
            role_prompt = f"""
            
        IMPORTANT: Adopt this specific Game Master personality and style:
        {gm_role.strip()}
        
        Embody this role consistently throughout the adventure. Let this personality shine through in your narration style, descriptions, and how you present challenges to the players.
        """
            system_prompt = base_prompt + role_prompt
        else:
            system_prompt = base_prompt
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {current_context}\n\nPrompt: {prompt}"}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            story_text = response.choices[0].message.content
            
            # Extract scene type for music selection
            scene_type = self._determine_scene_type(story_text)
            
            # Update context for future reference
            updated_context = self._update_context(current_context, story_text)
            
            return {
                "story": story_text,
                "scene_type": scene_type,
                "context": updated_context
            }
            
        except Exception as e:
            print(f"Error generating story: {e}")
            return {
                "story": "The tale continues as the adventurers face an unexpected turn of events...",
                "scene_type": "adventure",
                "context": current_context
            }
    
    def _determine_scene_type(self, story_text: str) -> str:
        """Determine the type of scene based on story content"""
        story_lower = story_text.lower()
        
        combat_keywords = ["attack", "fight", "battle", "combat", "weapon", "sword", "magic", "spell", "damage", "wound"]
        dialog_keywords = ["says", "speaks", "whispers", "shouts", "conversation", "talk", "voice"]
        exploration_keywords = ["explore", "search", "investigate", "examine", "discover", "path", "door", "room"]
        
        combat_score = sum(1 for word in combat_keywords if word in story_lower)
        dialog_score = sum(1 for word in dialog_keywords if word in story_lower)
        exploration_score = sum(1 for word in exploration_keywords if word in story_lower)
        
        if combat_score >= 2:
            return "combat"
        elif dialog_score >= 2:
            return "dialog"
        elif exploration_score >= 2:
            return "exploration"
        else:
            return "adventure"
    
    def _update_context(self, current_context: str, new_story: str) -> str:
        """Update the scene context with new story developments"""
        # Keep context concise by focusing on key elements
        context_lines = current_context.split('\n') if current_context else []
        
        # Add new story summary (keep last 3 story beats)
        new_summary = f"Recent: {new_story[:100]}..."
        context_lines.append(new_summary)
        
        # Keep only last 3 context entries to prevent context from growing too large
        if len(context_lines) > 3:
            context_lines = context_lines[-3:]
        
        return '\n'.join(context_lines)
    
    async def generate_character_response(self, character_name: str, situation: str, personality: str = "") -> str:
        """Generate dialog for NPCs"""
        try:
            prompt = f"""
            Generate a response for the character '{character_name}' in this situation: {situation}
            
            Character personality: {personality if personality else "Neutral, helpful"}
            
            Respond in character with 1-2 sentences of dialog.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating character response: {e}")
            return f"{character_name} looks at you thoughtfully but says nothing."