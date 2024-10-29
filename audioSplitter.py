import sys
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def splitAudio(inputFile, outputDir, minSegmentDurationSec=5):
    # # Carregar o arquivo de áudio
    audio = AudioSegment.from_file(inputFile)
    
    chunk = split_on_silence(audio, min_silence_len=300, silence_thresh=-50, keep_silence=True )
    
    print(f"Encontrados {len(chunk)} segmentos")
    
    for i, segment in enumerate(chunk):
        outputFile = os.path.join(outputDir, f"segment_{i}.mp3")
        segment.export(outputFile, format="mp3")
        print(f"Segmento {i} salvo em {outputFile}")

if __name__ == "__main__":
    # python audioSplitter.py audio.wav
    # if len(sys.argv) < 2:
    #     print("Falta o arquivo de áudio")
    #     print("Uso: python audioSplitter.py <arquivo de áudio>")
    #     sys.exit(1)
        
    inputFile = ".\\11-10-24ENTREVISTAPILOTO2.mp3"# sys.argv[1]
    print(f"Dividindo o arquivo de áudio {inputFile}")    
    outputDir =".\\teste\\"# inputFile.split("\\")[-1].split(".")[0]
    print(f"Salvando os segmentos em {outputDir}")
    os.makedirs(outputDir, exist_ok=True)
    splitAudio(inputFile, outputDir)