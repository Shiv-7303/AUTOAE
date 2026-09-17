import http.server
import socketserver
import os
import sys
import shutil
import subprocess
import tempfile
import time

PORT = int(os.environ.get('PORT', 3000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg_path():
    p = shutil.which("ffmpeg")
    if p:
        return p
    winget_dir = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    if os.path.exists(winget_dir):
        for root, dirs, files in os.walk(winget_dir):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
    return "ffmpeg"

def get_ffprobe_path():
    p = shutil.which("ffprobe")
    if p:
        return p
    ffmpeg_p = get_ffmpeg_path()
    probe_cand = ffmpeg_p.replace("ffmpeg.exe", "ffprobe.exe").replace("ffmpeg", "ffprobe")
    if os.path.exists(probe_cand):
        return probe_cand
    return "ffprobe"

FFMPEG_BIN = get_ffmpeg_path()
FFPROBE_BIN = get_ffprobe_path()
print(f"[*] Detected FFmpeg: {FFMPEG_BIN}")
print(f"[*] Detected FFprobe: {FFPROBE_BIN}")

def check_audio_stream(filepath):
    try:
        cmd = [FFPROBE_BIN, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", filepath]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return 'audio' in r.stdout.lower()
    except Exception:
        return False

class AutoAEHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Audio-Length')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)

        # ---------------------------------------------------------------------
        # 0. BACKGROUND VIDEO UPLOAD (Native server compositing for zero flicker)
        # ---------------------------------------------------------------------
        if parsed.path.startswith('/api/upload_bg_video'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_error(400, "Empty payload")
                    return
                temp_dir = tempfile.gettempdir()
                ts = int(time.time() * 1000)
                bg_filename = f"autoae_bg_{ts}.mp4"
                bg_path = os.path.join(temp_dir, bg_filename)
                with open(bg_path, 'wb') as f:
                    bytes_left = content_length
                    chunk_size = 65536
                    while bytes_left > 0:
                        chunk = self.rfile.read(min(bytes_left, chunk_size))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_left -= len(chunk)

                import json
                resp = json.dumps({"status": "ok", "id": bg_filename}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                print(f"[*] Stored background video: {bg_filename} ({content_length} bytes)")
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        # ---------------------------------------------------------------------
        # 1. DETERMINISTIC FRAME-PIPE RENDERER (100% Butter-Smooth Master Quality)
        # ---------------------------------------------------------------------
        if parsed.path.startswith('/api/render_frames'):
            try:
                qs = parse_qs(parsed.query)
                target_fps = int(qs.get('fps', ['60'])[0])
                target_w = qs.get('w', ['1920'])[0]
                target_h = qs.get('h', ['1080'])[0]
                quality = qs.get('quality', ['1080p_60'])[0]
                export_format = qs.get('format', ['mp4'])[0]
                bg_video_id = qs.get('bg_video_id', [None])[0]
                bg_dim = float(qs.get('bg_dim', ['0.25'])[0])
                total_dur = float(qs.get('dur', ['0'])[0])

                content_length = int(self.headers.get('Content-Length', 0))
                audio_length = int(self.headers.get('X-Audio-Length', 0))

                if content_length == 0:
                    self.send_error(400, "Empty payload")
                    return

                temp_dir = tempfile.gettempdir()
                ts = int(time.time() * 1000)
                audio_path = os.path.join(temp_dir, f"autoae_audio_{ts}.wav")
                output_ext = "webm" if export_format == "webm" else "mp4"
                output_path = os.path.join(temp_dir, f"autoae_render_{ts}.{output_ext}")

                if audio_length > 0:
                    audio_bytes = self.rfile.read(audio_length)
                    with open(audio_path, 'wb') as af:
                        af.write(audio_bytes)

                frames_length = content_length - audio_length
                frames_path = os.path.join(temp_dir, f"autoae_frames_{ts}.bin")
                with open(frames_path, 'wb') as ff:
                    bytes_left = frames_length
                    chunk_size = 65536
                    while bytes_left > 0:
                        read_len = min(bytes_left, chunk_size)
                        chunk = self.rfile.read(read_len)
                        if not chunk:
                            break
                        ff.write(chunk)
                        bytes_left -= len(chunk)

                bg_path = os.path.join(temp_dir, bg_video_id) if bg_video_id else None
                has_valid_bg = bg_path and os.path.exists(bg_path) and os.path.getsize(bg_path) > 0

                if export_format == "webm":
                    cmd = [
                        FFMPEG_BIN, "-y",
                        "-f", "image2pipe",
                        "-vcodec", "png",
                        "-framerate", str(target_fps),
                        "-i", frames_path,
                        "-c:v", "libvpx-vp9",
                        "-pix_fmt", "yuva420p",
                        "-b:v", "0",
                        "-crf", "18",
                        output_path
                    ]
                elif has_valid_bg:
                    # NATIVE ZERO-FLICKER FFMPEG COMPOSITING
                    has_bg_audio = check_audio_stream(bg_path)
                    has_render_audio = audio_length > 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0

                    filter_complex = f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},setsar=1[bg]; [bg]drawbox=c=black@{bg_dim}:replace=0[bgdim]; [bgdim][1:v]overlay=0:0:eof_action=endall[outv]"

                    cmd = [
                        FFMPEG_BIN, "-y",
                        "-stream_loop", "-1", "-i", bg_path,
                        "-f", "image2pipe", "-vcodec", "png", "-framerate", str(target_fps), "-i", frames_path,
                    ]

                    if has_render_audio:
                        cmd.extend(["-i", audio_path])

                    if has_bg_audio and has_render_audio:
                        filter_complex += "; [0:a][2:a]amix=inputs=2:duration=first[outa]"
                        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]", "-map", "[outa]"])
                    elif has_render_audio:
                        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]", "-map", "2:a"])
                    elif has_bg_audio:
                        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]", "-map", "0:a"])
                    else:
                        cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]"])

                    cmd.extend([
                        "-c:v", "libx264",
                        "-preset", "fast",
                        "-crf", "16",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac",
                        "-b:a", "192k",
                    ])
                    if total_dur > 0:
                        cmd.extend(["-t", f"{total_dur:.3f}"])
                    cmd.extend(["-movflags", "+faststart", output_path])
                else:
                    if audio_length > 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                        cmd = [
                            FFMPEG_BIN, "-y",
                            "-f", "image2pipe",
                            "-vcodec", "mjpeg",
                            "-framerate", str(target_fps),
                            "-i", frames_path,
                            "-i", audio_path,
                            "-c:v", "libx264",
                            "-preset", "fast",
                            "-crf", "16",
                            "-pix_fmt", "yuv420p",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-shortest",
                            "-movflags", "+faststart",
                            output_path
                        ]
                    else:
                        cmd = [
                            FFMPEG_BIN, "-y",
                            "-f", "image2pipe",
                            "-vcodec", "mjpeg",
                            "-framerate", str(target_fps),
                            "-i", frames_path,
                            "-c:v", "libx264",
                            "-preset", "fast",
                            "-crf", "16",
                            "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart",
                            output_path
                        ]

                print(f"[*] Deterministic frame-pipe encoding ({quality}, {target_fps}fps, format={export_format}, frames={os.path.getsize(frames_path)} bytes)...")
                res = subprocess.run(cmd, capture_output=True)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, 'rb') as f:
                        video_data = f.read()

                    filename = f"autoae_{quality}.{output_ext}"
                    content_type = "video/webm" if export_format == "webm" else "video/mp4"

                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.send_header('Content-Length', str(len(video_data)))
                    self.end_headers()
                    self.wfile.write(video_data)
                    print(f"[OK] Deterministic render finished: {filename} ({len(video_data)} bytes)")
                else:
                    err_msg = res.stderr.decode('utf-8', errors='ignore')
                    print("[!] FFmpeg render failed:", err_msg)
                    self.send_error(500, f"FFmpeg render error: {err_msg[:200]}")

                # Cleanup temp files
                if os.path.exists(frames_path):
                    try: os.remove(frames_path)
                    except: pass
                if os.path.exists(audio_path):
                    try: os.remove(audio_path)
                    except: pass
                if os.path.exists(output_path):
                    try: os.remove(output_path)
                    except: pass

            except Exception as e:
                print(f"[!] Error in render_frames: {e}")
                self.send_error(500, str(e))
            return

        # ---------------------------------------------------------------------
        # 2. LEGACY WEBM TO MP4 CONVERTER FALLBACK
        # ---------------------------------------------------------------------
        if parsed.path.startswith('/api/convert_to_mp4'):
            try:
                qs = parse_qs(parsed.query)
                target_fps = qs.get('fps', ['30'])[0]
                target_w = qs.get('w', [''])[0]
                target_h = qs.get('h', [''])[0]
                quality = qs.get('quality', ['4k_30'])[0]

                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_error(400, "Empty payload")
                    return

                video_bytes = self.rfile.read(content_length)

                temp_dir = tempfile.gettempdir()
                ts = int(time.time() * 1000)
                input_path = os.path.join(temp_dir, f"autoae_input_{ts}.webm")
                output_path = os.path.join(temp_dir, f"autoae_output_{ts}.mp4")

                with open(input_path, 'wb') as f:
                    f.write(video_bytes)

                # Configure filters for 4K / 30fps / custom resolution
                vf_filters = []
                if target_w and target_h:
                    vf_filters.append(f"scale={target_w}:{target_h}:flags=lanczos")
                else:
                    vf_filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")
                vf_filters.append(f"fps={target_fps}")

                # Convert to high-quality H.264 MP4 with YUV420p (universally playable)
                cmd = [
                    FFMPEG_BIN,
                    "-y",
                    "-i", input_path,
                    "-vf", ",".join(vf_filters),
                    "-r", str(target_fps),
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "17",
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    output_path
                ]

                print(f"[*] Encoding {quality} ({target_w}x{target_h} @ {target_fps}fps) via FFmpeg...")
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, 'rb') as f:
                        mp4_data = f.read()

                    filename = f"autoae_{quality}.mp4"
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/mp4')
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                    self.send_header('Content-Length', str(len(mp4_data)))
                    self.end_headers()
                    self.wfile.write(mp4_data)
                    print(f"[OK] Successfully encoded and sent 4K MP4 ({len(mp4_data)} bytes)")
                else:
                    # If ffmpeg had an issue, send back original with webm
                    print("[!] FFmpeg conversion failed, sending original:", proc.stderr.decode('utf-8', errors='ignore'))
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/webm')
                    self.send_header('Content-Length', str(len(video_bytes)))
                    self.end_headers()
                    self.wfile.write(video_bytes)

                # Clean temp files
                if os.path.exists(input_path):
                    try: os.remove(input_path)
                    except: pass
                if os.path.exists(output_path):
                    try: os.remove(output_path)
                    except: pass

            except Exception as e:
                print(f"[!] Error in convert_to_mp4: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Endpoint not found")

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), AutoAEHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("==================================================")
        print(f"AutoAE Motion Studio Server: {url}")
        print(f"Native FFmpeg MP4 Converter: READY")
        print("==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)
