import os
import subprocess
import sys

def build_executable():
    print("[*] Initializing compilation engine pipeline...")
    
    # Enforce automated pyinstaller installation dependency check
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller missing. Executing pip environment hook setup...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Core build arguments array
    # Bundles into a single file (--onefile), strips console popups (--windowed)
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        f"--name=Secure_Face_Blur_Studio_Pro",
        os.path.join("src", "app.py")
    ]
    
    print(f"[*] Executing payload packaging array matrix: {' '.join(cmd)}")
    subprocess.call(cmd)
    print("[+] Done! Standalone distribution artifact ready inside: '/dist/' folder.")

if __name__ == '__main__':
    build_executable()
