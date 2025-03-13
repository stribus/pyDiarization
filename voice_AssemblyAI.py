import os
import sys
import assemblyai as aai
import dotenv  

dotenv.load_dotenv()

def transcribe(file_path,speakers_expected=2,output='', lang='pt')->bool:        
    '''Transcribe audio file using AssemblyAI API'''
    aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,
        speaker_labels=True,
        speakers_expected=speakers_expected,
        language_code=lang
    )


    transcriber = aai.Transcriber(config=config)
    transcriber._client.timeout = 3000
    transcript = transcriber.transcribe(file_path)

    if transcript.status == aai.TranscriptStatus.error:
        print(transcript.error)
        #lança exceção
        raise Exception(transcript.error)
    else:
        if output == '':
            dir = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            output = os.path.join(dir, filename.split('.')[0] + '_transcript.txt')
            
        with open(output, 'w',encoding='utf-8', errors='ignore') as f:
            for utterance in transcript.utterances:
                f.write(f"LOCUTOR {utterance.speaker}: {utterance.text}\n")
                # print(f"{utterance.speaker}: {utterance.text}")
        print(f"Transcript saved to {output}")
        return True
    return False
            
        
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
        
    transcribe(file_path,speakers_expected,output)