import os
import sys
import assemblyai as aai
import dotenv
import subprocess
import json

dotenv.load_dotenv()

def get_audio_duration(file_path):
    """Obtém a duração do áudio em segundos usando ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        else:
            # Fallback: tentar obter duração via AssemblyAI após transcrição
            return None
    except Exception:
        return None

def transcribe(file_path,speakers_expected=2,output='', lang='pt')->tuple:        
    '''Transcribe audio file using AssemblyAI API
    Returns (success: bool, duration_seconds: float)'''
    
    # Obter duração do áudio
    duration_seconds = get_audio_duration(file_path)
    
    aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,
        speaker_labels=True,
        speakers_expected=speakers_expected,
        language_code=lang
    )

    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(file_path)

    if transcript.status == aai.TranscriptStatus.error:
        print(transcript.error)
        #lança exceção
        raise Exception(transcript.error)
    else:
        # Tentar obter duração do transcript se não conseguimos via ffprobe
        if duration_seconds is None and hasattr(transcript, 'audio_duration') and transcript.audio_duration:
            duration_seconds = transcript.audio_duration / 1000.0  # AssemblyAI retorna em millisegundos
            
        if output == '':
            dir = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            # está dando erro quando o arquivo tem ponto no nome
            # output = os.path.join(dir, filename.split('.')[0] + '_transcript.txt')
            # solução alternativa:
            output = os.path.join(dir, os.path.splitext(filename)[0] + '_transcript.txt')
            
        with open(output, 'w',encoding='utf-8', errors='ignore') as f:
            if transcript.utterances is not None:
                for utterance in transcript.utterances:
                    f.write(f"LOCUTOR {utterance.speaker}: {utterance.text}\n")
                    # print(f"{utterance.speaker}: {utterance.text}")
            else:
                f.write("Nenhuma fala foi encontrada na transcrição.\n")
        print(f"Transcript saved to {output}")
        return True, duration_seconds or 0.0
    return False, 0.0
            
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python voice-AssemblyAI.py <file_path> <speakers_expected> <output>")
        sys.exit(1)

    file_path = sys.argv[1]
    speakers_expected = 2
    output = ''
    if len(sys.argv) > 2:
        speakers_expected = int(sys.argv[2])
        
    if len(sys.argv) > 3:
        output = sys.argv[3]
        
    success, duration = transcribe(file_path,speakers_expected,output)
    if success and duration:
        print(f"Audio duration: {duration:.2f} seconds")