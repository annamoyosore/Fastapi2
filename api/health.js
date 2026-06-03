export default function handler(req, res) {
  res.status(200).json({
    status: "running",
    time: new Date().toISOString()
  });
}