#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests to improve code coverage to 90%+
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open, call
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class TestVeniceIntegration(unittest.TestCase):
    """Test suite for Venice AI integration module."""
    
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_venice_verifier_init(self):
        """Test VeniceAIVerifier initialization."""
        from venice_integration import VeniceAIVerifier
        
        verifier = VeniceAIVerifier()
        self.assertEqual(verifier.api_key, "test_key")
        self.assertEqual(verifier.base_url, "https://api.venice.ai/api/v1")
    
    def test_venice_verifier_no_key(self):
        """Test VeniceAIVerifier raises error without API key."""
        from venice_integration import VeniceAIVerifier
        
        with self.assertRaises(ValueError) as ctx:
            VeniceAIVerifier()
        self.assertIn("API key not provided", str(ctx.exception))
    
    @patch('venice_integration.requests.Session')
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_venice_verify_api_key_success(self, mock_session_class):
        """Test successful API key verification."""
        from venice_integration import VeniceAIVerifier
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "test-id"}
        
        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        verifier = VeniceAIVerifier("test_key")
        result = verifier.verify_api_key()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "API key is valid")
    
    @patch('venice_integration.requests.Session')
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_venice_verify_api_key_invalid(self, mock_session_class):
        """Test invalid API key verification."""
        from venice_integration import VeniceAIVerifier
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"x-request-id": "test-id"}
        
        mock_session = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        verifier = VeniceAIVerifier("test_key")
        result = verifier.verify_api_key()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid API key")
    
    @patch('venice_integration.requests.Session')
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_venice_fetch_models(self, mock_session_class):
        """Test fetching models from Venice API."""
        from venice_integration import VeniceAIVerifier
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"x-request-id": "test-id"}
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "model_spec": {"name": "Model 1"}},
                {"id": "model2", "model_spec": {"name": "Model 2"}}
            ]
        }
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        verifier = VeniceAIVerifier("test_key")
        result = verifier.fetch_models()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["models"]), 2)
    
    @patch('venice_integration.yaml')
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_config_updater_no_yaml(self, mock_yaml):
        """Test config updater when PyYAML is not available."""
        from venice_integration import VeniceAIConfigUpdater
        
        # Simulate PyYAML not installed
        mock_yaml.return_value = None
        import venice_integration
        venice_integration.yaml = None
        
        updater = VeniceAIConfigUpdater("test_key")
        result = updater.generate_raycast_config()
        
        self.assertFalse(result["success"])
        self.assertIn("PyYAML is not installed", result["error"])
        
        # Restore yaml
        venice_integration.yaml = mock_yaml
    
    @patch('venice_integration.VeniceAIVerifier')
    @patch('builtins.open', new_callable=mock_open)
    @patch('venice_integration.yaml')
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_config_updater_success(self, mock_yaml, mock_file, mock_verifier_class):
        """Test successful config update."""
        from venice_integration import VeniceAIConfigUpdater
        
        # Setup mock verifier
        mock_verifier = MagicMock()
        mock_verifier.api_key = "test_key"
        mock_verifier.fetch_models.return_value = {
            "success": True,
            "models": [
                {
                    "id": "test-model",
                    "model_spec": {
                        "name": "Test Model",
                        "availableContextTokens": 2048,
                        "capabilities": {"supportsVision": True},
                        "constraints": {"temperature": {"default": 0.7}}
                    }
                }
            ]
        }
        mock_verifier.verify_api_key.return_value = {"success": True}
        mock_verifier_class.return_value = mock_verifier
        
        updater = VeniceAIConfigUpdater("test_key")
        result = updater.update_raycast_config()
        
        self.assertTrue(result["success"])
    
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_image_generator_init(self):
        """Test VeniceAIImageGenerator initialization."""
        from venice_integration import VeniceAIImageGenerator
        
        generator = VeniceAIImageGenerator("test_key")
        self.assertEqual(generator.api_key, "test_key")
        self.assertEqual(generator.default_model, "lustify-sdxl")
        self.assertIn("square", generator.aspect_to_size)
    
    def test_image_generator_invalid_aspect(self):
        """Test invalid aspect ratio."""
        from venice_integration import VeniceAIImageGenerator
        
        generator = VeniceAIImageGenerator("test_key")
        with self.assertRaises(ValueError) as ctx:
            generator._size_from_aspect("invalid")
        self.assertIn("Invalid aspect ratio", str(ctx.exception))
    
    def test_image_generator_utils(self):
        """Test image generator utility methods."""
        from venice_integration import VeniceAIImageGenerator
        import hashlib
        import pathlib
        
        generator = VeniceAIImageGenerator("test_key")
        
        # Test _size_from_aspect
        width, height = generator._size_from_aspect("square")
        self.assertEqual((width, height), (1024, 1024))
        
        # Test _sha256
        test_data = b"test data"
        expected_hash = hashlib.sha256(test_data).hexdigest()
        self.assertEqual(generator._sha256(test_data), expected_hash)
        
        # Test _effective_dims
        w, h = generator._effective_dims("tall", None, None)
        self.assertEqual((w, h), (768, 1024))
        
        w, h = generator._effective_dims("tall", 800, 600)
        self.assertEqual((w, h), (800, 600))
    
    @patch('venice_integration.argparse.ArgumentParser')
    def test_venice_main_verify(self, mock_parser_class):
        """Test venice main function with --verify."""
        from venice_integration import main
        
        # Setup mock args
        mock_args = Mock()
        mock_args.verify = True
        mock_args.update_config = False
        mock_args.list_models = False
        mock_args.api_key = "test_key"
        mock_args.config_path = None
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        with patch('venice_integration.VeniceAIVerifier') as mock_verifier_class:
            mock_verifier = MagicMock()
            mock_verifier.verify_api_key.return_value = {"success": True}
            mock_verifier_class.return_value = mock_verifier
            
            with patch('venice_integration.json.dumps') as mock_dumps:
                result = main()
                
                self.assertEqual(result, 0)
                mock_verifier.verify_api_key.assert_called_once()
    
    @patch('venice_integration.argparse.ArgumentParser')
    def test_venice_main_no_api_key(self, mock_parser_class):
        """Test venice main function without API key."""
        from venice_integration import main
        
        # Setup mock args
        mock_args = Mock()
        mock_args.verify = True
        mock_args.api_key = None
        
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_parser_class.return_value = mock_parser
        
        with patch.dict(os.environ, {}, clear=True):
            result = main()
            self.assertEqual(result, 1)


