import sys
import os
import webbrowser
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# تشخیص مسیر فایل‌ها برای حالت توسعه و حالت اجرایی (EXE)
def get_base_path():
    if getattr(sys, 'frozen', False):
        # اگر برنامه به صورت exe اجرا شده باشد
        return sys._MEIPASS
    else:
        # اگر در حالت عادی پایتون اجرا شده باشد
        return os.path.abspath(".")

BASE_DIR = get_base_path()
BUILD_DIR = os.path.join(BASE_DIR, "frontend", "dist")

app = FastAPI(title="Professional Python React App")

# سرو کردن فایل‌های استاتیک React (فقط اگر بیلد گرفته شده باشند)
if os.path.exists(BUILD_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(BUILD_DIR, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    """
    این تابع تمام درخواست‌ها را به index.html ری‌دایرکت می‌کند
    تا Routing در سمت React (React Router) به درستی کار کند.
    """
    index_path = os.path.join(BUILD_DIR, "index.html")
    
    if not os.path.exists(index_path):
        return {"error": "Frontend build not found. Please run 'npm run build' in the frontend directory."}
    
    # اگر درخواست فایل خاصی باشد (مثل css, js, images) آن را برگردان
    requested_file = os.path.join(BUILD_DIR, full_path)
    if os.path.isfile(requested_file):
        return FileResponse(requested_file)
    
    # در غیر این صورت index.html را برگردان (برای SPA)
    return FileResponse(index_path)

@app.on_event("startup")
async def startup_event():
    # باز کردن خودکار مرورگر در هنگام اجرا (اختیاری)
    # webbrowser.open("http://localhost:8000")
    pass

if __name__ == "__main__":
    # اجرای سرور
    uvicorn.run(app, host="0.0.0.0", port=8000)
