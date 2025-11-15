#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test coverage for Qwen CLI Integration.

This test suite covers critical code paths that were previously untested:
1. External API Integrator provider configuration loading and model listing
2. Venice AI image upscaling functionality
3. GitKraken CLI command execution and error handling
4. Redaction functionality for sensitive data
5. Edge cases and error conditions
"""

import unittest
from unittest.mock import Mock, patch

from src import external_api_integrator
from src import gitkraken_integration
from src import venice_integration


class TestExternalAPIIntegratorCoverage(unittest.TestCase):
    """Tests for External API Integrator critical paths"""

    def test_raycast_config_file_discovery(self):
        """Test that Raycast config file is properly discovered in multiple locations."""
        integrator = external_api_integrator.ExternalAPIIntegrator()

        # Test with non-existent paths
        with patch("os.path.exists", return_value=False):
            result = integrator._find_raycast_providers_config()
            self.assertIsNone(result, "Should return None when no config file exists")

    def test_list_all_models_empty_providers(self):
        """Test list_all_models with no providers configured."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {}

        result = integrator.list_all_models()
        self.assertEqual(result, {}, "Should return empty dict for no providers")

    def test_list_all_models_multiple_providers(self):
        """Test list_all_models with multiple providers."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {
            "provider1": {"models": [{"id": "model1", "name": "Model 1"}]},
            "provider2": {"models": [{"id": "model2", "name": "Model 2"}]},
        }

        result = integrator.list_all_models()
        self.assertEqual(len(result), 2)
        self.assertIn("provider1", result)
        self.assertIn("provider2", result)

    def test_get_provider_api_key_from_config(self):
        """Test API key retrieval from provider config."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {"test": {"api_key": "config_key_123"}}

        key = integrator.get_default_provider_api_key("test")
        self.assertEqual(key, "config_key_123")

    def test_get_provider_api_key_from_env(self):
        """Test API key fallback to environment variable."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {"test": {"env_var": "TEST_API_KEY"}}

        with patch("os.getenv", return_value="env_key_456"):
            key = integrator.get_default_provider_api_key("test")
            self.assertEqual(key, "env_key_456")

    def test_chat_completion_missing_provider(self):
        """Test chat_completion with non-existent provider."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {}

        with self.assertRaises(ValueError) as ctx:
            integrator.chat_completion("nonexistent", "model", [])
        self.assertIn("not found", str(ctx.exception).lower())

    def test_chat_completion_missing_model(self):
        """Test chat_completion with non-existent model."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {"test": {"models": [{"id": "model1"}]}}

        with self.assertRaises(ValueError) as ctx:
            integrator.chat_completion("test", "nonexistent_model", [])
        self.assertIn("not found", str(ctx.exception).lower())


class TestRedactionFunctionality(unittest.TestCase):
    """Tests for sensitive data redaction"""

    def test_redact_simple_dict(self):
        """Test redaction of simple dictionary with API key."""
        data = {"api_key": "secret123", "name": "test"}
        result = external_api_integrator.redact_sensitive(data)

        self.assertEqual(result["api_key"], "***REDACTED***")
        self.assertEqual(result["name"], "test")

    def test_redact_nested_dict(self):
        """Test redaction of nested dictionaries."""
        data = {
            "config": {"api_key": "secret", "password": "pass123"},
            "user": "test_user",
        }
        result = external_api_integrator.redact_sensitive(data)

        self.assertEqual(result["config"]["api_key"], "***REDACTED***")
        self.assertEqual(result["config"]["password"], "***REDACTED***")
        self.assertEqual(result["user"], "test_user")

    def test_redact_list_of_dicts(self):
        """Test redaction of list containing dictionaries."""
        data = [
            {"api_key": "key1", "name": "item1"},
            {"token": "token1", "name": "item2"},
        ]
        result = external_api_integrator.redact_sensitive(data)

        self.assertEqual(result[0]["api_key"], "***REDACTED***")
        self.assertEqual(result[1]["token"], "***REDACTED***")
        self.assertEqual(result[0]["name"], "item1")

    def test_redact_mixed_case_keys(self):
        """Test redaction with various key case formats."""
        data = {"Api-Key": "secret1", "API_KEY": "secret2", "api_key": "secret3"}
        result = external_api_integrator.redact_sensitive(data)

        # All variations should be redacted
        self.assertEqual(result["Api-Key"], "***REDACTED***")
        self.assertEqual(result["API_KEY"], "***REDACTED***")
        self.assertEqual(result["api_key"], "***REDACTED***")

    def test_normalize_key_function(self):
        """Test the normalize_key helper function."""
        self.assertEqual(external_api_integrator.normalize_key("api_key"), "apikey")
        self.assertEqual(external_api_integrator.normalize_key("Api-Key"), "apikey")
        self.assertEqual(external_api_integrator.normalize_key("API_KEY"), "apikey")


class TestGitKrakenCLICoverage(unittest.TestCase):
    """Tests for GitKraken CLI integration"""

    def test_cli_not_installed(self):
        """Test behavior when GitKraken CLI is not installed."""
        with patch.object(
            gitkraken_integration.GitKrakenCLI, "_find_gk_cli", return_value=None
        ):
            cli = gitkraken_integration.GitKrakenCLI()

            result = cli.run_command(["version"])
            self.assertFalse(result["success"])
            self.assertIn("not installed", result["error"])

    def test_command_timeout(self):
        """Test handling of command timeout."""
        cli = gitkraken_integration.GitKrakenCLI()
        cli.cli_path = "/fake/path/gk"

        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["gk"], 30)):
            result = cli.run_command(["version"])
            self.assertFalse(result["success"])
            self.assertIn("timed out", result["error"].lower())

    def test_successful_command_execution(self):
        """Test successful command execution."""
        cli = gitkraken_integration.GitKrakenCLI()
        cli.cli_path = "/usr/local/bin/gk"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "GitKraken CLI v1.0.0"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = cli.version()
            self.assertTrue(result["success"])
            self.assertEqual(result["returncode"], 0)
            self.assertIn("v1.0.0", result["stdout"])


class TestVeniceAIImageGeneratorCoverage(unittest.TestCase):
    """Tests for Venice AI image generation critical paths"""

    def test_invalid_aspect_ratio(self):
        """Test handling of invalid aspect ratio."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test")

        with self.assertRaises(ValueError) as ctx:
            generator._size_from_aspect("invalid")
        self.assertIn("Invalid aspect ratio", str(ctx.exception))

    def test_sha256_calculation(self):
        """Test SHA256 hash calculation."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test")

        data = b"test data"
        hash_result = generator._sha256(data)

        # Verify it's a 64-character hex string
        self.assertEqual(len(hash_result), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in hash_result))

    def test_binary_image_response_detection(self):
        """Test detection of binary image responses."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test")

        # Test with image content type
        resp = Mock()
        resp.headers = {"Content-Type": "image/png"}
        self.assertTrue(generator._is_binary_image_response(resp))

        # Test with JSON content type
        resp.headers = {"Content-Type": "application/json"}
        self.assertFalse(generator._is_binary_image_response(resp))

    @patch("src.venice_integration.VeniceAIImageGenerator._session")
    def test_upscale_image_bytes_success(self, mock_session):
        """Test successful image upscaling from bytes."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test")

        # Setup mock response
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.headers = {
            "x-request-id": "test-req-id",
            "Content-Type": "application/json",
        }
        mock_resp.json.return_value = {
            "image": "dXBzY2FsZWRpbWFnZWRhdGE="
        }  # base64 encoded

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_resp
        mock_session.return_value = mock_session_instance

        # Upscale test data
        with patch("base64.b64decode", return_value=b"upscaled_data"):
            result_bytes, metadata = generator.upscale_image_bytes(b"original_data")

        self.assertEqual(result_bytes, b"upscaled_data")
        self.assertIn("request_id", metadata)


class TestVeniceAIVerifierCoverage(unittest.TestCase):
    """Tests for Venice AI verification"""

    def test_verifier_initialization_no_key(self):
        """Test verifier raises error when no API key provided."""
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                venice_integration.VeniceAIVerifier(api_key=None)
            self.assertIn("API key not provided", str(ctx.exception))

    @patch("venice_integration.VeniceAIVerifier._session")
    def test_verify_api_key_unauthorized(self, mock_session):
        """Test API key verification with unauthorized response."""
        verifier = venice_integration.VeniceAIVerifier(api_key="invalid_key")

        mock_resp = Mock()
        mock_resp.status_code = 401
        mock_resp.headers = {"x-request-id": "req-123"}

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_resp
        mock_session.return_value = mock_session_instance

        result = verifier.verify_api_key()

        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 401)
        self.assertIn("Invalid API key", result["message"])

    @patch("src.venice_integration.VeniceAIVerifier._session")
    def test_fetch_models_http_error(self, mock_session):
        """Test model fetching with HTTP error."""
        verifier = venice_integration.VeniceAIVerifier(api_key="test_key")

        import requests

        # Create a proper HTTPError with response object
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.headers = {"x-request-id": "test-123"}

        http_error = requests.HTTPError()
        http_error.response = mock_resp
        mock_resp.raise_for_status.side_effect = http_error

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_resp
        mock_session.return_value = mock_session_instance

        result = verifier.fetch_models()

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["status_code"], 500)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Tests for edge cases and error handling"""

    def test_empty_messages_list(self):
        """Test chat completion with empty messages list."""
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {
            "test": {
                "endpoint": "https://test.com",
                "api_key": "key",
                "models": [{"id": "model1"}],
            }
        }

        # Should not raise on empty messages, but might fail on API call
        with patch("external_api_integrator.requests.post") as mock_post:
            mock_post.side_effect = ValueError("API error")
            with self.assertRaises(ValueError):
                integrator.chat_completion("test", "model1", [])

    def test_venice_list_models_empty_result(self):
        """Test Venice list_models with empty API response."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test")

        with patch.object(
            venice_integration.VeniceAIVerifier,
            "fetch_models",
            return_value={"success": False, "error": "API error"},
        ):
            result = generator.list_models()

            self.assertEqual(result["all_models"], [])
            self.assertEqual(result["uncensored_models"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
