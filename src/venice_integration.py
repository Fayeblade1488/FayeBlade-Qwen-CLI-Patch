#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Venice AI Integration Module for Qwen Code
This module provides integration with Venice AI's image generation, model verification,
and Raycast configuration auto-update capabilities.
"""

import argparse
import base64
import hashlib
import json
import os
import pathlib
import random
import sys
import time
import types
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import yaml, with a fallback if not available
yaml: Optional[types.ModuleType]
try:
    import yaml
except ImportError:
    print(
        "Warning: PyYAML is not installed. Install it with 'pip install PyYAML' to use configuration auto-update functionality.",
        file=sys.stderr,
    )
    yaml = None


class VeniceAIVerifier:
    """
    A class to verify Venice AI API key and fetch model information.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("VENICE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. Use api_key parameter or set VENICE_API_KEY environment variable."
            )

        self.base_url = "https://api.venice.ai/api/v1"
        self.models_endpoint = f"{self.base_url}/models"
        self.chat_endpoint = f"{self.base_url}/chat/completions"

    def _session(self, timeout_connect=10, timeout_read=120) -> requests.Session:
        """Create a requests session with retry logic and timeout handling."""
        s = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        )
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.mount("http://", HTTPAdapter(max_retries=retry))
        s.headers.update(
            {
                "User-Agent": "qwen-cli-venice-integration/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        return s

    def _with_timeouts(self, func, timeouts: Tuple[int, int]):
        """Add timeout wrapper to request function.

        Args:
            func: The request function to wrap.
            timeouts: A tuple of (connect_timeout, read_timeout) in seconds.

        Returns:
            A wrapper function that adds timeout handling to the request.
        """

        def wrapper(method, url, **kwargs):
            """Wrapper function that applies timeouts and rate limiting to requests.

            Args:
                method: HTTP method (GET, POST, etc.).
                url: The URL to make the request to.
                **kwargs: Additional keyword arguments for the request.

            Returns:
                The response from the wrapped request function.
            """
            timeout = kwargs.pop("timeout", (timeouts[0], timeouts[1]))
            time.sleep(random.uniform(0, 0.05))
            return func(method, url, timeout=timeout, **kwargs)

        return wrapper

    def verify_api_key(self) -> Dict[str, Any]:
        """
        Verify the Venice AI API key by making a simple test request.

        Returns:
            Dictionary with verification result
        """
        s = self._session()
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make a simple request to verify the API key
        try:
            # Use chat completion with minimal parameters to verify the API
            data = {
                "model": "venice-uncensored",  # Use a known model
                "messages": [{"role": "user", "content": "test"}],
                "temperature": 0.1,
                "max_tokens": 5,
            }

            resp = s.post(self.chat_endpoint, headers=headers, json=data)
            req_id = resp.headers.get("x-request-id") or resp.headers.get(
                "X-Request-ID"
            )

            if resp.status_code in [
                200,
                400,
            ]:  # 200 for success, 400 for validation error (but key valid)
                # Even if the request fails due to validation, a 400 means the API key was accepted
                return {
                    "success": True,
                    "status_code": resp.status_code,
                    "request_id": req_id,
                    "message": "API key is valid",
                }
            elif resp.status_code == 401:
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "request_id": req_id,
                    "message": "Invalid API key",
                }
            else:
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "request_id": req_id,
                    "message": f"API returned unexpected status: {resp.status_code}",
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def fetch_models(self) -> Dict[str, Any]:
        """
        Fetch the list of available models from Venice AI API.

        Returns:
            Dictionary with models data
        """
        s = self._session()
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            resp = s.get(self.models_endpoint, headers=headers)
            resp.raise_for_status()

            data = resp.json()
            return {
                "success": True,
                "models": data.get("data", []),
                "request_id": resp.headers.get("x-request-id")
                or resp.headers.get("X-Request-ID"),
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {e}",
                "status_code": e.response.status_code,
                "request_id": e.response.headers.get("x-request-id")
                if e.response
                else None,
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


class VeniceAIConfigUpdater:
    """
    A class to generate and update Raycast configuration files with Venice AI models.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.verifier = VeniceAIVerifier(api_key)
        self.base_url = "https://api.venice.ai/api/v1"

    def generate_raycast_config(
        self, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a Raycast configuration file with updated model information.

        Args:
            output_path: Path to save the generated config file

        Returns:
            Dictionary with generation result
        """
        if yaml is None:
            return {
                "success": False,
                "error": "PyYAML is not installed. Install it with 'pip install PyYAML'",
            }

        # Fetch models from API
        models_result = self.verifier.fetch_models()
        if not models_result["success"]:
            return models_result

        models_data = models_result["models"]

        # Construct the configuration - DO NOT include the actual API key in the config
        config: Dict[str, List[Dict[str, Any]]] = {
            "providers": [
                {
                    "id": "venice",
                    "name": "Venice.ai",
                    "base_url": self.base_url,
                    "api_keys": {
                        # IMPORTANT: For security reasons, the actual API key should not be stored in
                        # the configuration file. The Raycast extension will read the API key from
                        # environment variables or prompt the user for it separately.
                        "openai": "${VENICE_API_KEY}"  # Placeholder that references environment variable
                    },
                    "models": [],
                }
            ]
        }

        # Process each model from the API response
        for model in models_data:
            model_id = model.get("id")
            model_details = model.get("model_spec", {})
            model_name = model_details.get("name")
            context = model_details.get("availableContextTokens", 0)

            # Create abilities object based on capabilities
            capabilities = model_details.get("capabilities", {})
            constraints = model_details.get("constraints", {})

            # Format abilities with proper structure
            temperature_supported = "temperature" in constraints
            temperature_default = constraints.get("temperature", {}).get("default", 0.7)
            vision_supported = capabilities.get("supportsVision", False)
            tools_supported = capabilities.get("supportsFunctionCalling", False)
            web_search_supported = capabilities.get("supportsWebSearch", False)
            reasoning_supported = capabilities.get("supportsReasoning", False)

            model_entry = {
                "id": model_id,
                "name": model_name,
                "context": context,
                "provider": "venice",
                "abilities": {
                    "temperature": {
                        "supported": temperature_supported,
                        "default": temperature_default,
                    },
                    "vision": {"supported": vision_supported},
                    "tools": {"supported": tools_supported},
                    "web_search": {"supported": web_search_supported},
                    "reasoning": {"supported": reasoning_supported},
                },
            }

            config["providers"][0]["models"].append(model_entry)

        # Determine output path
        if not output_path:
            output_path = os.path.expanduser("~/.config/raycast/ai/providers.yaml")

        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Write the config to file
            with open(output_path, "w") as file:
                yaml.dump(
                    config, file, default_flow_style=False, indent=2, sort_keys=False
                )

            return {
                "success": True,
                "config_path": output_path,
                "model_count": len(config["providers"][0]["models"]),
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to write config file: {str(e)}"}

    def update_raycast_config(self) -> Dict[str, Any]:
        """Updates the Raycast configuration with the latest Venice AI models.

        This method first verifies the API key stored in the verifier and
        then proceeds to generate and save the `providers.yaml` file in
        the default Raycast location.

        Returns:
            A dictionary confirming the result of the update operation.
        """
        if not self.verifier.api_key:
            return {
                "success": False,
                "error": "No API key provided or available in environment",
            }

        # First verify the API key
        verification_result = self.verifier.verify_api_key()
        if not verification_result["success"]:
            return verification_result

        # Generate updated config
        output_path = os.path.expanduser("~/.config/raycast/ai/providers.yaml")
        return self.generate_raycast_config(output_path=output_path)


class VeniceAIImageGenerator:
    """Handles interaction with Venice AI's image generation and upscaling APIs.

    This class provides a high-level interface for generating images,
    upscaling existing images, and listing available models. It is
    pre-configured with defaults suitable for uncensored image generation.

    Attributes:
        api_key (str): The Venice AI API key.
        base_url (str): The base URL for the Venice AI API.
        gen_endpoint (str): The endpoint for image generation.
        upscale_endpoint (str): The endpoint for image upscaling.
        default_model (str): The default model ID for generation.
        default_steps (int): The default number of inference steps.
        default_cfg (float): The default CFG scale.
        default_negative (str): The default negative prompt.
        default_safe_mode (bool): The default safe mode setting.
        aspect_to_size (Dict[str, Tuple[int, int]]): A mapping of aspect
            ratio names to pixel dimensions.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initializes the VeniceAIImageGenerator.

        Args:
            api_key: The Venice AI API key. If not provided, it will be
                retrieved from the `VENICE_API_KEY` environment variable.

        Raises:
            ValueError: If no API key is provided.
        """
        self.api_key = api_key or os.environ.get("VENICE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided. Use api_key parameter or set VENICE_API_KEY environment variable."
            )

        self.base_url = "https://api.venice.ai/api/v1"
        self.gen_endpoint = f"{self.base_url}/image/generate"
        self.upscale_endpoint = f"{self.base_url}/image/upscale"

        # Default settings for uncensored generation
        self.default_model = "lustify-sdxl"  # Uncensored model
        self.default_steps = 50  # Appropriate for lustify-sdxl model
        self.default_cfg = 5.0
        self.default_negative = ""  # Empty negative prompt for uncensored results
        self.default_safe_mode = False  # Disable safe mode for uncensored generation

        # Aspect ratio to dimensions mapping
        self.aspect_to_size = {
            "square": (1024, 1024),
            "tall": (768, 1024),
            "wide": (1024, 768),
        }

    def _session(self, timeout_connect=10, timeout_read=120) -> requests.Session:
        """Creates a requests session with retry logic and timeout handling.

        Returns:
            A `requests.Session` object configured with retry logic.
        """
        s = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        )
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.mount("http://", HTTPAdapter(max_retries=retry))
        s.headers.update(
            {
                "User-Agent": "qwen-cli-venice-integration/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        return s

    def _with_timeouts(self, func, timeouts: Tuple[int, int]):
        """Adds a timeout wrapper to a request function.

        Args:
            func: The request function to wrap.
            timeouts: A tuple of (connect_timeout, read_timeout) in seconds.

        Returns:
            A wrapper function that adds timeout handling to the request.
        """

        def wrapper(method, url, **kwargs):
            """Wrapper function that applies timeouts and rate limiting to requests.

            Args:
                method: HTTP method (GET, POST, etc.).
                url: The URL to make the request to.
                **kwargs: Additional keyword arguments for the request.

            Returns:
                The response from the wrapped request function.
            """
            timeout = kwargs.pop("timeout", (timeouts[0], timeouts[1]))
            time.sleep(random.uniform(0, 0.05))
            return func(method, url, timeout=timeout, **kwargs)

        return wrapper

    def _size_from_aspect(self, aspect: str) -> Tuple[int, int]:
        """Gets pixel dimensions from a named aspect ratio.

        Args:
            aspect: The name of the aspect ratio (e.g., "square").

        Returns:
            A tuple containing the width and height in pixels.

        Raises:
            ValueError: If the aspect ratio name is invalid.
        """
        if aspect not in self.aspect_to_size:
            raise ValueError(
                f"Invalid aspect ratio: {aspect}. Choose from {list(self.aspect_to_size)}"
            )
        return self.aspect_to_size[aspect]

    def _ensure_dir(self, p: pathlib.Path) -> None:
        """Ensures that a directory exists, creating it if necessary.

        Args:
            p: A `pathlib.Path` object representing the directory.
        """
        p.mkdir(parents=True, exist_ok=True)

    def _now_iso(self) -> str:
        """Gets the current time in UTC ISO 8601 format.

        Returns:
            A string representing the current time (e.g., "2023-10-27T10:00:00Z").
        """
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _save_bytes(self, path: pathlib.Path, data: bytes) -> None:
        """Saves a byte string to a file atomically.

        Writes to a temporary `.part` file first and then renames it to
        the final destination to prevent partial file writes.

        Args:
            path: The destination `pathlib.Path` for the file.
            data: The byte string to save.
        """
        self._ensure_dir(path.parent)
        tmp = path.with_suffix(path.suffix + ".part")
        with open(tmp, "wb") as f:
            f.write(data)
        tmp.replace(path)

    def _decode_image_from_json(self, payload: Dict[str, Any]) -> bytes:
        """Decodes a base64-encoded image from a JSON response payload.

        Args:
            payload: The JSON response dictionary from the API.

        Returns:
            The decoded image as a byte string.

        Raises:
            KeyError: If no image data is found in the payload.
        """
        if "image" in payload and isinstance(payload["image"], str):
            return base64.b64decode(payload["image"])
        if (
            "images" in payload
            and isinstance(payload["images"], list)
            and payload["images"]
        ):
            return base64.b64decode(payload["images"][0])
        raise KeyError("No image data found in response JSON.")

    def _is_binary_image_response(self, resp: requests.Response) -> bool:
        """Checks if a response object contains a binary image.

        Args:
            resp: The `requests.Response` object.

        Returns:
            True if the `Content-Type` header starts with "image/",
            False otherwise.
        """
        ctype = resp.headers.get("Content-Type", "")
        return ctype.startswith("image/")

    def _sha256(self, data: bytes) -> str:
        """Calculates the SHA256 hash of a byte string.

        Args:
            data: The byte string to hash.

        Returns:
            The hexadecimal SHA256 hash string.
        """
        return hashlib.sha256(data).hexdigest()

    def _effective_dims(
        self, aspect: str, width: Optional[int], height: Optional[int]
    ) -> Tuple[int, int]:
        """Determines the effective dimensions for image generation.

        If width and height are provided, they are used directly. Otherwise,
        the dimensions are derived from the specified aspect ratio name.

        Args:
            aspect: The name of the aspect ratio.
            width: The desired width in pixels.
            height: The desired height in pixels.

        Returns:
            A tuple containing the effective width and height.
        """
        if width and height:
            return int(width), int(height)
        return self._size_from_aspect(aspect)

    def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "tall",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_format: str = "png",
        image_style: Optional[str] = None,
        hide_watermark: bool = True,
        embed_exif: bool = False,
        safe_mode: Optional[bool] = None,
        auto_upscale: bool = True,
        upscale_scale: int = 4,
        upscale_enhance: bool = True,
        upscale_creativity: float = 0.15,
        upscale_replication: float = 0.35,
        upscale_prompt: Optional[str] = None,
        output_dir: str = "generated",
        output_name: Optional[str] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Generates an image using the Venice AI API.

        This method sends a request to the Venice AI image generation
        endpoint with a wide range of customizable parameters. It handles
        saving the generated image and its metadata to disk and can
        optionally trigger an automatic upscaling process.

        Args:
            prompt: The main text prompt for image generation.
            model: The specific model to use (e.g., 'lustify-sdxl').
                Defaults to the class's `default_model`.
            aspect_ratio: The desired aspect ratio ('square', 'tall', 'wide').
            width: An optional explicit width to override aspect ratio.
            height: An optional explicit height to override aspect ratio.
            steps: The number of inference steps.
            cfg_scale: The Classifier-Free Guidance scale.
            negative_prompt: A prompt describing what to avoid in the image.
            seed: A specific seed for reproducibility.
            output_format: The desired image format ('png' or 'webp').
            image_style: A style preset to apply.
            hide_watermark: If True, requests the API to hide watermarks.
            embed_exif: If True, requests EXIF metadata embedding.
            safe_mode: If True, enables content safety filtering.
            auto_upscale: If True, automatically upscale the generated image.
            upscale_scale: The factor by which to upscale the image (e.g., 4).
            upscale_enhance: If True, enhances details during upscaling.
            upscale_creativity: The creativity level for enhancement.
            upscale_replication: The replication factor for upscaling.
            upscale_prompt: An optional prompt to guide the enhancement.
            output_dir: The directory where generated files will be saved.
            output_name: A custom base name for the output files.
            verbose: If True, prints detailed progress to stderr.

        Returns:
            A dictionary containing the results of the operation, including
            paths to the generated image and metadata files, checksums, and
            any upscaling results.
        """
        # Set defaults if not provided
        model = model or self.default_model
        steps = steps or self.default_steps
        cfg_scale = cfg_scale or self.default_cfg
        negative_prompt = negative_prompt or self.default_negative
        safe_mode = safe_mode if safe_mode is not None else self.default_safe_mode

        if verbose:
            print(f"Generating image with prompt: '{prompt}' using model: {model}")

        # Get dimensions
        w, h = self._effective_dims(aspect_ratio, width, height)

        # Create the session and request
        s = self._session()
        data: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": w,
            "height": h,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "format": output_format,
            "hide_watermark": hide_watermark,
            "embed_exif_metadata": embed_exif,
            "safe_mode": safe_mode,  # Explicitly disable for uncensored generation
        }

        if seed is not None:
            data["seed"] = seed
        if image_style and image_style.lower() != "none":
            data["style_preset"] = image_style

        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = s.post(self.gen_endpoint, headers=headers, json=data)
        req_id = resp.headers.get("x-request-id") or resp.headers.get("X-Request-ID")

        try:
            resp.raise_for_status()
        except requests.HTTPError:
            err = {"status": resp.status_code, "text": resp.text, "request_id": req_id}
            try:
                err["json"] = resp.json()
            except Exception:
                pass
            raise requests.HTTPError(json.dumps(err)) from None

        # Handle the response
        if self._is_binary_image_response(resp):
            b = resp.content
            result = {}
        else:
            result = resp.json()
            # Extract image data from JSON response
            images_b64: List[str] = []
            if "images" in result and isinstance(result["images"], list):
                images_b64 = [img for img in result["images"] if isinstance(img, str)]
            elif "image" in result and isinstance(result["image"], str):
                images_b64 = [result["image"]]
            else:
                raise KeyError("No images found in generation response.")

            if not images_b64:
                raise ValueError("No image generated.")

            # Decode the first image
            b = base64.b64decode(images_b64[0])
        output = {"bytes": b, "meta": {"response": result, "request_id": req_id}}

        if verbose:
            print(
                f"[gen] got {len(b)} bytes (sha256={self._sha256(b)[:12]})",
                file=sys.stderr,
            )

        # Save the generated image
        out_dir = pathlib.Path(output_dir).resolve()
        upscaled_dir = out_dir / "upscaled"
        meta_dir = out_dir / "metadata"
        self._ensure_dir(out_dir)
        self._ensure_dir(upscaled_dir)
        self._ensure_dir(meta_dir)

        # Create filename
        ts_short = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        seed_tag = f"s{seed}" if seed is not None else "rnd"
        stem = f"{output_name or 'venice_image'}_{seed_tag}_{ts_short}_1"
        img_path = out_dir / f"{stem}.{output_format}"

        # Save image
        self._save_bytes(img_path, b)
        sha = self._sha256(b)

        # Create metadata
        meta_payload = {
            "timestamp": self._now_iso(),
            "mode": "generate",
            "request_params": {
                "prompt": prompt,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "width": w,  # Store actual resolved width
                "height": h,  # Store actual resolved height
                "steps": steps,
                "cfg_scale": cfg_scale,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "output_format": output_format,
                "image_style": image_style,
                "hide_watermark": hide_watermark,
                "embed_exif": embed_exif,
                "safe_mode": safe_mode,
            },
            "response_meta": output.get("meta", {}),
            "output_sha256": sha,
            "output_path": str(img_path),
        }

        # Save metadata
        meta_path = meta_dir / f"{stem}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, ensure_ascii=False, indent=2)

        result_dict = {
            "success": True,
            "generated_image_path": str(img_path),
            "metadata_path": str(meta_path),
            "image_sha256": sha,
            "request_id": req_id,
            "response_data": result,
        }

        # Upscale if requested
        if auto_upscale:
            try:
                up_bytes, up_meta = self.upscale_image_bytes(
                    b,
                    scale=upscale_scale,
                    enhance=upscale_enhance,
                    enhance_creativity=upscale_creativity,
                    enhance_prompt=upscale_prompt,
                    replication=upscale_replication,
                    verbose=verbose,
                )

                up_path = upscaled_dir / f"{stem}_upscaled.{output_format}"
                self._save_bytes(up_path, up_bytes)
                up_sha = self._sha256(up_bytes)

                up_meta_payload = {
                    "timestamp": self._now_iso(),
                    "mode": "upscale_post_gen",
                    "source_image": str(img_path),
                    "upscale_params": {
                        "scale": upscale_scale,
                        "enhance": upscale_enhance,
                        "creativity": upscale_creativity,
                        "replication": upscale_replication,
                        "enhance_prompt": upscale_prompt,
                    },
                    "response_meta": up_meta,
                    "output_sha256": up_sha,
                    "output_path": str(up_path),
                }

                up_meta_path = meta_dir / f"{stem}_upscaled.json"
                with open(up_meta_path, "w", encoding="utf-8") as f:
                    json.dump(up_meta_payload, f, ensure_ascii=False, indent=2)

                result_dict["upscaled_image_path"] = str(up_path)
                result_dict["upscaled_metadata_path"] = str(up_meta_path)
                result_dict["upscaled_image_sha256"] = up_sha

                if verbose:
                    print(f"Upscaled → {up_path}")

            except Exception as e:
                if verbose:
                    print(f"Warning: Upscaling failed: {e}", file=sys.stderr)
                result_dict["upscale_error"] = str(e)

        if verbose:
            print(f"Generated → {img_path}")

        return result_dict

    def upscale_image_bytes(
        self,
        image_bytes: bytes,
        scale: int = 4,
        enhance: bool = True,
        enhance_creativity: float = 0.15,
        enhance_prompt: Optional[str] = None,
        replication: float = 0.35,
        verbose: bool = False,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Upscales an image provided as a byte string.

        Args:
            image_bytes: The raw bytes of the image to upscale.
            scale: The factor by which to upscale (e.g., 4).
            enhance: If True, enhances details during upscaling.
            enhance_creativity: The creativity level for enhancement.
            enhance_prompt: An optional prompt to guide the enhancement.
            replication: The replication factor for upscaling.
            verbose: If True, prints detailed progress to stderr.

        Returns:
            A tuple containing the upscaled image as bytes and a
            dictionary of the response metadata.
        """
        s = self._session()
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
        data: Dict[str, Any] = {
            "image": img_b64,
            "scale": scale,
            "enhance": enhance,
            "enhanceCreativity": enhance_creativity,
            "replication": replication,
        }
        if enhance_prompt:
            data["enhancePrompt"] = enhance_prompt

        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = s.post(self.upscale_endpoint, headers=headers, json=data)
        req_id = resp.headers.get("x-request-id") or resp.headers.get("X-Request-ID")

        try:
            resp.raise_for_status()
        except requests.HTTPError:
            err = {"status": resp.status_code, "text": resp.text, "request_id": req_id}
            try:
                err["json"] = resp.json()
            except Exception:
                pass
            raise requests.HTTPError(json.dumps(err)) from None

        if self._is_binary_image_response(resp):
            up_bytes, payload = (
                resp.content,
                {"binary": True, "status_code": resp.status_code, "request_id": req_id},
            )
        else:
            payload = resp.json()
            up_bytes = self._decode_image_from_json(payload)
            payload["request_id"] = req_id

        if verbose:
            print(
                f"[upscale] got {len(up_bytes)} bytes (sha256={self._sha256(up_bytes)[:12]})",
                file=sys.stderr,
            )

        return up_bytes, payload

    def upscale_image_file(
        self,
        image_path: str,
        output_path: Optional[pathlib.Path] = None,
        scale: int = 4,
        enhance: bool = True,
        enhance_creativity: float = 0.15,
        enhance_prompt: Optional[str] = None,
        replication: float = 0.35,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Upscales an image from a file path.

        This method reads an image file, sends its content to the upscaling
        API, and saves the result to a new file.

        Args:
            image_path: The path to the local image file to upscale.
            output_path: The path to save the upscaled image. If not
                provided, a new name is generated based on the input path.
            scale: The factor by which to upscale (e.g., 4).
            enhance: If True, enhances details during upscaling.
            enhance_creativity: The creativity level for enhancement.
            enhance_prompt: An optional prompt to guide the enhancement.
            replication: The replication factor for upscaling.
            verbose: If True, prints detailed progress to stderr.

        Returns:
            A dictionary containing the results of the operation, including
            paths to the input and output files and their checksums.
        """
        # Read the input image
        with open(image_path, "rb") as f:
            raw = f.read()

        # Upscale
        up_bytes, up_meta = self.upscale_image_bytes(
            raw,
            scale,
            enhance,
            enhance_creativity,
            enhance_prompt,
            replication,
            verbose,
        )

        # Determine output path
        if output_path is None:
            path_obj = pathlib.Path(image_path)
            output_path = path_obj.with_name(
                f"{path_obj.stem}_upscaled{path_obj.suffix}"
            )

        # Save upscaled image
        with open(output_path, "wb") as f:
            f.write(up_bytes)

        result = {
            "success": True,
            "input_path": image_path,
            "output_path": output_path,
            "input_sha256": self._sha256(raw),
            "output_sha256": self._sha256(up_bytes),
            "request_id": up_meta.get("request_id"),
            "response_meta": up_meta,
        }

        if verbose:
            print(f"Upscaled image → {output_path}")

        return result

    def list_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lists all available models and a filtered list of uncensored models.

        This method makes a single API call to fetch all models and then
        filters them locally to provide a list of uncensored models.

        Returns:
            A dictionary with two keys:
            - 'all_models': A list of all available models.
            - 'uncensored_models': A filtered list of uncensored models.
            Returns a dictionary with empty lists if the request fails.
        """
        temp_verifier = VeniceAIVerifier(self.api_key)
        result = temp_verifier.fetch_models()

        if not result["success"]:
            print(f"Error listing models: {result.get('error', 'Unknown error')}")
            return {"all_models": [], "uncensored_models": []}

        all_models = result["models"]
        uncensored_keywords = ["uncensored", "lustify", "lustify-sdxl"]
        uncensored_models = []

        for model in all_models:
            model_id = model.get("id", "").lower()
            model_name = model.get("model_spec", {}).get("name", "").lower()
            if any(
                keyword in model_id or keyword in model_name
                for keyword in uncensored_keywords
            ):
                uncensored_models.append(model)

        return {"all_models": all_models, "uncensored_models": uncensored_models}


def main():
    """Main function to test the enhanced Venice AI integration."""
    parser = argparse.ArgumentParser(
        description="Enhanced Venice AI Integration with Verification and Auto-Update"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify the Venice AI API key"
    )
    parser.add_argument(
        "--update-config",
        action="store_true",
        help="Update Raycast configuration with latest models",
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List available Venice AI models"
    )
    parser.add_argument(
        "--api-key", type=str, help="Venice API key (or set VENICE_API_KEY env var)"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Path to save the config file (default: Raycast location)",
    )

    args = parser.parse_args()

    # Initialize the verifier
    try:
        api_key = args.api_key or os.environ.get("VENICE_API_KEY")
        if not api_key:
            print(
                "Error: No API key provided. Use --api-key or set VENICE_API_KEY environment variable.",
                file=sys.stderr,
            )
            return 1

        if args.verify:
            verifier = VeniceAIVerifier(api_key)
            result = verifier.verify_api_key()
            print(json.dumps(result, indent=2))

        elif args.update_config:
            updater = VeniceAIConfigUpdater(api_key)
            result = updater.update_raycast_config()
            print(json.dumps(result, indent=2))

        elif args.list_models:
            verifier = VeniceAIVerifier(api_key)
            result = verifier.fetch_models()
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
