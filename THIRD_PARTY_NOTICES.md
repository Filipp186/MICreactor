# Third-party notices

The PolyForm Noncommercial License applies only to original MICreactor code.
Third-party libraries, runtimes, and model files are excluded from that license
and remain governed by their respective licenses. Nothing in MICreactor's
license restricts rights granted by those third-party licenses.

Binary builds collect package-specific license files into
`THIRD_PARTY_LICENSES/packages`. The following list identifies the principal
runtime components; transitive package notices are included in the generated
license directory.

| Component | License | Upstream |
|---|---|---|
| Qt for Python: PySide6 and Shiboken6 | LGPL-3.0-only, GPL alternatives, or Qt Commercial | https://code.qt.io/cgit/pyside/pyside-setup.git/ |
| Python | PSF-2.0 | https://www.python.org/ |
| OpenAI Whisper and Whisper model weights | MIT | https://github.com/openai/whisper |
| faster-whisper | MIT | https://github.com/SYSTRAN/faster-whisper |
| CTranslate2 | MIT | https://github.com/OpenNMT/CTranslate2 |
| PyAudioWPatch / PyAudio / PortAudio | MIT and their included notices | https://github.com/s0d3s/PyAudioWPatch |
| NumPy | BSD-3-Clause and bundled component licenses | https://github.com/numpy/numpy |
| ONNX Runtime | MIT | https://github.com/microsoft/onnxruntime |
| Hugging Face Hub | Apache-2.0 | https://github.com/huggingface/huggingface_hub |
| tokenizers | Apache-2.0 | https://github.com/huggingface/tokenizers |
| PyAV | BSD-3-Clause | https://github.com/PyAV-Org/PyAV |
| SoundFile | BSD-3-Clause | https://github.com/bastibe/python-soundfile |
| libsndfile | LGPL-2.1-or-later | https://github.com/libsndfile/libsndfile |
| pyannote.audio | MIT | https://github.com/pyannote/pyannote-audio |
| pyannote speaker-diarization-community-1 model | CC-BY-4.0 | https://huggingface.co/pyannote/speaker-diarization-community-1 |
| PyInstaller bootloader | GPL-2.0-or-later with Bootloader Exception | https://github.com/pyinstaller/pyinstaller |

Qt/PySide6 distribution details and the corresponding-source written offer are
provided in `QT_LGPL_COMPLIANCE.md`. The LGPLv3 text is provided in
`THIRD_PARTY_LICENSES/LGPL-3.0.txt`.
