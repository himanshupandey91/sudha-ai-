#!/usr/bin/env bash

set -e

echo "=== Sudha AI: Building whisper.cpp ==="

if [ -d "whisper.cpp" ]; then
    echo "whisper.cpp directory already exists."
else
    git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git
fi

cd whisper.cpp

cmake -B build

cmake --build build --config Release -j2

echo "=== whisper.cpp build completed ==="

if [ -f "build/bin/whisper-cli" ]; then
    echo "whisper-cli found:"
    build/bin/whisper-cli --help | head -n 5
else
    echo "ERROR: whisper-cli was not found."
    exit 1
fi
