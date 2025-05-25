# 📄 PDFtoImage

**PDFtoImage** is a modern, open-source desktop application that converts PDF files into high-quality image formats such as **PNG**, **JPEG**, **BMP**, and **TIFF**.

Designed with a clean and responsive **PyQt6** interface, it simplifies the task of exporting PDF pages as individual images — efficiently, reliably, and beautifully.

---

## ✨ Features

- 🔄 Converts **each PDF page** into a **separate image**
- 🖼️ Supports multiple formats: **PNG**, **JPG/JPEG**, **BMP**, **TIFF**
- 🎯 Adjustable **DPI** (resolution) for precise image quality control
- 🧭 Simple and intuitive **drag-and-click UI** for input and output selection
- 📊 Real-time **progress bar** with cancel support
- ⚙️ Responsive UI with **background processing** (multithreading)
- 🧩 Detailed **error notifications** for failed conversions
- 🪟 One-click packaging as a **standalone Windows `.exe` file**
- 🎨 Optional custom **app icon** support

---

## 🧰 Requirements

- Python **3.8+**
- `pip` (Python package manager)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [Pillow (PIL)](https://pypi.org/project/Pillow/)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)
- [PyInstaller](https://pypi.org/project/pyinstaller/) (for `.exe` builds)

---

## 🚀 Installation

Clone this repository:
```bash
git clone https://github.com/asa07-salihg/PDFtoImage.git
cd PDFtoImage
```

Install the dependencies:
```bash
pip install PyQt6 Pillow PyMuPDF pyinstaller
```

---

## 🖥️ Running the Application

To run the app directly from source:
```bash
python PDFtoImage.py
```

Then:

1. 📂 Click **"Select Input PDF"** to choose your file  
2. 📁 Click **"Select Output Folder"** (a suggested folder appears automatically)  
3. 🎚️ Set your preferred **DPI**  
4. 🖼️ Select output format: PNG, JPG/JPEG, BMP, or TIFF  
5. ▶️ Click **"Start Conversion"**  
6. 🟩 Watch the live progress bar — click **"Cancel"** anytime  
7. ✅ Open the output folder to view your converted images

---

## 🏗️ Building a Standalone `.exe` (Windows Only)

The provided `build.py` script creates a single-file executable.

### Steps:
1. Ensure dependencies are installed:
    ```bash
    pip install PyQt6 Pillow PyMuPDF pyinstaller
    ```

2. *(Optional)* Add an icon:  
   Place your `icon.ico` file in the project directory.

3. Run the build script:
    ```bash
    python build.py
    ```

4. After a successful build, find `PDFPageConverter.exe` in the `dist/` folder.

---

## 📁 Project Structure

```
PDFtoImage/
├── PDFtoImage.py         # Main application (PyQt6 GUI)
├── build.py              # Build script using PyInstaller
├── icon.ico              # Optional icon for executable
├── README.md             # This documentation file
├── .gitignore            # Git ignored files
├── dist/                 # Generated .exe files (after build)
├── build/                # Temporary build files
└── docs/                 # (Optional) screenshots, extra docs
```

---

## 🛠️ Troubleshooting

- ❗ **Missing modules?**  
  Run: `pip install PyQt6 Pillow PyMuPDF pyinstaller`

- ⚠️ **Build issues with PyInstaller?**  
  Check `build.py` for necessary `--hidden-import` entries or consult [PyInstaller documentation](https://pyinstaller.org/).

- 🔐 **Permission errors?**  
  Make sure the selected output folder is writable.

---

## 🤝 Contributing

Contributions and feedback are welcome!  
To contribute:

1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for full details.

---

## 👤 Author

Developed by [asa07-salihg](https://github.com/asa07-salihg)

---

> 💡 *PDFtoImage is built for developers, students, and professionals who want simple yet powerful PDF conversion in one lightweight tool.*

**Happy converting!**
