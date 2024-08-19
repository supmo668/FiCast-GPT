from functools import lru_cache
import random
from typing import Any, Dict, List, Generator, Union
from collections.abc import AsyncGenerator
import warnings
import dotenv

from elevenlabs import Voice, play, voices

from .utils import CustomJSONEncoder
from .clients import tts_client_factory

dotenv.load_dotenv()

class TextToSpeech:
  voice_wildcards = ["random", "any"]

  def __init__(self, client_type: str, **kwargs: Any):
    """
    Initializes the TextToSpeech object.

    Args:
        client_type (str): The type of TTS client to use.
          Supported: 'api', 'elevenlabs'
    Returns:
        None
    """
    #### Init TTS Client
    self.client = tts_client_factory(client_type, **kwargs)

  @property
  def n_voices(self):
    return len(self.all_voices_by_id)
  
  @property
  @lru_cache(maxsize=None)
  def all_voices_by_id(self) -> Dict[str, Union[Voice, str, Any]]:
    return self.client.all_voices_by_id
  
  def get_random_voices(self):
    voices = list(self.all_voices_by_id.values())
    random.shuffle(voices)
    return voices
  
  def get_random_voice(self):
    return self.get_random_voices()[0]
  
  def get_voice(self, voice_id:str) -> Union[Voice, str]:
    """
    Retrieves a voice from the list of available voices based on the provided voice ID.
    Args:
        voice (str): The name of the voice to retrieve.
        save_meta (bool, optional): Whether to save the metadata of the retrieved voice. Defaults to True.
        output_dir (pathlib.Path, optional): The directory to save the metadata file. Defaults to "output/speech".
    Return: 
      The Voice object corresponding to the specified voice ID that `client.text_to_speech` identity with for generation
    """
    return self.all_voices_by_id[voice_id]
  
  def _validate_voice_type(self, voice: str | Voice) -> None:
    if isinstance(voice, Voice):
      return 
    elif isinstance(voice, str):
      if voice in self.voice_wildcards:
        return
      if self.all_voices_by_id.get(voice):
        return
      else:
        raise ValueError(f"Voice with ID `{voice}` not found. Supported wildcard options are {self.voice_wildcards}")
            
  def synthesize(
    self,
    text: str, 
    voice_id: int = None, 
    voice_name: str = "random", 
    **kwargs
  ) -> Generator[bytearray, None, None] | AsyncGenerator[bytearray, None, None]:
      
    # Check if both voice_id and voice_name are provided
    if voice_id and voice_name:
      warnings.warn("Both `voice_id` and `voice_name` are provided. Defaulting to `voice_id`.")
    # If only voice_name is provided, validate it
    if not voice_id and voice_name:
      self._validate_voice_type(voice_name)
      if voice_name in self.voice_wildcards:
          voice = self.get_random_voice()
      voice = voice_name
    else:
      # get voice by voice_id
      voice = self.get_voice(voice_id)
    # Synthesize the audio using the provided or selected voice
    audio = self.client.text_to_speech(
      text=text, voice=voice, **kwargs
    )
    return audio

class DialogueSynthesis(TextToSpeech):
  audio_encoding: str = "latin-1"
  def __init__(self, client_type="elevenlabs", **kwargs):
    super().__init__(client_type=client_type, **kwargs)
  
  def get_nth_voice_by_gender(self, nth: int, gender: str=None):
    if gender is None:
      return self.get_random_voice()
    assert gender in ['male', 'female', 'andy'], "Not a supported gender, must be 'male', 'female' or 'andy'"
    # loop through voices
    nth_voice = 0
    for _, voice in self.all_voices_by_id.items():
      if voice.labels.get("gender") == gender:
        gender_voice = voice
        if nth == nth_voice:
          return gender_voice
        nth_voice += 1
    if nth_voice == 0 or nth > nth_voice:
      warnings.warn(f"Could not find the {nth} voice for gender {gender}. Using the (n_available % nth) voice which is the {nth_voice} voice. Check as it may not be the desired or duplicate with existing voices", UserWarning)
    return self.get_random_voice()
  
if __name__=="__main__":
  from .utils import collect_audio, save_bytes_to_mp3
  def main():
    dialogue = DialogueSynthesis('elevenlabs')
    gen = dialogue.synthesize(
      (dialogue.all_voices)[0].voice_id, 
      "Hi David, how have you been?"
    )
    audio = collect_audio(gen)
    save_bytes_to_mp3(audio, 'ficast-outputs/dialogue/test.mp3')
    play(audio)
  
  main()


