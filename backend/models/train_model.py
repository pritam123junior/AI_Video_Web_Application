import os
import cv2
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm
import numpy as np
# --- Preprocess videos into frames ---
def preprocess_videos(input_path, output_path, frame_size=(320, 240)):
    """Preprocesses videos into frames of a specified size.

    Args:
        input_path (str): Path to the directory containing videos.
        output_path (str): Path to the directory where frames will be saved.
        frame_size (tuple, optional): The desired size (width, height) of the frames. Defaults to (320, 240).
    """

    os.makedirs(output_path, exist_ok=True)
    for class_folder in os.listdir(input_path):
        class_dir = os.path.join(input_path, class_folder)
        if not os.path.isdir(class_dir):
            continue

        for video_file in os.listdir(class_dir):
            video_path = os.path.join(class_dir, video_file)
            if not os.path.isfile(video_path) or not video_file.endswith(('.mp4', '.avi', '.mov')):
                continue

            output_dir = os.path.join(output_path, class_folder, os.path.splitext(video_file)[0])
            os.makedirs(output_dir, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame_resized = cv2.resize(frame, frame_size)  # Use frame_size for resizing
                frame_path = os.path.join(output_dir, f'frame_{frame_count:04d}.jpg')
                cv2.imwrite(frame_path, frame_resized)
                frame_count += 1
            cap.release()
            print(f"Processed {frame_count} frames from {video_file}")

# --- Define ImprovedGAN ---
class ImprovedGAN(nn.Module):
    """Improved Generative Adversarial Network (GAN) architecture.

    Args:
        latent_dim (int, optional): Dimensionality of the latent space. Defaults to 100.
        img_size (tuple, optional): Size (width, height) of the generated images. Defaults to (320, 240).
    """


    def __init__(self, latent_dim=100, img_size=(320, 240)):
        super(ImprovedGAN, self).__init__()
        self.latent_dim = latent_dim
        self.img_size = img_size  # Ensure img_size is a tuple

        # Calculate input size dynamically using NumPy (if necessary)
        input_size = int(np.prod(self.img_size)) * 3  # Calculate total number of elements for image (width * height * channels)

        self.generator = nn.Sequential(
            nn.Linear(self.latent_dim, 512),  # Increased layer size
            nn.ReLU(inplace=True),  # Use inplace=True for efficiency
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, input_size),  # Use calculated input size
            nn.Tanh()
        )

        self.discriminator = nn.Sequential(
            nn.Linear(input_size, 512),  # Increased layer size (use calculated input size)
            nn.LeakyReLU(0.2, inplace=True),  # Use inplace=True for efficiency
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),  # Use inplace=True for efficiency
            nn.Linear(256, 1),
            nn.Sigmoid()
        )


    def generate(self, z):
        return self.generator(z).view(-1, 3, *self.img_size)  # Use *img_size for dynamic shape

    def discriminate(self, x):
        return self.discriminator(x.view(x.size(0), -1))
# --- Main Script ---
if __name__ == '__main__':
    # --- Setup Device ---
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # --- Preprocess Videos ---
    input_videos_path = r"C:\Users\RGON\Documents\Dataset\UCF-101"
    output_frames_path = r"C:\Users\RGON\Documents\Dataset\processed_frames"  # New output directory
    if not os.path.exists(output_frames_path):
        preprocess_videos(input_videos_path, output_frames_path)

    # --- Define Dataset and DataLoader ---
    transform = transforms.Compose([
        transforms.Resize((320, 240)),  # Increased to 96
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    dataset = datasets.ImageFolder(output_frames_path, transform=transform)
    print(f"Dataset size: {len(dataset)}")

    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=4, pin_memory=True)

    # --- Initialize Model ---
    model = ImprovedGAN(img_size=(320, 240)).to(device)  # Pass img_size=96 to the constructor
    optimizer_gen = torch.optim.Adam(model.generator.parameters(), lr=2e-4, betas=(0.5, 0.999))
    optimizer_disc = torch.optim.Adam(model.discriminator.parameters(), lr=2e-4, betas=(0.5, 0.999))
    loss_fn = nn.BCELoss()

    # --- Training Loop ---
    num_epochs = 50
    latent_dim = 100
    save_interval = 5

    for epoch in range(num_epochs):
        model.train()
        total_gen_loss, total_disc_loss = 0.0, 0.0
        real_correct, fake_correct = 0, 0
        total_real, total_fake = 0, 0

        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        with tqdm(total=len(train_loader), desc=f"Epoch {epoch + 1}/{num_epochs}", unit="batch") as pbar:
            for real_frames, _ in train_loader:
                real_frames = real_frames.to(device)
                batch_size = real_frames.size(0)

                # Train Discriminator
                z = torch.randn(batch_size, latent_dim).to(device)
                fake_frames = model.generate(z).detach()
                real_labels = torch.ones(batch_size, 1).to(device)
                fake_labels = torch.zeros(batch_size, 1).to(device)

                real_preds = model.discriminate(real_frames)
                fake_preds = model.discriminate(fake_frames)

                loss_real = loss_fn(real_preds, real_labels)
                loss_fake = loss_fn(fake_preds, fake_labels)
                loss_disc = loss_real + loss_fake

                optimizer_disc.zero_grad()
                loss_disc.backward()
                optimizer_disc.step()

                # Train Generator
                z = torch.randn(batch_size, latent_dim).to(device)
                fake_frames = model.generate(z)
                fake_preds = model.discriminate(fake_frames)
                loss_gen = loss_fn(fake_preds, real_labels)

                optimizer_gen.zero_grad()
                loss_gen.backward()
                optimizer_gen.step()

                # Update losses
                total_gen_loss += loss_gen.item()
                total_disc_loss += loss_disc.item()

                # Accuracy calculations
                real_correct += (real_preds > 0.5).sum().item()
                fake_correct += (fake_preds < 0.5).sum().item()
                total_real += batch_size
                total_fake += batch_size

                # Update progress bar
                pbar.set_postfix({
                    "Gen Loss": f"{loss_gen.item():.4f}",
                    "Disc Loss": f"{loss_disc.item():.4f}"
                })
                pbar.update(1)

            avg_gen_loss = total_gen_loss / len(train_loader)
            avg_disc_loss = total_disc_loss / len(train_loader)

            real_accuracy = 100 * real_correct / total_real if total_real > 0 else 0
            fake_accuracy = 100 * fake_correct / total_fake if total_fake > 0 else 0
            avg_train_accuracy = (real_accuracy + fake_accuracy) / 2

            print(f"Epoch {epoch + 1}/{num_epochs} - Gen Loss: {avg_gen_loss:.4f}, Disc Loss: {avg_disc_loss:.4f}")
            print(f"Training Accuracy - Real: {real_accuracy:.2f}%, Fake: {fake_accuracy:.2f}%, Average: {avg_train_accuracy:.2f}%")

       
        # Save model periodically
        if (epoch + 1) % save_interval == 0:
            torch.save(model.state_dict(), f"gan_model_epoch_{epoch+1}.pth")
            print(f"Model saved at epoch {epoch + 1}")
   