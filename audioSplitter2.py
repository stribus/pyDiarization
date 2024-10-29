import librosa
from sklearn.cluster import KMeans
import pydub
import numpy as np

audio_path = '11-10-24ENTREVISTAPILOTO2.MP3'
print("Loading audio file...")
audio, sr = librosa.load(audio_path, sr=None)
audiofull = pydub.AudioSegment.from_file(audio_path)
print("Extracting MFCC features...")
mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)

kmeans = KMeans(n_clusters=2)  # assuming 2 speakers
kmeans.fit(mfccs.T)
speaker_labels = kmeans.labels_

frame_length = int(0.5 * sr)  # 500ms frame size in samples
hop_length = int(0.25 * sr)  # 250ms hop size in samples

print("Segmenting audio by speaker...")
frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
speaker_turns = []
print("Saving speaker turns to individual files...")
for i, frame in enumerate(frames.T):
    speaker_label = speaker_labels[i]
    speaker_turns.append((speaker_label, frame))
    
active_speaker = f"{speaker_turns[0][0]}"
start_time = 0
end_time = 0



print("Saving speaker turns to individual files...")
for i, (speaker_label, frame) in enumerate(speaker_turns):
    if (f"{speaker_label}" != active_speaker) or (i == len(speaker_turns) - 1):        
        file_name = f"speaker_{active_speaker}_{start_time:.2f}_{end_time:.2f}.wav"
        audio_segment = audiofull[start_time * 1000:end_time * 1000]            
        audio_segment.export(file_name, format="wav")
        if i == len(speaker_turns) - 1:
            break
        active_speaker = f"{speaker_label}"
        start_time = i * hop_length / sr        
        
    end_time = (i * hop_length / sr) + (frame_length / sr)
    
    # start_time = i * hop_length / sr
    # end_time = start_time + frame_length / sr
    # file_name = f"speaker_{speaker_label}_{start_time:.2f}_{end_time:.2f}.wav"
    # audio_segment = pydub.AudioSegment(
    #     data=frame.tobytes(),
    #     frame_rate=sr,
    #     sample_width=2,
    #     channels=1
    # )
    # audio_segment.export(file_name, format="wav")