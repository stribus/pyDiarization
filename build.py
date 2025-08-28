import os
import subprocess
import sys
import shutil

def check_env_file():
    """Verifica se o arquivo .env existe."""
    if not os.path.exists('.env'):
        print("⚠️  ATENÇÃO: Arquivo .env não encontrado!")
        print("📝 Um arquivo .env.example foi criado como modelo.")
        print("🔑 Copie o .env.example para .env e configure sua chave da API AssemblyAI.")
        print("🌐 Obtenha sua chave em: https://www.assemblyai.com/")
        response = input("Continuar mesmo assim? (s/N): ").lower().strip()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("❌ Build cancelado.")
            return False
    else:
        print("✅ Arquivo .env encontrado.")
    return True

def clean_build():
    """Remove arquivos de build anteriores."""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['TranscribeApp.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo diretório {dir_name}...")
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"Removendo arquivo {file_name}...")
            os.remove(file_name)

def check_pyinstaller():
    """Verifica se o PyInstaller está instalado, caso contrário, instala."""
    try:
        import PyInstaller
        print("PyInstaller já está instalado.")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller instalado com sucesso!")

def create_spec_file():
    """Cria um arquivo .spec personalizado para melhor controle das dependências."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_transcribe.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.')],
    hiddenimports=[
        'assemblyai',
        'dotenv', 
        'json',
        'subprocess',
        'threading',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.ttk',
        'tkinter.messagebox'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TranscribeApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('TranscribeApp.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Arquivo .spec criado com sucesso!")

def build_executable():
    """Constrói o executável usando PyInstaller."""
    print("Iniciando a criação do executável...")
    
    # Criar arquivo .spec se não existir
    if not os.path.exists('TranscribeApp.spec'):
        create_spec_file()
    
    # Usar o arquivo .spec em vez dos parâmetros da linha de comando
    pyinstaller_args = [
        "pyinstaller",
        "TranscribeApp.spec"
    ]
    
    # Executar PyInstaller
    try:
        result = subprocess.call(pyinstaller_args)
        if result == 0:
            print("\n✅ Executável criado com sucesso!")
            print("📁 Você pode encontrá-lo na pasta 'dist'")
            print("⚠️  Certifique-se de que o arquivo .env esteja na mesma pasta do executável.")
            print("⚠️  Para funcionar corretamente, você precisa ter o FFmpeg instalado no sistema.")
        else:
            print("❌ Erro durante a criação do executável!")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar PyInstaller: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Preparando para criar o executável...")
    
    # Verificar arquivo .env
    if not check_env_file():
        sys.exit(1)
    
    # Opção para limpar build anterior
    response = input("Deseja limpar builds anteriores? (s/N): ").lower().strip()
    if response in ['s', 'sim', 'y', 'yes']:
        clean_build()
    
    check_pyinstaller()
    
    success = build_executable()
    
    if success:
        print("\n🎉 Build concluído com sucesso!")
    else:
        print("\n💥 Build falhou. Verifique os erros acima.")
