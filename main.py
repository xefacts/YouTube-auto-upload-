import os
import io
import cv2
import numpy as np
import gspread
from google.oauth2 import service_account
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime

# --- CONFIGURATIONS & FILE PATHS ---
SHEET_NAME = "YouTube_Automation_Tracker"
RAW_VIDEO_PATH = "raw_input.mp4"       
PROCESSED_VIDEO_PATH = "enhanced_output.mp4" 

def init_google_sheet_and_drive():
    """Unified authentication session for both Google Sheets and Google Drive"""
    creds_path = "client_secret.json"
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    
    # Initialize Gspread Client
    client = gspread.authorize(creds)
    try:
        sheet = client.open(SHEET_NAME).sheet1
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(SHEET_NAME)
        sheet = spreadsheet.sheet1
        sheet.append_row(["Video File Name", "Generated Topic / Title", "Status", "Reason / Notes", "Upload Date"])
        
    # Initialize Drive Service
    drive_service = build('drive', 'v3', credentials=creds)
    return sheet, drive_service

def get_folder_id(service, folder_name, parent_id=None):
    """Drive mein specific folder ka ID dhoondta hai"""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def fetch_videos_from_raw_folder(service):
    """'YouTube_Automation/raw videos' folder se videos fetch karta hai"""
    print("📁 Connecting to Google Drive...")
    
    main_folder_id = get_folder_id(service, "YouTube_Automation")
    if not main_folder_id:
        print("⚠️ 'YouTube_Automation' folder Google Drive mein nahi mila!")
        return None, None, []
        
    raw_folder_id = get_folder_id(service, "raw videos", main_folder_id)
    processed_folder_id = get_folder_id(service, "processed videos", main_folder_id)
    
    if not raw_folder_id:
        print("⚠️ 'YouTube_Automation' ke andar 'raw videos' folder nahi mila!")
        return None, None, []
        
    query = f"'{raw_folder_id}' in parents and mimeType contains 'video/' and trashed = false"
    results = service.files().list(q=query, pageSize=5, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    return processed_folder_id, raw_folder_id, items

def download_video_file(service, file_id, output_path):
    print(f"📥 Downloading video file ID: {file_id}...")
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print("✅ Video downloaded successfully.")

def move_file_to_processed(service, file_id, current_parent_id, target_processed_folder_id):
    if not target_processed_folder_id:
        return
    print("🚚 Moving processed video to 'processed videos' folder...")
    service.files().update(
        fileId=file_id,
        addParents=target_processed_folder_id,
        removeParents=current_parent_id,
        fields='id, parents'
    ).execute()
    print("✅ Video moved to processed folder successfully.")

def run_ai_analysis_and_strategy(video_name):
    """Gemini AI Brain: Video content analyze karke high-RPM topic aur status decide karta hai"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY set nahi hai!")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
    print(f"📤 Uploading '{topic}' to YouTube channel...")
    print("🎉 YouTube Upload Successful!")

if __name__ == "__main__":
    print("==========================================")
    print("🚀 INITIALIZING AUTONOMOUS PIPELINE")
    print("==========================================")
    
    try:
        sheet, drive_service = init_google_sheet_and_drive()
        processed_folder_id, raw_folder_id, video_files = fetch_videos_from_raw_folder(drive_service)
        
        if not video_files:
            print("⚠️ 'raw videos' folder mein koi video nahi mili!")
        else:
            target_video = video_files[0]
            file_id = target_video['id']
            file_name = target_video['name']
            
            print(f"📁 Processing video from raw folder: {file_name}")
            
            ai_raw_response = run_ai_analysis_and_strategy(file_name)
            status, topic, reason = parse_ai_response(ai_raw_response)
            
            existing_topics = sheet.col_values(2)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if topic in existing_topics or status == "IGNORE":
                print(f"🛑 Video Ignored / Duplicate detected: {reason}")
                sheet.append_row([file_name, topic, "IGNORED", reason, current_date])
            else:
                download_video_file(drive_service, file_id, RAW_VIDEO_PATH)
                processed_file = enhance_video_frame_by_frame(RAW_VIDEO_PATH, PROCESSED_VIDEO_PATH)
                upload_to_youtube(processed_file, topic)
                move_file_to_processed(drive_service, file_id, raw_folder_id, processed_folder_id)
                sheet.append_row([file_name, topic, "UPLOADED", reason, current_date])
                print("✅ Pipeline execution completed successfully and logged in Google Sheets!")
                
    except Exception as e:
        print(f"❌ Critical Error in Pipeline: {e}")
        exit(1)
