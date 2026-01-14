#!/usr/bin/env python3
"""
Skill Registry - Dynamic skill discovery and loading
Gold Tier: Agent Skills Framework
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional
import importlib.util
import sys

from base_skill import Skill


class SkillRegistry:
    """
    Central registry for discovering and loading skills

    Allows dynamic discovery of skills from:
    - skills/ directory (Python modules)
    - Skill plugins
    - Built-in skills
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize skill registry

        Args:
            skills_dir: Directory to search for skill modules
        """
        self.skills_dir = skills_dir or Path(__file__).parent / 'skills'
        self.skills: Dict[str, Skill] = {}
        self.logger = logging.getLogger('SkillRegistry')

        # Ensure skills directory exists
        self.skills_dir.mkdir(exist_ok=True)

        self.logger.info(f"Skill registry initialized: {self.skills_dir}")

    def discover_skills(self) -> int:
        """
        Discover all skills in skills directory

        Returns:
            int: Number of skills discovered
        """
        self.logger.info("Discovering skills...")

        skill_files = list(self.skills_dir.glob('*_skill.py'))

        self.logger.info(f"Found {len(skill_files)} skill modules")

        for skill_file in skill_files:
            try:
                self._load_skill_module(skill_file)
            except Exception as e:
                self.logger.error(f"Failed to load skill from {skill_file.name}: {e}")

        self.logger.info(f"Discovered {len(self.skills)} skills")

        return len(self.skills)

    def _load_skill_module(self, skill_file: Path):
        """Load a skill from a Python module"""
        module_name = skill_file.stem

        # Import module
        spec = importlib.util.spec_from_file_location(module_name, skill_file)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load spec from {skill_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find Skill subclasses in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a Skill subclass (but not Skill itself)
            if (isinstance(attr, type) and
                issubclass(attr, Skill) and
                attr is not Skill):

                # Instantiate skill
                try:
                    skill_instance = attr()
                    self.register_skill(skill_instance)
                    self.logger.info(f"Loaded skill: {skill_instance.name}")
                except Exception as e:
                    self.logger.error(f"Failed to instantiate {attr_name}: {e}")

    def register_skill(self, skill: Skill):
        """
        Register a skill instance

        Args:
            skill: Skill instance to register
        """
        if skill.name in self.skills:
            self.logger.warning(f"Skill '{skill.name}' already registered, overwriting")

        self.skills[skill.name] = skill
        self.logger.debug(f"Registered skill: {skill.name}")

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name

        Args:
            name: Skill name

        Returns:
            Skill instance or None if not found
        """
        return self.skills.get(name)

    def list_skills(self) -> List[Dict]:
        """
        List all registered skills

        Returns:
            list: Skill information dictionaries
        """
        return [skill.get_info() for skill in self.skills.values()]

    def execute_skill(self, name: str, context: Dict) -> Dict:
        """
        Execute a skill by name

        Args:
            name: Skill name
            context: Execution context

        Returns:
            dict: Execution result
        """
        skill = self.get_skill(name)

        if not skill:
            return {
                'success': False,
                'error': f"Skill '{name}' not found"
            }

        return skill.safe_execute(context)

    def __repr__(self) -> str:
        return f"<SkillRegistry: {len(self.skills)} skills>"


# Global registry instance
_global_registry = None


def get_registry() -> SkillRegistry:
    """
    Get the global skill registry

    Returns:
        SkillRegistry: Global registry instance
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = SkillRegistry()
        _global_registry.discover_skills()

    return _global_registry


# CLI Interface
if __name__ == '__main__':
    print("=" * 70)
    print("Agent Skills Registry")
    print("=" * 70)
    print()

    # Initialize registry
    registry = SkillRegistry()

    # Discover skills
    count = registry.discover_skills()

    print(f"Discovered {count} skill(s)")
    print()

    # List skills
    if count > 0:
        print("Available Skills:")
        print()

        for skill_info in registry.list_skills():
            print(f"📦 {skill_info['name']} v{skill_info['version']}")
            print(f"   {skill_info['description']}")
            print(f"   Required params: {', '.join(skill_info['required_params']) or 'none'}")
            if skill_info['optional_params']:
                print(f"   Optional params: {', '.join(skill_info['optional_params'])}")
            print()
    else:
        print("No skills found.")
        print()
        print("Create skills in the skills/ directory:")
        print("  skills/my_skill.py")
        print()