class TestExternalAPIIntegrator(unittest.TestCase):
    """Test suite for External API Integrator."""
    
    @patch('external_api_integrator.os.path.exists', return_value=True)
    @patch('external_api_integrator.yaml')
    @patch('builtins.open', new_callable=mock_open, read_data='providers:\n  - id: test_provider\n    name: Test')
    def test_load_providers_success(self, mock_file, mock_yaml, mock_exists):
        """Test successful provider loading."""
        from external_api_integrator import ExternalAPIIntegrator
        
        mock_yaml.safe_load.return_value = {
            'providers': [
                {'id': 'test_provider', 'name': 'Test Provider'}
            ]
        }
        
        integrator = ExternalAPIIntegrator(providers_config_path='test.yaml')
        result = integrator.load_providers_from_config()
        
        self.assertTrue(result)
        self.assertIn('test_provider', integrator.providers)
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        from external_api_integrator import ExternalAPIIntegrator
        
        integrator = ExternalAPIIntegrator()
        integrator.providers = {
            'test': {'name': 'Test Provider', 'models': []}
        }
        
        info = integrator.get_provider_info('test')
        self.assertEqual(info['name'], 'Test Provider')
        
        none_info = integrator.get_provider_info('nonexistent')
        self.assertIsNone(none_info)
    
    def test_get_provider_models(self):
        """Test getting provider models."""
        from external_api_integrator import ExternalAPIIntegrator
        
        integrator = ExternalAPIIntegrator()
        integrator.providers = {
            'test': {
                'models': [
                    {'id': 'model1'},
                    {'id': 'model2'}
                ]
            }
        }
        
        models = integrator.get_provider_models('test')
        self.assertEqual(len(models), 2)
        
        empty_models = integrator.get_provider_models('nonexistent')
        self.assertEqual(len(empty_models), 0)
    
    def test_list_all_models(self):
        """Test listing all models."""
        from external_api_integrator import ExternalAPIIntegrator
        
        integrator = ExternalAPIIntegrator()
        integrator.providers = {
            'test1': {'models': [{'id': 'model1'}]},
            'test2': {'models': [{'id': 'model2'}]}
        }
        
        all_models = integrator.list_all_models()
        self.assertEqual(len(all_models), 2)
        self.assertIn('test1', all_models)
        self.assertIn('test2', all_models)
    
    @patch('external_api_integrator.requests.post')
    def test_chat_completion_success(self, mock_post):
        """Test successful chat completion."""
        from external_api_integrator import ExternalAPIIntegrator
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        integrator = ExternalAPIIntegrator()
        integrator.providers = {
            'test': {
                'endpoint': 'https://api.test.com/v1/chat/completions',
                'api_key': 'test_key',
                'models': [{'id': 'test-model'}]
            }
        }
        
        result = integrator.chat_completion(
            'test', 'test-model',
            [{'role': 'user', 'content': 'Hello'}]
        )
        
        self.assertIn('choices', result)
        mock_post.assert_called_once()
    
    def test_chat_completion_no_provider(self):
        """Test chat completion with non-existent provider."""
        from external_api_integrator import ExternalAPIIntegrator
        
        integrator = ExternalAPIIntegrator()
        with self.assertRaises(ValueError) as ctx:
            integrator.chat_completion(
                'nonexistent', 'model',
                [{'role': 'user', 'content': 'Hello'}]
            )
        self.assertIn('not found', str(ctx.exception).lower())


