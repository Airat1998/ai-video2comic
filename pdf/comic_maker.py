from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os


def get_stylized_images(video_path):
    stylized_dir = "/app/data/stylized"
    image_paths = [
        os.path.join(stylized_dir, f)
        for f in sorted(os.listdir(stylized_dir))
        if f.startswith("stylized_") and f.endswith(".png")
    ]
    return image_paths


def make_comic(image_paths, video_path):
    pdf_path = video_path.replace(".mp4", ".pdf").replace(
        "/app/data/", "/app/data/comics_"
    )
    c = canvas.Canvas(pdf_path, pagesize=A4)

    width, height = A4
    margin = 50
    img_w, img_h = 400, 300
    x = margin
    y = height - margin - img_h

    for idx, path in enumerate(image_paths):
        if not os.path.exists(path):
            continue

        try:
            c.drawImage(path, x, y, width=img_w, height=img_h)
        except Exception as e:
            print(f"⚠️ Ошибка вставки изображения {path}: {e}")
            continue

        x += img_w + 20
        if x + img_w > width:
            x = margin
            y -= img_h + 20
            if y < margin:
                c.showPage()
                x = margin
                y = height - margin - img_h

    c.save()
    print(f"📕 PDF сохранён: {pdf_path}")
    return pdf_path
