本程序提供了 flash UI, 用户可以通过 UI 上传待翻译的 pdf 文件:
并且可选择翻译为哪种语言. 

![sample_out](images/upload_page.png)

文件上传后, 可通过 UI 下载翻译完的文件.

![sample_out](images/download_page.png)

运行一下命令启动程序:
```bash
python app.py --model_type OpenAIModel --openai_api_key $OPENAI_API_KEY
```