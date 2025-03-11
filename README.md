# Audio Diarization Project | Projeto de Diarização de Áudio

[English](#english) | [Português](#português)

## English

### Overview
This project implements two different methods for audio diarization (speaker identification and segmentation). It provides solutions using both WhisperX with pyannote/speaker-diarization-3.1 and AssemblyAI's API.

### Features
- Two independent diarization methods:
  1. WhisperX + Pyannote implementation
  2. AssemblyAI API implementation
- Support for multiple speakers
- Audio format conversion and preprocessing
- Output in text format with speaker labels
- Portuguese language support

### Requirements
- Python 3.8+
- CUDA-compatible GPU (for WhisperX method)
- Required API keys:
  - HuggingFace API key (for pyannote)
  - AssemblyAI API key (for AssemblyAI method)

### Installation
1. Clone this repository
2. Install the required dependencies:
```bash
pip install whisperx torch ffmpeg-python pydub assemblyai python-dotenv
```
3. Create a `.env` file with your API keys:
```env
HF_API_KEY=your_huggingface_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
```

### Usage

#### Using WhisperX (diarizacao.py)
```bash
python diarizacao.py input_audio_file output_directory
```

#### Using AssemblyAI (voice-AssemblyAI.py)
```bash
python voice-AssemblyAI.py input_audio_file [speakers_expected] [output_file]
```

## Português

### Visão Geral
Este projeto implementa dois métodos diferentes para diarização de áudio (identificação e segmentação de falantes). Fornece soluções usando tanto WhisperX com pyannote/speaker-diarization-3.1 quanto a API da AssemblyAI.

### Funcionalidades
- Dois métodos independentes de diarização:
  1. Implementação WhisperX + Pyannote
  2. Implementação via API AssemblyAI
- Suporte para múltiplos falantes
- Conversão e pré-processamento de áudio
- Saída em formato texto com identificação dos falantes
- Suporte para língua portuguesa

### Requisitos
- Python 3.8+
- GPU compatível com CUDA (para método WhisperX)
- Chaves de API necessárias:
  - Chave API HuggingFace (para pyannote)
  - Chave API AssemblyAI (para método AssemblyAI)

### Instalação
1. Clone este repositório
2. Instale as dependências necessárias:
```bash
pip install whisperx torch ffmpeg-python pydub assemblyai python-dotenv
```
3. Crie um arquivo `.env` com suas chaves de API:
```env
HF_API_KEY=sua_chave_huggingface
ASSEMBLYAI_API_KEY=sua_chave_assemblyai
```

### Uso

#### Usando WhisperX (diarizacao.py)
```bash
python diarizacao.py arquivo_audio_entrada diretorio_saida
```

#### Usando AssemblyAI (voice-AssemblyAI.py)
```bash
python voice-AssemblyAI.py arquivo_audio_entrada [numero_falantes_esperados] [arquivo_saida]
```

## License | Licença

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.