import { sendTelegram } from "../lib/telegram.js";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();

  const { event, wallet, txHash, balance } = req.body;

  let message = `👛 <b>Wallet Event</b>\n\n`;

  switch (event) {
    case "wallet_connected":
      message += `Status: Connected\nWallet: ${wallet}`;
      break;

    case "wallet_disconnected":
      message += `Status: Disconnected\nWallet: ${wallet}`;
      break;

    case "transaction_sent":
      message += `Tx Sent\nWallet: ${wallet}\nHash: ${txHash}`;
      break;

    case "transaction_signed":
      message += `Tx Signed\nWallet: ${wallet}\nHash: ${txHash}`;
      break;

    case "balance_update":
      message += `Balance Check\nWallet: ${wallet}\nBalance: ${balance}`;
      break;

    default:
      message += `Event: ${event}`;
  }

  await sendTelegram(message);

  res.status(200).json({ ok: true });
}