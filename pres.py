import cv2
from PIL import Image

cap = cv2.VideoCapture(r"c:\Users\howec\Documents\IMG_7259.MP4")
ok, firstFrame = cap.read()
if not ok:
    raise SystemExit

x, y, w, h = map(int, cv2.selectROI("", firstFrame, False, False))
cv2.destroyAllWindows()

fps = cap.get(cv2.CAP_PROP_FPS)
stepFrames = int(fps * 5)

prevGray = None
pages = []
frameId = 0

while True:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameId)
    ok, frame = cap.read()
    if not ok:
        break

    crop = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    same = False
    if prevGray is not None:
        score = cv2.matchTemplate(gray, prevGray, cv2.TM_CCOEFF_NORMED).max()
        same = score >= 0.995

    if not same:
        pages.append(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
        prevGray = gray

    frameId += stepFrames

cap.release()

if pages:
    pages[0].save("slides.pdf", save_all=True, append_images=pages[1:])
print("Готово: slides.pdf, страниц:", len(pages))