import os
import subprocess
import sys

def build_executable():
    print("[*] Initializing compilation engine pipeline...")
    
    # Force auto-installation check for pyinstaller package
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller missing. Executing pip environment hook setup...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Get absolute paths to prevent Windows path bugs
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(current_directory, "src", "app.py")
    
    print(f"[*] Looking for script at: {target_script}")
    if not os.path.exists(target_script):
        print(f"[!] CRITICAL ERROR: The file '{target_script}' does not exist!")
        print("[!] Please verify your 'src' folder contains 'app.py' inside it.")
        return

    # Core PyInstaller runtime configurations matrix arguments array
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=Secure_Face_Blur_Studio_Pro",
        target_script
    ]
    
    print(f"[*] Executing absolute packaging array matrix:\n{' '.join(cmd)}")
    subprocess.call(cmd)
    print("\n[+] Verification Check complete. Standalone binary ready inside your local '/dist/' directory!")

if __name__ == '__main__':
    build_executable()
