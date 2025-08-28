# Build Instructions - Aplicação de Transcrição de Áudio

## Como Buildar o Executável

### Pré-requisitos

1. **Python 3.8+** instalado no sistema
2. **FFmpeg** instalado e disponível no PATH do sistema
   - Windows: Baixar de https://ffmpeg.org/download.html
   - Adicionar o FFmpeg ao PATH do Windows
3. **Chave da API AssemblyAI**
   - Criar conta em https://www.assemblyai.com/
   - Obter a chave da API no dashboard

### Passo a Passo

1. **Configure as variáveis de ambiente:**
   ```bash
   # Copie o arquivo de exemplo
   copy .env.example .env
   
   # Edite o arquivo .env e adicione sua chave da API
   # ASSEMBLYAI_API_KEY=sua_chave_aqui
   ```

2. **Instale as dependências:**
   ```bash
   pip install assemblyai python-dotenv pyinstaller ffmpeg-python
   ```

3. **Execute o build:**
   ```bash
   python build.py
   ```

4. **Siga as instruções do script:**
   - Confirme se deseja limpar builds anteriores
   - Aguarde o processo de build

### Resultado

O executável será criado em `dist/TranscribeApp.exe`

## Funcionalidades da Aplicação

### Interface Gráfica
- ✅ Seleção de arquivo de áudio (MP3, M4A, WAV, MKV)
- ✅ Configuração do número de locutores (1-10)
- ✅ Seleção de idioma (PT, ES, EN)
- ✅ Contador de tempo do áudio atual
- ✅ Contador de tempo total acumulado (HH:MM:SS)
- ✅ Botão de reset para o tempo acumulado
- ✅ Barra de progresso durante transcrição

### Contabilização de Tempo
- **Tempo atual:** Mostra a duração do arquivo de áudio selecionado
- **Tempo total:** Acumula o tempo de todos os áudios transcritos com sucesso
- **Persistência:** O tempo total é salvo em `transcription_stats.json`
- **Reset:** Botão para resetar o contador total

### Formatos Suportados
- MP3, M4A, WAV, MKV
- Saída: Arquivo TXT com formato `LOCUTOR A:`, `LOCUTOR B:`, etc.

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'assemblyai'"
- **Solução:** Execute novamente `python build.py` - o script foi atualizado para incluir as dependências

### Erro: "FFmpeg não encontrado"
- **Solução:** Instale o FFmpeg e adicione ao PATH do sistema

### Execução lenta
- **Normal:** A transcrição via AssemblyAI pode demorar alguns minutos dependendo do tamanho do arquivo

## Arquivos Criados

- `TranscribeApp.exe` - Executável principal
- `transcription_stats.json` - Estatísticas de tempo acumulado
- `*_transcript.txt` - Arquivos de transcrição gerados

## Uso do Executável

1. Execute `TranscribeApp.exe`
2. Clique em "Procurar" e selecione um arquivo de áudio
3. Configure o número de locutores esperados
4. Selecione o idioma
5. Clique em "Transcrever"
6. Aguarde o processamento (pode demorar alguns minutos)
7. O resultado será salvo como `{nome_do_arquivo}_transcript.txt`
