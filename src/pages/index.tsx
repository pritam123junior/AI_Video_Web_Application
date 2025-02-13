// /pages/index.tsx
import { SignUp } from "@clerk/nextjs";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function Home() {
  const { isLoaded, userId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && userId) {
      router.push("/dashboard");
    }
  }, [isLoaded, userId, router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-purple-600 text-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Welcome to AI Video Generator</h1>
        <p className="mt-4 text-lg">
          Sign in to upload images, write prompts, and generate AI-powered videos!
        </p>
        <div className="mt-10">
       
        </div>
      </div>
    </div>
  );
}
