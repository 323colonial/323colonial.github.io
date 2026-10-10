"""PNG request parts without recipe startup or scratch configuration."""
import base64, subprocess


def png_part(path, fit=None):
    data = subprocess.run(['magick', path] + (['-filter', 'Lanczos', '-resize', fit + '!'] if fit else []) + ['png:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(data).decode()}}
