import cv2, yt_dlp, io, uvicorn
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/convert")
def convert(req: VideoRequest):
    with yt_dlp.YoutubeDL({"format": "best[ext=mp4]", "quiet": True}) as ydl:
        stream_url = ydl.extract_info(req.url, download=False)["url"]

    cap = cv2.VideoCapture(stream_url)
    ok, firstFrame = cap.read()
    if not ok:
        raise SystemExit

    x, y, w, h = map(int, cv2.selectROI("", firstFrame, False, False, False))
    cv2.destroyAllWindows()

    fps = cap.get(cv2.CAP_PROP_FPS)
    stepFrames = int(fps * 5)
    prevGray, pages, frameId = None, [], 0

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameId)
        ok, frame = cap.read()
        if not ok:
            break
        crop = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        if prevGray is None or cv2.matchTemplate(gray, prevGray, cv2.TM_CCOEFF_NORMED).max() < 0.995:
            pages.append(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
            prevGray = gray
        frameId += stepFrames

    cap.release()
    buf = io.BytesIO()
    pages[0].save(buf, format="PDF", save_all=True, append_images=pages[1:])
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)