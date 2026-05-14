# import azure.cognitiveservices.speech as speechsdk
# from azure.cognitiveservices.speech.audio import PushAudioInputStream, AudioStreamFormat
# import os
# from dotenv import load_dotenv
# import asyncio
# from typing import Optional, AsyncGenerator, Callable
# import traceback

# load_dotenv()

# # Azure Configuration
# SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "").strip().strip('"').strip("'")
# SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "").strip().strip('"').strip("'").split('#')[0].strip()

# print(f"🔑 Speech Key: {SPEECH_KEY[:10]}...{SPEECH_KEY[-5:]} (len={len(SPEECH_KEY)})")
# print(f"🌍 Speech Region: [{SPEECH_REGION}] (len={len(SPEECH_REGION)})")

# # Voice configurations
# URDU_VOICE = "ur-PK-UzmaNeural"
# ENGLISH_VOICE = "en-US-JennyNeural"


# class VoiceEngine:
#     """Real-time Voice-to-Voice Engine for WebSocket"""

#     def __init__(self):
#         if not SPEECH_KEY or not SPEECH_REGION:
#             raise ValueError("Azure Speech credentials not configured in .env file")

#         self.speech_config = speechsdk.SpeechConfig(
#             subscription=SPEECH_KEY,
#             region=SPEECH_REGION
#         )

#         # English-only STT (auto-detect not supported on this subscription)
#         self.speech_config.speech_recognition_language = "en-US"

#         # Configure TTS output format
#         self.speech_config.set_speech_synthesis_output_format(
#             speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
#         )

#         # Audio stream for STT
#         self.push_stream = None
#         self.audio_config = None
#         self.speech_recognizer = None

#         # Recognition flags
#         self.is_recognizing = False
#         self.last_recognized_text = ""
#         self.detected_language = "en-US"

#         # Playback mute flag — when True, incoming audio is discarded
#         self.is_playing_audio = False

#         # Error callback
#         self.on_error_callback = None

#         # Event loop reference for thread-safe callbacks
#         self._loop: Optional[asyncio.AbstractEventLoop] = None

#     def start_continuous_recognition(
#         self,
#         on_recognized_callback: Callable,
#         on_recognizing_callback: Optional[Callable] = None,
#         on_error_callback: Optional[Callable] = None
#     ):
#         """Start continuous speech recognition (English-only)"""

#         self.on_error_callback = on_error_callback

#         try:
#             self._loop = asyncio.get_running_loop()
#         except RuntimeError:
#             self._loop = None

#         try:
#             # Create push stream for incoming audio
#             stream_format = AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
#             self.push_stream = PushAudioInputStream(stream_format=stream_format)
#             self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)

#             # Helper to safely schedule a coroutine from a non-asyncio thread
#             def _schedule_coroutine(coro):
#                 if self._loop and self._loop.is_running():
#                     asyncio.run_coroutine_threadsafe(coro, self._loop)

#             # English-only recognizer
#             self.speech_recognizer = speechsdk.SpeechRecognizer(
#                 speech_config=self.speech_config,
#                 audio_config=self.audio_config
#             )
#             print("🌐 Using English-only recognition (en-US)")

#             # Event handlers
#             def recognized_handler(evt):
#                 try:
#                     if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
#                         text = evt.result.text.strip()

#                         # Skip empty text
#                         if not text:
#                             return

#                         # Skip text received during playback
#                         if self.is_playing_audio:
#                             print(f"🔇 Ignored during playback: {text}")
#                             return

#                         # Detect language from text content
#                         self.detected_language = self.detect_language_from_text(text)
#                         self.last_recognized_text = text
#                         print(f"✅ Recognized ({self.detected_language}): {text}")

#                         if on_recognized_callback:
#                             on_recognized_callback(text, self.detected_language)

#                     elif evt.result.reason == speechsdk.ResultReason.NoMatch:
#                         pass

#                 except Exception as e:
#                     print(f"❌ Error in recognized_handler: {str(e)}")
#                     print(traceback.format_exc())

#             def recognizing_handler(evt):
#                 try:
#                     if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
#                         if self.is_playing_audio:
#                             return

#                         text = evt.result.text
#                         print(f"🎤 Recognizing: {text}")

