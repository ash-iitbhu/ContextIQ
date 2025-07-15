from pytubefix import YouTube


async def extract_youtube_transcript(url):
    try:
        yt = YouTube(url)
        if not yt.captions:
            return "No captions available for this video."

        if not yt.captions.get_by_language_code("a.en"):
            if not yt.captions.get_by_language_code("en"):
                return "No English captions available for this video."
            caption = yt.captions.get_by_language_code("en")
        else:
            caption = yt.captions.get_by_language_code("a.en")

        transcript = caption.generate_srt_captions()
        return transcript
    except Exception as e:
        return f"Error extracting YouTube transcript: {str(e)}"
