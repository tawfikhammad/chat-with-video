from typing import Tuple, Dict, List, Optional
from .base_controller import BaseController
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, 
    TranscriptsDisabled, 
    VideoUnavailable,
)
import re
class DataController(BaseController):
    def __init__(self, video_url: str):
        super().__init__()
        self.video_url = video_url

    def get_video_id(self) -> str:
    
        pattern = r'^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w\-_]{11})(?:\S+)?$'
        match = re.match(pattern, self.video_url)
        if match:
            self.logger.info(f"Extracted video ID: {match.group(1)}")
            return match.group(1)
        else:
            self.logger.error("Failed to extract video ID from URL")
            return None

    def get_video_metadata(self, video_id: str) -> Dict:

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            api_key = self.app_settings.YOUTUBE_API

            params = {
                "part": "snippet",
                "id": video_id,
                "key": api_key
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['items']:
                    snippet = data['items'][0]['snippet']

                    return {
                        "title": snippet.get("title", "Unavailable"),
                        "author": snippet.get("channelTitle", "Unavailable"),
                        "description": snippet.get("description", ""),
                        "publish_time": snippet.get("publishedAt", ""),
                    }
                else:
                    self.logger.error(f"Video not found for ID: {video_id}")
                    return None
            else:
                self.logger.error(f"API request failed with status {response.status_code}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error fetching video metadata: {str(e)}")
            return None
    
    def get_video_transcript(self, video_id: str) -> Optional[List[dict]]:

        try:
            languages = ['en', 'en-US', 'en-GB', 'a.en']
            
            for language in languages:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
                    if transcript:
                        return transcript
                except Exception:
                    continue

            self.logger.error(f"Unsupported language for this video ID: {video_id}")
            return None
            
        except NoTranscriptFound:
            self.logger.error(f"No transcript found for video ID: {video_id}")
            return None
        except TranscriptsDisabled:
            self.logger.error(f"Transcripts are disabled for video ID: {video_id}")
            return None
        except VideoUnavailable:
            self.logger.error(f"Video unavailable for ID: {video_id}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving transcript: {str(e)}")
            return None
        

