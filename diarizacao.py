import argparse
import datetime
import torch
import whisperx
import os
import sys
import logging
import dotenv
from datetime import datetime
import ffmpeg
from pydub import AudioSegment
from typing import Dict, Any, List
import warnings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def convert_audio_to_wav(input_file: str, output_file: str) -> None:
    logger.info(f"Convertendo {input_file} para WAV")
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Conversão completa. Gerado arquivo {output_file}")
    except ffmpeg.Error as e:
        logger.error(f"Erro durante a conversão do audio: {e.stderr.decode()}")
        raise

def add_silence_padding(input_file: str, output_file: str, pad_duration: int = 45000) -> None:
    """Adicionado um padding de silêncio ao áudio para melhorar a possibilidade de transcrição do inicio e fim do áudio."""
    audio = AudioSegment.from_wav(input_file)
    silence = AudioSegment.silent(duration=pad_duration)
    padded_audio = silence + audio + silence
    padded_audio.export(output_file, format="wav")
    logger.info(f"Adicionado {pad_duration}ms de silencio no inicio e no fim do {output_file}")


def merge_speaker_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agrupa segmentos de texto de um mesmo locutor."""
    merged_segments = []
    current_speaker = None
    current_text = ""

    for segment in segments:
        speaker = segment.get('speaker', 'Unknown Speaker')
        if speaker == current_speaker:
            current_text += " " + segment['text']
        else:
            if current_speaker is not None:
                merged_segments.append({
                    'speaker': current_speaker,
                    'text': current_text.strip()
                })
            current_speaker = speaker
            current_text = segment['text']

    if current_speaker is not None:
        merged_segments.append({
            'speaker': current_speaker,
            'text': current_text.strip()
        })

    return merged_segments

def save_result_as_text(result: Dict[str, Any], output_file: str):
    """Salva o resultado da transcrição em um arquivo de texto."""
    try:
        merged_segments = merge_speaker_segments(result['segments'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write the current date and time at the beginning of the file
            f.write(f"transcrevendo para o arquivo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for segment in merged_segments:
                f.write(f"{segment['speaker']}: {segment['text']}\n\n")
        
        logger.info(f"transcrição salva: {output_file}")
    except Exception as e:
        logger.error(f"Erro ao salvar transcrição: {str(e)}", exc_info=True)
        raise
    
def transcribe_audio(audio_file: str, output_dir: str, language: str, model:str = "large-v3")->Dict[str, Any]:
    """Transcreve e diariza um arquivo de áudio usando o modelo especificado."""  
    try:
        logger.info("Carregando modelo...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float32" if device == "cuda" else "int8"
        modelPipeline = whisperx.load_model(model, language=language, device=device, compute_type=compute_type)
        
        logger.info("Carregando áudio...")
        audio = whisperx.load_audio(audio_file)
        
        logger.info("Diarizando áudio...")
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=os.environ["HF_API_KEY"])
        diarize_segments = diarize_model(audio)

        logger.info("Transcrevendo áudio...")
        ## TODO: Verificar se é necessário alterar o batch_size e chunk_size
        result = modelPipeline.transcribe(audio, batch_size=10,chunk_size=10,print_progress=True)

        logger.info("Alinhando áudio...")
        alignment_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

        align_result = whisperx.align(result["segments"], alignment_model, metadata, audio=audio,device=device)

        logger.info("Atribuindo locutores...")
        result2 = whisperx.assign_word_speakers(diarize_segments, align_result)
        
        return result2      
        
    except Exception as e:
        logger.error(f"Erro ao transcrever áudio: {str(e)}", exc_info=True)
        raise
    
def check_audio_file(audio_file: str) -> bool:
    """Verifica se o arquivo de áudio existe e é acessível."""
    return os.path.exists(audio_file)

def get_audio_duration(audio_file: str) -> float:
    """Retorna a duração do arquivo de áudio em segundos."""
    try:
        file = ffmpeg.input(audio_file)
        duration = file.probe().duration
        return duration
    except Exception as e:
        logger.error(f"Erro ao obter duração do áudio: {str(e)}", exc_info=True)
        return 0.0

def main(input_file: str, output_dir: str):
    temp_wav_file = "temp_audio.wav"
    padded_wav_file = "padded_audio.wav"
    try:
        input_file = os.path.abspath(input_file)
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")
        
        convert_audio_to_wav(audio_file, temp_wav_file)
        
        add_silence_padding(temp_wav_file, padded_wav_file)
        
        output_dir = os.path.abspath(output_dir)        
        os.makedirs(output_dir, exist_ok=True)
        
        result = transcribe_audio(padded_wav_file, output_dir, language="pt")
        
        output = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_transcript.txt"
        output = os.path.join(output_dir, output)
        
        save_result_as_text(result, output)
    except Exception as e:
        logger.error(f"Erro ao verificar arquivo de áudio: {str(e)}", exc_info=True)
    finally:
        if os.path.exists(temp_wav_file):
            os.remove(temp_wav_file)
        if os.path.exists(padded_wav_file):
            os.remove(padded_wav_file)     
        
        
        

if (__name__ == "__main__"):
    warnings.filterwarnings("ignore")
    dotenv.load_dotenv()
    hf_api_key = os.getenv('HF_API_KEY')
    if hf_api_key is not None:
        os.environ["HF_API_KEY"] = hf_api_key
    
    
    parser = argparse.ArgumentParser(description="Transcreve e diariza um arquivo de áudio.")
    parser.add_argument("audio_file", type=str, help="Caminho para o arquivo de áudio a ser transcrito.")
    parser.add_argument("--output_dir", type=str, default="output", help="Diretório de saída para salvar o arquivo de transcrição.")
    
    args = parser.parse_args()
    audio_file = args.audio_file
    output_dir = args.output_dir
    
    main(audio_file, output_dir)