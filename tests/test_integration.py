#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Qwen CLI Integration
This script tests both GitKraken and Venice AI integration functionality.
"""

import os
import sys
import unittest
import subprocess
from unittest.mock import patch

from src.qwen_cli_integrator import QwenCLIIntegrator


class TestQwenCLIIntegration(unittest.TestCase):
    """Test suite for the Qwen CLI Integrator."""

    def setUp(self):
        """Set up for each test."""
        # Patch the environment for all tests in this class
        self.env_patcher = patch.dict(os.environ, {"VENICE_API_KEY": "fake_key"})
        self.env_patcher.start()
        self.integrator = QwenCLIIntegrator()

    def tearDown(self):
        """Tear down after each test."""
        self.env_patcher.stop()

    def test_help_output(self):
        """Test that help output works for all main commands."""
        print("\nTesting help output...")

        # Test main help
        result = subprocess.run(
            [sys.executable, "-m", "src.qwen_cli_integrator", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        print("✓ Main help output works correctly")

        # Test GitKraken help
        result = subprocess.run(
            [sys.executable, "-m", "src.qwen_cli_integrator", "gitkraken", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        print("✓ GitKraken help output works correctly")

        # Test Venice help
        result = subprocess.run(
            [sys.executable, "-m", "src.qwen_cli_integrator", "venice", "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        print("✓ Venice help output works correctly")

    @patch("src.qwen_cli_integrator.VeniceAIImageGenerator")
    def test_venice_generate_image_call(self, MockVeniceGenerator):
        """Test that calling venice generate command correctly calls the generator and returns the right data."""
        print("\nTesting Venice AI image generation call...")

        mock_instance = MockVeniceGenerator.return_value
        expected_result = {"success": True, "path": "/fake/path.png"}
        mock_instance.generate_image.return_value = expected_result

        integrator = QwenCLIIntegrator()
        result = integrator.venice_generate_image(prompt="a test prompt")

        mock_instance.generate_image.assert_called_once_with(prompt="a test prompt")
        self.assertEqual(result, expected_result)
        print(
            "✓ venice_generate_image correctly calls the integration and returns data."
        )

    @patch("src.qwen_cli_integrator.GitKrakenCLI")
    def test_gitkraken_command_dispatch(self, MockGitKrakenCLI):
        """Test that GitKraken commands are dispatched and return correct data."""
        print("\nTesting GitKraken command dispatch...")

        mock_instance = MockGitKrakenCLI.return_value
        mock_instance.is_installed.return_value = True
        expected_result = {"success": True, "stdout": "Mocked commit"}
        mock_instance.ai_commit.return_value = expected_result

        integrator = QwenCLIIntegrator()
        result = integrator.gitkraken_command("ai_commit", add_description=True)

        mock_instance.ai_commit.assert_called_once_with(add_description=True)
        self.assertEqual(result, expected_result)
        print("✓ gitkraken_command correctly dispatches and returns data.")

    @patch("src.qwen_cli_integrator.VeniceAIImageGenerator")
    def test_list_available_models_integrator(self, MockVeniceGenerator):
        """Test that the integrator correctly calls and processes list_models."""
        print("\nTesting list_available_models in the integrator...")

        mock_instance = MockVeniceGenerator.return_value
        mock_model_data = {
            "all_models": [{"id": "model-1"}],
            "uncensored_models": [{"id": "uncensored-model"}],
        }
        mock_instance.list_models.return_value = mock_model_data

        integrator = QwenCLIIntegrator()
        result = integrator.list_available_models()

        mock_instance.list_models.assert_called_once()
        self.assertTrue(result["success"])
        self.assertEqual(result["all_models"], mock_model_data["all_models"])
        self.assertEqual(
            result["uncensored_models"], mock_model_data["uncensored_models"]
        )
        print("✓ Integrator's list_available_models processes data correctly.")

    @patch("src.qwen_cli_integrator.VeniceAIConfigUpdater")
    def test_update_venice_config_call(self, MockConfigUpdater):
        """Test that the update_venice_config call is correctly handled."""
        print("\nTesting update_venice_config call...")

        mock_instance = MockConfigUpdater.return_value
        expected_result = {"success": True, "path": "/fake/config.yaml"}
        mock_instance.update_raycast_config.return_value = expected_result

        integrator = QwenCLIIntegrator()
        result = integrator.update_venice_config()

        # Verify that the updater was initialized with the correct API key
        MockConfigUpdater.assert_called_with(api_key="fake_key")
        # Verify the method was called without any arguments
        mock_instance.update_raycast_config.assert_called_once_with()
        self.assertEqual(result, expected_result)
        print("✓ update_venice_config calls the updater correctly.")


if __name__ == "__main__":
    print("Qwen CLI Integration - Test Suite")
    print("=" * 50)
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQwenCLIIntegration))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    # Check if tests failed and exit with a non-zero code if they did
    if result.failures or result.errors:
        print("\nTest suite failed.")
        sys.exit(1)
    else:
        print("\nTest suite completed successfully!")
        sys.exit(0)
