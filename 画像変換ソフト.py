import os
import sys
import webbrowser
import customtkinter as ctk
from tkinter import colorchooser  # 💡 色選択ダイアログを使うために追加
from PIL import Image, ImageOps

# 画面の初期設定
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    """ PyInstallerの一時フォルダ、または通常の実行フォルダから絶対パスを取得する """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("画像変換アプリ")
        self.geometry("500x780")
        ico_path = get_resource_path("ga.ico")
        self.iconbitmap(ico_path)


        # 状態保持用変数
        self.original_img = None
        self.processed_img = None
        self.selected_rgb = None  # 💡 選ばれた(R, G, B)をここに保存します

        # --- UIレイアウトの構築 ---
        self.main_frame = ctk.CTkScrollableFrame(self, width=460, height=740)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="画像変換アプリ", font=("Arial", 20, "bold")).pack(pady=10)

        # ファイル選択
        self.btn_upload = ctk.CTkButton(self.main_frame, text="画像を選択", command=self.load_image)
        self.btn_upload.pack(pady=10)
        self.lbl_file_status = ctk.CTkLabel(self.main_frame, text="ファイルが選択されていません", text_color="gray")
        self.lbl_file_status.pack()

        # モザイク度
        ctk.CTkLabel(self.main_frame, text="モザイク度 (0-7):").pack(pady=(15, 0))
        self.slider_mosaic = ctk.CTkSlider(self.main_frame, from_=0, to=7, number_of_steps=7, command=self.trigger_update)
        self.slider_mosaic.set(0)
        self.slider_mosaic.pack(pady=5)

        # モード選択（チェックボックス）
        self.var_dark = ctk.BooleanVar()
        self.chk_dark = ctk.CTkCheckBox(self.main_frame, text="ダークモード", variable=self.var_dark, command=self.trigger_update)
        self.chk_dark.pack(pady=5)

        self.var_sirokuro = ctk.BooleanVar()
        self.chk_sirokuro = ctk.CTkCheckBox(self.main_frame, text="白黒モード", variable=self.var_sirokuro, command=self.trigger_update)
        self.chk_sirokuro.pack(pady=5)

        # 💡 かぶせる色（ここをご提示のロジックベースに改良しました）
        ctk.CTkLabel(self.main_frame, text="かぶせる色:").pack(pady=(15, 0))
        self.color_buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.color_buttons_frame.pack(pady=5)
        
        # 色を選択するボタン
        self.btn_color_pick = ctk.CTkButton(self.color_buttons_frame, text="色を選択...", width=120, command=self.choose_color)
        self.btn_color_pick.grid(row=0, column=0, padx=5)
        
        # 色を初期化するボタン
        self.btn_color_reset = ctk.CTkButton(self.color_buttons_frame, text="色を初期化", width=100, fg_color="gray", hover_color="#555555", command=self.reset_color)
        self.btn_color_reset.grid(row=0, column=1, padx=5)

        # 現在選ばれている色コードを表示するラベル
        self.lbl_color_code = ctk.CTkLabel(self.main_frame, text="選択されていません", text_color="gray")
        self.lbl_color_code.pack(pady=2)

        # 保存形式
        ctk.CTkLabel(self.main_frame, text="保存形式:").pack(pady=(15, 0))
        self.var_format = ctk.StringVar(value="PNG")
        self.rb_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.rb_frame.pack()
        ctk.CTkRadioButton(self.rb_frame, text="PNG", variable=self.var_format, value="PNG", command=self.trigger_update).grid(row=0, column=0, padx=10)
        ctk.CTkRadioButton(self.rb_frame, text="JPG", variable=self.var_format, value="JPEG", command=self.trigger_update).grid(row=0, column=1, padx=10)

        # 保存ファイル名
        self.entry_filename = ctk.CTkEntry(self.main_frame, placeholder_text="保存ファイル名")
        self.entry_filename.insert(0, "new_image")
        self.entry_filename.pack(pady=15)

        # 変換して保存ボタン
        self.btn_process = ctk.CTkButton(self.main_frame, text="変換して保存", fg_color="#007bff", hover_color="#0056b3", command=self.save_image)
        self.btn_process.pack(pady=10)

        # プレビューエリア
        self.lbl_preview = ctk.CTkLabel(self.main_frame, text="")
        self.lbl_preview.pack(pady=15)

        # 🛠️ 前回の「padding」エラーを修正したGoogle検索エリア
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="#e0e0e0" if ctk.get_appearance_mode()=="Light" else "#333333")
        self.search_frame.pack(pady=20, padx=10, ipady=10, fill="x")
        
        ctk.CTkLabel(self.search_frame, text="加工する画像を調べるにはこちら：").pack(pady=(5, 0))
        self.entry_search = ctk.CTkEntry(self.search_frame, width=200)
        self.entry_search.insert(0, "画像素材")
        self.entry_search.pack(pady=5)
        self.btn_search = ctk.CTkButton(self.search_frame, text="Googleで検索", fg_color="#28a745", hover_color="#218838", command=self.google_search)
        self.btn_search.pack(pady=5)

    # --- ロジック関数 ---
    def load_image(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if file_path:
            self.lbl_file_status.configure(text=os.path.basename(file_path), text_color="green")
            self.original_img = Image.open(file_path).convert("RGBA")
            self.update_preview()

    def trigger_update(self, *args):
        if self.original_img:
            self.update_preview()

    def choose_color(self):
        # OS標準のカラーピッカーを開く
        color = colorchooser.askcolor(title="色を選択する")
        if color[0]:  # 色がキャンセルされずに選ばれた場合
            # color[0] は (R, G, B) の浮動小数点数なので、int型に変換して保存
            self.selected_rgb = tuple(map(int, color[0])) 
            # 選択されたカラーコード（例: #ff0000）をラベルに表示
            self.lbl_color_code.configure(text=f"選択中: {color[1]}", text_color=color[1])
            # ボタンの背景色を選んだ色に変える
            self.btn_color_pick.configure(fg_color=color[1])
            
            # 色を選んだら即座にプレビューに反映（update_previewを実行）
            self.trigger_update()

    def reset_color(self):
        self.selected_rgb = None
        self.lbl_color_code.configure(text="選択されていません", text_color="gray")
        # ボタンの色をデフォルト（戻す）
        self.btn_color_pick.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.trigger_update()

    def update_preview(self):
        if not self.original_img:
            return

        img = self.original_img.copy()
        w, h = img.size
        mosaic_val = int(self.slider_mosaic.get())
        dark_mode = self.var_dark.get()
        sirokuro_mode = self.var_sirokuro.get()

        # 1. モザイク処理
        if mosaic_val > 0:
            c = 2 ** (9 - (mosaic_val + 1))
            f, g = int(w / (300 / c)), int(h / (300 / c))
            if f > 0 and g > 0:
                img = img.resize((f, g), resample=Image.NEAREST).resize((w, h), resample=Image.NEAREST)

        # 2. 色をかぶせる (選ばれたRGBを使用)
        if self.selected_rgb:
            alpha = 100  # 透明度
            color_layer = Image.new("RGBA", img.size, self.selected_rgb + (alpha,))
            img = Image.alpha_composite(img, color_layer)

        # 3. ダークモード・白黒モード
        if dark_mode:
            if sirokuro_mode:
                img = img.convert("L").convert("1")
            else:
                img = img.convert("L")
        elif sirokuro_mode:
            img = img.convert("1")

        self.processed_img = img

        # 画面表示用に縮小プレビューを作成
        preview_size = 250
        ratio = min(preview_size / w, preview_size / h)
        preview_w, preview_h = int(w * ratio), int(h * ratio)
        
        # プレビュー表示の更新
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(preview_w, preview_h))
        self.lbl_preview.configure(image=ctk_img)
        self.lbl_preview.image = ctk_img

    def save_image(self):
        if self.processed_img is None:
            ctk.filedialog.messagebox.showerror("エラー", "先に画像をアップロードしてください")
            return

        file_name = self.entry_filename.get()
        selected_format = self.var_format.get()
        ext = ".jpg" if selected_format == "JPEG" else ".png"

        save_path = ctk.filedialog.asksaveasfilename(initialfile=f"{file_name}{ext}", filetypes=[(f"{selected_format} files", f"*{ext}")])
        
        if save_path:
            if selected_format == "JPEG":
                rgb_img = Image.new("RGB", self.processed_img.size, (255, 255, 255))
                mask = self.processed_img.split()[3] if self.processed_img.mode == 'RGBA' else None
                rgb_img.paste(self.processed_img, mask=mask)
                rgb_img.save(save_path, format="JPEG", quality=90)
            else:
                self.processed_img.save(save_path, format="PNG")
            
            ctk.filedialog.messagebox.showinfo("成功", f"画像を保存しました:\n{save_path}")

    def google_search(self):
        query = self.entry_search.get()
        url = f"https://www.google.com/search?q={query}&udm=2"
        webbrowser.open(url)

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()