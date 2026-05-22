#!/bin/sh
set -eu

echo "Updating iSH packages..."
apk update

echo "Installing Python, pip, FFmpeg, Node.js, and certificates..."
apk add --no-cache python3 py3-pip ffmpeg nodejs ca-certificates

echo "Installing yt-dlp..."
python3 -m pip install --break-system-packages -U yt-dlp

mkdir -p "$HOME/bin"
mkdir -p "$HOME/Documents/YouTube WAV"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cp "$SCRIPT_DIR/ytwav.py" "$HOME/bin/ytwav.py"

cat > "$HOME/bin/ytwav" <<'SH'
#!/bin/sh
python3 "$HOME/bin/ytwav.py" "$@"
SH
chmod +x "$HOME/bin/ytwav" "$HOME/bin/ytwav.py"

PROFILE="$HOME/.profile"
touch "$PROFILE"
if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$PROFILE"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE"
fi

echo ""
echo "Done."
echo "Restart iSH or run:"
echo '  export PATH="$HOME/bin:$PATH"'
echo ""
echo "Usage:"
echo '  ytwav "https://www.youtube.com/watch?v=..."'
