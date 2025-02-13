import aiGeneration from '../backend/ai_generation';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { images } = req.body;
    try {
      const videoPath = await aiGeneration(images);
      res.status(200).json({ message: 'Video generated successfully', videoPath });
    } catch (error) {
      res.status(500).json({ error: 'Video generation failed' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
