import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import json
from datetime import datetime, timedelta
from voice_AssemblyAI import transcribe

class TranscribeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcrição de Áudio - AssemblyAI")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Arquivo para salvar estatísticas
        self.stats_file = "transcription_stats.json"
        
        # Variáveis
        self.file_path = tk.StringVar()
        self.speakers = tk.IntVar(value=2)
        self.language = tk.StringVar(value="pt")
        self.is_processing = False
        self.current_audio_duration = 0.0
        self.total_time_transcribed = self.load_total_time()
        
        # Variáveis para displays de tempo
        self.current_time_var = tk.StringVar(value="00:00:00")
        self.total_time_var = tk.StringVar(value="00:00:00")
        
        self.create_widgets()
        self.center_window()
        self.update_time_displays()
        
    def load_total_time(self):
        """Carrega o tempo total transcrito do arquivo de estatísticas"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('total_seconds', 0.0)
        except Exception:
            pass
        return 0.0
    
    def save_total_time(self):
        """Salva o tempo total transcrito no arquivo de estatísticas"""
        try:
            data = {
                'total_seconds': self.total_time_transcribed,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar estatísticas: {e}")
    
    def format_duration(self, seconds):
        """Formata duração em segundos para HH:MM:SS"""
        if seconds <= 0:
            return "00:00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def update_time_displays(self):
        """Atualiza os displays de tempo na interface"""
        current_time = self.format_duration(self.current_audio_duration)
        total_time = self.format_duration(self.total_time_transcribed)
        
        self.current_time_var.set(current_time)
        self.total_time_var.set(total_time)
    
    def reset_total_time(self):
        """Reseta o tempo total acumulado"""
        result = messagebox.askyesno("Confirmar Reset", 
                                   "Tem certeza que deseja resetar o tempo total acumulado?")
        if result:
            self.total_time_transcribed = 0.0
            self.save_total_time()
            self.update_time_displays()
            messagebox.showinfo("Reset Realizado", "Tempo total resetado com sucesso!")
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Transcrição de Áudio com Diarização", 
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para seleção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="Arquivo de Áudio")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        file_entry.pack(side=tk.LEFT, padx=(10, 5), pady=10, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(file_frame, text="Procurar", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        
        # Frame para configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações")
        config_frame.pack(fill=tk.X, pady=10)
        
        # Número de locutores
        speakers_label = ttk.Label(config_frame, text="Número de locutores:")
        speakers_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        speakers_spinbox = ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.speakers, width=5)
        speakers_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Idioma
        language_label = ttk.Label(config_frame, text="Idioma:")
        language_label.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        
        language_combo = ttk.Combobox(config_frame, textvariable=self.language, 
                                      values=["pt", "es", "en_us", "en"], width=10, state="readonly")
        language_combo.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)
        
        # Frame para estatísticas de tempo
        time_frame = ttk.LabelFrame(main_frame, text="Estatísticas de Tempo")
        time_frame.pack(fill=tk.X, pady=10)
        
        # Tempo do áudio atual
        current_label = ttk.Label(time_frame, text="Duração do áudio atual:")
        current_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.current_time_display = ttk.Label(time_frame, textvariable=self.current_time_var,
                                            font=("Courier", 12, "bold"), foreground="blue")
        self.current_time_display.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Tempo total acumulado
        total_label = ttk.Label(time_frame, text="Tempo total transcrito:")
        total_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.total_time_display = ttk.Label(time_frame, textvariable=self.total_time_var,
                                          font=("Courier", 12, "bold"), foreground="green")
        self.total_time_display.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Botão de reset
        reset_button = ttk.Button(time_frame, text="Reset Total", command=self.reset_total_time)
        reset_button.grid(row=1, column=2, padx=20, pady=5)
        
        # Frame para botão de transcrição
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.transcribe_button = ttk.Button(button_frame, text="Transcrever", command=self.start_transcription)
        self.transcribe_button.pack(pady=10)
        
        # Frame para progresso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, padx=10)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=0)
        
        self.status_label = ttk.Label(status_frame, text="Pronto para transcrever", 
                                    wraplength=580, anchor="center")
        self.status_label.pack(fill=tk.X, expand=True)
    
    def browse_file(self):
        """Abre diálogo para selecionar arquivo de áudio"""
        filetypes = (("Arquivos de áudio", "*.mp3 *.m4a *.wav *.mkv *.ogg *.opus"), ("Todos os arquivos", "*.*"))
        file_path = filedialog.askopenfilename(title="Selecione um arquivo de áudio", filetypes=filetypes)
        if file_path:
            self.file_path.set(file_path)
            # Obter duração do áudio selecionado
            self.get_current_audio_duration(file_path)
    
    def get_current_audio_duration(self, file_path):
        """Obtém a duração do áudio atual e atualiza a interface"""
        try:
            from voice_AssemblyAI import get_audio_duration
            duration = get_audio_duration(file_path)
            if duration:
                self.current_audio_duration = duration
            else:
                self.current_audio_duration = 0.0
        except Exception:
            self.current_audio_duration = 0.0
        
        self.update_time_displays()
    
    def start_transcription(self):
        """Inicia o processo de transcrição em uma thread separada"""
        if not self.file_path.get():
            messagebox.showerror("Erro", "Selecione um arquivo de áudio primeiro.")
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.transcribe_button.config(state=tk.DISABLED)
        self.status_label.config(text="Transcrevendo... Este processo pode demorar vários minutos.")
        self.progress_bar.start()
        
        # Iniciar thread para não bloquear a interface
        thread = threading.Thread(target=self.run_transcription)
        thread.daemon = True
        thread.start()
    
    def run_transcription(self):
        """Executa a transcrição em uma thread separada"""
        try:
            success, duration = transcribe(
                file_path=self.file_path.get(),
                speakers_expected=self.speakers.get(),
                output='',  # Usar padrão
                lang=self.language.get()
            )
            
            if success and duration > 0:
                # Atualizar tempo total acumulado
                self.total_time_transcribed += duration
                self.save_total_time()
            
            # Atualizar UI na thread principal
            self.root.after(0, self.transcription_complete, success, duration)
        except Exception as e:
            # Atualizar UI na thread principal em caso de erro
            self.root.after(0, self.transcription_complete, False, 0.0, str(e))
    
    def transcription_complete(self, success, duration=0.0, error_message=""):
        """Chamado quando a transcrição é concluída"""
        self.progress_bar.stop()
        self.is_processing = False
        self.transcribe_button.config(state=tk.NORMAL)
        
        # Atualizar displays de tempo
        self.update_time_displays()
        
        if success:
            # Obtém o caminho de saída (mesmo que a função transcribe)
            dir_path = os.path.dirname(self.file_path.get())
            filename = os.path.basename(self.file_path.get())
            output_path = os.path.join(dir_path, filename.split('.')[0] + '_transcript.txt')
            
            duration_str = self.format_duration(duration) if duration > 0 else "N/A"
            self.status_label.config(text=f"Transcrição concluída! Duração: {duration_str}")
            messagebox.showinfo("Concluído", f"A transcrição foi salva em:\n{output_path}\n\nDuração do áudio: {duration_str}")
        else:
            self.status_label.config(text="Erro na transcrição")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a transcrição:\n{error_message}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TranscribeApp(root)
    root.mainloop()
