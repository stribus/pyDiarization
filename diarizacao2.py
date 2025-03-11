import argparse
import logging
import os
import whisperx
import torch
import ffmpeg
from pydub import AudioSegment
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_mkv_to_wav(input_file: str, output_file: str) -> None:
    logger.info(f"Converting {input_file} to WAV format")
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Conversion completed. WAV file saved as {output_file}")
    except ffmpeg.Error as e:
        logger.error(f"Error during MKV to WAV conversion: {e.stderr.decode()}")
        raise

def add_silence_padding(input_file: str, output_file: str, pad_duration: int = 45000) -> None:
    """I did this to add silence padding to the beginning of the audio file for diarization."""
    audio = AudioSegment.from_wav(input_file)
    silence = AudioSegment.silent(duration=pad_duration)
    padded_audio = silence + audio
    padded_audio.export(output_file, format="wav")
    logger.info(f"Added {pad_duration}ms silence padding to {output_file}")

def transcribe_and_diarize_with_whisperx(audio_file: str, model_name: str, hf_token: str) -> Dict[str, Any]:
    """Here I perform transcription and diarization using WhisperX."""
    logger.info(f"Starting WhisperX transcription and diarization with model {model_name}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float32" if device == "cuda" else "float32"
    logger.info(f"Using device: {device}, compute type: {compute_type}")

    try:
        # Load the Whisper model
        model = whisperx.load_model(model_name, device=device, compute_type=compute_type)
        logger.info("WhisperX model loaded successfully")

        # Transcribe the audio
        result = model.transcribe(audio_file, batch_size=16)
        logger.info("Audio transcription completed")

        # Perform forced alignment
        alignment_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result3 = whisperx.align(result["segments"], alignment_model, metadata, audio_file, device=device)
        logger.info("Forced alignment completed")

        # Perform speaker diarization
        diarization_pipeline = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
        diarization_result = diarization_pipeline(audio_file)
        logger.info("Speaker diarization completed")

        # Assign speaker labels
        result = whisperx.assign_word_speakers(diarization_result, result)
        logger.info("Speaker labels assigned to transcription")

        return result

    except Exception as e:
        logger.error(f"Error in WhisperX transcription and diarization: {str(e)}", exc_info=True)
        raise

def merge_speaker_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge consecutive segments from the same speaker."""
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
    """Save the transcription result as a formatted text file."""
    try:
        merged_segments = merge_speaker_segments(result['segments'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write the current date and time at the beginning of the file
            f.write(f"Transcription generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for segment in merged_segments:
                f.write(f"{segment['speaker']}: {segment['text']}\n\n")
        
        logger.info(f"Transcription saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving transcription: {str(e)}", exc_info=True)
        raise

def main(input_file: str, output_file: str, model_name: str, hf_token: str):
    try:
        # Convert MKV to WAV
        temp_wav_file = "temp_audio.wav"
        convert_mkv_to_wav(input_file, temp_wav_file)
        
        # Add silence padding
        padded_wav_file = "padded_audio.wav"
        add_silence_padding(temp_wav_file, padded_wav_file)
        
        # Perform transcription and diarization
        result = transcribe_and_diarize_with_whisperx(padded_wav_file, model_name, hf_token)
        
        # Save the result as text
        save_result_as_text(result, output_file)
        
        # Clean up temporary files
        os.remove(temp_wav_file)
        os.remove(padded_wav_file)
        logger.info("Temporary audio files removed")
        
        logger.info("Transcription and diarization process completed successfully")

    except Exception as e:
        logger.error(f"An error occurred during the process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhisperX Transcription and Diarization for MKV files")
    parser.add_argument("input_file", help="Path to the input MKV file")
    parser.add_argument("output_file", help="Path to save the output transcription")
    parser.add_argument("--model", default="large-v3", help="WhisperX model to use (default: large-v3)")
    parser.add_argument("--hf_token", required=True, help="HuggingFace token for diarization")
    args = parser.parse_args()

    main(args.input_file, args.output_file, args.model, args.hf_token)