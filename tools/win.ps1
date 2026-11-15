# win.ps1 shot <out.png>            capture only the Victoria 2 window
# win.ps1 click <x> <y>             left click at window-relative coordinates
# win.ps1 key <sendkeys string>     send keys to the game window
# win.ps1 scroll <x> <y> <delta>    mouse wheel at window-relative coordinates
param([string]$cmd, [string]$a, [string]$b, [string]$c)
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, int d, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
"@
[void][W]::SetProcessDPIAware()
$p = Get-Process v2game -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { "NO GAME"; exit 1 }
$h = $p.MainWindowHandle
$r = New-Object W+RECT; [void][W]::GetClientRect($h, [ref]$r)
$o = New-Object W+POINT; [void][W]::ClientToScreen($h, [ref]$o)
[void][W]::SetForegroundWindow($h); Start-Sleep -Milliseconds 300
if ($cmd -eq 'shot') {
  $w = $r.R - $r.L; $ht = $r.B - $r.T
  $bmp = New-Object System.Drawing.Bitmap $w, $ht
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($o.X, $o.Y, 0, 0, $bmp.Size)
  $bmp.Save($a, [System.Drawing.Imaging.ImageFormat]::Png)
  "shot ${w}x${ht} at $($o.X),$($o.Y)"
} elseif ($cmd -eq 'click') {
  [void][W]::SetCursorPos($o.X + [int]$a, $o.Y + [int]$b); Start-Sleep -Milliseconds 150
  [W]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 80
  [W]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero); "clicked $a,$b"
} elseif ($cmd -eq 'scroll') {
  [void][W]::SetCursorPos($o.X + [int]$a, $o.Y + [int]$b); Start-Sleep -Milliseconds 150
  [W]::mouse_event(0x800, 0, 0, [int]$c, [UIntPtr]::Zero); "scrolled $c"
} elseif ($cmd -eq 'key') {
  [System.Windows.Forms.SendKeys]::SendWait($a); "sent $a"
}
