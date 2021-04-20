# words_transribe
使用Google Speech to Text API 实现单词书的音频转文字

## 语音转录
1. 构建google云存储，上传长音频文件
2. 使用长语音转录功能获得整个文件的文本

## 语音文件划分
每个单词之前都有固定长度的提示音，在这里是2339ms。使用pydub的split_on_scilence()可以将文件拆分，找到提升音再重组即可完成
