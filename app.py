import os

from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

from ai_translator.model import OpenAIModel
from ai_translator.translator import PDFTranslator
from ai_translator.utils import ArgumentParser, ConfigLoader


class FileUploader:
    def __init__(self, translator: PDFTranslator):
        self.translator = translator
        self.app = Flask(__name__, template_folder='templates')
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        self.app.config['DOWNLOAD_FOLDER'] = 'downloads'
        if not os.path.exists(self.app.config['UPLOAD_FOLDER']):
            os.makedirs(self.app.config['UPLOAD_FOLDER'])
        if not os.path.exists(self.app.config['DOWNLOAD_FOLDER']):
            os.makedirs(self.app.config['DOWNLOAD_FOLDER'])
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])
        self.app.add_url_rule('/download/<filename>', 'download', self.download)

    def index(self):
        return render_template('index.html')

    def upload(self):
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        file_format = request.form["file_format"]
        target_language = request.form["target_language"]

        if file.filename == '':
            return redirect(request.url)

        if file:
            upload_filename = secure_filename(file.filename)
            filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], upload_filename)
            file.save(filepath)

            # Add backend processing logic here, e.g. extracting PDF content
            filename = upload_filename.split(".")[0]
            filename = filename + "." + ("pdf" if file_format.lower() == "pdf" else "md")
            download_filepath = os.path.join(self.app.config['DOWNLOAD_FOLDER'], filename)
            self.translator.translate_pdf(
                filepath, file_format=file_format, target_language=target_language,
                output_file_path=download_filepath, pages=None)

            return render_template('result.html', filename=filename)

    def download(self, filename):
        # filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
        return send_from_directory(self.app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

    def run(self):
        self.app.run(debug=True)


def main():
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    model = OpenAIModel(model=model_name, api_key=api_key)

    pdf_file_path = args.book if args.book else config['common']['book']
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    # translator.translate_pdf(pdf_file_path, file_format)

    uploader = FileUploader(translator)
    uploader.run()


if __name__ == '__main__':
    main()
