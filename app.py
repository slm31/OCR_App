import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import io
from PIL import Image
import base64 # Required for decorative images/styles

# --- CONFIGURATION AND SETUP ---

# 1. Load Environment Variables (API Key)
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

# Define the absolute path to the unified MP4 audio folder
# ⚠️ IMPORTANT: Verify this path on your system.
AUDIO_FOLDER = "sounds" 

# =======================================================
# UTILITY: MAPPER FUNCTION (Arabic Letter to MP4 File)
# =======================================================
def get_audio_filename(letter: str) -> str | None:
    """
    Maps the Arabic letter identified through pattern matching to the correct .mp4 audio file path.
    Assumes all 36 required files are present and unified to .mp4.
    """
    # 1. Clean the letter returned by the processing engine
    normalized_letter = letter.strip()
    
    # 2. Mapping Dictionary: Arabic Letter -> Base Filename (MP4 extension is added later)
    # This dictionary uses the base filenames matching the 36 available audio files.
    mapping_base = {
        'ع': 'ain', 'ا': 'alif', 'أ': 'alif_hamza_foq', 'إ': 'alif_hamza_taht', 
        'آ': 'alif_madda', 'ى': 'alif_maqsura', 'ب': 'baa', 'ض': 'daad', 
        'د': 'daal', 'ذ': 'dhaal', 'ف': 'faa', 'غ': 'ghain', 
        'ح': 'haa', 'ه': 'hah', 'ء': 'hamza', 'ج': 'jeem', 
        'ك': 'kaaf', 'خ': 'khaa', 'ل': 'laam', 'م': 'meem', 
        'ن': 'noon', 'ق': 'qaaf', 'ر': 'raa', 'ص': 'saad', 
        'س': 'seen', 'ش': 'sheen', 'ط': 'taat', 'ة': 'taa_marbuta', 
        'ت': 'taa', 'ث': 'thaa', 'و': 'waw', 'ؤ': 'waw_hamza', 
        'ي': 'yaa', 'ئ': 'yaa_hamza', 'ظ': 'zaat', 'ز': 'zay',

        # Robust matching for common hamza/yaa forms
        'أ': 'alif_hamza_foq', 'إ': 'alif_hamza_taht', 'ي': 'yaa', 'ئ': 'yaa_hamza',
    }
    
    base_name = mapping_base.get(normalized_letter)
    
    if base_name:
        filename = base_name + '.mp4' 
        full_path = os.path.join(AUDIO_FOLDER, filename)
        
        # Check for file existence
        if os.path.exists(full_path):
            return full_path
    
    return None

# =======================================================
# CORE PROCESSING FUNCTION
# =======================================================
def identify_arabic_letter_from_bytes(image_bytes: bytes, mime_type: str):
    """
    Sends the image data to the processing engine for Arabic letter identification.
    """
    if not API_KEY:
        st.error("❌ خطأ: مفتاح API غير موجود.")
        return "❌ فشل الاتصال"

    try:
        # Note: The underlying function uses Google's multimodal models.
        client = genai.Client(api_key=API_KEY)
        
        # Prompt optimized to return only the single letter (in Arabic)
        prompt = (
            "انظر بدقة إلى الحرف العربي المرسوم في هذه الصورة. مهمتك هي التمييز بين الحروف المتشابهة جداً."
            " **انتبه بشكل خاص** للنقاط (مثل التمييز بين الذال 'ذ' والزاي 'ز')."
            " **يجب أن تكون إجابتك** أحد الأحرف التالية فقط: ا، أ، إ، آ، ى، ب، ت، ث، ج، ح، خ، د، ذ، ر، ز، س، ش، ء، ص، ض، ط، ظ، ع، غ، ف، ق، ك، ل، م، ن، هـ، و، ؤ، ي، ئ، ة." 
            " أجب بالحرف نفسه فقط، بدون أي كلام آخر أو شرح، لضمان المطابقة الآلية الناجحة. على سبيل المثال، إذا كان الحرف هو 'ذ'، أجب بـ 'ذ'."
        )
        
        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt
        ]

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )

        return response.text.strip()
        
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الاتصال بالمعالج: {e}")
        return "❌ فشل المعالجة"

# =======================================================
# STREAMLIT UI DESIGN (Enhanced Arabic Interface)
# =======================================================
st.set_page_config(page_title="مُعرف الحروف العربية (بالمقارنة الآلية)", layout="wide")

