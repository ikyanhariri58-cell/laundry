from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
import os
import shutil
import subprocess
import threading

# ==========================================
# LOGIC SETUP MESIN (WAJIB BUAT ANDROID)
# ==========================================
def setup_ffmpeg(update_status):
    """Menyiapkan mesin FFmpeg agar bisa dijalankan di Android"""
    app_folder = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_source = os.path.join(app_folder, 'ffmpeg')
    
    # Lokasi internal HP yang punya izin eksekusi
    internal_dir = App.get_running_app().user_data_dir
    ffmpeg_target = os.path.join(internal_dir, 'ffmpeg')

    if not os.path.exists(ffmpeg_target):
        update_status("Menyiapkan mesin cuci video...")
        try:
            shutil.copyfile(ffmpeg_source, ffmpeg_target)
            os.chmod(ffmpeg_target, 0o755) # Izin eksekusi (chmod +x)
            update_status("Mesin siap digunakan!")
        except Exception as e:
            update_status(f"Gagal setup: {e}")
            return None
    return ffmpeg_target

# ==========================================
# LOGIC PROSES VIDEO (Pake Subprocess)
# ==========================================
def process_video(config, update_status):
    ffmpeg_exe = setup_ffmpeg(update_status)
    if not ffmpeg_exe: return

    folder_path = config['folder']
    if not os.path.exists(folder_path):
        update_status("Error: Folder tidak ada!")
        return

    out_folder = os.path.join(folder_path, "Hasil_Laundry")
    if not os.path.exists(out_folder): os.makedirs(out_folder)

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp4', '.mkv'))]
    wm_path = os.path.join(folder_path, "logo.png")
    has_wm = os.path.exists(wm_path)

    if not files:
        update_status("Zonk! Gak ada video.")
        return

    total = len(files)
    for i, filename in enumerate(files):
        in_path = os.path.join(folder_path, filename)
        out_path = os.path.join(out_folder, f"CLEAN_{filename}")
        update_status(f"[{i+1}/{total}] Mencuci: {filename}")

        # --- RAKIT PERINTAH FFmpeg ---
        cmd = [ffmpeg_exe, "-y", "-i", in_path]
        
        # Filter Chain
        filters = []
        
        # 1. Watermark Bergerak
        if has_wm:
            cmd.extend(["-i", wm_path])
            filters.append("[1:v]scale=150:-1[wm]")
            if config['moving_wm']:
                filters.append("[0:v][wm]overlay=x='mod(t*30,W-w)':y='mod(t*15,H-h)'[v1]")
            else:
                filters.append("[0:v][wm]overlay=x=W-w-20:y=20[v1]")
            v_label = "[v1]"
        else:
            v_label = "[0:v]"

        # 2. Speed & Noise
        v_filters = []
        a_filters = []
        if config['speed']:
            v_filters.append("setpts=0.95*PTS")
            a_filters.append("atempo=1.05")
        if config['noise']:
            v_filters.append("noise=alls=5:allf=t")
        
        if v_filters:
            filters.append(f"{v_label}{','.join(v_filters)}[v_final]")
            v_label = "[v_final]"

        # Gabungkan Filter
        if filters:
            cmd.extend(["-filter_complex", ";".join(filters), "-map", v_label, "-map", "0:a"])
        
        if a_filters:
            cmd.extend(["-af", ",".join(a_filters)])

        # Metadata & Output
        if config['remove_meta']:
            cmd.extend(["-map_metadata", "-1"])
            
        cmd.extend(["-preset", "superfast", "-crf", "28", out_path])

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except:
            print(f"Gagal di file: {filename}")

    update_status("✅ SELESAI! Cek folder Hasil_Laundry")

# ==========================================
# UI APLIKASI
# ==========================================
class LaundryApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        root.add_widget(Label(text="LAUNDRY MOBILE PRO", font_size=22, bold=True, color=(0,1,1,1)))
        
        self.path_input = TextInput(text="/sdcard/Download/Bahan", multiline=False, size_hint=(1, None), height=50)
        root.add_widget(self.path_input)

        settings = GridLayout(cols=2, spacing=10)
        self.chk_speed = CheckBox(active=True); settings.add_widget(self.chk_speed); settings.add_widget(Label(text="Speed 1.05x"))
        self.chk_noise = CheckBox(active=True); settings.add_widget(self.chk_noise); settings.add_widget(Label(text="Noise AI"))
        self.chk_moving = CheckBox(active=True); settings.add_widget(self.chk_moving); settings.add_widget(Label(text="WM Gerak"))
        root.add_widget(settings)

        self.btn_run = Button(text="GAS CUCI! 🚀", font_size=20, background_color=(0, 0.8, 0, 1))
        self.btn_run.bind(on_press=self.start_laundry)
        root.add_widget(self.btn_run)

        self.status = Label(text="Siap...", size_hint=(1, 0.3))
        root.add_widget(self.status)
        return root

    def update_label(self, text):
        def update(dt): self.status.text = text
        Clock.schedule_once(update)

    def start_laundry(self, instance):
        config = {
            'folder': self.path_input.text,
            'speed': self.chk_speed.active,
            'noise': self.chk_noise.active,
            'remove_meta': True,
            'moving_wm': self.chk_moving.active
        }
        self.btn_run.disabled = True
        threading.Thread(target=process_video, args=(config, self.update_label)).start()
        threading.Timer(10.0, lambda: setattr(self.btn_run, 'disabled', False)).start()

if __name__ == '__main__':
    LaundryApp().run()