#                         if on_recognizing_callback:
#                             on_recognizing_callback(text)
#                 except Exception as e:
#                     print(f"❌ Error in recognizing_handler: {str(e)}")

#             def canceled_handler(evt):
#                 print(f"❌ Recognition canceled: {evt.result.reason}")

#                 error_details = "Unknown error"

#                 try:
#                     cancellation = evt.result.cancellation_details
#                     print(f"   Cancellation reason: {cancellation.reason}")

#                     detail_text = getattr(cancellation, 'error_details', 'No details')
#                     print(f"   Error details: {detail_text}")

#                     if cancellation.reason == speechsdk.CancellationReason.Error:
#                         error_details = str(detail_text)

#                         if "AuthenticationFailure" in error_details:
#                             error_details = "Azure Speech authentication failed. Check API key and region."
#                         elif "ConnectionFailure" in error_details:
#                             error_details = "Cannot connect to Azure Speech. Check internet."
#                         elif "Forbidden" in error_details:
#                             error_details = "Access denied. Check subscription."

#                     elif cancellation.reason == speechsdk.CancellationReason.EndOfStream:
#                         error_details = "Audio stream ended"

#                 except Exception as inner_e:
#                     print(f"   ❌ Error reading cancellation details: {str(inner_e)}")
#                     error_details = f"Cancellation error: {str(inner_e)}"

#                 if self.on_error_callback:
#                     _schedule_coroutine(self._call_error_callback(error_details))

#             def session_started_handler(evt):
#                 print("🎙️ Recognition session started")

#             def session_stopped_handler(evt):
#                 print("🛑 Recognition session stopped")

#             # Attach event handlers
#             self.speech_recognizer.recognized.connect(recognized_handler)
#             self.speech_recognizer.recognizing.connect(recognizing_handler)
#             self.speech_recognizer.canceled.connect(canceled_handler)
#             self.speech_recognizer.session_started.connect(session_started_handler)
#             self.speech_recognizer.session_stopped.connect(session_stopped_handler)

#             # Start continuous recognition
#             self.speech_recognizer.start_continuous_recognition_async().get()
#             self.is_recognizing = True

#             print("🎤 Continuous recognition started successfully")

#         except Exception as e:
#             error_msg = f"Failed to start recognition: {str(e)}"
#             print(f"❌ {error_msg}")
#             print(traceback.format_exc())

#             if self.on_error_callback and self._loop and self._loop.is_running():
#                 asyncio.run_coroutine_threadsafe(
#                     self._call_error_callback(error_msg), self._loop
#                 )
#             raise

#     async def _call_error_callback(self, error_details: str):
#         """Helper to safely invoke the error callback"""
#         if self.on_error_callback:
#             self.on_error_callback(error_details)

#     def write_audio_chunk(self, audio_chunk: bytes):
#         """Write incoming audio chunk to recognition stream"""
#         try:
#             # Don't feed audio to recognizer during playback
#             if self.is_playing_audio:
#                 return

#             if self.push_stream and self.is_recognizing:
#                 self.push_stream.write(audio_chunk)
#         except Exception as e:
#             print(f"❌ Error writing audio chunk: {str(e)}")

#     def stop_recognition(self):
#         """Stop continuous recognition"""
#         try:
#             if self.speech_recognizer and self.is_recognizing:
#                 self.speech_recognizer.stop_continuous_recognition_async().get()
#                 self.is_recognizing = False

#                 if self.push_stream:
#                     self.push_stream.close()

#                 print("🛑 Continuous recognition stopped")
#         except Exception as e:
#             print(f"⚠️ Error stopping recognition: {str(e)}")

#     def mute(self):
#         """Mute mic (stop feeding audio to STT)"""
#         self.is_playing_audio = True
#         print("🔇 Mic muted")

#     def unmute(self):
#         """Unmute mic (resume feeding audio to STT)"""
#         self.is_playing_audio = False
#         print("🎤 Mic unmuted")

#     async def text_to_speech_stream(
#         self,
#         text: str,
#         language: str = "en-US"
#     ) -> AsyncGenerator[bytes, None]:
#         """
#         Convert text to speech and stream audio chunks.
#         NOTE: Caller is responsible for mute/unmute timing.
#         """

