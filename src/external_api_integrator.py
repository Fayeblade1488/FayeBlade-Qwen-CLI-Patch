#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External API Integrator Module for Qwen CLI
This module handles integration with external API providers like Venice.ai
based on configurations from Raycast or other external sources.
"""

import argparse
import json
import os
import sys
import types
from typing import Any, Dict, List, Optional

import requests

# Try to import yaml, with a fallback if not available
yaml: Optional[types.ModuleType]
try:
    import yaml
except ImportError:
    print(
        "Warning: PyYAML is not installed. Install it with 'pip install PyYAML' to use external API providers functionality.",
        file=sys.stderr,
    )
    yaml = None


class ExternalAPIIntegrator:
    """Integrates with external AI providers using configuration files.

    This class loads provider details, such as API endpoints and models, from
    a YAML configuration file (e.g., from Raycast). It provides methods to
    list available providers and models, and to perform chat completions
    using a specified provider.

    Attributes:
        providers_config_path (Optional[str]): The path to the provider
            configuration YAML file.
        providers (Dict[str, Any]): A dictionary holding the configuration
            for all loaded providers, keyed by provider ID.
    """

    def __init__(self, providers_config_path: Optional[str] = None):
        """Initializes the ExternalAPIIntegrator.

        Args:
            providers_config_path: An optional path to the providers'
                configuration file. If not provided, it will search in the
                default Raycast config locations.
        """
        self.providers_config_path = (
            providers_config_path or self._find_raycast_providers_config()
        )
        self.providers: Dict[str, Any] = {}
        if self.providers_config_path:
            self.load_providers_from_config()

    def _find_raycast_providers_config(self) -> Optional[str]:
        """Finds the Raycast providers configuration file in common locations.

        Returns:
            The path to the configuration file if found, otherwise None.
        """
        possible_paths = [
            os.path.expanduser("~/.config/raycast/ai/providers.yaml"),
            os.path.expanduser("~/.config/raycast/ai/providers.yml"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def load_providers_from_config(self) -> bool:
        """Loads provider configurations from the YAML file.

        Parses the YAML file specified in `providers_config_path` and populates
        the `providers` dictionary.

        Returns:
            True if providers were loaded successfully, False otherwise.
        """
        if not self.providers_config_path or not os.path.exists(
            self.providers_config_path
        ):
            return False

        if yaml is None:
            return False

        try:
            with open(self.providers_config_path, "r") as f:
                config_data = yaml.safe_load(f)

            if config_data and "providers" in config_data:
                # Convert list of providers to dict keyed by provider ID
                if isinstance(config_data["providers"], list):
                    for provider in config_data["providers"]:
                        provider_id = provider.get("id")
                        if provider_id:
                            self.providers[provider_id] = provider
                elif isinstance(config_data["providers"], dict):
                    self.providers = config_data["providers"]
                return True
        except Exception as e:
            print(f"Error loading providers config: {e}", file=sys.stderr)

        return False

    def get_available_providers(self) -> List[str]:
        """Returns a list of available provider IDs.

        Returns:
            A list of provider ID strings.
        """
        return list(self.providers.keys())

    def get_provider_info(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Gets detailed information about a specific provider.

        Args:
            provider_id: The ID of the provider to retrieve information for.

        Returns:
            A dictionary containing provider information, or None if the
            provider is not found.
        """
        return self.providers.get(provider_id)

    def get_provider_models(self, provider_id: str) -> List[Dict[str, Any]]:
        """Gets available models for a specific provider.

        Args:
            provider_id: The ID of the provider to retrieve models for.

        Returns:
            A list of model dictionaries, or an empty list if the provider
            is not found or has no models.
        """
        provider_info = self.get_provider_info(provider_id)
        if provider_info and "models" in provider_info:
            return provider_info["models"]
        return []

    def get_default_provider_api_key(self, provider_id: str) -> Optional[str]:
        """Gets the API key for a provider, with environment variable fallback.

        Args:
            provider_id: The ID of the provider.

        Returns:
            The API key string if found, otherwise None.
        """
        provider_info = self.get_provider_info(provider_id)
        if not provider_info:
            return None

        # Try to get from provider config first
        api_key = provider_info.get("api_key")
        if api_key:
            return api_key

        # Fallback to environment variable
        env_var = provider_info.get("env_var")
        if env_var:
            return os.getenv(env_var)

        return None

    def chat_completion(
        self,
        provider_id: str,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Performs a chat completion using the specified provider and model.

        Args:
            provider_id: The ID of the provider to use.
            model_id: The ID of the model to use.
            messages: A list of message dictionaries with 'role' and 'content' keys.
            temperature: The temperature parameter for generation (default: 0.7).
            max_tokens: The maximum number of tokens to generate (optional).

        Returns:
            A dictionary containing the completion result.

        Raises:
            ValueError: If the provider or model is not found, or if no API key is available.
            requests.RequestException: If the API request fails.
        """
        provider_info = self.get_provider_info(provider_id)
        if not provider_info:
            raise ValueError(f"Provider '{provider_id}' not found")

        # Find the model
        models = self.get_provider_models(provider_id)
        model_info = None
        for model in models:
            if model.get("id") == model_id:
                model_info = model
                break

        if not model_info:
            raise ValueError(
                f"Model '{model_id}' not found for provider '{provider_id}'"
            )

        # Get API key
        api_key = self.get_default_provider_api_key(provider_id)
        if not api_key:
            raise ValueError(f"No API key found for provider '{provider_id}'")

        # Get API endpoint
        api_endpoint = provider_info.get("endpoint")
        if not api_endpoint:
            raise ValueError(f"No API endpoint configured for provider '{provider_id}'")

        # Prepare headers with provider-specific auth format support
        headers = {"Content-Type": "application/json"}

        # Support provider-specific Authorization header formats
        auth_header_format = provider_info.get("auth_header_format", "Bearer {api_key}")
        if auth_header_format:
            headers["Authorization"] = auth_header_format.format(api_key=api_key)
        else:
            headers["Authorization"] = f"Bearer {api_key}"

        # Prepare payload
        payload = {"model": model_id, "messages": messages, "temperature": temperature}

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                api_endpoint, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Re-raise with additional context while preserving the original exception
            raise ValueError(
                f"API request failed for provider '{provider_id}': {str(e)}"
            ) from e

    def list_all_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lists all models from all loaded providers.

        Returns:
            A dictionary mapping provider IDs to their respective model lists.
        """
        all_models = {}
        for provider_id in self.get_available_providers():
            models = self.get_provider_models(provider_id)
            all_models[provider_id] = models
        return all_models


def normalize_key(key: str) -> str:
    """Normalize a key for sensitive comparison: lowercase, remove underscores and hyphens.

    Args:
        key: The key string to normalize.

    Returns:
        The normalized key string.
    """
    return key.lower().replace("_", "").replace("-", "")


def redact_sensitive(data):
    """
    Recursively redact sensitive information from a (possibly nested) dict or list.

    This function traverses dictionaries and lists, identifying keys that contain
    sensitive information (such as API keys, passwords, tokens) and replacing their
    values with '***REDACTED***' to prevent accidental logging of secrets.

    Args:
        data: The data structure to redact. Can be a dict, list, or any other type.

    Returns:
        A new data structure with sensitive values redacted. Non-dict/list types
        are returned unchanged.

    Examples:
        >>> redact_sensitive({"api_key": "secret123", "name": "test"})
        {"api_key": "***REDACTED***", "name": "test"}
        >>> redact_sensitive({"Api-Key": "secret123"})
        {"Api-Key": "***REDACTED***"}
    """
    SENSITIVE_KEYS = {
        "api_key",
        "api_keys",
        "password",
        "secret",
        "token",
        "access_token",
    }
    NORMALIZED_SENSITIVE_KEYS = {normalize_key(k) for k in SENSITIVE_KEYS}

    if isinstance(data, dict):
        return {
            k: (
                "***REDACTED***"
                if normalize_key(k) in NORMALIZED_SENSITIVE_KEYS
                else redact_sensitive(v)
            )
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive(item) for item in data]
    else:
        return data


def main() -> int:
    """Main function for command-line usage.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    if yaml is None:
        print(
            "Error: PyYAML is required for this functionality. Please install it with 'pip install PyYAML'",
            file=sys.stderr,
        )
        return 1

    parser = argparse.ArgumentParser(description="External API Integrator for Qwen CLI")
    parser.add_argument(
        "--config-path", type=str, help="Path to providers configuration file"
    )
    parser.add_argument(
        "--list-providers", action="store_true", help="List available providers"
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List models for all providers"
    )
    parser.add_argument(
        "--provider", type=str, help="Provider ID to use for operations"
    )
    parser.add_argument("--model", type=str, help="Model ID to use for operations")
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for generation"
    )
    parser.add_argument(
        "--message", type=str, help="Single message to send to the model"
    )

    args = parser.parse_args()

    # Initialize the integrator
    integrator = ExternalAPIIntegrator(providers_config_path=args.config_path)

    if args.list_providers:
        providers = integrator.get_available_providers()
        print("Available providers:")
        for provider in providers:
            print(f"  - {provider}")

    elif args.list_models:
        all_models = integrator.list_all_models()
        for provider_id, models in all_models.items():
            print(f"\nModels for provider '{provider_id}':")
            for model in models:
                print(
                    f"  - {model.get('id', 'unknown')} ({model.get('name', 'unnamed')})"
                )

    elif args.provider and args.message:
        if not args.model:
            print(
                "Error: --model is required when using --provider and --message",
                file=sys.stderr,
            )
            return 1

        try:
            # Format the message as a chat message
            messages = [{"role": "user", "content": args.message}]

            # Call the chat completion
            result = integrator.chat_completion(
                provider_id=args.provider,
                model_id=args.model,
                messages=messages,
                temperature=args.temperature,
            )

            print(json.dumps(redact_sensitive(result), indent=2))
        except (ValueError, requests.RequestException) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
