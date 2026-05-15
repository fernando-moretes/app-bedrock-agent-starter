#!/usr/bin/env bash
# Build a Lambda deployment package: zip the src/ + runtime dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
DIST="$BUILD/lambda"

rm -rf "$BUILD"
mkdir -p "$DIST"

python -m pip install \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  --target "$DIST" \
  --upgrade \
  boto3 pydantic

cp -r "$ROOT/src/agent" "$DIST/agent"

cd "$DIST"
zip -qr "$BUILD/lambda.zip" .
echo "built: $BUILD/lambda.zip"
