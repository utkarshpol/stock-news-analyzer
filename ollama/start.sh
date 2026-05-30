#!/bin/sh

ollama serve &

sleep 5

if ! ollama list | grep -q "gemma3:4b"; then
    echo "Downloading gemma3:4b..."
    ollama pull gemma3:4b
fi

wait