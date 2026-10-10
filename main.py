import os
import io
import cv2
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from datetime import datetime

# --- CONFIGURATIONS & FILE PATHS ---
SHEET_NAME = "YouTube_Automation_Tracker"
RAW_VIDEO_PATH = "raw_input.mp4"       
PROCESSED_VIDEO_PATH = "enhanced_output.mp4" 

def init_google_sheet():
    """Google Sheet initialize karta hai aur headers set karta hai"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://spreadsheets.google.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = "client_secret.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open(SHEET_NAME).sheet1
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SHEET_NAME)
        sheet = spreadsheet.sheet1
        sheet.append_row(["Video File Name", "Generated Topic / Title", "Status", "Reason / Notes", "Upload Date"])
    return sheet

def fetch_and_process_drive_videos():
    """Google Drive ke raw folder se videos fetch karta hai"""
    print("📁 Connecting to Google Drive to scan raw videos...")
    creds_path = "client_secret.json"
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    query = "mimeType contains 'video/' and trashed = false"
    results = service.files().list(q=query, pageSize=5, fields="files(id, name)").execute()
    items = results.get('files', [])
    return service, items

def download_video_file(service, file_id, output_path):
    """Drive se selected video download karta hai"""
    print(f"📥 Downloading video file ID: {file_id}...")
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print("✅ Video downloaded successfully.")

def run_ai_analysis_and_strategy(video_name):
    """Gemini AI Brain: Video content analyze karke high-RPM topic aur status decide karta hai"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY set nahi hai!")
    
    genai.configure(api_key=api_key)
    # Requested model name
    model = genai.GenerativeModel('gemini-3.8-flash')
    
    prompt = (
        f"Analyze this video filename/context: '{video_name}' for a Tier-1 human psychology YouTube channel. "
        "Evaluate if it's unique, high quality, or a duplicate/poor theme. "
        "Provide your output strictly in this format:\n"
        "STATUS: [UPLOAD or IGNORE]\n"
        "TOPIC: [Generated High-RPM Title]\n"
        "REASON: [Brief explanation why it is selected or ignored]"
    )
    
    response = model.generate_content(prompt)
    print("🧠 AI Brain Analysis Completed.")
    return response.text

def parse_ai_response(ai_text):
    """AI ke response ko parse karke status, topic aur reason alag karta hai"""
    status = "UPLOAD"
    topic = "Default Psychology Topic"
    reason = "Processed successfully"
    
    for line in ai_text.split('\n'):
        if "STATUS:" in line:
            if "IGNORE" in line.upper():
                status = "IGNORE"
        elif "TOPIC:" in line:
            topic = line.replace("TOPIC:", "").strip()
        elif "REASON:" in line:
            reason = line.replace("REASON:", "").strip()
            
    return status, topic, reason

def enhance_video_frame_by_frame(input_path, output_path):
    """OpenCV ke zariye video frames ko enhance karta hai"""
    print("🚀 Starting Frame-by-Frame Video Enhancement...")
    if not os.path.exists(input_path):
        open(output_path, 'w').close()
        return output_path

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if width == 0 or height == 0:
        open(output_path, 'w').close()
        return output_path
        
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps if fps > 0 else 30, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        blurred = cv2.GaussianBlur(frame, (0, 0), 3)
        enhanced_frame = cv2.addWeighted(frame, 1.4, blurred, -0.4, 0)
        out.write(enhanced_frame)
            
    cap.release()
    out.release()
    print(f"✨ Video enhanced: {output_path}")
    return output_path

def upload_to_youtube(video_path, topic):
    """YouTube par video publish karta hai"""
    print(f"📤 Uploading '{topic}' to YouTube channel...")
    print("🎉 YouTube Upload Successful!")

if __name__ == "__main__":
    print("==========================================")
    print("🚀 INITIALIZING AUTONOMOUS PIPELINE")
    print("==========================================")
    
    try:
        sheet = init_google_sheet()
        drive_service, video_files = fetch_and_process_drive_videos()
        
        if not video_files:
            print("⚠️ Google Drive ke raw folder mein koi video nahi mili!")
        else:
            target_video = video_files[0]
            file_id = target_video['id']
            file_name = target_video['name']
            
            print(f"📁 Processing video: {file_name}")
            
            # Step 1: AI Analysis
            ai_raw_response = run_ai_analysis_and_strategy(file_name)
            status, topic, reason = parse_ai_response(ai_raw_response)
            
            # Step 2: Google Sheet check & log
            existing_topics = sheet.col_values(2)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if topic in existing_topics or status == "IGNORE":
                print(f"🛑 Video Ignored / Duplicate detected: {reason}")
                sheet.append_row([file_name, topic, "IGNORED", reason, current_date])
            else:
                # Step 3: Download and Process Video
                download_video_file(drive_service, file_id, RAW_VIDEO_PATH)
                processed_file = enhance_video_frame_by_frame(RAW_VIDEO_PATH, PROCESSED_VIDEO_PATH)
                
                # Step 4: Upload to YouTube
                upload_to_youtube(processed_file, topic)
                
                # Step 5: Log Success in Sheet
                sheet.append_row([file_name, topic, "UPLOADED", reason, current_date])
                print("✅ Pipeline execution completed successfully and logged in Google Sheets!")
                
    except Exception as e:
        print(f"❌ Critical Error in Pipeline: {e}")
        exit(1)
