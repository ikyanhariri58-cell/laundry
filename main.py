from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import os
import threading
import ffmpeg

# ==========================================
# LOGIC LAUNDRY PRO (MOVING WM & SMALL SUB)
# ==========================================
def process_video(config, update_status):
    folder_path = config['folder']
    if not os.path.exists(folder_path):
        update_status("Error: Folder tidak ditemukan!")
        return

    out_folder = os.path.join(folder_path, "Hasil_Laundry")
    if not os.path.exists(out_folder): os.makedirs(out_folder)

    # Ambil video
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp4', '.mkv'))]
    
    # Cek Watermark Otomatis (logo.png)
    wm_path = os.path.join(folder_path, "logo.png")
    has_wm = os.path.exists(wm_path)
    
    if not files:
        update_status("Zonk! Gak ada video di folder itu.")
        return

    total = len(files)
    update_status(f"Target: {total} Video\nWM: {'Ada' if has_wm else 'Tidak'}")

    for i, filename in enumerate(files):
        in_path = os.path.join(folder_path, filename)
        out_path = os.path.join(out_folder, f"CLEAN_{filename}")
        
        # Cek Subtitle Otomatis
        srt_name = os.path.splitext(filename)[0] + ".srt"
        srt_path = os.path.join(folder_path, srt_name)
        has_sub = os.path.exists(srt_path)

        update_status(f"[{i+1}/{total}] Proses: {filename}...")

        try:
            # 1. Input Video
            stream = ffmpeg.input(in_path)
            v = stream.video
            a = stream.audio

            # 2. Trim (Potong Durasi)
            probe = ffmpeg.probe(in_path)
            duration = float(probe['format']['duration'])
            
            trim_start = float(config['trim_start'])
            trim_end = float(config['trim_end'])
            new_duration = duration - trim_start - trim_end
            
            if new_duration > 0 and (trim_start > 0 or trim_end > 0):
                v = v.filter('trim', start=trim_start, duration=new_duration).filter('setpts', 'PTS-STARTPTS')
                a = a.filter('atrim', start=trim_start, duration=new_duration).filter('asetpts', 'PTS-STARTPTS')

            # 3. Efek Visual Dasar
            if config['speed']:
                v = v.filter('setpts', '0.952*PTS') 
                a = a.filter('atempo', 1.05)
            
            if config['noise']:
                v = v.filter('noise', alls=5, allf='t')

            # 4. WATERMARK BERGERAK (Anti-Copyright Ultimate)
            if has_wm:
                wm = ffmpeg.input(wm_path).filter('scale', 150, -1) # Resize logo jadi kecil (lebar 150px)
                
                if config['moving_wm']:
                    # Rumus Matematika: Bergerak memantul pelan (Diagonal Bouncing)
                    overlay_cmd = "x='mod(t*30,W-w)':y='mod(t*15,H-h)'"
                else:
                    # Diem di Pojok Kanan Atas (Default)
                    overlay_cmd = "x=W-w-20:y=20"
                
                v = ffmpeg.overlay(v, wm, **parse_overlay(overlay_cmd))

            # 5. Burn Subtitle (Font Size 12)
            if has_sub:
                style = "FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,MarginV=20"
                safe_srt = srt_path.replace("\\", "/")
                v = v.filter('subtitles', safe_srt, force_style=style)

            # 6. Render
            args = {'vcodec': 'libx264', 'preset': 'superfast', 'crf': 28, 'acodec': 'aac'}
            if config['remove_meta']:
                args['map_metadata'] = -1

            runner = ffmpeg.output(v, a, out_path, **args)
            runner.run(quiet=True, overwrite_output=True)

        except Exception as e:
            print(f"Error {filename}: {e}")

    update_status("✅ DONE! Cek folder Hasil_Laundry")

def parse_overlay(cmd_str):
    params = {}
    for part in cmd_str.split(':'):
        if '=' in part:
            key, val = part.split('=', 1)
            params[key] = val
    return params

# ==========================================
# UI APLIKASI
# ==========================================
class LaundryApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Judul GANTI JADI LAUNDRY MOBILE
        root.add_widget(Label(text="LAUNDRY MOBILE v3", font_size=22, bold=True, size_hint=(1, 0.1), color=(0,1,1,1)))

        # Input Path
        root.add_widget(Label(text="Lokasi Folder (Wajib ada logo.png jika mau WM):", size_hint=(1, None), height=30))
        self.path_input = TextInput(text="/sdcard/Download/Bahan_Video", multiline=False, size_hint=(1, None), height=50)
        root.add_widget(self.path_input)

        # Setting Grid
        settings = GridLayout(cols=2, spacing=10, size_hint=(1, 0.35))
        
        # Kiri
        col1 = BoxLayout(orientation='vertical')
        
        row_speed = BoxLayout()
        self.chk_speed = CheckBox(active=True)
        row_speed.add_widget(self.chk_speed)
        row_speed.add_widget(Label(text="Speed 1.05x"))
        col1.add_widget(row_speed)

        row_noise = BoxLayout()
        self.chk_noise = CheckBox(active=True)
        row_noise.add_widget(self.chk_noise)
        row_noise.add_widget(Label(text="Noise"))
        col1.add_widget(row_noise)

        row_wm = BoxLayout()
        self.chk_moving = CheckBox(active=True) # Default gerak
        row_wm.add_widget(self.chk_moving)
        row_wm.add_widget(Label(text="WM Gerak"))
        col1.add_widget(row_wm)
        
        settings.add_widget(col1)

        # Kanan (Trim)
        col2 = BoxLayout(orientation='vertical')
        
        col2.add_widget(Label(text="Potong Awal (detik):"))
        self.trim_start = TextInput(text="0", multiline=False, input_filter='float')
        col2.add_widget(self.trim_start)
        
        col2.add_widget(Label(text="Potong Akhir (detik):"))
        self.trim_end = TextInput(text="0", multiline=False, input_filter='float')
        col2.add_widget(self.trim_end)
        
        # Checkbox Hapus Metadata (Selalu Aktif tapi hidden)
        self.chk_meta = CheckBox(active=True, size_hint=(0,0), opacity=0) 
        root.add_widget(self.chk_meta) 

        settings.add_widget(col2)
        root.add_widget(settings)

        # Tombol
        self.btn_run = Button(text="GAS CUCI! 🚀", font_size=20, background_color=(0, 0.8, 0, 1), size_hint=(1, 0.15))
        self.btn_run.bind(on_press=self.start_laundry)
        root.add_widget(self.btn_run)

        # Log
        self.status = Label(text="Siap...", font_size=14, size_hint=(1, 0.3))
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
            'remove_meta': self.chk_meta.active,
            'moving_wm': self.chk_moving.active,
            'trim_start': self.trim_start.text,
            'trim_end': self.trim_end.text
        }
        
        self.btn_run.disabled = True
        self.status.text = "Memulai mesin..."
        threading.Thread(target=process_video, args=(config, self.update_label)).start()
        threading.Timer(5.0, lambda: setattr(self.btn_run, 'disabled', False)).start()

if __name__ == '__main__':
    LaundryApp().run()