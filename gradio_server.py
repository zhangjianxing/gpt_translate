import gradio as gr

from ai_translator.translator import PDFTranslator, TranslationConfig
from ai_translator.utils import ArgumentParser, LOG


class APP:
    def __init__(self, translator: PDFTranslator):
        self.translator = translator

    def translation(self, input_file, source_language, target_language, style, max_pages, glm_host):
        LOG.debug(f"[翻译任务]\n源文件: {input_file.name}\n源语言: {source_language}\n目标语言: {target_language}")
        output_file_path = self.translator.translate_pdf(
            input_file.name,
            source_language=source_language,
            target_language=target_language,
            style=style,
            max_pages=max_pages,
            glm_host=glm_host,
        )
        return output_file_path

    def launch_gradio(self):
        iface = gr.Interface(
            fn=self.translation,
            title="OpenAI-Translator v2.0(PDF 电子书翻译工具)",
            inputs=[
                gr.File(label="上传PDF文件"),
                gr.Textbox(label="源语言（默认：英文）", placeholder="English", value="English"),
                gr.Textbox(label="目标语言（默认：中文）", placeholder="Chinese", value="Chinese"),
                gr.Textbox(label="风格（如:小说、新闻稿、作家风格, 默认：普通）", placeholder="normal", value="normal"),
                gr.Textbox(label="最多翻译几页(全部翻译选 0, 默认:2)", placeholder="2", value="2"),
                gr.Textbox(label="GLM server (e.g. http://localhost:8000/v1), default: chatGPT", placeholder="", value="")
            ],
            outputs=[
                gr.File(label="下载翻译文件")
            ],
            allow_flagging="never"
        )
        iface.launch(share=True, server_name="0.0.0.0")


def main():
    # 解析命令行
    args = ArgumentParser().parse_arguments()

    # 初始化配置单例
    config = TranslationConfig()
    config.initialize(args)

    # 初始化 translator
    translator = PDFTranslator(config.model_name)
    app = APP(translator)
    # 启动 Gradio 服务
    app.launch_gradio()


if __name__ == "__main__":
    main()
