import sys
import os
import fitz
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QComboBox,
    QProgressBar, QMessageBox, QGridLayout, QStatusBar, QGroupBox
)
class PdfProcessingThread(QThread):
    """Handles PDF processing in a separate thread to keep the GUI responsive."""
    progress_update = pyqtSignal(int)
    total_pages_known = pyqtSignal(int)
    finished_conversion = pyqtSignal(str, bool, list)  # Message, success, list of page_save_errors

    def __init__(self, input_pdf_path, output_directory, dpi, image_format):
        super().__init__()
        self.input_pdf_path = input_pdf_path
        self.output_directory = output_directory
        self.dpi = dpi
        self.image_format = image_format.lower()
        self._is_interruption_requested = False  # For cleaner interruption

    def request_interruption_sync(self):  # Ensure thread-safe interruption request
        self._is_interruption_requested = True

    def run(self):
        """Converts PDF pages to images."""
        page_save_errors = []
        if not os.path.exists(self.input_pdf_path):
            self.finished_conversion.emit(f"Error: Input PDF file not found:\n{self.input_pdf_path}", False,
                                          page_save_errors)
            return

        try:
            os.makedirs(self.output_directory, exist_ok=True)
        except OSError as e:
            self.finished_conversion.emit(f"Error creating output directory '{self.output_directory}': {e}", False,
                                          page_save_errors)
            return

        converted_count = 0
        doc = None  # Initialize doc to None for finally block
        try:
            doc = fitz.open(self.input_pdf_path)
            total_pages = len(doc)
            if total_pages == 0:
                self.finished_conversion.emit("Error: The PDF file is empty or could not be read.", False,
                                              page_save_errors)
                return  # doc.close() will be handled in finally

            self.total_pages_known.emit(total_pages)

            for i in range(total_pages):
                if self._is_interruption_requested:  # Check custom flag
                    self.finished_conversion.emit("Conversion cancelled by user.", False, page_save_errors)
                    return

                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=self.dpi, alpha=False)

                if pix.alpha:
                    pil_image = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                else:
                    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGB')

                try:
                    output_filename = f"page_{i + 1}.{self.image_format}"
                    output_image_path = os.path.join(self.output_directory, output_filename)
                    pil_image.save(output_image_path)
                    converted_count += 1
                except Exception as e_save:
                    error_detail = f"Page {i + 1}: {e_save}"
                    print(f"  Error saving {error_detail}")  # Keep console log for debugging
                    page_save_errors.append(error_detail)

                self.progress_update.emit(i + 1)

        except Exception as e_pdf:
            self.finished_conversion.emit(f"Error processing PDF with PyMuPDF: {e_pdf}", False, page_save_errors)
            return
        finally:
            if doc:
                doc.close()

        if converted_count > 0:
            msg = f"Successfully converted {converted_count} page(s) to '{self.output_directory}'."
            if page_save_errors:
                msg += f"\nHowever, {len(page_save_errors)} page(s) could not be saved."
            self.finished_conversion.emit(msg, True, page_save_errors)

        elif total_pages > 0 and not self._is_interruption_requested:
            msg = "No pages were successfully converted."
            if page_save_errors:
                msg += f"\n{len(page_save_errors)} page(s) encountered errors during saving."
            self.finished_conversion.emit(msg, False, page_save_errors)
        elif not self._is_interruption_requested:  # If not cancelled and no pages
            self.finished_conversion.emit("No pages were processed or an error occurred.", False, page_save_errors)


