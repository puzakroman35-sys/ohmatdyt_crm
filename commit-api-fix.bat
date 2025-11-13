@echo off
cd ohmatdyt-crm
git add nginx/nginx.prod.conf
cd ..
git add FIX_API_URL_DOUBLE_PREFIX.md
git commit -m "Fix: Remove trailing slash in nginx proxy_pass to preserve /api/ prefix"
git push origin main
git push adelina main
echo Done!
pause
