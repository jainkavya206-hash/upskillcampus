import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
        ".ppt", ".pptx", ".csv",
    ],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json"],
}
OTHER_CATEGORY = "Others"


def get_category(file_extension: str) -> str:
    extension = file_extension.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return OTHER_CATEGORY


def get_available_destination(folder: str, filename: str) -> str:
    base, extension = os.path.splitext(filename)
    destination = os.path.join(folder, filename)
    counter = 1

    while os.path.exists(destination):
        destination = os.path.join(folder, f"{base}_{counter}{extension}")
        counter += 1

    return destination


def organize_folder(target_directory: str, log_callback) -> None:
    if not os.path.isdir(target_directory):
        log_callback(f"ERROR: '{target_directory}' is not a valid folder.")
        return

    moved_count = 0
    skipped_count = 0

    for item_name in os.listdir(target_directory):
        source_path = os.path.join(target_directory, item_name)

        if os.path.isdir(source_path) or item_name == os.path.basename(__file__):
            continue

        _, extension = os.path.splitext(item_name)
        category = get_category(extension) if extension else OTHER_CATEGORY
        category_folder = os.path.join(target_directory, category)
        os.makedirs(category_folder, exist_ok=True)
        destination_path = get_available_destination(category_folder, item_name)

        try:
            shutil.move(source_path, destination_path)
            log_callback(f"Moved '{item_name}'  ->  {category}/")
            moved_count += 1
        except Exception as error:
            log_callback(f"Could not move '{item_name}': {error}")
            skipped_count += 1

    log_callback("")
    log_callback(f"Done! {moved_count} file(s) organized, {skipped_count} skipped.")


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        root.title("File Organizer")
        root.geometry("560x420")
        root.resizable(False, False)

        top_frame = tk.Frame(root, pady=15)
        top_frame.pack(fill="x", padx=15)

        tk.Label(
            top_frame,
            text="Folder to organize:",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        path_row = tk.Frame(top_frame)
        path_row.pack(fill="x", pady=(5, 0))

        self.path_entry = tk.Entry(path_row, font=("Segoe UI", 10))
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=4)

        tk.Button(
            path_row,
            text="Browse...",
            command=self.browse_folder,
        ).pack(side="left", padx=(8, 0))

        self.organize_button = tk.Button(
            root,
            text="Organize Files",
            font=("Segoe UI", 11, "bold"),
            bg="#2e7d32",
            fg="white",
            height=2,
            command=self.start_organizing,
        )
        self.organize_button.pack(fill="x", padx=15, pady=15)

        tk.Label(
            root,
            text="Activity log:",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=15)

        self.log_box = scrolledtext.ScrolledText(
            root,
            height=14,
            font=("Consolas", 9),
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected)

    def log(self, message: str):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")
        self.root.update_idletasks()

    def start_organizing(self):
        target_directory = self.path_entry.get().strip()

        if not target_directory:
            messagebox.showwarning(
                "No folder selected",
                "Please choose a folder first.",
            )
            return

        confirm = messagebox.askyesno(
            "Confirm",
            f"This will move files inside:\n\n{target_directory}\n\n"
            "into new category sub-folders (Images, Documents, etc). Continue?",
        )
        if not confirm:
            return

        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state="disabled")

        self.log(f"Organizing: {target_directory}")
        self.log("-" * 50)
        organize_folder(target_directory, self.log)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
