from typing import Optional

from ai_translator.translator.pdf_parser import PDFParser
from ai_translator.translator.translation_chain import TranslationChain
from ai_translator.translator.translation_chain_glm import TranslationChainGLM
from ai_translator.translator.writer import Writer


class PDFTranslator:
    def __init__(self, model_name: str):
        self.translate_chain = TranslationChain(model_name)
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(
            self,
            input_file: str,
            output_file_format: str = 'markdown',
            source_language: str = "English",
            target_language: str = 'Chinese',
            style: str = 'normal',
            max_pages='2',
            glm_host='',
    ):
        pages = None
        try:
            if int(max_pages) > 0:
                pages = int(max_pages)
        except:
            pass

        self.book = self.pdf_parser.parse_pdf(input_file, pages)

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                # Translate content.original
                if glm_host == '':
                    translation, status = self.translate_chain.run(content, source_language, target_language, style)
                else:
                    print("use GLM")
                    translate_chain = TranslationChainGLM(glm_host)
                    translation, status = translate_chain.run(content, source_language, target_language, style)
                # Update the content in self.book.pages directly
                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)

        return self.writer.save_translated_book(self.book, output_file_format)