class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Images Converter")
        self.setGeometry(200, 200, 600, 300)  # Adjusted window size
        # self.setWindowIcon(QIcon("path/to/your/icon.png")) # Uncomment and set path for an icon

        self.input_pdf_path = ""
        self.output_directory_path = ""
        self.processing_thread = None

        # UI elements will be initialized in setup_ui
        self.btn_select_pdf = None
        self.lbl_input_pdf = None
        self.btn_select_output_folder = None
        self.lbl_output_folder = None
        self.spin_dpi = None
        self.combo_format = None
        self.btn_start_conversion = None
        self.btn_cancel_conversion = None  # For Cancel button
        self.progress_bar = None
        self.status_bar = None

        self.setup_ui()

    def setup_ui(self):  # Renamed from initui
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Input/Output Group ---
        io_group_box = QGroupBox("File Selection")
        input_group_layout = QGridLayout()

        self.btn_select_pdf = QPushButton("Select Input PDF")
        self.btn_select_pdf.clicked.connect(self.select_input_pdf_dialog)
        input_group_layout.addWidget(self.btn_select_pdf, 0, 0)

        self.lbl_input_pdf = QLabel("No PDF selected")
        self.lbl_input_pdf.setStyleSheet("QLabel { padding-left: 5px; }")
        input_group_layout.addWidget(self.lbl_input_pdf, 0, 1)

        self.btn_select_output_folder = QPushButton("Select Output Folder")
        self.btn_select_output_folder.clicked.connect(self.select_output_folder_dialog)
        input_group_layout.addWidget(self.btn_select_output_folder, 1, 0)

        self.lbl_output_folder = QLabel("No folder selected")
        self.lbl_output_folder.setStyleSheet("QLabel { padding-left: 5px; }")
        input_group_layout.addWidget(self.lbl_output_folder, 1, 1)
        io_group_box.setLayout(input_group_layout)

        # --- Options Group ---
        options_group_box = QGroupBox("Conversion Options")
        options_layout = QHBoxLayout()

        lbl_dpi = QLabel("DPI:")
        options_layout.addWidget(lbl_dpi)
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 600)
        self.spin_dpi.setValue(300)
        self.spin_dpi.setSingleStep(10)
        options_layout.addWidget(self.spin_dpi)

        options_layout.addSpacing(20)  # Add some space

        lbl_format = QLabel("Format:")
        options_layout.addWidget(lbl_format)
        self.combo_format = QComboBox()
        self.combo_format.addItems(["png", "jpg", "jpeg", "bmp", "tiff"])
        options_layout.addWidget(self.combo_format)

        options_layout.addStretch(1)
        options_group_box.setLayout(options_layout)

        # --- Control Buttons ---
        control_buttons_layout = QHBoxLayout()
        self.btn_start_conversion = QPushButton("Start Conversion")
        self.btn_start_conversion.setFixedHeight(35)
        self.btn_start_conversion.clicked.connect(self.start_conversion_process)
        control_buttons_layout.addWidget(self.btn_start_conversion)

        self.btn_cancel_conversion = QPushButton("Cancel")  # Cancel button
        self.btn_cancel_conversion.setFixedHeight(35)
        self.btn_cancel_conversion.setEnabled(False)  # Initially disabled
        self.btn_cancel_conversion.clicked.connect(self.cancel_conversion_process)
        control_buttons_layout.addWidget(self.btn_cancel_conversion)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)  # Important: Add status bar to QMainWindow
        self.status_bar.showMessage("Ready")

        # --- Add to Main Layout ---
        main_layout.addWidget(io_group_box)
        main_layout.addWidget(options_group_box)
        main_layout.addLayout(control_buttons_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addStretch(1)

    def select_input_pdf_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Input PDF", self.input_pdf_path or "",
                                                   "PDF Files (*.pdf);;All Files (*)")
        if file_name:
            self.input_pdf_path = file_name
            self.lbl_input_pdf.setText(os.path.basename(file_name))
            self.status_bar.showMessage(f"Input PDF: {os.path.basename(file_name)}")
            if not self.output_directory_path:  # Only suggest if output is not already set
                base, _ = os.path.splitext(os.path.basename(file_name))
                suggested_dir = os.path.join(os.path.dirname(file_name), f"{base}_images")
                self.output_directory_path = suggested_dir
                self.lbl_output_folder.setText(os.path.basename(suggested_dir))

    def select_output_folder_dialog(self):
        initial_dir = os.path.dirname(self.input_pdf_path) if self.input_pdf_path else \
            (self.output_directory_path or "")  # Use existing output or input path
        dir_name = QFileDialog.getExistingDirectory(self, "Select Output Folder", initial_dir)
        if dir_name:
            self.output_directory_path = dir_name
            self.lbl_output_folder.setText(os.path.basename(dir_name))
            self.status_bar.showMessage(f"Output Folder: {os.path.basename(dir_name)}")

    def start_conversion_process(self):
        if not self.input_pdf_path:
            QMessageBox.warning(self, "Input Missing", "Please select an input PDF file.")
            return
        if not self.output_directory_path:
            QMessageBox.warning(self, "Output Missing", "Please select an output folder.")
            return

        self.btn_start_conversion.setEnabled(False)
        self.btn_cancel_conversion.setEnabled(True)  # Enable cancel button
        self.status_bar.showMessage("Processing... Please wait.")
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # Indeterminate until total_pages is known
        self.progress_bar.setFormat("Processing...")

        self.processing_thread = PdfProcessingThread(
            self.input_pdf_path,
            self.output_directory_path,
            self.spin_dpi.value(),
            self.combo_format.currentText()
        )
        self.processing_thread.progress_update.connect(self.update_progress_bar)
        self.processing_thread.total_pages_known.connect(self.set_progress_bar_max)
        self.processing_thread.finished_conversion.connect(self.on_conversion_finished)
        self.processing_thread.start()

    def cancel_conversion_process(self):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.request_interruption_sync()
            self.status_bar.showMessage("Cancellation requested...")
            self.btn_cancel_conversion.setEnabled(False)  # Disable after clicking

    def set_progress_bar_max(self, total_pages):
        if total_pages > 0:
            self.progress_bar.setMaximum(total_pages)
            self.progress_bar.setFormat(f"%v / {total_pages} pages (%p%)")
        else:
            self.progress_bar.setMaximum(1)  # Avoid division by zero if 0 pages
            self.progress_bar.setFormat("No pages to process.")

    def update_progress_bar(self, current_page):
        self.progress_bar.setValue(current_page)

    def on_conversion_finished(self, message, success, page_save_errors):
        self.status_bar.showMessage(message)
        self.btn_start_conversion.setEnabled(True)
        self.btn_cancel_conversion.setEnabled(False)  # Disable cancel button

        if success and self.progress_bar.value() == self.progress_bar.maximum() and self.progress_bar.maximum() > 0:
            self.progress_bar.setFormat("Completed!")
        elif not success and "cancelled" in message.lower():
            self.progress_bar.setFormat("Cancelled")
        else:
            self.progress_bar.setFormat("Finished with issues or no pages")

        if page_save_errors:
            error_summary = "Could not save the following pages:\n" + "\n".join(page_save_errors[:5])  # Show first 5
            if len(page_save_errors) > 5:
                error_summary += f"\n...and {len(page_save_errors) - 5} more."
            QMessageBox.warning(self, "Page Saving Errors", error_summary)

        if success:
            QMessageBox.information(self, "Conversion Status", message)
        elif "cancelled" not in message.lower():  # Don't show critical for user cancel
            QMessageBox.critical(self, "Conversion Error", message)

        self.processing_thread = None

    def closeEvent(self, event):
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(self, 'Confirm Exit',
                                         "Conversion is in progress. Are you sure you want to exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.processing_thread.request_interruption_sync()
                self.processing_thread.wait(1000)  # Give thread a moment to react
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle("Fusion") # Example of setting a style
    main_window = PDFConverterApp()
    main_window.show()
    sys.exit(app.exec())