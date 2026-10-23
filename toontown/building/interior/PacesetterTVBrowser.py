import ctypes
import json
import os
import re
import sys
import time
from ctypes import wintypes
from urllib.parse import parse_qs, urlparse

WINDOW_TITLE = 'Pacesetter TV YouTube Browser'
GWL_STYLE = -16
WS_CHILD = 0x40000000
WS_POPUP = 0x80000000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00080000
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020

user32 = ctypes.windll.user32
parent_hwnd = 0
selection_path = ''
window = None

user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
user32.SetParent.restype = wintypes.HWND
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetWindowPos.restype = wintypes.BOOL
user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND


def _write_result(data):
    if not selection_path:
        return
    folder = os.path.dirname(selection_path)
    os.makedirs(folder, exist_ok=True)
    temp_path = selection_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as output:
        json.dump(data, output)
    os.replace(temp_path, selection_path)


def _normalize_video_url(url):
    parsed = urlparse(str(url).strip())
    host = (parsed.hostname or '').lower()
    video_id = ''
    if host == 'youtu.be':
        video_id = parsed.path.strip('/').split('/')[0]
    elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'):
        if parsed.path == '/watch':
            video_id = parse_qs(parsed.query).get('v', [''])[0]
        elif parsed.path.startswith(('/shorts/', '/embed/', '/live/')):
            parts = parsed.path.strip('/').split('/')
            if len(parts) > 1:
                video_id = parts[1]
    if not re.fullmatch(r'[A-Za-z0-9_-]{6,20}', video_id):
        return ''
    return 'https://www.youtube.com/watch?v=' + video_id


def _find_own_window():
    process_id = os.getpid()
    matches = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == process_id:
            length = user32.GetWindowTextLengthW(hwnd)
            title_buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, title_buffer, length + 1)
            if title_buffer.value == WINDOW_TITLE:
                matches.append(hwnd)
                return False
        return True

    user32.EnumWindows(callback, 0)
    return matches[0] if matches else 0


def _embed_window():
    hwnd = 0
    for _ in range(30):
        hwnd = _find_own_window()
        if hwnd:
            break
        time.sleep(0.05)

    if not hwnd or not user32.IsWindow(parent_hwnd):
        _write_result({'error': 'Could not attach the YouTube browser to the Panda3D game window.'})
        if window:
            window.destroy()
        return

    style = user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
    style = (style & ~(WS_POPUP | WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)) | WS_CHILD
    user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
    user32.SetParent(hwnd, parent_hwnd)
    if user32.GetParent(hwnd) != parent_hwnd:
        _write_result({'error': 'Windows could not embed the YouTube browser inside the game window.'})
        if window:
            window.destroy()
        return

    rect = wintypes.RECT()
    if not user32.GetClientRect(parent_hwnd, ctypes.byref(rect)):
        _write_result({'error': 'Could not read the game window size for the YouTube browser.'})
        if window:
            window.destroy()
        return

    parent_width = max(1, rect.right - rect.left)
    parent_height = max(1, rect.bottom - rect.top)
    width = max(640, int(parent_width * 0.85))
    height = max(360, int(parent_height * 0.80))
    x = (parent_width - width) // 2
    y = (parent_height - height) // 2
    user32.SetWindowPos(hwnd, 0, x, y, width, height, SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW | SWP_FRAMECHANGED)
    user32.SetFocus(hwnd)


class VideoSelectionAPI:
    def select_video(self, url):
        normalized_url = _normalize_video_url(url)
        if not normalized_url:
            return False
        _write_result({'url': normalized_url})
        return True

    def close(self):
        if window:
            window.destroy()
        return True


INJECT_SCRIPT = r'''(function() {
  if (window.__pacesetterTvBridgeInstalled) return;
  window.__pacesetterTvBridgeInstalled = true;

  function normalizeVideoUrl(value) {
    try {
      const url = new URL(String(value || ''), window.location.href);
      const host = url.hostname.toLowerCase();
      let id = '';
      if (host === 'youtu.be') id = url.pathname.replace(/^\/+/, '').split('/')[0];
      else if (['youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'].includes(host)) {
        if (url.pathname === '/watch') id = url.searchParams.get('v') || '';
        else if (/^\/(shorts|embed|live)\//.test(url.pathname)) id = url.pathname.split('/')[2] || '';
      }
      return /^[A-Za-z0-9_-]{6,20}$/.test(id) ? 'https://www.youtube.com/watch?v=' + id : '';
    } catch (_) { return ''; }
  }

  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.textContent = '×';
  closeButton.title = 'Close YouTube browser (Esc)';
  closeButton.setAttribute('aria-label', 'Close YouTube browser');
  closeButton.style.cssText = 'position:fixed;right:8px;bottom:8px;z-index:2147483647;width:36px;height:36px;border:1px solid #666;border-radius:6px;background:rgba(25,25,25,.88);color:white;font:700 25px/30px Arial,sans-serif;cursor:pointer;opacity:.8;padding:0;';
  closeButton.addEventListener('mouseenter', function() { closeButton.style.opacity = '1'; });
  closeButton.addEventListener('mouseleave', function() { closeButton.style.opacity = '.8'; });
  closeButton.addEventListener('click', function(event) {
    event.preventDefault();
    event.stopPropagation();
    if (window.pywebview && window.pywebview.api) window.pywebview.api.close();
  });
  function addCloseButton() {
    if (!document.getElementById('__pacesetter-tv-close')) {
      closeButton.id = '__pacesetter-tv-close';
      (document.body || document.documentElement).appendChild(closeButton);
    }
  }
  addCloseButton();

  document.addEventListener('click', function(event) {
    if (event.target && event.target.closest && event.target.closest('#__pacesetter-tv-close')) return;
    const anchor = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!anchor) return;
    const url = normalizeVideoUrl(anchor.href);
    if (!url) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.stopImmediatePropagation) event.stopImmediatePropagation();
    if (window.pywebview && window.pywebview.api) {
      Promise.resolve(window.pywebview.api.select_video(url)).then(function(accepted) {
        if (accepted) return window.pywebview.api.close();
      }).catch(function(error) {
        console.error('Unable to send the selected video to Pacesetter TV:', error);
      });
    }
  }, true);

  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && window.pywebview && window.pywebview.api) window.pywebview.api.close();
  }, true);
})();'''


def _inject_video_selection():
    try:
        window.evaluate_js(INJECT_SCRIPT)
    except Exception:
        pass


def main():
    global parent_hwnd, selection_path, window
    if len(sys.argv) < 3:
        raise SystemExit(1)
    parent_hwnd = int(sys.argv[1])
    selection_path = sys.argv[2]

    import webview

    api = VideoSelectionAPI()
    window = webview.create_window(
        WINDOW_TITLE,
        'https://www.youtube.com/',
        width=1200,
        height=720,
        resizable=False,
        frameless=True,
        text_select=True,
        zoomable=True,
        js_api=api,
    )
    window.events.before_show += lambda *_: _embed_window()
    window.events.loaded += lambda *_: _inject_video_selection()
    profile_root = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
    storage_path = os.path.join(profile_root, 'ProjectAltis', 'PacesetterTV', 'browser-profile')
    os.makedirs(storage_path, exist_ok=True)
    webview.start(gui='edgechromium', private_mode=False, storage_path=storage_path)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        try:
            _write_result({'error': str(exc)})
        except Exception:
            pass
        raise
