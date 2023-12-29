from setuptools import setup

setup(name='whisper-diarization',
      version=0.20,
      description='Python 3 library for diarization',
      long_description='Deployment package for https://github.com/MahmoudAshraf97/whisper-diarization. It adds a developer interface that can be used from Python scripts.',
      author='Laurent Esingle',
      author_email='laurent.esingle1@outlook.com',
      url='https://github.com/LaurentEsingle/whisper-diarization',
      license='https://github.com/MahmoudAshraf97/whisper-diarization/blob/main/LICENSE',
      packages=[
        'whisperdiarization'
        ],
      install_requires=[
          'youtokentome @ git+https://github.com/LahiLuk/YouTokenToMe',
          'wget',
          'nemo_toolkit[asr]==1.20.0',
          'transformers>=4.26.1',
          'whisperx @ git+https://github.com/m-bain/whisperX.git@a5dca2cc65b1a37f32a347e574b2c56af3a7434a',
          'demucs @ git+https://github.com/facebookresearch/demucs#egg=demucs',
          'deepmultilingualpunctuation'
      ],
      keywords=['whisper', 'transcription', 'diarization', 'ASR', 'VAD'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Terminals",
          "Topic :: Utilities",
          'Programming Language :: Python :: 3.10'
      ],
      zip_safe=False)
