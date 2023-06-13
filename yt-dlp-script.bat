@ECHO OFF
REM Downloads Video, converts into MKV and embeds subtitles
REM https://askubuntu.com/questions/1022855/download-everything-from-a-youtube-video-using-youtube-dl/1022993#1022993
set path="LearnItalianWithLucrezia"
set youtubeURL="https://www.youtube.com/@lucreziaoddone/videos"
IF NOT EXIST "./archive/videos/%folderPath%/" MKDIR "./archive/videos/%folderPath%/" 
IF NOT EXIST "./archive/videos/%folderPath%/%folderPath%.ytdlarchive" ECHO. > "./archive/videos/%folderPath%/%folderPath%.ytdlarchive" 
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
--download-archive "./archive/videos/%folderPath%/%folderPath%.ytdlarchive" ^
--format "bestvideo+bestaudio/best" ^
--merge-output-format "mkv" ^
--ffmpeg-location "C:\Users\Lupin\Desktop\ffmpeg\bin\ffmpeg.exe" ^
--output "./archive/videos/%folderPath%/%%(upload_date)s_%%(id)s/%folderPath%_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"%youtubeURL%"

IF NOT EXIST "./archive/videos/%folderPath%/%folderPath%.ytdlarchive" ECHO. > "./archive/videos/%folderPath%/%folderPath%_subtitles.ytdlarchive" 
REM Downloads additional externally available SUBTITLES to the folder of downloaded video
yt-dlp ^
--skip-download ^
--retries "3" ^
--call-home ^
--sub-langs "en" ^
--convert-subs "srt" ^
--output "./archive/videos/%folderPath%/%%(upload_date)s_%%(id)s/%folderPath%_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"%youtubeURL%"


REM Downloads additional and missing THUMBNAILS
yt-dlp ^
--skip-download ^
--write-all-thumbnails ^
--ignore-config ^
--id ^
--output "./archive/videos/%folderPath%/%%(upload_date)s_%%(id)s/%folderPath%_%%(upload_date)s_%%(id)s_%%(title)s.%%(ext)s" ^
"%youtubeURL%"
PAUSE