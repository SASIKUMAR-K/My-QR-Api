from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
import re
import urllib.parse
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)


def is_hex_color(value: str) -> bool:
    """Validate if the provided string is a valid hex color."""
    if re.fullmatch(r'^#[0-9A-Fa-f]{6}$', value):
        return True
    return False


@app.get("/text")
async def generate_qr(
    text: str,
    size: int = Query(default=10, ge=1, le=40),
    fg: str = Query(default="#000000"),  # default black
    bg: str = Query(default="#FFFFFF")   # default white
):
    # Decode hex color values if they are URL encoded
    fg = urllib.parse.unquote(fg)
    bg = urllib.parse.unquote(bg)

    logging.info(f"Received fg color: {fg}")
    logging.info(f"Received bg color: {bg}")

    if not is_hex_color(fg):
        logging.error(f"Invalid fg color: {fg}")
        raise HTTPException(
            status_code=400, detail="Invalid fg hex color value")
    if not is_hex_color(bg):
        logging.error(f"Invalid bg color: {bg}")
        raise HTTPException(
            status_code=400, detail="Invalid bg hex color value")

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color=fg, back_color=bg)

    # Save the image to a BytesIO object
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
