# iPhone 獨立下載 YouTube 音訊轉 WAV 工具

這是不用上架 App Store、也不需要 Windows 電腦執行轉檔的 iPhone 方案。做法是在 iPhone 安裝 iSH，讓 iPhone 本機跑 `yt-dlp` 與 `ffmpeg`。

## 你需要先準備

1. 在 iPhone 安裝 iSH。
2. 開啟 iSH。
3. 把本資料夾的 `install_ish.sh` 與 `ytwav.py` 放進 iSH，或直接複製檔案內容貼到 iSH 建立檔案。

## 第一次安裝

在 iSH 執行：

```sh
chmod +x install_ish.sh
./install_ish.sh
```

這會安裝：

- Python 3
- pip
- ffmpeg
- nodejs
- yt-dlp

## 使用方式

執行：

```sh
ytwav "https://www.youtube.com/watch?v=OOQH2ouSkfw"
```

輸出的 WAV 會存到：

```text
~/Documents/YouTube WAV
```

檔名會盡量包含 YouTube metadata 裡標示的 BPM 與調性，例如：

```text
Song Title - 143 BPM - C# minor.wav
```

如果影片描述欄沒有 BPM/調性，iPhone 版會先輸出 WAV，但不做完整音訊分析。完整 BPM/Key fallback 分析目前仍以 Windows Flutter 版較完整。

## 合法用途提醒

請只下載你有權使用、授權下載或合法可保存的內容。不要用於繞過 DRM、付費牆、登入限制或平台限制。