class TestAutoConfig(unittest.TestCase):
    """Test suite for auto config module."""
    
    @patch('auto_config.sys.argv', ['auto_config.py', '--verify', '--api-key', 'test_key'])
    @patch('auto_config.VeniceAIVerifier')
    def test_auto_config_verify(self, mock_verifier_class):
        """Test auto config with verify flag."""
        from auto_config import main
        
        mock_verifier = MagicMock()
        mock_verifier.verify_api_key.return_value = {"success": True}
        mock_verifier_class.return_value = mock_verifier
        
        with patch('auto_config.json.dumps'):
            result = main()
            self.assertEqual(result, 0)
    
    @patch('auto_config.sys.argv', ['auto_config.py', '--update-config'])
    def test_auto_config_no_api_key(self):
        """Test auto config without API key."""
        from auto_config import main
        
        with patch.dict(os.environ, {}, clear=True):
            result = main()
            self.assertEqual(result, 1)


class TestGitKrakenCLI(unittest.TestCase):
    """Test suite for GitKraken CLI integration."""
    
    @patch('gitkraken_integration.subprocess.run')
    def test_find_gk_cli(self, mock_run):
        """Test finding GitKraken CLI."""
        from gitkraken_integration import GitKrakenCLI
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '/usr/local/bin/gk'
        mock_run.return_value = mock_result
        
        cli = GitKrakenCLI()
        self.assertEqual(cli.cli_path, '/usr/local/bin/gk')
        self.assertTrue(cli.is_installed())
    
    @patch('gitkraken_integration.subprocess.run')
    @patch('os.path.exists')
    def test_find_gk_cli_fallback(self, mock_exists, mock_run):
        """Test finding GitKraken CLI with fallback paths."""
        from gitkraken_integration import GitKrakenCLI
        
        # which command fails
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        # First path doesn't exist, second does
        mock_exists.side_effect = [False, True]
        
        cli = GitKrakenCLI()
        self.assertEqual(cli.cli_path, '/opt/homebrew/bin/gk')
    
    @patch('gitkraken_integration.subprocess.run')
    def test_run_command_not_installed(self, mock_run):
        """Test running command when GitKraken is not installed."""
        from gitkraken_integration import GitKrakenCLI
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        cli = GitKrakenCLI()
        cli.cli_path = None
        
        result = cli.run_command(['version'])
        self.assertFalse(result['success'])
        self.assertIn('not installed', result['error'])
    
    @patch('gitkraken_integration.subprocess.run')
    def test_various_commands(self, mock_run):
        """Test various GitKraken commands."""
        from gitkraken_integration import GitKrakenCLI
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'success'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        cli = GitKrakenCLI()
        cli.cli_path = '/usr/local/bin/gk'
        
        # Test version
        result = cli.version()
        self.assertTrue(result['success'])
        
        # Test ai_commit
        result = cli.ai_commit(add_description=True)
        self.assertTrue(result['success'])
        
        # Test workspace_list
        result = cli.workspace_list()
        self.assertTrue(result['success'])


