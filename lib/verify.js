export function verifySecret(req) {
  const secret = req.headers["x-webhook-secret"];
  return secret === process.env.WEBHOOK_SECRET;
}