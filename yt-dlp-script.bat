@ECHO OFF
REM Downloads Video, converts into MKV and embeds subtitles
REM https://askubuntu.com/questions/1022855/download-everything-from-a-youtube-video-using-youtube-dl/1022993#1022993
IF NOT EXIST "./archive/videos/LearnItalianWithLucrezia/" MKDIR "./archive/videos/LearnItalianWithLucrezia/" 
IF NOT EXIST "./archive/videos/LearnItalianWithLucrezia/LearnItalianWithLucrezia.ytdlarchive" ECHO. > "./archive/videos/LearnItalianWithLucrezia/LearnItalianWithLucrezia.ytdlarchive" 
yt-dlp ^
--retries "3" ^
--no-overwrites ^
--call-home ^
--write-info-json ^
--write-description ^
--write-thumbnail ^
--sub-langs "en" ^
--convert-subs "srt" ^
--write-annotations ^
--add-metadata ^
--embed-subs ^
--download-archive "./archive/videos/LearnItalianWithLucrezia/LearnItalianWithLucrezia.ytdlarchive" ^
--format "bestvideo+bestaudio/best" ^
--merge-output-format "mkv" ^
--ffmpeg-location "C:\Users\Lupin\Desktop\ffmpeg\bin\ffmpeg.exe" ^
--output "./archive/videos/LearnItalianWithLucrezia/%%(upload_date)s_%%(id)s/LearnItalianWithLucrezia_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"https://www.youtube.com/@lucreziaoddone/videos"

IF NOT EXIST "./archive/videos/LearnItalianWithLucrezia/LearnItalianWithLucrezia.ytdlarchive" ECHO. > "./archive/videos/LearnItalianWithLucrezia/LearnItalianWithLucrezia_subtitles.ytdlarchive" 
REM Downloads additional externally available SUBTITLES to the folder of downloaded video
yt-dlp ^
--skip-download ^
--retries "3" ^
--call-home ^
--sub-langs "en" ^
--convert-subs "srt" ^
--output "./archive/videos/LearnItalianWithLucrezia/%%(upload_date)s_%%(id)s/LearnItalianWithLucrezia_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"https://www.youtube.com/@lucreziaoddone/videos"


REM Downloads additional and missing THUMBNAILS
yt-dlp ^
--skip-download ^
--write-all-thumbnails ^
--ignore-config ^
--id ^
--output "./archive/videos/LearnItalianWithLucrezia/%%(upload_date)s_%%(id)s/LearnItalianWithLucrezia_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"https://www.youtube.com/@lucreziaoddone/videos"
PAUSE