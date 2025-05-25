import PyInstaller.__main__
import os
import shutil

# --- Settings ---
APP_NAME = "PDFPageConverter"  # Name of the executable to be created (without extension)
SCRIPT_FILE = "PDFtoImage.py"  # Your main Python script's name (KEEP YOUR FILENAME)
ICON_FILE = "icon.ico"  # Name of the icon file to use (optional, must be in the same directory)
OUTPUT_DIR = "dist"  # Folder where PyInstaller outputs will be created
BUILD_DIR = "build"  # Folder where PyInstaller temporary files will be created

# Additional data files for PyInstaller (if needed)
# Example: If your application needs some images or external files
# datas = [('path/to/your/image.png', 'images_folder_in_exe')]
datas = []

# It's often a good idea to include hooks and hidden imports for PyQt6.
# PyInstaller usually finds them automatically, but manual addition might be necessary sometimes.
hidden_imports = [
    'PyQt6.sip',
    'PyQt6.QtGui',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'fitz',  # For PyMuPDF
    'fitz.fitz',  # Sometimes needed for PyMuPDF to be packaged correctly
    'PIL'  # For Pillow
]

# PyInstaller command arguments
pyinstaller_args = [
    f'--name={APP_NAME}',
    '--onefile',  # Creates a single EXE file
    '--windowed',  # Hides the console window (for GUI applications)
    # '--noconsole', # Serves the same purpose as '--windowed', sometimes used
    '--clean',  # Cleans previous build files
    # '--uac-admin', # If your application requires administrator rights (usually not needed)
]

if ICON_FILE and os.path.exists(ICON_FILE):
    pyinstaller_args.append(f'--icon={ICON_FILE}')
else:
    print(f"Warning: Icon file '{ICON_FILE}' not found. Proceeding without an icon.")
    # If an icon file is not mandatory, you can remove this line or let the application proceed.
    # If you don't want to build without an icon:
    # raise FileNotFoundError(f"Icon file not found: {ICON_FILE}")

for data_pair in datas:
    # For the separator in --add-data, PyInstaller usually handles it.
    # The common format is 'source:destination_in_bundle' or 'source;destination_in_bundle' for Windows.
    # PyInstaller often correctly interprets ':' for both.
    # To be very specific for Windows:
    # separator = ';' if os.name == 'nt' else ':'
    # pyinstaller_args.append(f'--add-data={data_pair[0]}{separator}{data_pair[1]}')
    # Using ':' is generally fine:
    pyinstaller_args.append(f'--add-data={data_pair[0]}:{data_pair[1]}')

for hidden_import in hidden_imports:
    pyinstaller_args.append(f'--hidden-import={hidden_import}')

# Add the main script file at the end
pyinstaller_args.append(SCRIPT_FILE)


def build_executable():
    print(f"Building '{APP_NAME}.exe' from source: '{SCRIPT_FILE}'...")
    print(f"PyInstaller arguments: {' '.join(pyinstaller_args)}")

    try:
        # Clean up previous build/dist folders (PyInstaller --clean does this, but let's be sure)
        if os.path.exists(OUTPUT_DIR):
            print(f"Removing previous output directory: {OUTPUT_DIR}...")
            shutil.rmtree(OUTPUT_DIR)
        if os.path.exists(BUILD_DIR):
            print(f"Removing previous build directory: {BUILD_DIR}...")
            shutil.rmtree(BUILD_DIR)

        spec_file = f"{APP_NAME}.spec"
        if os.path.exists(spec_file):
            print(f"Removing previous .spec file: {spec_file}...")
            os.remove(spec_file)

        PyInstaller.__main__.run(pyinstaller_args)
        print("\nBuild process successful!")
        print(f"Executable created at: {os.path.join(os.getcwd(), OUTPUT_DIR, APP_NAME + '.exe')}")  # Show full path

        # Post-build cleanup (optional, PyInstaller usually handles this)
        if os.path.exists(BUILD_DIR):
            print(f"Cleaning up temporary build directory: {BUILD_DIR}...")
            try:
                shutil.rmtree(BUILD_DIR)
            except Exception as e:
                print(f"Warning: Could not completely clean up build directory: {e}")

        if os.path.exists(spec_file):
            print(f"Cleaning up .spec file: {spec_file}...")
            try:
                os.remove(spec_file)
            except Exception as e:
                print(f"Warning: Could not remove .spec file: {e}")

    except SystemExit as e:  # PyInstaller sometimes exits with SystemExit
        if e.code == 0:
            print("\nBuild process successful (SystemExit code 0)!")
            print(f"Executable created at: {os.path.join(os.getcwd(), OUTPUT_DIR, APP_NAME + '.exe')}")
        else:
            print("\nBuild process failed (SystemExit)!")
            print(f"Error code: {e.code}")
    except Exception as e:
        print("\nBuild process failed!")
        print(f"Error: {e}")


if __name__ == '__main__':
    build_executable()