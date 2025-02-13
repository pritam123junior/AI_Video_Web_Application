import { getVideos } from '../backend/db';

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const videos = await getVideos();
      res.status(200).json(videos);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch videos' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
