import streamlit as st
from fpdf import FPDF
from PIL import Image
import openai
import requests
from io import BytesIO

# OpenAI API Anahtarı
openai.api_key = "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"  # OpenAI API anahtarınızı buraya yapıştırın

# PDF Sınıfı
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", style="B", size=14)
        self.cell(0, 10, "Hikaye ve Görseller PDF", align="C", ln=True)
        self.ln(10)

    def chapter_title(self, chapter_num, title):
        self.set_font("Arial", style="B", size=12)
        self.cell(0, 10, f"Bölüm {chapter_num}: {title}", ln=True)
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_image(self, image_path):
        self.image(image_path, x=10, w=180)
        self.ln(10)

# Hikaye Üretimi
def generate_story(prompt, age_group="Yetişkin"):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Sen bir hikaye anlatıcısısın. Hikaye {age_group} yaş grubuna hitap edecek."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Hikaye üretiminde bir hata oluştu: {e}")
        return None

# Görsel Üretimi
def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        return Image.open(BytesIO(image_response.content))
    except Exception as e:
        st.error(f"Görsel üretiminde bir hata oluştu: {e}")
        return None

# PDF Oluşturma
def create_pdf(story_parts, visual_prompts, output_path="hikaye_ve_gorseller.pdf"):
    pdf = PDF()
    pdf.add_page()

    for i, (part, prompt) in enumerate(zip(story_parts, visual_prompts), start=1):
        pdf.chapter_title(i, f"Bölüm {i}")
        pdf.chapter_body(part)
        image = generate_image(prompt)
        if image:
            temp_image_path = f"temp_image_{i}.jpg"
            image.save(temp_image_path)
            pdf.add_image(temp_image_path)

    pdf.output(output_path)
    return output_path

# Streamlit Arayüzü
st.title("AI Destekli Hikaye ve Görsel PDF Oluşturucu")

# Kullanıcı Girdileri
age_group = st.selectbox("Hikaye hangi yaş grubuna hitap edecek?", ["3-6", "7-12", "13-18", "Yetişkin"])
story_prompt = st.text_area("Hikaye için bir prompt girin:")
visual_style = st.selectbox("Görseller hangi türde oluşturulacak?", ["Çizgi Film", "Karakalem", "Gerçekçi", "Soyut"])

if st.button("Hikaye ve Görselleri Oluştur"):
    if story_prompt.strip():
        with st.spinner("Hikaye oluşturuluyor..."):
            story = generate_story(story_prompt, age_group)
        if story:
            story_parts = story.split("\n\n")  # Hikayeyi paragraflara böl
            visual_prompts = [f"{part[:50]}... Görsel türü: {visual_style}." for part in story_parts]

            with st.spinner("PDF oluşturuluyor..."):
                pdf_path = create_pdf(story_parts, visual_prompts)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="PDF'i İndir",
                    data=f.read(),
                    file_name="hikaye_ve_gorseller.pdf",
                    mime="application/pdf"
                )
    else:
        st.error("Lütfen bir hikaye prompt'u girin!")
