#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for bug fixes in Qwen CLI Integration.

This file contains tests that verify the fixes for three identified bugs:
1. Unreachable code in venice_integration.py main() function
2. Incorrect exception handling in external_api_integrator.py
3. Incorrect metadata storage in venice_integration.py generate_image()
"""

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src import external_api_integrator
from src import venice_integration


class TestBugFix1_VeniceMainFunction(unittest.TestCase):
    """Tests for Bug #1: Fix unreachable code in venice_integration.py main()"""

    @patch("src.venice_integration.VeniceAIConfigUpdater")
    @patch("src.venice_integration.os.environ.get")
    @patch(
        "sys.argv",
        ["venice_integration.py", "--update-config", "--api-key", "test_key"],
    )
    def test_update_config_flag_works_independently(self, mock_env, mock_updater_class):
        """
        Test that --update-config flag works independently (Bug #1 fix verification).

        Before the fix, --update-config was unreachable because it was inside the
        args.verify block. This test ensures it can be called independently.
        """
        # Setup mocks
        mock_env.return_value = None
        mock_updater_instance = Mock()
        mock_updater_instance.update_raycast_config.return_value = {
            "success": True,
            "config_path": "/test/path",
        }
        mock_updater_class.return_value = mock_updater_instance

        # Run the main function
        with patch("builtins.print"):  # Suppress output
            result = venice_integration.main()

        # Verify the updater was created and called
        mock_updater_class.assert_called_once_with("test_key")
        mock_updater_instance.update_raycast_config.assert_called_once()
        self.assertEqual(result, 0, "Main should return 0 on success")

    @patch("src.venice_integration.VeniceAIVerifier")
    @patch("sys.argv", ["venice_integration.py", "--verify", "--api-key", "test_key"])
    def test_verify_flag_works_independently(self, mock_verifier_class):
        """
        Test that --verify flag still works independently after the fix.
        """
        # Setup mocks
        mock_verifier_instance = Mock()
        mock_verifier_instance.verify_api_key.return_value = {
            "success": True,
            "message": "API key is valid",
        }
        mock_verifier_class.return_value = mock_verifier_instance

        # Run the main function
        with patch("builtins.print"):
            result = venice_integration.main()

        # Verify the verifier was created and called
        mock_verifier_class.assert_called_once_with("test_key")
        mock_verifier_instance.verify_api_key.assert_called_once()
        self.assertEqual(result, 0)


class TestBugFix2_ExceptionHandling(unittest.TestCase):
    """Tests for Bug #2: Fix incorrect exception handling in external_api_integrator.py"""

    @patch("external_api_integrator.requests.post")
    def test_exception_handling_preserves_context(self, mock_post):
        """
        Test that API exceptions are properly handled with context preservation.

        Before the fix, RequestException was incorrectly re-raised, potentially
        losing context. Now it should raise ValueError with proper chaining.
        """
        # Import requests module to create proper exception
        import requests

        # Create a mock requests exception
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        original_error = requests.RequestException("Connection timeout")
        mock_post.side_effect = original_error

        # Create integrator with mock provider config
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {
            "test_provider": {
                "id": "test_provider",
                "name": "Test Provider",
                "endpoint": "https://api.test.com/chat",
                "api_key": "test_key",
                "models": [{"id": "test-model", "name": "Test Model"}],
            }
        }

        # Attempt chat completion - should raise ValueError with proper context
        with self.assertRaises(ValueError) as context:
            integrator.chat_completion(
                provider_id="test_provider",
                model_id="test-model",
                messages=[{"role": "user", "content": "test"}],
            )

        # Verify the exception message includes provider context
        self.assertIn("test_provider", str(context.exception))
        self.assertIn("API request failed", str(context.exception))

        # Verify exception chaining is preserved
        self.assertIsNotNone(context.exception.__cause__)


