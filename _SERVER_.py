from flask import Flask, request, send_file, render_template_string
import qrcode
import io

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>QR Code Generator</title>
</head>
<body style="font-family:sans-serif; text-align:center; margin-top:50px;">
    <h2>QR Code Generator</h2>
    <form method="get" action="/qr">
        <input type="text" name="urn" placeholder="Enter URN" required
               style="padding:10px; width:200px;">
        <button type="submit" style="padding:10px;">Generate</button>
    </form>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/qr")
def generate_qr():
    urn = request.args.get("urn", "").strip()
    if not urn:
        return " URN missing!", 400

    img = qrcode.make(urn)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