# --- CUSTOM PROJECT HEADER ---
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: 'Arial', sans-serif;'>مُعَرِّف الحروف العربية بالنطق </h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #34495E; font-family: 'Arial', sans-serif;'>مشروع التعرف على الأحرف العربية (Arabic OCR)</h3>", unsafe_allow_html=True)

st.divider()

# Project Info (Enhanced Formatting)
st.markdown("<h4 style='text-align: center; color: #28a745;'>عال 430 - تعريب الحاسبات</h4>", unsafe_allow_html=True)

info_cols = st.columns(3)
with info_cols[0]:
    st.markdown("<p style='text-align: center; font-size: 18px;'>👨‍🎓 <b> </b></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #17a2b8; font-weight: bold;'>سلمان الجبرين</p>", unsafe_allow_html=True)
with info_cols[1]:
    st.markdown("<p style='text-align: center; font-size: 18px;'>🧑‍🏫 <b>:إشراف الدكتور</b></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #28a745; font-weight: bold;'>أ.د. عبدالملك السلمان</p>", unsafe_allow_html=True)
with info_cols[2]:
    st.markdown("<p style='text-align: center; font-size: 18px;'>👨‍🎓 <b> </b></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #17a2b8; font-weight: bold;'>فارس الزهراني</p>", unsafe_allow_html=True)

st.divider()

# --- INPUT SECTION ---
st.subheader("📸 إدخال الحرف للمقارنة")
st.markdown("يمكنك رفع صورة مكتوبة بخط اليد أو مطبوعة، أو استخدام كاميرا الجهاز مباشرة:")

input_cols = st.columns(2)

with input_cols[0]:
    uploaded_file = st.file_uploader(
        "1. رفع صورة من الجهاز (PNG أو JPG):", 
        type=["png", "jpg", "jpeg"]
    )

with input_cols[1]:
    camera_image = st.camera_input("2. التقاط صورة مباشرة للحرف:")

# Determine the source image
source_image = camera_image if camera_image is not None else uploaded_file

# --- PROCESSING AND OUTPUT ---

if source_image is not None:
    
    st.divider()
    st.subheader("🔍 نتيجة المقارنة الآلية")
    
    col_img, col_res = st.columns([1, 2])
    
    with col_img:
        st.image(source_image, caption='الصورة المُدخلة', use_container_width=True) # Updated to use_container_width

    with col_res:
        st.info("جاري إرسال الصورة للمقارنة الآلية...")
        
        image_bytes = source_image.getvalue()
        mime_type = f"image/{source_image.type.split('/')[-1]}"
        
        # Run the processing
        with st.spinner('⏳ يرجى الانتظار، المعالج يقوم بمطابقة البيانات...'):
            identified_letter = identify_arabic_letter_from_bytes(image_bytes, mime_type)
        
        # Display Final Result
        st.markdown("### ✅ الحرف المُتعرَّف عليه:")
        
        if identified_letter and identified_letter.startswith('❌'):
            st.error(f"فشل المطابقة: {identified_letter}")
        else:
            st.balloons() 
            st.markdown(f"<p style='font-size: 80px; text-align: center; color: #DC3545; font-weight: bold;'>{identified_letter}</p>", unsafe_allow_html=True)
            st.success(f"تمت المطابقة بنجاح مع الحرف: **{identified_letter}**")
            
            # --- Audio Playback ---
            st.markdown("---")
            st.markdown("### 🔈 نطق الحرف (مطابقة آلية):")
            audio_file_path = get_audio_filename(identified_letter)
            
            if audio_file_path and os.path.exists(audio_file_path):
                # نقرأ الصوت ونحوله Base64
                with open(audio_file_path, "rb") as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
            
                # عنصر HTML يشغل الصوت تلقائيًا (فعليًا)
                audio_html = f"""
                    <audio autoplay>
                        <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                        متصفحك لا يدعم تشغيل الصوت.
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            
            else:
                st.warning(f"⚠️ لم يتم العثور على الملف الصوتي للحرف '{identified_letter}' في مجلد الأصوات.")


else:
    st.info("يرجى رفع أو التقاط صورة للحرف العربي للبدء في عملية المقارنة الآلية.")

st.divider()
st.markdown("<p style='text-align: center; color: #888;'> إن أحسنا فمن الله، وإن أسأنا أو أخطأنا فمن أنفسنا والشيطان. </p>", unsafe_allow_html=True)
