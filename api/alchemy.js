import { sendTelegram } from "../lib/telegram.js";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();

  const data = req.body;

  const message = `
🔗 <b>Alchemy Event</b>

Type: ${data.event?.activity?.type || "Unknown"}
From: ${data.event?.activity?.fromAddress || "N/A"}
To: ${data.event?.activity?.toAddress || "N/A"}
Hash: ${data.event?.activity?.hash || "N/A"}
Network: ${data.network || "Unknown"}
`;

  await sendTelegram(message);

  res.status(200).json({ ok: true });
}