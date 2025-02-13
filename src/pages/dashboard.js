import { useState } from "react";
import axios from "axios";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/router";
import { useEffect } from "react";
import UploadForm from '../components/UploadForm';
export default function Dashboard() {
  const { isLoaded, userId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !userId) {
      router.push("/sign-in");
    }
  }, [isLoaded, userId, router]);

  if (!isLoaded || !userId) {
    return <div>Loading...</div>; // Show a loading screen while checking auth
  }

 
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [generatedVideos, setGeneratedVideos] = useState([]);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleGenerate = async () => {
    if (!image || !prompt) {
      alert("Please upload an image and enter a prompt.");
      return;
    }

    setLoading(true);

    try {
      // Step 1: Upload Image
      const formData = new FormData();
      formData.append("image", image);

      const uploadResponse = await axios.post("/api/upload-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const imagePath = uploadResponse.data.imagePath;

      // Step 2: Generate Video
      const generateResponse = await axios.post("/api/generate-video", {
        userId: "current-user-id", // Replace with Clerk user ID
        prompt,
        imagePath,
      });

      setGeneratedVideos((prev) => [generateResponse.data.video, ...prev]);
      alert("Video generated successfully!");
    } catch (error) {
      console.error("Error generating video:", error);
      alert("Failed to generate video.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-center text-blue-600">AI Video Generator</h1>
        <p className="mt-2 text-center text-gray-500">
          Upload an image and describe the action you'd like to see (e.g., "hugging" or "kissing").
        </p>

        <div className="mt-6">
          <div className="flex flex-col space-y-4">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="block w-full text-sm text-gray-600 border border-gray-300 rounded-md file:mr-4 file:py-2 file:px-4 file:border-0 file:text-sm file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
            />

            <input
              type="text"
              placeholder="Enter prompt (e.g., hugging, kissing)"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            />

            <button
              onClick={handleGenerate}
              className="w-full p-3 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition"
              disabled={loading}
            >
              {loading ? "Generating..." : "Generate Video"}
            </button>
          </div>
        </div>

        <div className="mt-10">
          <h2 className="text-xl font-bold text-gray-700">Generated Videos</h2>
          <div className="mt-4 space-y-6">
            {generatedVideos.length > 0 ? (
              generatedVideos.map((video) => (
                <div key={video.id} className="bg-gray-50 p-4 rounded-md shadow">
                  <h3 className="text-lg font-semibold">{video.prompt}</h3>
                  <video controls className="mt-2 w-full">
                    <source src={video.video_url} type="video/mp4" />
                  </video>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No videos generated yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
