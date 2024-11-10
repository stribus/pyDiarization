import datetime
import torch
import whisperx
import os
import sys
import dotenv
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


dotenv.load_dotenv()

os.environ["HF_API_KEY"] = os.getenv('HF_API_KEY')

# Use caminho absoluto
audio_file = os.path.abspath("23 de out. 22.10.mp3")

# Verifique se arquivo existe
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")

output_dir = os.path.abspath(".\\teste\\")
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float32" if device == "cuda" else "int8"
print(f"Usando device: {device}, compute type: {compute_type}")

model = whisperx.load_model("large-v2", language="pt", device=device, compute_type=compute_type)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio)
print("Transcription: ", result["segments"])

diarize_model = whisperx.DiarizationPipeline(
    use_auth_token=os.environ["HF_API_KEY"])

diarize_segments = diarize_model(audio)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"])

output = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_transcript.txt"
output = os.path.join(output_dir, output)
os.makedirs(output_dir, exist_ok=True)

with open(output, 'w', encoding='utf-8', errors='ignore') as f:
    for segment in result["segments"]:
        f.write(f"LOCUTOR {segment['speaker']}: {segment['text']}\n")
        print(f"LOCUTOR {segment['speaker']}: {segment['text']}")