import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from typing import Optional, Tuple
import io

load_dotenv()

# Azure Speech Configuration
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Voice configurations
URDU_VOICE = "ur-PK-UzmaNeural"  # Female Urdu voice
ENGLISH_VOICE = "en-US-JennyNeural"  # Female English voice (professional)

# Audio output directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = BASE_DIR / "audio_files"
AUDIO_DIR.mkdir(exist_ok=True)


class VoiceService:
    """Azure Speech Services Integration"""
    
    def __init__(self):
        """Initialize Azure Speech Config"""
        self.speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )
        
        # Set audio format for high quality
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
    
    
    def text_to_speech(
        self, 
        text: str, 
        language: str = "auto",
        save_file: bool = True
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            language: 'urdu', 'english', or 'auto' (auto-detect)
            save_file: Whether to save audio as .mp3 file
            
        Returns:
            Tuple of (audio_bytes, file_path)
        """
        
        # Auto-detect language if not specified
        if language == "auto":
            language = self._detect_language(text)
        
        # Select voice based on language
        if language == "urdu":
            voice_name = URDU_VOICE
        else:
            voice_name = ENGLISH_VOICE
        
        self.speech_config.speech_synthesis_voice_name = voice_name
        
        try:
            if save_file:
                # Generate unique filename
                filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
                file_path = AUDIO_DIR / filename
                
                # Configure audio output to file
                audio_config = speechsdk.audio.AudioOutputConfig(
                    filename=str(file_path)
                )
                
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    # Read file as bytes
                    with open(file_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    return audio_bytes, str(file_path)
                else:
                    print(f"Speech synthesis failed: {result.reason}")
                    return None, None
            
            else:
                # Return audio stream without saving
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=None
                )
                
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return result.audio_data, None
                else:
                    print(f"Speech synthesis failed: {result.reason}")
                    return None, None
                    
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return None, None
    
    
    def speech_to_text(
        self, 
        audio_data: bytes,
        language: str = "auto"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert speech to text
        
        Args:
            audio_data: Audio file bytes (WAV format preferred)
            language: 'urdu', 'english', or 'auto' (supports both)
            
        Returns:
            Tuple of (recognized_text, detected_language)
        """
        
        try:
            # Save audio temporarily
            temp_file = AUDIO_DIR / f"temp_{uuid.uuid4().hex[:8]}.wav"
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            # Configure audio input
            audio_config = speechsdk.audio.AudioConfig(filename=str(temp_file))
            
            if language == "auto":
                # Auto-detect language (English or Urdu)
                auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                    languages=["en-US", "ur-PK"]
                )
                
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    auto_detect_source_language_config=auto_detect_config,
                    audio_config=audio_config
                )
            else:
                # Specific language
                if language == "urdu":
                    self.speech_config.speech_recognition_language = "ur-PK"
                else:
                    self.speech_config.speech_recognition_language = "en-US"
                
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
            
            # Perform recognition
            result = speech_recognizer.recognize_once_async().get()
            
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                detected_lang = "urdu" if "ur" in str(result.language) else "english"
                return result.text, detected_lang
            
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized")
                return None, None
            
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")
                return None, None
                
        except Exception as e:
            print(f"STT Error: {str(e)}")
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            return None, None
    
    
    def _detect_language(self, text: str) -> str:
        """
        Auto-detect language from text
        
        Args:
            text: Input text
            
        Returns:
            'urdu' or 'english'
        """
        # Check for Urdu Unicode range (basic check)
        urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "english"
        
        # If more than 30% characters are Urdu, consider it Urdu
        if (urdu_chars / total_chars) > 0.3:
            return "urdu"
        else:
            return "english"
    
    
    def get_available_voices(self) -> dict:
        """
        Get list of available voices
        
        Returns:
            Dictionary with voice information
        """
        return {
            "urdu": {
                "voice_name": URDU_VOICE,
                "language": "ur-PK",
                "gender": "Female",
                "description": "Uzma - Professional Urdu voice"
            },
            "english": {
                "voice_name": ENGLISH_VOICE,
                "language": "en-US",
                "gender": "Female",
                "description": "Jenny - Professional English voice"
            }
        }


# Global instance
voice_service = VoiceService()