class TestQwenCLIIntegrator(unittest.TestCase):
    """Test suite for main Qwen CLI Integrator."""
    
    @patch.dict(os.environ, {"VENICE_API_KEY": "test_key"})
    def test_integrator_init_with_key(self):
        """Test integrator initialization with API key."""
        from qwen_cli_integrator import QwenCLIIntegrator
        
        with patch('qwen_cli_integrator.VeniceAIImageGenerator') as mock_venice:
            integrator = QwenCLIIntegrator()
            self.assertIsNotNone(integrator.venice_api_key)
            mock_venice.assert_called_once_with(api_key="test_key")
    
    def test_integrator_init_no_key(self):
        """Test integrator initialization without API key."""
        from qwen_cli_integrator import QwenCLIIntegrator
        
        with patch.dict(os.environ, {}, clear=True):
            integrator = QwenCLIIntegrator()
            self.assertIsNone(integrator.venice)
            self.assertIsNone(integrator.venice_api_key)
    
    @patch('qwen_cli_integrator.GitKrakenCLI')
    def test_gitkraken_command_unknown(self, mock_gk_class):
        """Test unknown GitKraken command."""
        from qwen_cli_integrator import QwenCLIIntegrator
        
        mock_gk = MagicMock()
        mock_gk.is_installed.return_value = True
        mock_gk_class.return_value = mock_gk
        
        integrator = QwenCLIIntegrator()
        result = integrator.gitkraken_command('unknown_command')
        
        self.assertFalse(result['success'])
        self.assertIn('Unknown', result['error'])
    
    @patch('qwen_cli_integrator.ExternalAPIIntegrator')
    def test_list_external_providers(self, mock_ext_class):
        """Test listing external providers."""
        from qwen_cli_integrator import QwenCLIIntegrator
        
        mock_ext = MagicMock()
        mock_ext.get_available_providers.return_value = ['provider1']
        mock_ext.list_all_models.return_value = {'provider1': []}
        mock_ext_class.return_value = mock_ext
        
        integrator = QwenCLIIntegrator()
        result = integrator.list_external_providers()
        
        self.assertTrue(result['success'])
        self.assertIn('providers', result)
    
    @patch('qwen_cli_integrator.sys.argv', ['qwen_cli_integrator.py', '--help'])
    @patch('qwen_cli_integrator.sys.exit')  # Mock sys.exit as argparse exits on --help
    @patch('qwen_cli_integrator.argparse.ArgumentParser')
    def test_main_help(self, mock_parser_class, mock_sys_exit):
        """Test main function with --help (argparse exits with code 0)."""
        from qwen_cli_integrator import main
        
        mock_parser = MagicMock()
        # When --help is provided, argparse's parse_args raises SystemExit(0)
        mock_parser.parse_args.side_effect = SystemExit(0)
        mock_parser_class.return_value = mock_parser
        
        # Call main and expect SystemExit to be caught
        try:
            main()
        except SystemExit:
            pass  # Expected behavior
        
        # Verify parse_args was called (which triggers help output)
        mock_parser.parse_args.assert_called_once()

    @patch('qwen_cli_integrator.sys.argv', ['qwen_cli_integrator.py', 'invalid_subcommand'])
    @patch('qwen_cli_integrator.argparse.ArgumentParser')
    def test_main_invalid_subcommand(self, mock_parser_class):
        """Test main function with invalid subcommand (prints help and returns 1)."""
        from qwen_cli_integrator import main

        mock_parser = MagicMock()
        # Simulate parse_args returning a Namespace with an invalid subcommand
        # Corrected: 'dest' for subparsers is 'tool', not 'command'
        mock_parser.parse_args.return_value = argparse.Namespace(tool='invalid_subcommand')
        mock_parser_class.return_value = mock_parser

        # For invalid tool, main() calls parser.print_help() and returns 1
        result = main()
        
        mock_parser.print_help.assert_called_once()  # Assert parser.print_help is called
        self.assertEqual(result, 1)  # Assert return code is 1

if __name__ == '__main__':
    unittest.main()