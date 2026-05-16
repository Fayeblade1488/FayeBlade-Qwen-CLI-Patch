#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen Code Integration Module
This module combines GitKraken CLI and Venice AI image generation capabilities
for use within the Qwen Code environment.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

# Import our integration modules
from gitkraken_integration import GitKrakenCLI
from venice_integration import VeniceAIImageGenerator, VeniceAIVerifier, VeniceAIConfigUpdater
from external_api_integrator import ExternalAPIIntegrator


class QwenCLIIntegrator:
    """Orchestrates integrations with GitKraken, Venice AI, and other external APIs.

    This class serves as the main hub for the command-line tool. It initializes
    the necessary integration clients and provides methods to delegate commands
    to the appropriate module, whether it's for version control, AI image
    generation, or chat functionalities.

    Attributes:
        gitkraken (GitKrakenCLI): An instance of the GitKraken CLI wrapper.
        venice_api_key (Optional[str]): The API key for Venice AI, loaded
            from the environment.
        venice (Optional[VeniceAIImageGenerator]): An instance of the Venice AI
            image generator, initialized if an API key is available.
    """

    def __init__(self):
        """Initializes the QwenCLIIntegrator."""
        self.gitkraken = GitKrakenCLI()
        self.venice_api_key = os.environ.get("VENICE_API_KEY")
        self.venice = None
        
        # Initialize Venice if API key is available
        if self.venice_api_key:
            try:
                self.venice = VeniceAIImageGenerator(api_key=self.venice_api_key)
            except ValueError as e:
                print(f"Warning: Venice AI not initialized: {e}", file=sys.stderr)
    
    def gitkraken_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Executes a GitKraken CLI command.

        This method acts as a dispatcher, mapping a command string to the
        corresponding method in the `GitKrakenCLI` instance.

        Args:
            command: The name of the GitKraken command to execute (e.g.,
                'ai_commit', 'workspace_list').
            **kwargs: Keyword arguments to pass to the corresponding
                `GitKrakenCLI` method.

        Returns:
            A dictionary containing the result of the command execution.
            This typically includes 'success', 'stdout', and 'stderr'.
        """
        if not self.gitkraken.is_installed():
            return {
                'success': False,
                'error': 'GitKraken CLI (gk) is not installed or not in PATH'
            }
        
        # Map command to the appropriate method
        method_map = {
            # AI commands
            'ai_changelog': self.gitkraken.ai_changelog,
            'ai_commit': self.gitkraken.ai_commit,
            'ai_explain_branch': self.gitkraken.ai_explain_branch,
            'ai_explain_commit': self.gitkraken.ai_explain_commit,
            'ai_pr_create': self.gitkraken.ai_pr_create,
            'ai_resolve': self.gitkraken.ai_resolve,
            'ai_tokens': self.gitkraken.ai_tokens,
            
            # Auth commands
            'auth_login': self.gitkraken.auth_login,
            'auth_logout': self.gitkraken.auth_logout,
            
            # Graph commands
            'graph': self.gitkraken.graph,
            
            # Issue commands
            'issue_assign': self.gitkraken.issue_assign,
            'issue_list': self.gitkraken.issue_list,
            
            # MCP commands
            'mcp_start': self.gitkraken.mcp_start,
            'mcp_install': self.gitkraken.mcp_install,
            'mcp_uninstall': self.gitkraken.mcp_uninstall,
            
            # Organization commands
            'organization_list': self.gitkraken.organization_list,
            'organization_set': self.gitkraken.organization_set,
            'organization_unset': self.gitkraken.organization_unset,
            
            # Provider commands
            'provider_add': self.gitkraken.provider_add,
            'provider_list': self.gitkraken.provider_list,
            'provider_remove': self.gitkraken.provider_remove,
            
            # Version command
            'version': self.gitkraken.version,
            
            # Work commands
            'work_list': self.gitkraken.work_list,
            'work_info': self.gitkraken.work_info,
            'work_start': self.gitkraken.work_start,
            'work_set': self.gitkraken.work_set,
            'work_branch': self.gitkraken.work_branch,
            'work_commit': self.gitkraken.work_commit,
            'work_push': self.gitkraken.work_push,
            'work_pr_create': self.gitkraken.work_pr_create,
            'work_pr_merge': self.gitkraken.work_pr_merge,
            'work_delete': self.gitkraken.work_delete,
            'work_update': self.gitkraken.work_update,
            
            # Workspace commands
            'workspace_list': self.gitkraken.workspace_list,
            'workspace_info': self.gitkraken.workspace_info,
            'workspace_create': self.gitkraken.workspace_create,
            'workspace_set': self.gitkraken.workspace_set,
            'workspace_unset': self.gitkraken.workspace_unset,
            'workspace_update': self.gitkraken.workspace_update,
            'workspace_delete': self.gitkraken.workspace_delete,
            'workspace_refresh': self.gitkraken.workspace_refresh,
            'workspace_clone': self.gitkraken.workspace_clone,
        }
        
        if command not in method_map:
            return {
                'success': False,
                'error': f'Unknown GitKraken command: {command}'
            }
        
        try:
            method = method_map[command]
            result = method(**kwargs)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def venice_generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generates an image using the Venice AI service.

        This is a wrapper around the `generate_image` method in the
        `VeniceAIImageGenerator` class.

        Args:
            prompt: The text prompt for image generation.
            **kwargs: Additional parameters to pass to the image generator,
                such as `model`, `aspect_ratio`, `steps`, etc.

        Returns:
            A dictionary containing the result of the image generation,
            including file paths and metadata. Returns an error dictionary
            if Venice AI is not initialized.
        """
        if not self.venice:
            return {
                'success': False,
                'error': 'Venice AI not initialized - please set VENICE_API_KEY environment variable'
            }
        
        try:
            result = self.venice.generate_image(prompt=prompt, **kwargs)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def venice_upscale_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """Upscales an image using the Venice AI service.

        This is a wrapper around the `upscale_image_file` method in the
        `VeniceAIImageGenerator` class.

        Args:
            image_path: The local path to the image file to be upscaled.
            **kwargs: Additional parameters for the upscaling process,
                such as `scale`, `enhance`, etc.

        Returns:
            A dictionary containing the result of the upscaling operation.
            Returns an error dictionary if Venice AI is not initialized.
        """
        if not self.venice:
            return {
                'success': False,
                'error': 'Venice AI not initialized - please set VENICE_API_KEY environment variable'
            }
        
        try:
            result = self.venice.upscale_image_file(image_path, **kwargs)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_available_models(self) -> Dict[str, Any]:
        """Lists available models from the Venice AI service.

        This method fetches all models and also provides a filtered list of
        models identified as 'uncensored'.

        Returns:
            A dictionary containing lists of all models and just the
            uncensored models. Returns an error dictionary if Venice AI
            is not initialized.
        """
        if not self.venice:
            return {
                'success': False,
                'error': 'Venice AI not initialized - please set VENICE_API_KEY environment variable'
            }
        
        try:
            # The list_models method now returns a dictionary containing both lists
            model_data = self.venice.list_models()
            return {
                'success': True,
                'all_models': model_data.get('all_models', []),
                'uncensored_models': model_data.get('uncensored_models', [])
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def external_chat_completion(self, provider_id: str, model_id: str, messages: list, **kwargs) -> Dict[str, Any]:
        """Performs a chat completion using an external API provider.

        This method initializes the `ExternalAPIIntegrator` and calls its
        `chat_completion` method.

        Args:
            provider_id: The unique identifier for the API provider.
            model_id: The unique identifier for the model to use.
            messages: A list of message dictionaries for the conversation.
            **kwargs: Additional parameters to pass to the chat completion API,
                such as `temperature` or `max_tokens`.

        Returns:
            A dictionary containing the result of the chat completion.
        """
        try:
            # Initialize the external API integrator
            external_api = ExternalAPIIntegrator()
            
            # Perform the chat completion
            result = external_api.chat_completion(
                provider_id=provider_id,
                model_id=model_id,
                messages=messages,
                **kwargs
            )
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_external_providers(self) -> Dict[str, Any]:
        """Lists available external API providers and their models.

        This method initializes the `ExternalAPIIntegrator` to load provider
        configurations and return a list of available providers and their
        respective models.

        Returns:
            A dictionary containing a list of provider IDs and a mapping of
            provider IDs to their available models.
        """
        try:
            # Initialize the external API integrator
            external_api = ExternalAPIIntegrator()
            
            # Get the available providers
            providers = external_api.get_available_providers()
            
            # Also get models for each provider
            all_models = external_api.list_all_models()
            
            return {
                'success': True,
                'providers': providers,
                'models': all_models
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_venice_api(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Verifies a Venice AI API key.

        This is a wrapper around the `verify_api_key` method in the
        `VeniceAIVerifier` class.

        Args:
            api_key: The API key to verify. If not provided, the key from
                the environment will be used.

        Returns:
            A dictionary containing the verification result.
        """
        try:
            # Use provided API key or fallback to environment
            key_to_use = api_key or self.venice_api_key
            if not key_to_use:
                return {
                    'success': False,
                    'error': 'No API key provided for verification'
                }
            
            # Initialize the verifier
            verifier = VeniceAIVerifier(api_key=key_to_use)
            
            # Perform verification
            result = verifier.verify_api_key()
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_venice_config(self) -> Dict[str, Any]:
        """Updates the Raycast configuration with the latest Venice AI models.

        This is a wrapper around the `update_raycast_config` method in the
        `VeniceAIConfigUpdater` class. It uses the API key stored in the
        instance.

        Returns:
            A dictionary containing the result of the configuration update.
        """
        try:
            if not self.venice_api_key:
                return {
                    'success': False,
                    'error': 'No API key provided for configuration update'
                }
            
            # Initialize the config updater with the instance's API key
            updater = VeniceAIConfigUpdater(api_key=self.venice_api_key)
            
            # Perform the update
            result = updater.update_raycast_config()
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """The main entry point for the command-line interface.

    This function parses command-line arguments and calls the appropriate
    method in the `QwenCLIIntegrator` class to execute the requested command.
    """
    parser = argparse.ArgumentParser(description="Qwen Code Integration Tool")
    subparsers = parser.add_subparsers(dest="tool", help="Available tools")
    
    # GitKraken subcommands
    gk_parser = subparsers.add_parser("gitkraken", help="GitKraken CLI integration")
    gk_subparsers = gk_parser.add_subparsers(dest="gk_command", help="GitKraken commands")
    
    # Common arguments for GitKraken commands
    common_gk_args = {
        "path": {"type": str, "help": "Repository path", "required": False},
    }
    
    # AI commands
    ai_changelog = gk_subparsers.add_parser("ai_changelog", help="Generate changelog with AI")
    ai_changelog.add_argument("--base", type=str, help="Base branch or commit")
    ai_changelog.add_argument("--head", type=str, help="Head branch or commit")
    ai_changelog.add_argument("--path", type=str, help="Repository path")
    
    ai_commit = gk_subparsers.add_parser("ai_commit", help="Generate commit with AI")
    ai_commit.add_argument("--add-description", action="store_true", help="Add description to commit message")
    ai_commit.add_argument("--path", type=str, help="Repository path")
    
    ai_explain_branch = gk_subparsers.add_parser("ai_explain_branch", help="Explain branch changes with AI")
    ai_explain_branch.add_argument("--branch", type=str, help="Branch to explain (default: HEAD)")
    ai_explain_branch.add_argument("--path", type=str, help="Repository path")
    
    ai_explain_commit = gk_subparsers.add_parser("ai_explain_commit", help="Explain commit changes with AI")
    ai_explain_commit.add_argument("commit_sha", type=str, help="Commit SHA to explain")
    ai_explain_commit.add_argument("--path", type=str, help="Repository path")
    
    ai_pr_create = gk_subparsers.add_parser("ai_pr_create", help="Create PR with AI")
    ai_pr_create.add_argument("--path", type=str, help="Repository path")
    
    ai_resolve = gk_subparsers.add_parser("ai_resolve", help="Resolve conflicts with AI")
    ai_resolve.add_argument("--path", type=str, help="Repository path")
    
    gk_subparsers.add_parser("ai_tokens", help="Show GitKraken AI tokens used")
    
    # Common commands
    gk_subparsers.add_parser("version", help="Show GitKraken CLI version")
    
    # Work commands
    work_list = gk_subparsers.add_parser("work_list", help="List work items")
    
    work_start = gk_subparsers.add_parser("work_start", help="Start a new work item")
    work_start.add_argument("name", type=str, help="Name for the work item")
    work_start.add_argument("--issue", type=str, help="Issue key to link")
    work_start.add_argument("--branch", type=str, help="Branch name")
    work_start.add_argument("--base-branch", type=str, help="Base branch")
    work_start.add_argument("--include-repos", type=str, help="Include repos (comma-separated)")
    work_start.add_argument("--exclude-repos", type=str, help="Exclude repos (comma-separated)")
    
    # Workspace commands
    ws_list = gk_subparsers.add_parser("workspace_list", help="List workspaces")
    ws_info = gk_subparsers.add_parser("workspace_info", help="Show workspace info")
    ws_info.add_argument("--name", type=str, help="Workspace name")
    
    # Venice AI subcommands
    venice_parser = subparsers.add_parser("venice", help="Venice AI integration")
    venice_subparsers = venice_parser.add_subparsers(dest="venice_command", help="Venice commands")
    
    # Image generation command
    gen_parser = venice_subparsers.add_parser("generate", help="Generate an image")
    gen_parser.add_argument("--prompt", type=str, required=True, help="Prompt for image generation")
    gen_parser.add_argument("--model", type=str, default="lustify-sdxl", help="Model to use")
    gen_parser.add_argument("--aspect-ratio", type=str, default="tall", choices=["square", "tall", "wide"], 
                            help="Aspect ratio for output")
    gen_parser.add_argument("--output-dir", type=str, default="generated", help="Output directory")
    gen_parser.add_argument("--output-name", type=str, help="Output filename")
    gen_parser.add_argument("--steps", type=int, default=30, help="Number of inference steps")
    gen_parser.add_argument("--cfg-scale", type=float, default=5.0, help="Classifier-free guidance scale")
    gen_parser.add_argument("--seed", type=int, help="Random seed")
    gen_parser.add_argument("--format", type=str, default="png", choices=["png", "webp"], help="Output format")
    gen_parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    gen_parser.add_argument("--no-safe-mode", action="store_true", help="Disable safe mode")
    gen_parser.add_argument("--no-watermark", action="store_true", help="Hide watermark")
    gen_parser.add_argument("--upscale", action="store_true", help="Auto-upscale generated images")
    gen_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # Upscale command
    upscale_parser = venice_subparsers.add_parser("upscale", help="Upscale an image")
    upscale_parser.add_argument("--input", type=str, required=True, help="Input image path")
    upscale_parser.add_argument("--output", type=str, help="Output image path")
    upscale_parser.add_argument("--scale", type=int, default=4, help="Upscale scale factor")
    upscale_parser.add_argument("--enhance", action="store_true", help="Enhance details")
    upscale_parser.add_argument("--creativity", type=float, default=0.15, help="Enhance creativity")
    upscale_parser.add_argument("--replication", type=float, default=0.35, help="Replication factor")
    upscale_parser.add_argument("--prompt", type=str, help="Enhancement prompt")
    upscale_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # List models command
    venice_subparsers.add_parser("list-models", help="List available Venice AI models")
    venice_subparsers.add_parser("verify", help="Verify Venice API key (uses VENICE_API_KEY)")

    # External providers (Raycast-style providers.yaml)
    external_parser = subparsers.add_parser(
        "external", help="External API providers (reads ~/.config/raycast/ai/providers.yaml)"
    )
    external_subparsers = external_parser.add_subparsers(dest="external_command", help="External commands")
    external_subparsers.add_parser("list-providers", help="List configured providers and models")
    ext_chat = external_subparsers.add_parser("chat", help="Chat completion via a configured provider")
    ext_chat.add_argument("--provider", type=str, required=True, help="Provider ID from providers config")
    ext_chat.add_argument("--model", type=str, required=True, help="Model ID")
    ext_chat.add_argument("--message", type=str, required=True, help="User message")
    ext_chat.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    ext_chat.add_argument("--max-tokens", type=int, default=None, help="Max tokens to generate")

    args = parser.parse_args()
    
    # Initialize the integrator
    integrator = QwenCLIIntegrator()
    
    if args.tool == "gitkraken":
        if args.gk_command is None:
            parser.print_help()
            return 1
            
        # Prepare arguments for the command
        kwargs = {}
        for key, value in vars(args).items():
            if key not in ["tool", "gk_command"]:
                kwargs[key] = value
        
        # Execute GitKraken command
        result = integrator.gitkraken_command(args.gk_command, **kwargs)
        print(json.dumps(result, indent=2))
        
    elif args.tool == "venice":
        if args.venice_command is None:
            parser.print_help()
            return 1
            
        if args.venice_command == "generate":
            # Determine safe mode
            if args.no_safe_mode:
                safe_mode = False
            elif args.safe_mode:
                safe_mode = True
            else:
                safe_mode = False  # Default to False for uncensored
            
            result = integrator.venice_generate_image(
                prompt=args.prompt,
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                steps=args.steps,
                cfg_scale=args.cfg_scale,
                seed=args.seed,
                output_format=args.format,
                safe_mode=safe_mode,
                hide_watermark=args.no_watermark,
                auto_upscale=args.upscale,
                output_dir=args.output_dir,
                output_name=args.output_name,
                verbose=args.verbose
            )
            print(json.dumps(result, indent=2))
            
        elif args.venice_command == "upscale":
            result = integrator.venice_upscale_image(
                image_path=args.input,
                output_path=args.output,
                scale=args.scale,
                enhance=args.enhance,
                enhance_creativity=args.creativity,
                enhance_prompt=args.prompt,
                replication=args.replication,
                verbose=args.verbose
            )
            print(json.dumps(result, indent=2))
            
        elif args.venice_command == "list-models":
            result = integrator.list_available_models()
            print(json.dumps(result, indent=2))

        elif args.venice_command == "verify":
            result = integrator.verify_venice_api()
            print(json.dumps(result, indent=2))

    elif args.tool == "external":
        if args.external_command is None:
            parser.print_help()
            return 1

        if args.external_command == "list-providers":
            result = integrator.list_external_providers()
            print(json.dumps(result, indent=2))

        elif args.external_command == "chat":
            messages = [{"role": "user", "content": args.message}]
            kwargs = {"temperature": args.temperature}
            if args.max_tokens is not None:
                kwargs["max_tokens"] = args.max_tokens
            result = integrator.external_chat_completion(
                provider_id=args.provider,
                model_id=args.model,
                messages=messages,
                **kwargs,
            )
            print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())