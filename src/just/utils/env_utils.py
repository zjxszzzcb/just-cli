import json
import os
import warnings

from abc import ABC
from typing import Any, Literal, Union, get_type_hints, get_origin, get_args, List, Dict, NewType, Self


AbsolutePath = NewType("AbsolutePath", str)
LowerString = NewType("LowerString", str)
UpperString = NewType("UpperString", str)
URL = NewType("URL", str)


_type_validators = {
    str: str,
    int: int,
    float: float,
    bool: lambda x: (str(x).lower() in ("true", "1", "yes")),
    list: json.loads,
    dict: json.loads,

    List: json.loads,
    Dict: json.loads,
    
    LowerString: lambda x: str(x).lower(),
    UpperString: lambda x: str(x).upper(),
    AbsolutePath: lambda x: os.path.abspath(str(x)),
    URL: lambda x: str(x).rstrip('/'),
}


class EnvConfig(ABC):
    """
    Abstract base class for dynamic environment variable configuration.
    
    This class provides automatic environment variable reading and type conversion
    based on class attribute type annotations. When accessing any attribute,
    it first checks if an environment variable with the same name exists,
    and if so, converts it to the appropriate type based on the type hint.
    """
    
    def __init_subclass__(cls, **kwargs):
        """Initialize subclass and collect bound environment variable processors."""
        super().__init_subclass__(**kwargs)
        cls._cached_type_hints = None
    
    def __getattribute__(self, name: str) -> Any:
        """
        Override attribute access to dynamically read from environment variables.
        
        This method intercepts all attribute access and:
        1. Checks if it's a private/special attribute (starts with '_')
        2. Gets type hints from the class
        3. If the attribute has a type hint, tries to read from environment variable
        4. Converts the environment variable value to the appropriate type
        5. Falls back to the default class attribute value if env var is not set
        
        Args:
            name: The name of the attribute being accessed
            
        Returns:
            The value from environment variable (converted to proper type) or default value
        """
        # First check if it's a special method or private attribute
        # These should use normal attribute access to avoid infinite recursion
        if name.startswith('_'):
            return super().__getattribute__(name)

        # Get cached type hints to determine expected types for configuration attributes
        cls = super().__getattribute__("__class__")
        if cls._cached_type_hints is None:
            cls._cached_type_hints = get_type_hints(cls)
        
        type_hints = cls._cached_type_hints
        if name not in type_hints:
            return super().__getattribute__(name)

        # This is a configuration attribute with a type annotation
        # Try to get value from environment variable, fallback to class default
        try:
            default_value = super().__getattribute__(name)
        except AttributeError:
            default_value = None

        env_value = os.getenv(name, default_value)
        if not isinstance(env_value, str):
            return env_value

        target_type = type_hints[name]
        return self._convert_string_to_target_type(env_value, target_type)

    @staticmethod
    def _convert_string_to_target_type(string_value: str, target_type: type) -> Any:
        """
        Convert environment variable string to the target type based on type annotation.
        
        This method handles type conversion for various Python types commonly used
        in configuration. It supports:
        - Basic types: str, int, float, bool
        - Collections: list, tuple (expects JSON format)
        - Special types: Literal (validates against allowed values)
        - Generic types: Optional, Union (recursively processes type arguments)
        
        Args:
            string_value: The string value from environment variable or default
            target_type: The target type from type annotation
            
        Returns:
            The converted value in the appropriate type
        """
        if target_type in _type_validators:
            try:
                return _type_validators[target_type](string_value.strip())
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                raise ValueError(f"Failed to convert '{string_value}' to {target_type}: {e}") from e

        # Handle generic types (like Optional, Union, List[str], etc.)
        origin_type = get_origin(target_type)

        if origin_type is Literal:
            # For Literal types, validate that the value is one of the allowed literals
            available_literals = get_args(target_type)
            for literal_value in available_literals:
                try:
                    transformed_value = _type_validators[type(literal_value)](string_value)
                except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                    transformed_value = string_value

                if literal_value == transformed_value:
                    return literal_value

            raise ValueError(f"Invalid literal value: {string_value}, must be one of {available_literals}")

        if origin_type is Union:
            # Handle Union types by trying each type in order
            type_args = get_args(target_type)
            for arg_type in type_args:
                # Skip NoneType for Optional[T] handling
                if arg_type is type(None):
                    continue
                try:
                    return EnvConfig.convert_string_to_target_type(string_value, arg_type)
                except (ValueError, TypeError):
                    continue
            # If all conversions failed, raise error with all attempted types
            raise ValueError(f"Could not convert '{string_value}' to any of {type_args}")
        elif origin_type:
            # For other generic types (like List, Optional), recursively convert using origin type
            return EnvConfig.convert_string_to_target_type(string_value, origin_type)

        # Fallback for unsupported types - return as string with warning
        warnings.warn(f"Unsupported type: {target_type}, returning as string")
        return string_value

    @property
    def keys(self) -> Self:
        class EnvConfigKeys(self.__class__):
            def __getattribute__(self, item):
                if item.startswith('_'):
                    return super().__getattribute__(item)
                _ = super().__getattribute__(item)
                return item
        return EnvConfigKeys()
