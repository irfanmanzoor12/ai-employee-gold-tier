#!/usr/bin/env python3
"""
Base Skill Class - Agent Skills Framework
Gold Tier Requirement: All AI functionality as Agent Skills

A Skill is a reusable, composable unit of AI functionality.
Skills can be discovered, loaded, and executed dynamically.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class Skill(ABC):
    """
    Abstract base class for all Agent Skills

    Skills encapsulate AI functionality in a standardized way that allows:
    - Dynamic discovery and loading
    - Composition into workflows
    - Consistent error handling
    - Audit logging
    """

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        """
        Initialize a skill

        Args:
            name: Unique skill identifier (e.g., "reasoning", "drafting")
            description: Human-readable description of what the skill does
            version: Semantic version of the skill
        """
        self.name = name
        self.description = description
        self.version = version
        self.logger = logging.getLogger(f"Skill.{name}")

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill with given context

        Args:
            context: Input data and configuration for skill execution
                Common keys:
                - vault_path: Path to AI Employee Vault
                - input_file: Path to input file (if applicable)
                - params: Skill-specific parameters

        Returns:
            dict: Result with standardized structure:
                {
                    'success': bool,
                    'output': Any (skill-specific output),
                    'error': str (if success=False),
                    'metadata': dict (execution metadata)
                }
        """
        pass

    @abstractmethod
    def get_required_params(self) -> List[str]:
        """
        Return list of required parameters for this skill

        Returns:
            list: Parameter names required in context
        """
        pass

    def get_optional_params(self) -> List[str]:
        """
        Return list of optional parameters for this skill

        Returns:
            list: Parameter names that are optional in context
        """
        return []

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate that context contains all required parameters

        Args:
            context: Context to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required = self.get_required_params()
        missing = [p for p in required if p not in context]

        if missing:
            self.logger.error(f"Missing required parameters: {missing}")
            return False

        return True

    def log_execution(self, context: Dict[str, Any], result: Dict[str, Any],
                     execution_time: float):
        """
        Log skill execution for audit trail

        Args:
            context: Input context
            result: Execution result
            execution_time: Time taken in seconds
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'skill': self.name,
            'version': self.version,
            'success': result.get('success', False),
            'execution_time': execution_time,
            'context_keys': list(context.keys()),
            'error': result.get('error')
        }

        if result.get('success'):
            self.logger.info(f"Skill '{self.name}' executed successfully in {execution_time:.2f}s")
        else:
            self.logger.error(f"Skill '{self.name}' failed: {result.get('error')}")

        # Write to audit log
        vault_path = context.get('vault_path')
        if vault_path:
            vault = Path(vault_path)
            log_file = vault / 'Logs' / 'skills_execution.jsonl'
            log_file.parent.mkdir(exist_ok=True)

            import json
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

    def safe_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill with error handling and logging

        This is the main entry point for skill execution.
        It wraps execute() with validation, error handling, and logging.

        Args:
            context: Input context

        Returns:
            dict: Execution result
        """
        import time

        self.logger.info(f"Executing skill: {self.name}")

        # Validate context
        if not self.validate_context(context):
            return {
                'success': False,
                'error': 'Invalid context - missing required parameters',
                'metadata': {'skill': self.name}
            }

        # Execute with timing
        start_time = time.time()

        try:
            result = self.execute(context)
            execution_time = time.time() - start_time

            # Ensure result has required fields
            if 'success' not in result:
                result['success'] = False
                result['error'] = 'Skill did not return success status'

            # Add metadata
            if 'metadata' not in result:
                result['metadata'] = {}

            result['metadata'].update({
                'skill': self.name,
                'version': self.version,
                'execution_time': execution_time
            })

            # Log execution
            self.log_execution(context, result, execution_time)

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            self.logger.exception(f"Skill '{self.name}' raised exception: {e}")

            result = {
                'success': False,
                'error': str(e),
                'metadata': {
                    'skill': self.name,
                    'version': self.version,
                    'execution_time': execution_time,
                    'exception_type': type(e).__name__
                }
            }

            self.log_execution(context, result, execution_time)

            return result

    def get_info(self) -> Dict[str, Any]:
        """
        Get skill information for discovery

        Returns:
            dict: Skill metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'required_params': self.get_required_params(),
            'optional_params': self.get_optional_params()
        }

    def __repr__(self) -> str:
        return f"<Skill: {self.name} v{self.version}>"


class SkillComposer:
    """
    Composes multiple skills into a workflow

    Allows chaining skills where output of one becomes input of next
    """

    def __init__(self, skills: List[Skill]):
        """
        Initialize composer with list of skills

        Args:
            skills: Skills to compose in execution order
        """
        self.skills = skills
        self.logger = logging.getLogger('SkillComposer')

    def execute(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all skills in sequence

        Args:
            initial_context: Starting context for first skill

        Returns:
            dict: Combined results from all skills
        """
        self.logger.info(f"Composing {len(self.skills)} skills")

        context = initial_context.copy()
        results = []

        for i, skill in enumerate(self.skills):
            self.logger.info(f"Executing skill {i+1}/{len(self.skills)}: {skill.name}")

            result = skill.safe_execute(context)
            results.append({
                'skill': skill.name,
                'result': result
            })

            if not result.get('success'):
                self.logger.error(f"Skill {skill.name} failed, stopping composition")
                return {
                    'success': False,
                    'error': f"Skill '{skill.name}' failed",
                    'completed_skills': i,
                    'total_skills': len(self.skills),
                    'results': results
                }

            # Pass output to next skill's context
            if 'output' in result:
                context[f'{skill.name}_output'] = result['output']

        return {
            'success': True,
            'completed_skills': len(self.skills),
            'total_skills': len(self.skills),
            'results': results
        }


# Decorator for easy skill creation
def skill(name: str, description: str, version: str = "1.0.0"):
    """
    Decorator to convert a function into a Skill

    Example:
        @skill("example", "Example skill")
        def my_skill(context):
            return {'success': True, 'output': 'done'}
    """
    def decorator(func):
        class FunctionSkill(Skill):
            def __init__(self):
                super().__init__(name, description, version)
                self.func = func

            def execute(self, context):
                return self.func(context)

            def get_required_params(self):
                # Extract from function signature if possible
                return []

        return FunctionSkill()

    return decorator
