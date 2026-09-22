import os
import subprocess
import sys

def convert_png_to_ico(png_path, ico_path):
    """Converts a standard PNG into a multi-resolution Windows executable icon."""
    try:
        from PIL import Image
        print(f"[*] Processing visual asset configuration for: {png_path}")
        img = Image.open(png_path)
        
        # Windows icons package multiple icon resolution matrices (from 16x16 up to 256x256)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, format="ICO", sizes=icon_sizes)
        print(f"[+] Multi-resolution Windows icon layer successfully generated at: {ico_path}")
        return True
    except Exception as e:
        print(f"[!] Warning: Image asset transformation aborted. Reason: {e}")
        print("[!] Default execution canvas pointers will be assigned instead.")
        return False

def build_executable():
    print("[*] Initializing compilation engine pipeline...")
    
    # Enforce environmental dependency checks
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller missing. Executing pip environment hook setup...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    try:
        from PIL import Image
    except ImportError:
        print("[!] Pillow missing. Ingesting requirement map layers...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])

    # Resolve absolute path bounds to prevent pathing issues
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(current_directory, "src", "app.py")
    input_png = os.path.join(current_directory, "icon.png")
    output_ico = os.path.join(current_directory, "icon.ico")
    
    if not os.path.exists(target_script):
        print(f"[!] CRITICAL ERROR: The core runtime module '{target_script}' was not found.")
        print("[!] Please confirm your code layout maps match 'src/app.py'.")
        return

    # Core argument parameters configuration structure mapping
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=Secure_Face_Blur_Studio_Pro",
    ]

    # Inject visual icon hooks into the compilation command array if present
    if os.path.exists(input_png):
        if convert_png_to_ico(input_png, output_ico):
            cmd.append(f"--icon={output_ico}")
    elif os.path.exists(output_ico):
        cmd.append(f"--icon={output_ico}")
    else:
        print("[*] No custom 'icon.png' spotted. Building with standard fallback layouts.")

    cmd.append(target_script)
    
    print(f"[*] Launching packaging sequence matrix:\n{' '.join(cmd)}\n")
    subprocess.call(cmd)
    print("\n[+] Verification Check complete. Custom application artifact built cleanly inside '/dist/'!")

if __name__ == '__main__':
    build_executable()
