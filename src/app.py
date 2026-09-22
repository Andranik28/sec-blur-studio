import cv2
import numpy as np
import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image, ImageTk
import secrets
import string

def encrypt_data(data: bytes, password: str) -> bytes:
    key = sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, data, None)

def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    key = sha256(password.encode()).digest()
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

def strip_forensic_metadata(image_matrix: np.ndarray) -> np.ndarray:
    """Removes hidden application footprints, device signatures, and EXIF segments."""
    _, encoded = cv2.imencode('.png', image_matrix)
    clean_matrix = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return clean_matrix

def encode_stego(image_path: str, output_path: str, display_img: np.ndarray, data: bytes):
    flat_img = display_img.copy().flatten()
    data_to_hide = struct.pack('>I', len(data)) + data
    
    if len(data_to_hide) * 8 <= len(flat_img):
        bits = np.unpackbits(np.frombuffer(data_to_hide, dtype=np.uint8))
        flat_img[:len(bits)] = (flat_img[:len(bits)] & ~1) | bits
        stego_img = flat_img.reshape(display_img.shape)
        cv2.imwrite(output_path, stego_img)
        with open(output_path, 'rb') as f:
            file_data = f.read()
        with open(output_path, 'wb') as f:
            f.write(file_data + b"[LSB]" + b"[ERR_FILE_TRUNCATED_CRC_MISMATCH]")
    else:
        cv2.imwrite(output_path, display_img)
        with open(output_path, 'rb') as f:
            file_data = f.read()
        with open(output_path, 'wb') as f:
            f.write(file_data + data_to_hide + b"[APP]" + b"[ERR_DATA_PACKET_CORRUPTED]")

def decode_stego(image_path: str, stego_img: np.ndarray) -> bytes:
    with open(image_path, 'rb') as f:
        file_data = f.read()
        
    if b"[LSB]" in file_data:
        flat_img = stego_img.flatten()
        header_bits = flat_img[:32] & 1
        len_bytes = np.packbits(header_bits).tobytes()
        data_len = struct.unpack('>I', len_bytes)[0]
        
        payload_bits = flat_img[32:32 + data_len * 8] & 1
        return np.packbits(payload_bits).tobytes()
        
    elif b"[APP]" in file_data:
        png_iend = file_data.find(b"\x49\x45\x4e\x44\xae\x42\x60\x82")
        if png_iend != -1:
            start_pos = png_iend + 8
            data_block = file_data[start_pos:]
            idx_app = data_block.find(b"[APP]")
            if idx_app != -1:
                real_block = data_block[:idx_app]
                data_len = struct.unpack('>I', real_block[:4])[0]
                return real_block[4:4+data_len]
        raise ValueError("Damaged payload segment array.")
    else:
        return b""
class FaceStegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Face Blur Studio Pro v4.6")
        self.root.geometry("1400x850")
        self.root.configure(bg="#121212")
        
        # State Initialization
        self.original_img = None      
        self.display_img = None       
        self.mask = None              
        self.saved_blur_mask = None   
        self.mode = "draw" 
        self.blur_style = "gaussian"
        self.drawing = False
        self.loaded_file_path = None  
        
        # Scroll & Pan View Parameters
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_panning = False
        
        # Sizing Indicators States
        self.show_size_circle = False
        self.hide_circle_job = None
        
        self.rect_start_x = None
        self.rect_start_y = None
        self.current_rect_id = None
        self.undo_stack = []
        
        self.setup_ui()

    def setup_ui(self):
        sidebar = tk.Frame(self.root, bg="#1e1e1e", width=300, bd=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        title_lbl = tk.Label(sidebar, text="🛡️ BLUR STUDIO ULTRA", font=("Helvetica", 13, "bold"), bg="#1e1e1e", fg="#00adb5")
        title_lbl.pack(pady=15)
        
        # --- FILES PANEL ---
        sec_files = tk.LabelFrame(sidebar, text=" File Transactions ", bg="#1e1e1e", fg="#888888", font=("Arial", 9, "bold"), bd=1, labelanchor="n")
        sec_files.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Button(sec_files, text="📂 Load Active File", command=self.load_image_standard, bg="#393e46", fg="white", activebackground="#00adb5", bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        tk.Button(sec_files, text="🔓 Execute Stego Decrypt", command=self.trigger_decrypt_action, bg="#2d4059", fg="#4edf75", font=("Arial", 9, "bold"), activebackground="#00adb5", bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        tk.Button(sec_files, text="🧹 Strip Metadata / Forensics", command=self.strip_active_metadata_action, bg="#2c2c2c", fg="#ffc107", font=("Arial", 9, "bold"), bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        tk.Button(sec_files, text="🗂️ Bulk Processing Engine", command=self.process_bulk_folder, bg="#393e46", fg="white", bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        
        # --- TOOLS PANEL ---
        sec_tools = tk.LabelFrame(sidebar, text=" Extraction Countermeasures ", bg="#1e1e1e", fg="#888888", font=("Arial", 9, "bold"), bd=1, labelanchor="n")
        sec_tools.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Button(sec_tools, text="🤖 AI Face Scanner Detection", command=self.auto_detect_faces, bg="#00adb5", fg="white", font=("Arial", 10, "bold"), bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_draw = tk.Button(sec_tools, text="✏️ Mask Brush Matrix", command=lambda: self.set_mode("draw"), bg="#252a34", fg="white", bd=0, height=2)
        self.btn_draw.pack(fill=tk.X, padx=10, pady=2)
        
        self.btn_rect = tk.Button(sec_tools, text="⬜ Rectangular Boundary Select", command=lambda: self.set_mode("rectangle"), bg="#252a34", fg="white", bd=0, height=2)
        self.btn_rect.pack(fill=tk.X, padx=10, pady=2)
        
        self.btn_erase = tk.Button(sec_tools, text="🧽 Clear Mask / Selective Eraser", command=lambda: self.set_mode("erase"), bg="#252a34", fg="white", bd=0, height=2)
        self.btn_erase.pack(fill=tk.X, padx=10, pady=2)
        
        style_frame = tk.Frame(sec_tools, bg="#1e1e1e")
        style_frame.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(style_frame, text="Blur Engine Matrix:", bg="#1e1e1e", fg="#888888", font=("Arial", 9)).pack(side=tk.LEFT)
        self.blur_style_var = tk.StringVar(value="gaussian")
        style_menu = tk.OptionMenu(style_frame, self.blur_style_var, "gaussian", "pixelate", command=self.on_blur_style_toggle)
        style_menu.config(bg="#393e46", fg="white", bd=0, highlightthickness=0, activebackground="#00adb5")
        style_menu["menu"].config(bg="#393e46", fg="white")
        style_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10,0))
        
        # Single Shared Tools Diameter Slider
        size_frame = tk.Frame(sec_tools, bg="#1e1e1e")
        size_frame.pack(fill=tk.X, padx=10, pady=4)
        
        b_lbl_frame = tk.Frame(size_frame, bg="#1e1e1e")
        b_lbl_frame.pack(fill=tk.X)
        tk.Label(b_lbl_frame, text="Tool Size Diameter:", bg="#1e1e1e", fg="#eeeeee", font=("Arial", 8)).pack(side=tk.LEFT)
        self.size_val_lbl = tk.Label(b_lbl_frame, text="30px", bg="#1e1e1e", fg="#00adb5", font=("Arial", 8, "bold"))
        self.size_val_lbl.pack(side=tk.RIGHT)
        
        self.size_slider = tk.Scale(size_frame, from_=5, to=150, orient=tk.HORIZONTAL, bg="#1e1e1e", fg="white", highlightthickness=0, troughcolor="#393e46", activebackground="#00adb5", showvalue=False, command=self.on_size_slider_change)
        self.size_slider.set(30)
        self.size_slider.pack(fill=tk.X, pady=(0,2))

        # Core Blurring Radius Intensity Slider
        blur_rad_frame = tk.Frame(sec_tools, bg="#1e1e1e")
        blur_rad_frame.pack(fill=tk.X, padx=10, pady=4)
        
        br_lbl_frame = tk.Frame(blur_rad_frame, bg="#1e1e1e")
        br_lbl_frame.pack(fill=tk.X)
        tk.Label(br_lbl_frame, text="Obfuscation Kernel Power:", bg="#1e1e1e", fg="#eeeeee", font=("Arial", 8)).pack(side=tk.LEFT)
        self.blur_rad_lbl = tk.Label(br_lbl_frame, text="18%", bg="#1e1e1e", fg="#ffc107", font=("Arial", 8, "bold"))
        self.blur_rad_lbl.pack(side=tk.RIGHT)
        
        self.blur_rad_slider = tk.Scale(blur_rad_frame, from_=1, to=40, orient=tk.HORIZONTAL, bg="#1e1e1e", fg="white", highlightthickness=0, troughcolor="#393e46", activebackground="#00adb5", showvalue=False, command=self.on_blur_rad_slider_change)
        self.blur_rad_slider.set(18)
        self.blur_rad_slider.pack(fill=tk.X, pady=(0,2))

        # --- SECURITY PANEL ---
        sec_crypto = tk.LabelFrame(sidebar, text=" Encryption Parameters ", bg="#1e1e1e", fg="#888888", font=("Arial", 9, "bold"), bd=1, labelanchor="n")
        sec_crypto.pack(fill=tk.X, padx=15, pady=5)
        
        pass_frame = tk.Frame(sec_crypto, bg="#1e1e1e")
        pass_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.pass_var = tk.StringVar()
        self.pass_var.trace_add("write", self.check_password_strength)
        self.entry_pass = tk.Entry(pass_frame, textvariable=self.pass_var, show="*", bg="#252a34", fg="white", bd=0, insertbackground="white", font=("Arial", 11))
        self.entry_pass.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        tk.Button(pass_frame, text="🎲", command=self.generate_strong_password, bg="#00adb5", fg="white", bd=0, width=3, font=("Arial", 9, "bold"), cursor="hand2").pack(side=tk.RIGHT, padx=(2,0))
        self.btn_show_pass = tk.Button(pass_frame, text="👁️", command=self.toggle_password_visibility, bg="#393e46", fg="white", bd=0, width=3, cursor="hand2")
        self.btn_show_pass.pack(side=tk.RIGHT, padx=(2,0))
        
        self.lbl_strength = tk.Label(sec_crypto, text="Entropy Level: Nil", bg="#1e1e1e", fg="#888888", font=("Arial", 8, "italic"))
        self.lbl_strength.pack(anchor=tk.W, padx=10, pady=1)
        
        tk.Button(sec_crypto, text="💨 Render Composite Mask", command=self.apply_blur_render, bg="#ffc107", fg="black", font=("Arial", 9, "bold"), bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        tk.Button(sec_crypto, text="🔒 Finalize Stego-Container", command=self.encrypt_and_save, bg="#ff4a5a", fg="white", font=("Arial", 9, "bold"), bd=0, height=2, cursor="hand2").pack(fill=tk.X, padx=10, pady=4)
        
        tk.Button(sidebar, text="↩️ Rollback Step (Undo)", command=self.trigger_undo, bg="#393e46", fg="white", bd=0, height=2, cursor="hand2").pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=15)

        # Scrollbar Layout Workspace
        self.canvas_container = tk.Frame(self.root, bg="#121212")
        self.canvas_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.v_scroll = tk.Scrollbar(self.canvas_container, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(self.canvas_container, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(self.canvas_container, bg="#1a1a1a", highlightthickness=0, xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
    def update_preview(self):
        if self.original_img is None: return
        
        h, w = self.original_img.shape[:2]
        kernel_percentage = self.blur_rad_slider.get() / 100.0
        
        if self.blur_style == "pixelate":
            block_factor = max(int(max(h, w) * (kernel_percentage * 0.22)), 4)
            small_matrix = cv2.resize(self.original_img, (max(1, w // block_factor), max(1, h // block_factor)), interpolation=cv2.INTER_LINEAR)
            obfuscated_entire = cv2.resize(small_matrix, (w, h), interpolation=cv2.INTER_NEAREST)
            salt_pepper_noise = np.random.randint(0, 15, (h, w, 3), dtype=np.int16)
            obfuscated_entire = np.clip(obfuscated_entire.astype(np.int16) + salt_pepper_noise, 0, 255).astype(np.uint8)
        else:
            kernel_size = int(max(h, w) * kernel_percentage) | 1  
            obfuscated_entire = cv2.GaussianBlur(self.original_img, (kernel_size, kernel_size), 0)
        
        mask_3ch = cv2.merge([self.saved_blur_mask, self.saved_blur_mask, self.saved_blur_mask])
        base_canvas = np.where(mask_3ch == 255, obfuscated_entire, self.original_img)
        
        preview_canvas = base_canvas.copy()
        if np.any(self.mask == 255):
            overlay = preview_canvas.copy()
            overlay[self.mask == 255] = (0, 0, 255)  
            cv2.addWeighted(overlay, 0.4, preview_canvas, 0.6, 0, preview_canvas)
            
        rgb_img = cv2.cvtColor(preview_canvas, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        
        container_w = max(self.canvas.winfo_width(), 800)
        container_h = max(self.canvas.winfo_height(), 500)
        
        fit_scale = min(container_w / w, container_h / h)
        scaled_w = int(w * fit_scale * self.zoom_level)
        scaled_h = int(h * fit_scale * self.zoom_level)
        
        if scaled_w > 0 and scaled_h > 0:
            pil_img = pil_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
            
        self.tk_photo = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        
        scroll_w = max(scaled_w, container_w)
        scroll_h = max(scaled_h, container_h)
        self.canvas.config(scrollregion=(0, 0, scroll_w, scroll_h))
        
        self.img_center_x = scroll_w // 2 + self.pan_x
        self.img_center_y = scroll_h // 2 + self.pan_y
        
        self.canvas.create_image(self.img_center_x, self.img_center_y, anchor=tk.CENTER, image=self.tk_photo)
        
        self.img_top_left_x = self.img_center_x - (scaled_w // 2)
        self.img_top_left_y = self.img_center_y - (scaled_h // 2)
        
        self.scale_to_orig_x = w / scaled_w if scaled_w > 0 else 1
        self.scale_to_orig_y = h / scaled_h if scaled_h > 0 else 1
        
        if self.show_size_circle and self.mode in ["draw", "erase"]:
            diameter = self.size_slider.get()
            indicator_radius = int((diameter / self.scale_to_orig_x) / 2)
            indicator_radius = max(3, min(indicator_radius, min(scroll_w, scroll_h) // 4))
            
            color_anchor = "#00adb5" if self.mode == "draw" else "#ff4a5a"
            self.canvas.create_oval(
                self.img_center_x - indicator_radius, self.img_center_y - indicator_radius,
                self.img_center_x + indicator_radius, self.img_center_y + indicator_radius,
                outline=color_anchor, width=3, dash=(4, 2)
            )

    def convert_event_to_image_coords(self, event):
        if self.original_img is None: return None
        canvas_x = self.canvas.canvasx(event.x) - self.img_top_left_x
        canvas_y = self.canvas.canvasy(event.y) - self.img_top_left_y
        
        img_x = int(canvas_x * self.scale_to_orig_x)
        img_y = int(canvas_y * self.scale_to_orig_y)
        
        h, w = self.original_img.shape[:2]
        if 0 <= img_x < w and 0 <= img_y < h:
            return img_x, img_y
        return None

    def toggle_password_visibility(self):
        if self.entry_pass.cget("show") == "*":
            self.entry_pass.config(show="")
            self.btn_show_pass.config(text="🙈")
        else:
            self.entry_pass.config(show="*")
            self.btn_show_pass.config(text="👁️")

    def generate_strong_password(self):
        upper = "".join(secrets.choice(string.ascii_uppercase) for _ in range(4))
        lower = "".join(secrets.choice(string.ascii_lowercase) for _ in range(4))
        digits = "".join(secrets.choice(string.digits) for _ in range(4))
        special = "".join(secrets.choice("!@#$%^&*()_+=-[]{}|") for _ in range(4))
        strong_pass = list(upper + lower + digits + special)
        secrets.SystemRandom().shuffle(strong_pass)
        final_pass = "".join(strong_pass)
        
        self.pass_var.set(final_pass)
        self.root.clipboard_clear()
        self.root.clipboard_append(final_pass)

    def check_password_strength(self, *args):
        password = self.pass_var.get()
        if not password:
            self.lbl_strength.config(text="Entropy Level: Nil", fg="#888888")
            return
        
        has_len = len(password) >= 12
        has_digit = any(c.isdigit() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_special = any(c in "!@#$%^&*()_+=-[]{}|;':\",./<>?" for c in password)
        
        metrics_score = sum([has_len, has_digit, has_upper, has_special])
        if len(password) >= 16 and metrics_score == 4:
            self.lbl_strength.config(text="🟢 Enterprise Strong Configuration", fg="#4edf75")
        elif metrics_score >= 3 and len(password) >= 10:
            self.lbl_strength.config(text="🟢 Enterprise Strong Configuration", fg="#4edf75")
        elif metrics_score <= 2:
            self.lbl_strength.config(text="🔴 Low Security Risk Profile", fg="#ff4a5a")
        else:
            self.lbl_strength.config(text="🟡 Moderate Entropy Threshold", fg="#ffc107")

    def set_mode(self, mode):
        self.mode = mode
        self.btn_draw.config(bg="#00adb5" if mode == "draw" else "#252a34")
        self.btn_rect.config(bg="#00adb5" if mode == "rectangle" else "#252a34")
        self.btn_erase.config(bg="#00adb5" if mode == "erase" else "#252a34")
        self.update_preview()

    def on_blur_style_toggle(self, val):
        self.blur_style = val
        self.update_preview()

    def on_size_slider_change(self, val):
        self.size_val_lbl.config(text=f"{val}px")
        self.show_size_circle = True
        self.update_preview()
        
        if self.hide_circle_job:
            self.root.after_cancel(self.hide_circle_job)
        self.hide_circle_job = self.root.after(1500, self.clear_size_circle_view)

    def on_blur_rad_slider_change(self, val):
        self.blur_rad_lbl.config(text=f"{val}%")
        self.update_preview()

    def clear_size_circle_view(self):
        self.show_size_circle = False
        self.update_preview()

    def save_to_undo_stack(self):
        if self.mask is not None and self.saved_blur_mask is not None:
            self.undo_stack.append((self.mask.copy(), self.saved_blur_mask.copy()))
            if len(self.undo_stack) > 25:
                self.undo_stack.pop(0)
    def start_draw(self, event):
        if self.original_img is None: return
        
        if event.num == 2:
            self.is_panning = True
            self.pan_start_x = event.x - self.pan_x
            self.pan_start_y = event.y - self.pan_y
            self.canvas.config(cursor="fleur")
            return
            
        self.save_to_undo_stack()
        coords = self.convert_event_to_image_coords(event)
        
        c_ax = self.canvas.canvasx(event.x)
        c_ay = self.canvas.canvasy(event.y)
        
        if self.mode == "rectangle":
            self.rect_start_x = c_ax
            self.rect_start_y = c_ay
            self.current_rect_id = self.canvas.create_rectangle(c_ax, c_ay, c_ax, c_ay, outline="#00adb5", width=2, dash=(4, 4))
        elif coords:
            self.drawing = True
            self.prev_x, self.prev_y = coords
            self.draw_motion(event)

    def draw_motion(self, event):
        if self.original_img is None: return
        
        if self.is_panning:
            self.pan_x = event.x - self.pan_start_x
            self.pan_y = event.y - self.pan_start_y
            self.update_preview()
            return

        c_ax = self.canvas.canvasx(event.x)
        c_ay = self.canvas.canvasy(event.y)

        if self.mode == "rectangle" and self.current_rect_id:
            self.canvas.coords(self.current_rect_id, self.rect_start_x, self.rect_start_y, c_ax, c_ay)
            return

        if not self.drawing: return
        coords = self.convert_event_to_image_coords(event)
        if not coords: return
        
        curr_x, curr_y = coords
        diameter = self.size_slider.get()
        
        if self.mode == "draw":
            cv2.line(self.mask, (self.prev_x, self.prev_y), (curr_x, curr_y), 255, thickness=diameter)
        elif self.mode == "erase":
            cv2.line(self.saved_blur_mask, (self.prev_x, self.prev_y), (curr_x, curr_y), 0, thickness=diameter)
            cv2.line(self.mask, (self.prev_x, self.prev_y), (curr_x, curr_y), 0, thickness=diameter)
            
        self.prev_x, self.prev_y = curr_x, curr_y
        self.update_preview()

    def end_draw(self, event):
        if event.num == 2 or self.is_panning:
            self.is_panning = False
            self.canvas.config(cursor="cross")
            return
            
        self.drawing = False
        if self.mode == "rectangle" and self.current_rect_id:
            self.canvas.delete(self.current_rect_id)
            self.current_rect_id = None
            
            c_ax = self.canvas.canvasx(event.x)
            c_ay = self.canvas.canvasy(event.y)
            
            canvas_start_x = self.rect_start_x - self.img_top_left_x
            canvas_start_y = self.rect_start_y - self.img_top_left_y
            canvas_end_x = c_ax - self.img_top_left_x
            canvas_end_y = c_ay - self.img_top_left_y
            
            x1 = int(canvas_start_x * self.scale_to_orig_x)
            y1 = int(canvas_start_y * self.scale_to_orig_y)
            x2 = int(canvas_end_x * self.scale_to_orig_x)
            y2 = int(canvas_end_y * self.scale_to_orig_y)
            
            h, w = self.original_img.shape[:2]
            start_x, end_x = max(0, min(x1, w-1)), max(0, min(x2, w-1))
            start_y, end_y = max(0, min(y1, h-1)), max(0, min(y2, h-1))
            
            rx_min, rx_max = min(start_x, end_x), max(start_x, end_x)
            ry_min, ry_max = min(start_y, end_y), max(start_y, end_y)
            
            if rx_max > rx_min and ry_max > ry_min:
                cv2.rectangle(self.mask, (rx_min, ry_min), (rx_max, ry_max), 255, -1)
                self.update_preview()

    def on_canvas_wheel_scroll(self, event):
        if self.original_img is None: return
        zoom_factor = 1.1 if event.delta > 0 else 0.9
        new_zoom = self.zoom_level * zoom_factor
        if 0.4 <= new_zoom <= 12.0:
            self.zoom_level = new_zoom
            self.update_preview()

    def trigger_undo(self):
        if not self.undo_stack: return
        prev_mask, prev_saved_mask = self.undo_stack.pop()
        self.mask = prev_mask
        self.saved_blur_mask = prev_saved_mask
        self.update_preview()
    def load_image_standard(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path: return
        
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("IO Engine Error", "Failed to decode target image format array context.")
            return
            
        self.original_img = img
        self.display_img = img.copy()
        self.mask = np.zeros(img.shape[:2], dtype=np.uint8)
        self.saved_blur_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        self.loaded_file_path = file_path
        self.undo_stack.clear()
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.update_preview()

    def strip_active_metadata_action(self):
        if self.original_img is None: return
        self.save_to_undo_stack()
        self.original_img = strip_forensic_metadata(self.original_img)
        messagebox.showinfo("Forensic Cleared", "Deep structure byte-wipe executed. All tracking fields removed.")

    def trigger_decrypt_action(self):
        if self.original_img is None or not self.loaded_file_path: return
        password = self.pass_var.get()
        if not password:
            messagebox.showwarning("Cypher Initialization", "Encryption key configuration profile is empty.")
            return
            
        try:
            encrypted_payload = decode_stego(self.loaded_file_path, self.original_img)
            decrypted_payload = decrypt_data(encrypted_payload, password)
            
            mask_len, orig_len = struct.unpack('>II', decrypted_payload[:8])
            orig_start = 8 + mask_len
            orig_bytes = decrypted_payload[orig_start:orig_start + orig_len]
            
            nparr_orig = np.frombuffer(orig_bytes, np.uint8)
            
            # REVEAL CLEAN RESTORED IMAGE: Completely clear mask frames to show pure pixels instantly
            self.original_img = cv2.imdecode(nparr_orig, cv2.IMREAD_COLOR)
            self.saved_blur_mask = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
            self.mask = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
            self.undo_stack.clear()
            
            self.update_preview()
            messagebox.showinfo("Decryption Success", "Valid matching crypto-key parsed. Pristine original image fully restored on the canvas.")
        except Exception:
            messagebox.showerror("Crypto Failure", "Authentication handshake failed. Key profile mismatches canvas payload structural hashes.")

    def auto_detect_faces(self):
        if self.original_img is None: return
        self.save_to_undo_stack()
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(self.mask, (x, y), (x + w, y + h), 255, -1)
            
        self.update_preview()

    def apply_blur_render(self):
        if self.original_img is None: return
        if not np.any(self.mask == 255): return
            
        self.save_to_undo_stack()
        self.saved_blur_mask = cv2.bitwise_or(self.saved_blur_mask, self.mask)
        self.mask = np.zeros(self.original_img.shape[:2], dtype=np.uint8)
        self.update_preview()

    def encrypt_and_save(self):
        if self.original_img is None: return
        if np.any(self.mask == 255): self.apply_blur_render()
            
        if not np.any(self.saved_blur_mask == 255):
            messagebox.showwarning("Warning", "No modifications detected on masking plane arrays.")
            return
            
        password = self.pass_var.get()
        if not password:
            messagebox.showwarning("Key Signature Missing", "Set an execution password inside the system fields prior container wrapping.")
            return
        
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
        if not output_path: return

        clean_orig = strip_forensic_metadata(self.original_img)

        _, encoded_mask = cv2.imencode('.png', self.saved_blur_mask)
        _, encoded_orig = cv2.imencode('.png', clean_orig)
        
        payload = struct.pack('>II', len(encoded_mask.tobytes()), len(encoded_orig.tobytes())) + encoded_mask.tobytes() + encoded_orig.tobytes()

        try:
            encrypted_payload = encrypt_data(payload, password)
            h_b, w_b = clean_orig.shape[:2]
            kernel_percentage = self.blur_rad_slider.get() / 100.0
            
            if self.blur_style == "pixelate":
                block_factor = max(int(max(h_b, w_b) * (kernel_percentage * 0.22)), 4)
                small_matrix = cv2.resize(clean_orig, (max(1, w_b // block_factor), max(1, h_b // block_factor)), interpolation=cv2.INTER_LINEAR)
                obfuscated_entire = cv2.resize(small_matrix, (w_b, h_b), interpolation=cv2.INTER_NEAREST)
                salt_pepper_noise = np.random.randint(0, 15, (h_b, w_b, 3), dtype=np.int16)
                obfuscated_entire = np.clip(obfuscated_entire.astype(np.int16) + salt_pepper_noise, 0, 255).astype(np.uint8)
            else:
                kernel_size = int(max(h_b, w_b) * kernel_percentage) | 1
                obfuscated_entire = cv2.GaussianBlur(clean_orig, (kernel_size, kernel_size), 0)
                
            mask_3ch = cv2.merge([self.saved_blur_mask, self.saved_blur_mask, self.saved_blur_mask])
            flat_display = np.where(mask_3ch == 255, obfuscated_entire, clean_orig)
            
            encode_stego(self.loaded_file_path, output_path, flat_display, encrypted_payload)
            messagebox.showinfo("Success", "Stego-container packaged and signed securely.")
        except Exception as e:
            messagebox.showerror("Packaging Aborted", str(e))

    def process_bulk_folder(self):
        input_dir = filedialog.askdirectory(title="Select Target Folder Input")
        if not input_dir: return
        
        password = self.pass_var.get()
        if not password:
            messagebox.showwarning("Bulk Handshake Warning", "Set a global batch password string inside the UI parameters panel first.")
            return
        
        output_dir = os.path.join(input_dir, "processed_faces")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        supported_exts = (".png", ".jpg", ".jpeg", ".bmp")
        processed_count = 0
        
        for file_name in os.listdir(input_dir):
            if file_name.lower().endswith(supported_exts):
                file_path = os.path.join(input_dir, file_name)
                img = cv2.imread(file_path)
                if img is None: continue
                
                clean_img = strip_forensic_metadata(img)
                gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) == 0: continue  
                
                bulk_mask = np.zeros(clean_img.shape[:2], dtype=np.uint8)
                for (x, y, w, h) in faces:
                    cv2.rectangle(bulk_mask, (x, y), (x + w, y + h), 255, -1)
                    
                h_b, w_b = clean_img.shape[:2]
                kernel_percentage = self.blur_rad_slider.get() / 100.0
                
                if self.blur_style == "pixelate":
                    block_factor = max(int(max(h_b, w_b) * (kernel_percentage * 0.22)), 4)
                    small_matrix = cv2.resize(clean_img, (max(1, w_b // block_factor), max(1, h_b // block_factor)), interpolation=cv2.INTER_LINEAR)
                    obfuscated_entire = cv2.resize(small_matrix, (w_b, h_b), interpolation=cv2.INTER_NEAREST)
                    salt_pepper_noise = np.random.randint(0, 15, (h_b, w_b, 3), dtype=np.int16)
                    obfuscated_entire = np.clip(obfuscated_entire.astype(np.int16) + salt_pepper_noise, 0, 255).astype(np.uint8)
                else:
                    kernel_size = int(max(h_b, w_b) * kernel_percentage) | 1
                    obfuscated_entire = cv2.GaussianBlur(clean_img, (kernel_size, kernel_size), 0)
                
                mask_3ch = cv2.merge([bulk_mask, bulk_mask, bulk_mask])
                bulk_display = np.where(mask_3ch == 255, obfuscated_entire, clean_img)
                
                _, encoded_mask = cv2.imencode('.png', bulk_mask)
                _, encoded_orig = cv2.imencode('.png', clean_img)
                
                payload = struct.pack('>II', len(encoded_mask.tobytes()), len(encoded_orig.tobytes())) + encoded_mask.tobytes() + encoded_orig.tobytes()
                encrypted_payload = encrypt_data(payload, password)
                
                out_file_path = os.path.join(output_dir, os.path.splitext(file_name) + ".png")
                encode_stego(file_path, out_file_path, bulk_display, encrypted_payload)
                processed_count += 1
                
        messagebox.showinfo("Batch Complete", f"Successfully structured {processed_count} files into output array map.")

if __name__ == '__main__':
    root = tk.Tk()
    app = FaceStegoApp(root)
    
    # Event tracking and window configuration bounds
    root.bind("<Configure>", lambda e: app.update_preview() if e.widget == root else None)
    app.canvas.bind("<ButtonPress-1>", app.start_draw)
    app.canvas.bind("<B1-Motion>", app.draw_motion)
    app.canvas.bind("<ButtonRelease-1>", app.end_draw)
    
    # Middle Mouse button bindings for Scroll Pan shifts tracking configurations
    app.canvas.bind("<ButtonPress-2>", app.start_draw)
    app.canvas.bind("<B2-Motion>", app.draw_motion)
    app.canvas.bind("<ButtonRelease-2>", app.end_draw)
    
    # MouseWheel zoom binding structure tracking map assignment
    app.canvas.bind("<MouseWheel>", app.on_canvas_wheel_scroll)
    
    root.mainloop()