#         try:
#             # Select voice based on language
#             if "ur" in language.lower():
#                 voice_name = URDU_VOICE
#             else:
#                 voice_name = ENGLISH_VOICE

#             self.speech_config.speech_synthesis_voice_name = voice_name

#             # Use None audio config to get audio data in memory
#             synthesizer = speechsdk.SpeechSynthesizer(
#                 speech_config=self.speech_config,
#                 audio_config=None
#             )

#             print(f"🔊 Synthesizing ({voice_name}): {text[:50]}...")

#             # Synthesize speech
#             result = synthesizer.speak_text_async(text).get()

#             if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#                 audio_data = result.audio_data
#                 print(f"✅ TTS completed: {len(audio_data)} bytes")

#                 # Stream the audio data in chunks
#                 chunk_size = 4096
#                 offset = 0

#                 while offset < len(audio_data):
#                     end = min(offset + chunk_size, len(audio_data))
#                     chunk = audio_data[offset:end]
#                     yield chunk
#                     offset = end
#                     await asyncio.sleep(0.01)

#                 print(f"✅ Streamed {offset} bytes in {offset // chunk_size + 1} chunks")

#             elif result.reason == speechsdk.ResultReason.Canceled:
#                 cancellation = result.cancellation_details
#                 error_msg = getattr(cancellation, 'error_details', 'Unknown TTS error')
#                 print(f"❌ TTS canceled: {cancellation.reason}")
#                 print(f"   Error: {error_msg}")
#                 raise Exception(f"TTS failed: {error_msg}")

#             else:
#                 print(f"❌ TTS unexpected result: {result.reason}")
#                 raise Exception(f"TTS failed with reason: {result.reason}")

#         except Exception as e:
#             print(f"❌ TTS error: {str(e)}")
#             print(traceback.format_exc())
#             raise

#     def detect_language_from_text(self, text: str) -> str:
#         """Detect language from text content (Urdu Unicode detection)"""
#         urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
#         total_chars = len([c for c in text if c.isalpha()])

#         if total_chars == 0:
#             return "en-US"

#         if (urdu_chars / total_chars) > 0.3:
#             return "ur-PK"
#         else:
#             return "en-US"

#     def cleanup(self):
#         """Cleanup resources"""
#         try:
#             self.is_playing_audio = False
#             self.stop_recognition()

#             if self.speech_recognizer:
#                 self.speech_recognizer = None

#             if self.push_stream:
#                 self.push_stream = None

#             print("🧹 VoiceEngine cleanup completed")
#         except Exception as e:
#             print(f"⚠️ Cleanup error: {str(e)}")


# def create_voice_engine() -> VoiceEngine:
#     """Create a new VoiceEngine instance for each WebSocket connection"""
#     return VoiceEngine()































































import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import PushAudioInputStream, AudioStreamFormat
import os
from dotenv import load_dotenv
import asyncio
from typing import Optional, AsyncGenerator, Callable
import traceback

load_dotenv()

# Azure Configuration
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "").strip().strip('"').strip("'")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "").strip().strip('"').strip("'").split('#')[0].strip()

print(f"🔑 Speech Key: {SPEECH_KEY[:10]}...{SPEECH_KEY[-5:]} (len={len(SPEECH_KEY)})")
print(f"🌍 Speech Region: [{SPEECH_REGION}] (len={len(SPEECH_REGION)})")

# Voice configurations
URDU_VOICE = "ur-PK-UzmaNeural"
ENGLISH_VOICE = "en-US-JennyNeural"


