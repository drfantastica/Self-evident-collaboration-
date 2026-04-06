#!/bin/bash
# ignite — start mlx_lm inference server for OpenClaw
echo "🔥 Starting qwen3:32b via mlx-lm..."
mlx_lm.server --model mlx-community/Qwen3-32B-4bit --port 8080
