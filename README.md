# ChatGpt-LineBot
1. 在".../ChatGpt-LineBot-main"路徑，Terminal端下指令: pip install -r requirements.txt

I modify vercel.json, origin file code:
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 2400
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