class VoiceEngine:
    """Real-time Voice-to-Voice Engine for WebSocket"""

    def __init__(self):
        if not SPEECH_KEY or not SPEECH_REGION:
            raise ValueError("Azure Speech credentials not configured in .env file")

        self.speech_config = speechsdk.SpeechConfig(
            subscription=SPEECH_KEY,
            region=SPEECH_REGION
        )

        # English-only STT (auto-detect not supported on this subscription)
        self.speech_config.speech_recognition_language = "en-US"

        # Configure TTS output format
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        # Audio stream for STT
        self.push_stream = None
        self.audio_config = None
        self.speech_recognizer = None

        # Recognition flags
        self.is_recognizing = False
        self.last_recognized_text = ""
        self.detected_language = "en-US"

        # Playback mute flag
        self.is_playing_audio = False

        # Error callback
        self.on_error_callback = None

        # Event loop reference for thread-safe callbacks
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start_continuous_recognition(
        self,
        on_recognized_callback: Callable,
        on_recognizing_callback: Optional[Callable] = None,
        on_error_callback: Optional[Callable] = None
    ):
        """Start continuous speech recognition (English-only)"""

        self.on_error_callback = on_error_callback

        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None

        try:
            # Create push stream for incoming audio
            stream_format = AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
            self.push_stream = PushAudioInputStream(stream_format=stream_format)
            self.audio_config = speechsdk.audio.AudioConfig(stream=self.push_stream)

            def _schedule_coroutine(coro):
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(coro, self._loop)

            # English-only recognizer
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )
            print("🌐 Using English-only recognition (en-US)")

            def recognized_handler(evt):
                try:
                    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        text = evt.result.text.strip()

                        if not text:
                            return

                        if self.is_playing_audio:
                            print(f"🔇 Ignored during playback: {text}")
                            return

                        self.detected_language = self.detect_language_from_text(text)
                        self.last_recognized_text = text
                        print(f"✅ Recognized ({self.detected_language}): {text}")

                        if on_recognized_callback:
                            on_recognized_callback(text, self.detected_language)

                    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                        pass

                except Exception as e:
                    print(f"❌ Error in recognized_handler: {str(e)}")
                    print(traceback.format_exc())

            def recognizing_handler(evt):
                try:
                    if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                        if self.is_playing_audio:
                            return

                        text = evt.result.text
                        print(f"🎤 Recognizing: {text}")

                        if on_recognizing_callback:
                            on_recognizing_callback(text)
                except Exception as e:
                    print(f"❌ Error in recognizing_handler: {str(e)}")

            def canceled_handler(evt):
                print(f"❌ Recognition canceled: {evt.result.reason}")

                error_details = "Unknown error"

                try:
                    cancellation = evt.result.cancellation_details
                    print(f"   Cancellation reason: {cancellation.reason}")

                    detail_text = getattr(cancellation, 'error_details', 'No details')
                    print(f"   Error details: {detail_text}")

                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        error_details = str(detail_text)

                        if "AuthenticationFailure" in error_details:
                            error_details = "Azure Speech authentication failed. Check API key and region."
                        elif "ConnectionFailure" in error_details:
                            error_details = "Cannot connect to Azure Speech. Check internet."
                        elif "Forbidden" in error_details:
                            error_details = "Access denied. Check subscription."

                    elif cancellation.reason == speechsdk.CancellationReason.EndOfStream:
                        error_details = "Audio stream ended"

                except Exception as inner_e:
                    print(f"   ❌ Error reading cancellation details: {str(inner_e)}")
                    error_details = f"Cancellation error: {str(inner_e)}"

                if self.on_error_callback:
                    _schedule_coroutine(self._call_error_callback(error_details))

            def session_started_handler(evt):
                print("🎙️ Recognition session started")

            def session_stopped_handler(evt):
                print("🛑 Recognition session stopped")

            self.speech_recognizer.recognized.connect(recognized_handler)
            self.speech_recognizer.recognizing.connect(recognizing_handler)
            self.speech_recognizer.canceled.connect(canceled_handler)
            self.speech_recognizer.session_started.connect(session_started_handler)
            self.speech_recognizer.session_stopped.connect(session_stopped_handler)

            self.speech_recognizer.start_continuous_recognition_async().get()
            self.is_recognizing = True

            print("🎤 Continuous recognition started successfully")

        except Exception as e:
            error_msg = f"Failed to start recognition: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())

            if self.on_error_callback and self._loop and self._loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._call_error_callback(error_msg), self._loop
                )
            raise

    async def _call_error_callback(self, error_details: str):
        """Helper to safely invoke the error callback"""
        if self.on_error_callback:
            self.on_error_callback(error_details)

    def write_audio_chunk(self, audio_chunk: bytes):
        """Write incoming audio chunk to recognition stream"""
        try:
            if self.is_playing_audio:
                return

            if self.push_stream and self.is_recognizing:
                self.push_stream.write(audio_chunk)
        except Exception as e:
            print(f"❌ Error writing audio chunk: {str(e)}")

    def stop_recognition(self):
        """Stop continuous recognition"""
        try:
            if self.speech_recognizer and self.is_recognizing:
                self.speech_recognizer.stop_continuous_recognition_async().get()
                self.is_recognizing = False

                if self.push_stream:
                    self.push_stream.close()

                print("🛑 Continuous recognition stopped")
        except Exception as e:
            print(f"⚠️ Error stopping recognition: {str(e)}")

    def mute(self):
        """Mute mic (stop feeding audio to STT)"""
        self.is_playing_audio = True
        print("🔇 Mic muted")

    def unmute(self):
        """Unmute mic (resume feeding audio to STT)"""
        self.is_playing_audio = False
        print("🎤 Mic unmuted")

    async def text_to_speech_stream(
        self,
        text: str,
        language: str = "en-US"
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to speech and stream audio chunks."""

        try:
            if "ur" in language.lower():
                voice_name = URDU_VOICE
            else:
                voice_name = ENGLISH_VOICE

            self.speech_config.speech_synthesis_voice_name = voice_name

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )

            print(f"🔊 Synthesizing ({voice_name}): {text[:50]}...")

            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                print(f"✅ TTS completed: {len(audio_data)} bytes")

                chunk_size = 4096
                offset = 0

                while offset < len(audio_data):
                    end = min(offset + chunk_size, len(audio_data))
                    chunk = audio_data[offset:end]
                    yield chunk
                    offset = end
                    await asyncio.sleep(0.01)

                print(f"✅ Streamed {offset} bytes in {offset // chunk_size + 1} chunks")

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = getattr(cancellation, 'error_details', 'Unknown TTS error')
                print(f"❌ TTS canceled: {cancellation.reason}")
                print(f"   Error: {error_msg}")
                raise Exception(f"TTS failed: {error_msg}")

            else:
                print(f"❌ TTS unexpected result: {result.reason}")
                raise Exception(f"TTS failed with reason: {result.reason}")

        except Exception as e:
            print(f"❌ TTS error: {str(e)}")
            print(traceback.format_exc())
            raise

    def detect_language_from_text(self, text: str) -> str:
        """Detect language from text (Unicode Urdu + Roman Urdu)"""
        # Check Unicode Urdu characters
        urdu_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars > 0 and (urdu_chars / total_chars) > 0.3:
            return "ur-PK"

        # Check Roman Urdu words
        roman_urdu_words = {
            'mujhe', 'mujhay', 'mein', 'main', 'hai', 'hain', 'kya', 'kyun',
            'kaise', 'kab', 'kahan', 'aur', 'ya', 'se', 'ka', 'ke', 'ki',
            'ko', 'par', 'ne', 'ho', 'karna', 'dena', 'lena',
            'batao', 'bata', 'bataye', 'btao', 'fasal', 'kheti', 'khet',
            'pani', 'paani', 'khad', 'beej', 'zameen', 'zamin', 'mitti',
            'chahiye', 'zaroorat', 'apni', 'apna', 'apne', 'mera', 'meri',
            'zyada', 'kam', 'acha', 'ye', 'yeh', 'woh', 'wo', 'lagana', 'dalna',
            'kitna', 'kitni', 'konsi', 'kaunsa', 'waqt',
            'hum', 'tum', 'aap', 'bohat', 'bahut', 'thoda',
            'gandum', 'chawal', 'makki', 'kapas', 'ganna', 'sarson',
            'haan', 'nahi', 'nhi', 'ji', 'shukriya',
            'abhi', 'pehle', 'baad', 'kal', 'aaj',
            'din', 'raat', 'subah', 'shaam', 'dopahar',
        }

        words = text.lower().split()
        if len(words) == 0:
            return "en-US"

        urdu_count = sum(1 for w in words if w.strip('.,?!:;') in roman_urdu_words)
        ratio = urdu_count / len(words)

        if ratio >= 0.25:
            return "ur-PK"

        return "en-US"

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.is_playing_audio = False
            self.stop_recognition()

            if self.speech_recognizer:
                self.speech_recognizer = None

            if self.push_stream:
                self.push_stream = None

            print("🧹 VoiceEngine cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")


def create_voice_engine() -> VoiceEngine:
    """Create a new VoiceEngine instance for each WebSocket connection"""
    return VoiceEngine()