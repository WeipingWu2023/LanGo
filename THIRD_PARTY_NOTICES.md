# Third-party notices

LanGo 1.3's application code, original detective illustration, and icon are licensed under the root MIT LICENSE. No third-party anime characters or artwork are included.

The app sends submitted text to [DeepSeek](https://api.deepseek.com/) to generate every definition and translation. DeepSeek's [platform terms](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html) and pricing apply. LanGo includes no DeepSeek model weights or corpus and is not affiliated with DeepSeek. Each user supplies their own API key.

The Windows bundle includes CPython, Tcl/Tk, OpenSSL, zlib, Expat, liblzma, PyInstaller runtime components and Inno Setup installer code. Their full notices are in `packaging/licenses/` in source and `licenses/` in the installed application. Pillow is used at build time to generate the icon and is not bundled as application code.

ECDICT and WordNet were bundled in LanGo 1.1 and 1.2. Version 1.3 no longer bundles or queries those datasets. Their original release tags and notices remain in Git history.
