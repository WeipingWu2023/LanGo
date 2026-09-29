# LanGo 1.3.2

LanGo is now a DeepSeek-powered English learning and bilingual translation app with a bright detective theme, original character art, and a redesigned shortcut icon.

English words receive sense-by-sense English definitions, Chinese explanations, usage notes, relevant synonyms and antonyms, and at least three paired English/Chinese examples per returned sense. English sentences translate to Chinese, and Chinese input translates to natural English. All results come from DeepSeek; the former translation-provider quota message is gone.

The API key is read from the `DEEPSEEK_API_KEY` environment variable for the current Windows user; it is never bundled or pushed to GitHub. Each installer recipient needs their own key and DeepSeek account. DeepSeek API use may incur charges. The app needs internet for every lookup and AI content can be wrong or incomplete. A response with unusually many senses can exceed the provider's output limit.

Windows 10/11 x64. This installer is unsigned, so Windows may display an unknown-publisher warning. Verify `LanGo-Setup-1.3.2-Windows-x64.exe` using `SHA256SUMS.txt`. Running the installer updates the existing installation and leaves saved words in `%LOCALAPPDATA%\LanGo` intact.
