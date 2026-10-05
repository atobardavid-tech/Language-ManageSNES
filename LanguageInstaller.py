import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sys
import xml.etree.ElementTree as ET

# Detect whether the program is running as an EXE or as a Python script
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

LANGUAGES_DIR = os.path.join(BASE_DIR, "Languages")

# Rutas por defecto iniciales
DEFAULT_PSNES_DIR = os.path.join(APP_DIR, "psnes")
DEFAULT_ROMS_DIR = os.path.join(DEFAULT_PSNES_DIR, "roms")
DEFAULT_SOURCE_GAMES_DIR = os.path.join(APP_DIR, "games")
DEFAULT_SOURCE_IMAGES_DIR = os.path.join(DEFAULT_SOURCE_GAMES_DIR, "media", "images")

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)

def open_game_manager(language):
    window.withdraw()
     
    manager_win = tk.Toplevel(window)
    manager_win.title("Game Manager - PSNES")
    manager_win.geometry("1100x800") 
    manager_win.resizable(True, True)
     
    icon_path = resource_path("icono.ico")
    if os.path.exists(icon_path):
        manager_win.iconbitmap(icon_path)

    # Variables de rutas configurables (inicializadas con los valores por defecto)
    current_source_games = DEFAULT_SOURCE_GAMES_DIR
    current_source_images = DEFAULT_SOURCE_IMAGES_DIR
    current_roms_dir = DEFAULT_ROMS_DIR

    # Cargar y parsear el archivo gamelist.xml del idioma seleccionado usando <path>
    gamelist_descriptions = {}
    selected_gamelist_path = os.path.join(LANGUAGES_DIR, language, "gamelist.xml")
    if os.path.exists(selected_gamelist_path):
        try:
            tree = ET.parse(selected_gamelist_path)
            root = tree.getroot()
            for game in root.findall("game"):
                path_elem = game.find("path")
                desc_elem = game.find("desc")
                if path_elem is not None and path_elem.text:
                    # Extraer el nombre base del archivo desde el path (ej: "./roms/juego.smc" -> "juego")
                    raw_path = path_elem.text.strip()
                    base_file_name = os.path.basename(raw_path)
                    game_key, _ = os.path.splitext(base_file_name)
                    
                    game_key = game_key.lower()
                    desc_text = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else "No description available."
                    gamelist_descriptions[game_key] = desc_text
        except Exception:
            pass

    # Contenedor principal
    main_frame = tk.Frame(manager_win)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Panel Superior para Configurar Rutas ---
    paths_frame = tk.LabelFrame(main_frame, text=" Directory Configuration ", font=("Segoe UI", 9, "bold"))
    paths_frame.pack(fill=tk.X, padx=0, pady=(0, 8))

    # Ruta de Origen (Games)
    src_path_frame = tk.Frame(paths_frame)
    src_path_frame.pack(fill=tk.X, padx=8, pady=4)
    tk.Label(src_path_frame, text="Source Games Dir:", font=("Segoe UI", 9), width=18, anchor="w").pack(side=tk.LEFT)
    src_path_var = tk.StringVar(value=current_source_games)
    src_path_entry = tk.Entry(src_path_frame, textvariable=src_path_var, font=("Segoe UI", 9), state="readonly")
    src_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def change_source_dir():
        nonlocal current_source_games, current_source_images
        new_dir = filedialog.askdirectory(initialdir=current_source_games, title="Select Source Games Folder", parent=manager_win)
        if new_dir:
            current_source_games = new_dir
            src_path_var.set(current_source_games)
            current_source_images = os.path.join(current_source_games, "media", "images")
            src_img_path_var.set(current_source_images)
            populate_lists(search_left_var.get(), search_right_var.get())

    src_btn = tk.Button(src_path_frame, text="Browse...", command=change_source_dir, font=("Segoe UI", 9), width=10)
    src_btn.pack(side=tk.RIGHT)

    # Ruta de Imágenes de Origen (Source Images)
    src_img_path_frame = tk.Frame(paths_frame)
    src_img_path_frame.pack(fill=tk.X, padx=8, pady=4)
    tk.Label(src_img_path_frame, text="Source Images Dir:", font=("Segoe UI", 9), width=18, anchor="w").pack(side=tk.LEFT)
    src_img_path_var = tk.StringVar(value=current_source_images)
    src_img_path_entry = tk.Entry(src_img_path_frame, textvariable=src_img_path_var, font=("Segoe UI", 9), state="readonly")
    src_img_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def change_source_images_dir():
        nonlocal current_source_images
        new_dir = filedialog.askdirectory(initialdir=current_source_images, title="Select Source Images Folder", parent=manager_win)
        if new_dir:
            current_source_images = new_dir
            src_img_path_var.set(current_source_images)

    src_img_btn = tk.Button(src_img_path_frame, text="Browse...", command=change_source_images_dir, font=("Segoe UI", 9), width=10)
    src_img_btn.pack(side=tk.RIGHT)

    # Ruta de Destino (Roms)
    dest_path_frame = tk.Frame(paths_frame)
    dest_path_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
    tk.Label(dest_path_frame, text="Destination ROMs:", font=("Segoe UI", 9), width=18, anchor="w").pack(side=tk.LEFT)
    dest_path_var = tk.StringVar(value=current_roms_dir)
    dest_path_entry = tk.Entry(dest_path_frame, textvariable=dest_path_var, font=("Segoe UI", 9), state="readonly")
    dest_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def change_dest_dir():
        nonlocal current_roms_dir
        new_dir = filedialog.askdirectory(initialdir=current_roms_dir, title="Select Destination ROMs Folder", parent=manager_win)
        if new_dir:
            current_roms_dir = new_dir
            dest_path_var.set(current_roms_dir)
            populate_lists(search_left_var.get(), search_right_var.get())

    dest_btn = tk.Button(dest_path_frame, text="Browse...", command=change_dest_dir, font=("Segoe UI", 9), width=10)
    dest_btn.pack(side=tk.RIGHT)

    # Contenedor inferior para las columnas de juegos y previsualización
    content_sub_frame = tk.Frame(main_frame)
    content_sub_frame.pack(fill=tk.BOTH, expand=True)

    # Panel Izquierdo: Juegos disponibles
    left_container = tk.LabelFrame(content_sub_frame, text=" Available Games ", font=("Segoe UI", 10, "bold"))
    left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Panel Central
    center_frame = tk.Frame(content_sub_frame, width=320, bg="#f0f0f0", highlightthickness=1, highlightbackground="#ccc")
    center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
    center_frame.pack_propagate(False)

    tk.Label(center_frame, text="Image Preview", font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(pady=(6, 2))
     
    img_preview_label = tk.Label(center_frame, text="No image available", bg="#e0e0e0", fg="#666")
    img_preview_label.pack(padx=10, pady=(0, 6))

    tk.Label(center_frame, text="Description", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=(0, 2))
     
    desc_text_box = tk.Text(center_frame, wrap=tk.WORD, font=("Segoe UI", 12), bg="white", fg="#333", height=10, state=tk.DISABLED)
    desc_text_box.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

    # Panel Derecho: Juegos instalados
    right_container = tk.LabelFrame(content_sub_frame, text=" Installed Games ", font=("Segoe UI", 10, "bold"))
    right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    current_preview_image = None

    def update_preview_and_description(filename, is_installed_list=False):
        nonlocal current_preview_image
        base_name, _ = os.path.splitext(filename)
        found_img = None
         
        dest_images_dir = os.path.join(current_roms_dir, "media", "images")
         
        img_search_dirs = [
            dest_images_dir,
            current_source_images
        ] if is_installed_list else [
            current_source_images,
            dest_images_dir
        ]
         
        for search_dir in img_search_dirs:
            for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]:
                img_path = os.path.join(search_dir, base_name + ext)
                if os.path.exists(img_path):
                    found_img = img_path
                    break
            if found_img:
                break
         
        if found_img:
            try:
                pil_img = Image.open(found_img)
                target_width = 300
                w_percent = (target_width / float(pil_img.size[0]))
                h_size = int((float(pil_img.size[1]) * float(w_percent)))
                 
                max_height = 240
                if h_size > max_height:
                     h_size = max_height
                     h_percent = (max_height / float(pil_img.size[1]))
                     target_width = int((float(pil_img.size[0]) * float(h_percent)))

                pil_img = pil_img.resize((target_width, h_size), Image.Resampling.LANCZOS)
                current_preview_image = ImageTk.PhotoImage(pil_img)
                img_preview_label.config(image=current_preview_image, text="")
            except Exception as e:
                print(f"Error loading image: {e}")
                img_preview_label.config(image="", text="Error loading image")
        else:
            img_preview_label.config(image="", text="No image available")

        # Actualizar descripción basada en la coincidencia del <path> mapeado
        desc_text_box.config(state=tk.NORMAL)
        desc_text_box.delete("1.0", tk.END)
         
        match_key = base_name.strip().lower()
        description_found = "No description available for this game."
         
        for k, v in gamelist_descriptions.items():
            if match_key == k or match_key in k or k in match_key:
                description_found = v
                break
                 
        desc_text_box.insert(tk.END, description_found)
        desc_text_box.config(state=tk.DISABLED)

    # --- CONFIGURACIÓN LISTA IZQUIERDA (DISPONIBLES) ---
    search_left_frame = tk.Frame(left_container)
    search_left_frame.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(search_left_frame, text="Search:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 3))
    search_left_var = tk.StringVar()
    search_left_entry = tk.Entry(search_left_frame, textvariable=search_left_var, width=15)
    search_left_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    select_all_left_var = tk.BooleanVar(value=False)
    def toggle_select_all_left():
        state = select_all_left_var.get()
        for fname, var in game_vars.items():
            if search_left_var.get().lower() in fname.lower():
                var.set(state)

    select_all_left_chk = tk.Checkbutton(search_left_frame, text="Select All", variable=select_all_left_var, command=toggle_select_all_left, font=("Segoe UI", 9))
    select_all_left_chk.pack(side=tk.RIGHT)

    canvas_left_frame = tk.Frame(left_container)
    canvas_left_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    canvas_l = tk.Canvas(canvas_left_frame, bg="white", highlightthickness=1, highlightbackground="#ccc")
    scrollbar_l = ttk.Scrollbar(canvas_left_frame, orient="vertical", command=canvas_l.yview)
    scrollable_left = tk.Frame(canvas_l, bg="white")

    scrollable_left.bind("<Configure>", lambda e: canvas_l.configure(scrollregion=canvas_l.bbox("all")))
    canvas_l.create_window((0, 0), window=scrollable_left, anchor="nw")
    canvas_l.configure(yscrollcommand=scrollbar_l.set)
    canvas_l.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_l.pack(side=tk.RIGHT, fill=tk.Y)

    # --- CONFIGURACIÓN LISTA DERECHA (INSTALADOS) ---
    search_right_frame = tk.Frame(right_container)
    search_right_frame.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(search_right_frame, text="Search:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 3))
    search_right_var = tk.StringVar()
    search_right_entry = tk.Entry(search_right_frame, textvariable=search_right_var, width=15)
    search_right_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    select_all_right_var = tk.BooleanVar(value=False)
    def toggle_select_all_right():
        state = select_all_right_var.get()
        for fname, var in installed_vars.items():
            if search_right_var.get().lower() in fname.lower():
                var.set(state)

    select_all_right_chk = tk.Checkbutton(search_right_frame, text="Select All", variable=select_all_right_var, command=toggle_select_all_right, font=("Segoe UI", 9))
    select_all_right_chk.pack(side=tk.RIGHT)

    canvas_right_frame = tk.Frame(right_container)
    canvas_right_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    canvas_r = tk.Canvas(canvas_right_frame, bg="white", highlightthickness=1, highlightbackground="#ccc")
    scrollbar_r = ttk.Scrollbar(canvas_right_frame, orient="vertical", command=canvas_r.yview)
    scrollable_right = tk.Frame(canvas_r, bg="white")

    scrollable_right.bind("<Configure>", lambda e: canvas_r.configure(scrollregion=canvas_r.bbox("all")))
    canvas_r.create_window((0, 0), window=scrollable_right, anchor="nw")
    canvas_r.configure(yscrollcommand=scrollbar_r.set)
    canvas_r.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_r.pack(side=tk.RIGHT, fill=tk.Y)

    game_vars = {}
    installed_vars = {}
    row_frames_left = []
    row_frames_right = []
    focus_left_idx = 0
    focus_right_idx = 0

    def get_source_games():
        if os.path.exists(current_source_games):
            return [f for f in os.listdir(current_source_games) if os.path.isfile(os.path.join(current_source_games, f))]
        return []

    def get_installed_games():
        if os.path.exists(current_roms_dir):
            return [f for f in os.listdir(current_roms_dir) if os.path.isfile(os.path.join(current_roms_dir, f)) and f.lower() != "gamelist.xml"]
        return []

    def highlight_left(index):
        nonlocal focus_left_idx
        if not row_frames_left: return
        focus_left_idx = max(0, min(index, len(row_frames_left) - 1))
        for idx, (rf, fname, _) in enumerate(row_frames_left):
            if idx == focus_left_idx:
                rf.config(bg="#d0e8ff")
                for child in rf.winfo_children():
                    try: child.config(bg="#d0e8ff")
                    except: pass
                update_preview_and_description(fname, is_installed_list=False)
            else:
                rf.config(bg="white")
                for child in rf.winfo_children():
                    try: child.config(bg="white")
                    except: pass

    def highlight_right(index):
        nonlocal focus_right_idx
        if not row_frames_right: return
        focus_right_idx = max(0, min(index, len(row_frames_right) - 1))
        for idx, (rf, fname, _) in enumerate(row_frames_right):
            if idx == focus_right_idx:
                rf.config(bg="#ffe0e0")
                for child in rf.winfo_children():
                    try: child.config(bg="#ffe0e0")
                    except: pass
                update_preview_and_description(fname, is_installed_list=True)
            else:
                rf.config(bg="white")
                for child in rf.winfo_children():
                    try: child.config(bg="white")
                    except: pass

    def populate_lists(filter_left="", filter_right=""):
        for widget in scrollable_left.winfo_children(): widget.destroy()
        row_frames_left.clear()
        game_vars.clear()

        source_files = get_source_games()
        filtered_source = [f for f in sorted(source_files) if filter_left.lower() in f.lower()]

        for idx, filename in enumerate(filtered_source):
            if filename not in game_vars:
                game_vars[filename] = tk.BooleanVar(value=False)
             
            row_frame = tk.Frame(scrollable_left, bg="white")
            row_frame.pack(fill=tk.X, anchor="w", padx=2, pady=2)

            chk = tk.Checkbutton(row_frame, text=filename, variable=game_vars[filename], bg="white", anchor="w", font=("Segoe UI", 9))
            chk.pack(side=tk.LEFT, fill=tk.X, expand=True)
             
            row_frame.bind("<Button-1>", lambda e, i=idx, f=filename: (highlight_left(i), update_preview_and_description(f, False)))
            chk.bind("<Button-1>", lambda e, i=idx, f=filename: (highlight_left(i), update_preview_and_description(f, False)))

            row_frames_left.append((row_frame, filename, chk))

        if row_frames_left:
            highlight_left(0)

        for widget in scrollable_right.winfo_children(): widget.destroy()
        row_frames_right.clear()
        installed_vars.clear()

        installed_files = get_installed_games()
        filtered_installed = [f for f in sorted(installed_files) if filter_right.lower() in f.lower()]

        for idx, filename in enumerate(filtered_installed):
            if filename not in installed_vars:
                installed_vars[filename] = tk.BooleanVar(value=False)

            row_frame = tk.Frame(scrollable_right, bg="white")
            row_frame.pack(fill=tk.X, anchor="w", padx=2, pady=2)

            chk = tk.Checkbutton(row_frame, text=filename, variable=installed_vars[filename], bg="white", anchor="w", font=("Segoe UI", 9))
            chk.pack(side=tk.LEFT, fill=tk.X, expand=True)
             
            row_frame.bind("<Button-1>", lambda e, i=idx, f=filename: (highlight_right(i), update_preview_and_description(f, True)))
            chk.bind("<Button-1>", lambda e, i=idx, f=filename: (highlight_right(i), update_preview_and_description(f, True)))

            row_frames_right.append((row_frame, filename, chk))

        if row_frames_right:
            highlight_right(0)

    populate_lists()

    search_left_var.trace("w", lambda *args: populate_lists(search_left_var.get(), search_right_var.get()))
    search_right_var.trace("w", lambda *args: populate_lists(search_left_var.get(), search_right_var.get()))

    # Botones inferiores del Manager
    btn_frame = tk.Frame(manager_win)
    btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    def go_back():
        manager_win.destroy()
        window.deiconify()

    back_btn = tk.Button(btn_frame, text="< Back", command=go_back, width=12, font=("Segoe UI", 9))
    back_btn.pack(side=tk.LEFT)

    def delete_selected_game():
        selected_to_delete = [name for name, var in installed_vars.items() if var.get()]
        if not selected_to_delete:
            messagebox.showwarning("Warning", "Please select at least one installed game to delete.", parent=manager_win)
            return
         
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_to_delete)} selected game(s) and their images?", parent=manager_win):
            return

        try:
            dest_images_dir = os.path.join(current_roms_dir, "media", "images")
            for current_game in selected_to_delete:
                game_path = os.path.join(current_roms_dir, current_game)
                if os.path.exists(game_path):
                    os.remove(game_path)

                base_name, _ = os.path.splitext(current_game)
                for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]:
                    img_path = os.path.join(dest_images_dir, base_name + ext)
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        break
                installed_vars.pop(current_game, None)

            select_all_right_var.set(False)
            populate_lists(search_left_var.get(), search_right_var.get())
            messagebox.showinfo("Success", "Successfully deleted selected games.", parent=manager_win)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=manager_win)

    delete_btn = tk.Button(btn_frame, text="Delete Selected", command=delete_selected_game, width=18, bg="#f44336", fg="white", font=("Segoe UI", 9, "bold"))
    delete_btn.pack(side=tk.RIGHT, padx=5)

    def process_installation():
        selected_games = [name for name, var in game_vars.items() if var.get()]
        if not selected_games:
            messagebox.showwarning("Warning", "Please select at least one game from the available list.", parent=manager_win)
            return

        try:
            if not os.path.exists(current_roms_dir):
                os.makedirs(current_roms_dir, exist_ok=True)

            dest_images_dir = os.path.join(current_roms_dir, "media", "images")
            os.makedirs(dest_images_dir, exist_ok=True)

            copied_count = 0
            for game_name in selected_games:
                src_game_path = os.path.join(current_source_games, game_name)
                dest_game_path = os.path.join(current_roms_dir, game_name)
                 
                if os.path.exists(src_game_path):
                    shutil.copy2(src_game_path, dest_game_path)
                    copied_count += 1

                base_name, _ = os.path.splitext(game_name)
                for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]:
                    img_filename = base_name + ext
                    src_img_path = os.path.join(current_source_images, img_filename)
                    if os.path.exists(src_img_path):
                        shutil.copy2(src_img_path, os.path.join(dest_images_dir, img_filename))
                        break
                game_vars[game_name].set(False)

            select_all_left_var.set(False)
            messagebox.showinfo("Success", f'Successfully installed {copied_count} games into target directory.', parent=manager_win)
            populate_lists(search_left_var.get(), search_right_var.get())

        except Exception as error:
            messagebox.showerror("Error", f"Installation failed: {str(error)}", parent=manager_win)

    install_btn = tk.Button(btn_frame, text="Install Selected", command=process_installation, width=18, bg="#4CAF50", fg="white", font=("Segoe UI", 9, "bold"))
    install_btn.pack(side=tk.RIGHT, padx=5)

    def exit_app():
        manager_win.destroy()
        window.destroy()

    exit_btn = tk.Button(btn_frame, text="Exit", command=exit_app, width=10, bg="#607D8B", fg="white", font=("Segoe UI", 9, "bold"))
    exit_btn.pack(side=tk.LEFT, padx=5)

    manager_win.protocol("WM_DELETE_WINDOW", exit_app)

