
import streamlit as st
import whisper
import tempfile
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title='Kukuk Assistant', layout='centered')

with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title('🚗 Kukuk Smart Assistant')

uploaded_audio = st.file_uploader('Upload voice note (MP3)', type=['mp3'])
uploaded_image = st.file_uploader('Upload a photo (JPG/PNG)', type=['jpg', 'jpeg', 'png'])
note_text = st.text_area('Write additional notes')

st.markdown('### Inspection Checklist')
moteur = st.checkbox('Moteur')
freinage = st.checkbox('Freinage')
suspension = st.checkbox('Châssis / Suspension')
direction = st.checkbox('Direction')
boite = st.checkbox('Boîte de vitesses')
pneus = st.checkbox('Pneus')

def categorize(text):
    text = text.lower()
    if 'engine' in text:
        return 'Moteur'
    elif 'brake' in text:
        return 'Freinage'
    elif 'suspension' in text or 'chassis' in text:
        return 'Châssis / Suspension'
    elif 'steering' in text or 'direction' in text:
        return 'Direction'
    elif 'gear' in text or 'transmission' in text:
        return 'Boîte de vitesses'
    elif 'tire' in text or 'wheel' in text:
        return 'Pneus'
    else:
        return 'Autres'

def generate_pdf(vehicle, date, sections, checklist):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Smart Test Drive Report', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Vehicle: {vehicle}', ln=True)
    pdf.cell(0, 10, f'Date: {date}', ln=True)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Checklist:', ln=True)
    pdf.set_font('Arial', '', 12)
    for item in checklist:
        pdf.cell(0, 10, f" - {item}", ln=True)

    pdf.ln(5)
    for i, section in enumerate(sections, 1):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"{i}. Section: {section['zone']}", ln=True)
        pdf.set_font('Arial', '', 12)
        if 'issue' in section:
            pdf.multi_cell(0, 10, f"Issue: {section['issue']}")
        if 'photo' in section:
            try:
                pdf.image(section['photo'], w=100)
            except:
                pdf.cell(0, 10, f"(Photo not loaded: {section['photo']})", ln=True)
        pdf.ln(5)

    output_file = 'Kukuk_Smart_Assistant_Report.pdf'
    pdf.output(output_file)
    return output_file

if st.button('Generate Report'):
    if uploaded_audio and uploaded_image and note_text:
        with open(uploaded_image.name, 'wb') as f:
            f.write(uploaded_image.getbuffer())

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
            tmp_audio.write(uploaded_audio.read())
            tmp_audio_path = tmp_audio.name

        model = whisper.load_model('base')
        transcription = model.transcribe(tmp_audio_path)['text']
        category = categorize(transcription)

        selected = []
        if moteur: selected.append('Moteur')
        if freinage: selected.append('Freinage')
        if suspension: selected.append('Châssis / Suspension')
        if direction: selected.append('Direction')
        if boite: selected.append('Boîte de vitesses')
        if pneus: selected.append('Pneus')

        report_data = [
            {'zone': category, 'issue': transcription},
            {'zone': 'Photo Input', 'photo': uploaded_image.name},
            {'zone': 'Manual Note', 'issue': note_text}
        ]

        pdf_file = generate_pdf('Demo Car', datetime.now().strftime('%Y-%m-%d'), report_data, selected)

        st.success('PDF Report generated successfully!')
        with open(pdf_file, 'rb') as f:
            st.download_button('Download Report', f, file_name=pdf_file)
    else:
        st.warning('Please upload all required inputs.')
