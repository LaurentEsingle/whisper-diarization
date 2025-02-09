import os
import re
from datetime import datetime
import subprocess
from whisperdiarization import helpers

diarization_path = os.path.dirname(helpers.__file__)

class DiarizationResult:
    """
        Result of Diarization.Start() call.

        DiarizationResult object contains the following properties:
            - ReturnCode: 1 if errors encountered during diariztion, 0 otherwise
            - Output: output of diarization execution
            - Error: errors encountered if any
    """

    def __init__(self) -> None:
        self._ReturnCode = 0
        self._Output = ""
        self._Error = ""

    @property
    def ReturnCode(self):
        return self._ReturnCode
    
    @ReturnCode.setter
    def ReturnCode(self, value):
        self._ReturnCode = int(value)

    @property
    def Output(self):
        return self._Output
    
    @Output.setter
    def Output(self, value):
        self._Output = str(value)

    @property
    def Error(self):
        return self._Error
    
    @Error.setter
    def Error(self, value):
        self._Error = str(value)


class Diarization:
    """
    Whisper ASR capabilities with Voice Activity Detection (VAD) and Speaker Embedding to identify the speaker for each sentence in the transcription generated by Whisper.
    
    :param str audiofilename:
        The name of the audio file to be processed

    :param bool no_stem:
        (Optional) Disables source separation

    :param str model_name:
        (Optional) The model to be used for ASR, default is 'medium.en'

    :param bool suppress_numerals:
        (Optional) Transcribes numbers in their pronounced letters instead of digits, improves alignment accuracy

    :param str device:
        (Optional) Choose which device to use, defaults to "cuda" if available

    :param int batch_size:
        (Optional) Batch size for batched inference, reduce if you run out of memory, set to 0 for non-batched inference

    :param str language:
        (Optional) Manually select language, useful if language detection failed
        Available languages:
            {en, fr, de, es, it, ja, zh, nl, uk, pt}
    
    """


    def __init__(
            self,
            audiofilename: str,
            no_stem: bool = False,
            model_name: str = "medium.en",
            suppress_numerals: bool = False,
            device: str = "cuda",
            language: str = "en",
            batch_size: int = 8
    ):

        self._audio = audiofilename
        self._no_stem = no_stem
        self._suppress_numerals = suppress_numerals
        self._model_name = model_name
        self._batch_size = batch_size
        self._language = language
        self._device = device
        self.start_text = ""

    @property
    def audio(self):
        return self._audio
    
    @property
    def no_stem(self):
        return self._no_stem
    
    @property
    def suppress_numerals(self):
        return self._suppress_numerals
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def batch_size(self):
        return str(self._batch_size)
    
    @property
    def language(self):
        return self._language
    
    @property
    def device(self):
        return self._device


    def format_text(self, text: str) -> str:
        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return  "[" + formatted_time + "] " + text + "\n"


    def clean_output(self, text: str) -> str:
        final_result = ""

        for line in text.splitlines(keepends=False):
            # Check if the line contains a percentage
            match = re.search(r"(\d+)%\|", line)
            if match:
                # If it's not "100%", skip this line
                if match.group(1) != "100":
                    continue
            final_result += (line + " \n")

        return final_result


    def Start(self, parallel: bool = False) -> DiarizationResult:
        if parallel:
            process_name = "diarize_parallel.py"
            mode_text = "Using parallel mode"
        else:
            process_name = "diarize.py"
            mode_text = "Not using parallel mode"

        transcript_filename = self.audio.split('.')[0] + '.txt'
        srt_filename = self.audio.split('.')[0] + '.srt'
        lang = self.language if len(self.language) > 0 else "None"

        text = "Starting diarization process...\n\n\t" + "Input file: " + self.audio + "\n\t" + \
            "Transcript file: " + transcript_filename + "\n\t" + "SRT file: " + srt_filename + "\n\t" + \
            "Parameters:" + "\n\t\t" + \
                "--whisper-model " + self.model_name + "\n\t\t" + \
                "--batch-size " + self.batch_size + "\n\t\t" + \
                "--device " + self.device + "\n\t\t" + \
                "--no-stem " + str(self.no_stem) + "\n\t\t" + \
                "--suppress_numerals " + str(self.suppress_numerals) + "\n\t\t" + \
                "--language " + lang + "\n\t" + \
                mode_text + "\n"

        self.start_text = self.format_text(text)
        dresult = DiarizationResult()

        command = ["python3", process_name,
            "-a", self.audio,
            "--whisper-model", self.model_name,
            "--batch-size", self.batch_size,
            "--device",self.device
        ]
        
        if len(self.language) > 0:
            command.extend(["--language", self.language])
        if self.no_stem:
            command.append("--no-stem")
        if self.suppress_numerals:
            command.append("--suppress_numerals")

        diarize_process = subprocess.Popen(
            command,
            cwd=diarization_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, bufsize=1, universal_newlines=True
        )

        standard_output, error_output = diarize_process.communicate()
        has_errors = False
        search_words = ["exception", "traceback"]

        if error_output:
            has_errors = any(word.lower() in error_output.lower() for word in search_words)
            if has_errors:
                dresult.Error = self.clean_output(error_output)
                dresult.ReturnCode = 1

        if standard_output:
            if has_errors:
                dresult.Output = self.start_text + self.clean_output(standard_output)
            else:
                dresult.Output = self.start_text + self.clean_output(standard_output + '\n' + error_output)

        return dresult
