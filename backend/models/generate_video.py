import torch
import torchvision.transforms as transforms
from PIL import Image, ImageDraw
import cv2
import numpy as np
from train_model import MobileNetV3Classifier


# Load classifier
def load_model():
    model = MobileNetV3Classifier(num_classes=101)  # Adjust to UCF101 classes
    model.load_state_dict(torch.load("./backend/models/video_classifier.pth"))  # Update path if needed
    model.eval()
    return model


def generate_video(image_path, output_path, prompt):
    model = load_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

    # Load input image
    image = Image.open(image_path).convert('RGB')
    input_image = np.array(image.resize((100, 100)))  # Resizing input image for animation

    # Predict action class
    transformed_image = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(transformed_image)
        action_class = torch.argmax(output, dim=1).item()

    print(f"Predicted Action: {action_class}")

    # Prepare video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 10, (224, 224))

    # Generate frames
    for frame_num in range(30):  # Generate a 3-second video at 10 FPS
        frame = np.zeros((224, 224, 3), dtype=np.uint8)  # Blank frame

        # Calculate position for the moving image
        x_offset = (frame_num * 5) % (224 - 100)
        y_offset = (frame_num * 3) % (224 - 100)

        # Place the input image onto the frame
        frame[y_offset:y_offset+100, x_offset:x_offset+100] = input_image

        # Convert to PIL for text overlay
        frame_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame_pil)

        # Overlay the prompt and predicted action class using the default font
        draw.text((10, 10), f"Prompt: {prompt}", fill=(255, 255, 255))
        draw.text((10, 200), f"Action: {action_class}", fill=(255, 255, 255))

        # Convert back to NumPy for OpenCV
        frame = np.array(frame_pil)
        out.write(frame)

    out.release()
    print(f"Video saved at {output_path}")


# Main function to run the video generation
if __name__ == "__main__":
    input_image_path = "./public/uploads/input.jpg"  # Path to the input image
    output_video_path = "./public/uploads/generated_video.mp4"  # Path to save the video
    prompt_text = input("Enter a prompt for the video: ")  # Prompt entered by the user
    generate_video(input_image_path, output_video_path, prompt_text)