def install_language():
    language = language_combo.get()
    if not language:
        messagebox.showwarning("Warning", "Please select a language.")
        return

    try:
        # 1. Copiar gamelist.xml a psnes/roms/
        source_gamelist = os.path.join(LANGUAGES_DIR, language, "gamelist.xml")
        if not os.path.exists(source_gamelist):
            messagebox.showerror("Error", f"Missing gamelist.xml for language: {language}")
            return

        target_roms_dir = DEFAULT_ROMS_DIR
        os.makedirs(target_roms_dir, exist_ok=True)
        destination_gamelist = os.path.join(target_roms_dir, "gamelist.xml")
        shutil.copy2(source_gamelist, destination_gamelist)

        # 2. Copiar default.ttf a skins/default/
        if language.lower() == "english":
            font_source = resource_path(os.path.join("font", "English", "default.ttf"))
        else:
            font_source = resource_path(os.path.join("font", "Other", "default.ttf"))

        skin_dest_dir = os.path.join(APP_DIR, "skins", "default")
        if os.path.exists(font_source):
            os.makedirs(skin_dest_dir, exist_ok=True)
            shutil.copy2(font_source, os.path.join(skin_dest_dir, "default.ttf"))
        else:
            messagebox.showwarning("Warning", f"Font file default.ttf not found at: {font_source}")

        # Mensaje de éxito en inglés y apertura del administrador de juegos
        messagebox.showinfo("Success", f"Language '{language}' and configuration applied successfully!")
        open_game_manager(language)

    except Exception as error:
        messagebox.showerror("Error", f"Failed to apply language setup: {str(error)}")

# --- Ventana Principal ---
window = tk.Tk()

icon_path = resource_path("icono.ico")
if os.path.exists(icon_path):
    window.iconbitmap(icon_path)

window.title("Change Language")
window.geometry("380x180")
window.resizable(False, False)

title_label = tk.Label(window, text="Select a language:", font=("Segoe UI", 11))
title_label.pack(pady=(20, 8))

language_list = sorted([
    folder for folder in os.listdir(LANGUAGES_DIR)
    if os.path.isdir(os.path.join(LANGUAGES_DIR, folder))
]) if os.path.exists(LANGUAGES_DIR) else []

language_combo = ttk.Combobox(window, values=language_list, state="readonly", width=32)
language_combo.pack()

if language_list:
    language_combo.current(0)

install_button = tk.Button(window, text="Next: Manage Games", command=install_language, width=22)
install_button.pack(pady=22)

window.mainloop()