import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { image } = req.body;
    const uploadPath = path.join(process.cwd(), 'public', 'uploads', `${Date.now()}.png`);
    fs.writeFileSync(uploadPath, Buffer.from(image, 'base64'));
    res.status(200).json({ message: 'Image uploaded successfully', path: uploadPath });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
