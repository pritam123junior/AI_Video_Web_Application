export async function getDizzleData(apiKey) {
    const response = await fetch('https://dizzle.api.endpoint', {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    return response.json();
  }
  