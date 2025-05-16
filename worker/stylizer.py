import os
import cv2
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import CannyDetector
from pdf.comic_maker import make_comic, get_stylized_images

device = "cuda" if torch.cuda.is_available() else "cpu"

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

canny = CannyDetector()

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    safety_checker=None,
    torch_dtype=torch.float16
).to(device)

pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_xformers_memory_efficient_attention()


def stylize_frame(frame_path, output_path):
    print(f"📸 Обработка кадра: {frame_path}")
    image = Image.open(frame_path).convert("RGB")

    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    caption_ids = blip_model.generate(**inputs, max_new_tokens=30)
    caption = blip_processor.decode(caption_ids[0], skip_special_tokens=True)

    np_image = cv2.imread(frame_path)
    canny_map = canny(np_image)
    control_image = Image.fromarray(canny_map)

    result = pipe(
        prompt=f"comic book style, {caption}",
        image=control_image,
        num_inference_steps=30
    )
    result.images[0].save(output_path)
    print(f"✅ Сохранено: {output_path}")


def stylize_video(video_path):
    print(f"🎬 Обработка видео: {video_path}")

    os.makedirs("/app/data/frames", exist_ok=True)
    os.makedirs("/app/data/stylized", exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % 15 == 0:
            original_path = f"/app/data/frames/frame_{frame_id}.png"
            stylized_path = f"/app/data/stylized/stylized_{frame_id}.png"

            cv2.imwrite(original_path, frame)
            stylize_frame(original_path, stylized_path)

        frame_id += 1

    cap.release()

    image_paths = get_stylized_images(video_path)
    pdf_path = make_comic(image_paths, video_path)
    print(f"🎉 Комикс готов: {pdf_path}")
