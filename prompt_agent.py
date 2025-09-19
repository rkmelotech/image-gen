#!/usr/bin/env python3
"""
Prompt Generation Agent
Automatically generates detailed prompts for character scenes and updates test.py
"""

import re
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from itertools import combinations

class PromptAgent:
    def __init__(self):
        # Character themes and properties
        self.character_themes = {
            "Ballerina Cappuccina": {
                "colors": ["pink", "rose gold", "white"],
                "props": ["tutu", "ballet shoes", "tiara", "ribbons"],
                "style": "elegant and graceful",
                "personality": "graceful"
            },
            "Stick": {
                "colors": ["brown", "wooden", "natural"],
                "props": ["leaves", "twigs", "forest items"],
                "style": "simple and natural",
                "personality": "down-to-earth"
            },
            "Tralalelo Tralala": {
                "colors": ["aqua-blue", "light blue", "grey"],
                "props": ["sharks", "ocean items", "slime bucket"],
                "style": "playful and oceanic",
                "personality": "playful"
            },
            "Cappuccino Assassino": {
                "colors": ["coffee brown", "cream", "dark espresso"],
                "props": ["coffee cups", "steam", "cafe items"],
                "style": "mysterious and caffeinated",
                "personality": "mysterious"
            },
            "Brr Brr Patapim": {
                "colors": ["icy blue", "white", "frost"],
                "props": ["snowflakes", "ice crystals", "winter items"],
                "style": "cool and refreshing",
                "personality": "cool"
            },
            "Alligator": {
                "colors": ["green", "swamp green", "muddy brown"],
                "props": ["water plants", "logs", "swamp items"],
                "style": "wild and reptilian",
                "personality": "wild"
            },
            "Elephant": {
                "colors": ["grey", "dusty brown", "earthy"],
                "props": ["peanuts", "trees", "safari items"],
                "style": "gentle and majestic",
                "personality": "gentle"
            },
            "Hippo": {
                "colors": ["purple", "lavender", "soft grey"],
                "props": ["water lilies", "mud", "river items"],
                "style": "chunky and lovable",
                "personality": "lovable"
            },
            "Orca": {
                "colors": ["black", "white", "icy-white"],
                "props": ["waves", "ocean items", "fish"],
                "style": "majestic and marine",
                "personality": "majestic"
            },
            "Pigeon": {
                "colors": ["soft-grey", "white", "blue-grey"],
                "props": ["feathers", "city items", "breadcrumbs"],
                "style": "urban and nimble",
                "personality": "nimble"
            },
            "Espressina": {
                "colors": ["dark brown", "coffee", "cream"],
                "props": ["espresso cups", "steam", "coffee beans"],
                "style": "energetic and caffeinated",
                "personality": "energetic"
            },
            "Chimpanzini": {
                "colors": ["brown", "tan", "jungle green"],
                "props": ["bananas", "vines", "jungle items"],
                "style": "playful and mischievous",
                "personality": "mischievous"
            },
            "Gusini": {
                "colors": ["white", "orange", "pond blue"],
                "props": ["water drops", "pond items", "feathers"],
                "style": "graceful and aquatic",
                "personality": "graceful"
            },
            "Teepot": {
                "colors": ["ceramic white", "steam blue", "warm brown"],
                "props": ["tea cups", "steam", "tea leaves"],
                "style": "warm and cozy",
                "personality": "cozy"
            },
            "Tung": {
                "colors": ["bright yellow", "energetic orange", "sunny"],
                "props": ["musical notes", "rhythm items", "sound waves"],
                "style": "rhythmic and energetic",
                "personality": "rhythmic"
            },
            "Fish": {
                "colors": ["ocean blue", "scale silver", "coral"],
                "props": ["bubbles", "seaweed", "coral items"],
                "style": "fluid and aquatic",
                "personality": "fluid"
            },
            "Hamster": {
                "colors": ["golden brown", "fluffy white", "cozy beige"],
                "props": ["nuts", "wheel", "cozy bedding"],
                "style": "cute and energetic",
                "personality": "energetic"
            },
            "Orange": {
                "colors": ["bright orange", "citrus yellow", "sunny"],
                "props": ["citrus slices", "sunshine", "fresh items"],
                "style": "bright and refreshing",
                "personality": "cheerful"
            }
        }

        # Location templates - simple, no descriptive words
        self.location_templates = {
            "bedroom": "bedroom",
            "kitchen": "kitchen",
            "park": "park",
            "forest": "forest",
            "city": "city",
            "beach": "beach",
            "classroom": "classroom",
            "garden": "garden",
            "ocean": "ocean",
            "pool": "pool",
            "mountain": "snowy mountain landscape"
        }

        # Action templates - simple, no adverbs
        self.action_templates = {
            "sleeping": "sleeping",
            "playing": "playing",
            "eating": "eating",
            "walking": "walking",
            "dancing": "dancing",
            "reading": "reading",
            "painting": "painting",
            "singing": "singing",
            "swimming": "swimming",
            "flying": "flying",
            "running": "running",
            "jumping": "jumping",
            "standing": "standing"
        }

    def parse_input(self, input_str: str) -> Dict[str, Any]:
        """Parse input format: count|characters|actions|locations"""
        parts = [p.strip() for p in input_str.split('|')]
        if len(parts) != 4:
            raise ValueError("Format: count|characters|actions|locations")

        count = int(parts[0])
        characters_str = parts[1]
        actions_str = parts[2]
        locations_str = parts[3]

        # Parse character distribution
        char_config = self._parse_characters(characters_str)

        # Parse actions
        actions = [a.strip() for a in actions_str.split(',')]
        if actions == ['RANDOM']:
            actions = list(self.action_templates.keys())

        # Parse locations
        locations = [l.strip() for l in locations_str.split(',')]
        if locations == ['RANDOM']:
            locations = list(self.location_templates.keys())

        return {
            'count': count,
            'char_config': char_config,
            'actions': actions,
            'locations': locations
        }

    def _parse_characters(self, characters_str: str) -> Dict[str, Any]:
        """Parse character distribution syntax"""
        # Check for character count specification [2] or [1-3]
        count_match = re.match(r'\[(\d+)(?:-(\d+))?\](.+)', characters_str)
        if count_match:
            min_chars = int(count_match.group(1))
            max_chars = int(count_match.group(2)) if count_match.group(2) else min_chars
            chars_part = count_match.group(3)
            distribution = 'count_specified'
        else:
            min_chars = max_chars = None
            chars_part = characters_str
            distribution = 'auto'

        # Check if characters should be together (+) or separate (,)
        if '+' in chars_part:
            characters = [c.strip() for c in chars_part.split('+')]
            mode = 'together'
        else:
            characters = [c.strip() for c in chars_part.split(',')]
            mode = 'separate'

        # Handle ALL keyword
        if characters == ['ALL']:
            characters = list(self.character_themes.keys())

        return {
            'characters': characters,
            'mode': mode,
            'distribution': distribution,
            'min_chars': min_chars,
            'max_chars': max_chars
        }

    def generate_character_combinations(self, char_config: Dict[str, Any], count: int) -> List[List[str]]:
        """Generate character combinations based on configuration"""
        characters = char_config['characters']
        mode = char_config['mode']
        distribution = char_config['distribution']
        min_chars = char_config['min_chars']
        max_chars = char_config['max_chars']

        combinations_list = []

        if mode == 'together':
            # All characters together in each scene
            for _ in range(count):
                combinations_list.append(characters[:])

        elif mode == 'separate':
            if distribution == 'count_specified':
                # Generate combinations with specified character count
                available_chars = characters[:]
                for _ in range(count):
                    if min_chars == max_chars:
                        char_count = min_chars
                    else:
                        char_count = random.randint(min_chars, max_chars)

                    if len(available_chars) < char_count:
                        available_chars = characters[:]  # Reset if we run out

                    selected = random.sample(available_chars, min(char_count, len(available_chars)))
                    combinations_list.append(selected)

                    # Remove selected characters to avoid immediate repetition
                    for char in selected:
                        if char in available_chars:
                            available_chars.remove(char)
            else:
                # One character per scene, cycle through if needed
                for i in range(count):
                    char_index = i % len(characters)
                    combinations_list.append([characters[char_index]])

        return combinations_list

    def generate_prompt(self, characters: List[str], action: str, location: str) -> str:
        """Generate detailed prompt for given characters, action, and location"""
        if len(characters) == 1:
            return self._generate_single_character_prompt(characters[0], action, location)
        else:
            return self._generate_multi_character_prompt(characters, action, location)

    def _generate_single_character_prompt(self, character: str, action: str, location: str) -> str:
        """Generate prompt for single character"""
        if character not in self.character_themes:
            return f"{character} {action} in {location}"

        action_desc = self.action_templates.get(action, action)
        location_desc = self.location_templates.get(location, location)

        # Simple, direct prompt
        prompt = f"{character} {action_desc} in {location_desc}"
        return prompt

    def _generate_multi_character_prompt(self, characters: List[str], action: str, location: str) -> str:
        """Generate prompt for multiple characters"""
        if not all(char in self.character_themes for char in characters):
            char_list = " and ".join(characters)
            return f"{char_list} {action} in {location}"

        # Create character list for prompt
        if len(characters) == 2:
            char_phrase = f"{characters[0]} and {characters[1]}"
        else:
            char_phrase = ", ".join(characters[:-1]) + f", and {characters[-1]}"

        action_desc = self.action_templates.get(action, action)
        location_desc = self.location_templates.get(location, location)

        # Simple, direct prompt
        prompt = f"{char_phrase} {action_desc} in {location_desc}"
        return prompt

    def generate_prompts_from_input(self, input_str: str) -> List[str]:
        """Generate all prompts from input string"""
        try:
            config = self.parse_input(input_str)

            # Generate character combinations
            char_combinations = self.generate_character_combinations(
                config['char_config'],
                config['count']
            )

            prompts = []
            actions = config['actions']
            locations = config['locations']

            for i, characters in enumerate(char_combinations):
                # Select action and location
                action = actions[i % len(actions)]
                location = locations[i % len(locations)]

                # Generate prompt
                prompt = self.generate_prompt(characters, action, location)
                prompts.append(prompt)

            return prompts

        except Exception as e:
            print(f"❌ Error parsing input: {e}")
            return []

    def update_test_py(self, prompts: List[str], test_file_path: str = "/Users/rabankolster/Desktop/genai_work/test.py") -> bool:
        """Update the JOINT_PROMPTS in test.py with generated prompts"""
        test_path = Path(test_file_path)

        if not test_path.exists():
            print(f"❌ {test_file_path} not found")
            return False

        try:
            # Read current content
            content = test_path.read_text()

            # Create new prompts section
            prompts_str = '[\n'
            for i, prompt in enumerate(prompts):
                # Escape quotes in prompt
                escaped_prompt = prompt.replace('"', '\\"')
                prompts_str += f'    "{escaped_prompt}"'
                if i < len(prompts) - 1:
                    prompts_str += ','
                prompts_str += '\n'
            prompts_str += '    ]'

            # Replace JOINT_PROMPTS section
            pattern = r'JOINT_PROMPTS = \[.*?\]'
            replacement = f'JOINT_PROMPTS = {prompts_str}'

            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

            # Write back to file
            test_path.write_text(new_content)
            print(f"✅ Updated {test_file_path} with {len(prompts)} prompts")
            return True

        except Exception as e:
            print(f"❌ Error updating file: {e}")
            return False

def main():
    """Interactive prompt generation"""
    agent = PromptAgent()

    print("🤖 Prompt Generation Agent")
    print("Format: count|characters|actions|locations")
    print("\nExamples:")
    print("  5|Orange,Pigeon,Orca|swimming|beach")
    print("  3|Orange+Pigeon|playing,eating|park")
    print("  2|[2]Orange,Pigeon,Orca,Hamster|RANDOM|bedroom,kitchen")
    print("  1|ALL|dancing|garden")
    print("\nEnter 'quit' to exit\n")

    while True:
        user_input = input("Enter prompt specs: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            break

        if not user_input:
            continue

        try:
            prompts = agent.generate_prompts_from_input(user_input)

            if not prompts:
                print("❌ No valid prompts generated")
                continue

            print(f"\n📝 Generated {len(prompts)} prompts:")
            for i, prompt in enumerate(prompts, 1):
                print(f"{i}. {prompt[:100]}...")

            update = input("\nUpdate test.py? (y/n): ").strip().lower()
            if update == 'y':
                agent.update_test_py(prompts)

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()