class TestBugFix3_MetadataStorage(unittest.TestCase):
    """Tests for Bug #3: Fix incorrect metadata storage in generate_image()"""

    @patch("src.venice_integration.VeniceAIImageGenerator._session")
    @patch("src.venice_integration.VeniceAIImageGenerator._save_bytes")
    @patch("src.venice_integration.VeniceAIImageGenerator._ensure_dir")
    @patch("builtins.open", new_callable=mock_open)
    def test_metadata_stores_actual_dimensions(
        self, mock_file, mock_ensure, mock_save, mock_session
    ):
        """
        Test that metadata stores actual resolved dimensions, not None values.

        Before the fix, if width/height were None (relying on aspect_ratio),
        the metadata would store None instead of the actual dimensions used.
        """
        # Setup mocks
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.headers = {"x-request-id": "test-123"}
        mock_resp.json.return_value = {"images": ["base64encodedimagedata"]}
        mock_resp.content = b"fake_image_data"

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_resp
        mock_session.return_value = mock_session_instance

        # Create generator
        generator = venice_integration.VeniceAIImageGenerator(api_key="test_key")

        # Generate image with aspect_ratio (no explicit width/height)
        with patch("src.venice_integration.pathlib.Path.resolve") as mock_resolve:
            mock_resolve.return_value = Path("/tmp/test")
            with patch("base64.b64decode", return_value=b"decoded_image"):
                generator.generate_image(
                    prompt="test prompt",
                    aspect_ratio="tall",  # Should resolve to 768x1024
                    auto_upscale=False,
                    verbose=False,
                )

        # Verify metadata file was written
        self.assertTrue(mock_file.called, "Metadata file should be written")

        # Get the JSON data written to the metadata file
        handle = mock_file()
        json_write_calls = [call for call in handle.write.call_args_list]

        if json_write_calls:
            # Reconstruct the JSON from write calls
            json_content = "".join([str(call[0][0]) for call in json_write_calls])
            metadata = json.loads(json_content)

            # Verify actual dimensions are stored (768x1024 for "tall")
            self.assertEqual(
                metadata["request_params"]["width"],
                768,
                "Width should be resolved to 768 for 'tall' aspect ratio",
            )
            self.assertEqual(
                metadata["request_params"]["height"],
                1024,
                "Height should be resolved to 1024 for 'tall' aspect ratio",
            )
            self.assertIsNotNone(
                metadata["request_params"]["width"],
                "Width should not be None in metadata",
            )
            self.assertIsNotNone(
                metadata["request_params"]["height"],
                "Height should not be None in metadata",
            )

    def test_effective_dims_resolves_correctly(self):
        """Test that _effective_dims properly resolves aspect ratios to dimensions."""
        generator = venice_integration.VeniceAIImageGenerator(api_key="test_key")

        # Test with aspect ratio
        w, h = generator._effective_dims("square", None, None)
        self.assertEqual((w, h), (1024, 1024))

        w, h = generator._effective_dims("tall", None, None)
        self.assertEqual((w, h), (768, 1024))

        w, h = generator._effective_dims("wide", None, None)
        self.assertEqual((w, h), (1024, 768))

        # Test with explicit dimensions
        w, h = generator._effective_dims("tall", 512, 768)
        self.assertEqual(
            (w, h), (512, 768), "Explicit dimensions should override aspect ratio"
        )


class TestBugFixIntegration(unittest.TestCase):
    """Integration tests to verify all bug fixes work together"""

    def test_all_fixes_applied(self):
        """Smoke test to ensure all fixes are in place without breaking existing functionality."""
        # Test 1: Verify venice_integration.main has proper branching
        with patch("sys.argv", ["test", "--help"]):
            with patch("builtins.print"):
                # Should not crash and should handle help properly
                try:
                    venice_integration.main()
                except SystemExit:
                    pass  # argparse calls sys.exit on --help

        # Test 2: Verify external_api_integrator exception handling
        integrator = external_api_integrator.ExternalAPIIntegrator()
        integrator.providers = {}

        with self.assertRaises(ValueError) as ctx:
            integrator.chat_completion("nonexistent", "model", [])
        self.assertIn("not found", str(ctx.exception).lower())

        # Test 3: Verify VeniceAIImageGenerator has _effective_dims
        generator = venice_integration.VeniceAIImageGenerator(api_key="test_key")
        self.assertTrue(hasattr(generator, "_effective_dims"))
        self.assertTrue(callable(generator._effective_dims))


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
