use mister_fpga::core::MisterFpgaCore;
use mister_fpga::fpga::osd_io::{OsdDisable, OsdEnable, OsdIoWriteLine};
use std::time::{Duration, Instant};
use tracing::debug;

/// How long a status message stays visible on the OSD.
const MESSAGE_DURATION: Duration = Duration::from_millis(1500);

/// OSD line width in pixels (columns).
const OSD_WIDTH: usize = 256;

/// Character width: 5 data columns + 1 spacing column.
const CHAR_WIDTH: usize = 6;

/// Manages transient status messages on the FPGA OSD overlay.
pub struct StatusOsd {
    /// When the current message expires, or None if hidden.
    visible_until: Option<Instant>,
}

impl StatusOsd {
    pub fn new() -> Self {
        Self {
            visible_until: None,
        }
    }

    /// Show a status message on the OSD. Auto-hides after MESSAGE_DURATION.
    pub fn show(&mut self, core: &mut MisterFpgaCore, text: &str) {
        let line_buf = render_centered(text);

        // Enable OSD and write one line
        if let Err(e) = core.spi_mut().execute(OsdEnable) {
            debug!("OSD enable failed: {e}");
            return;
        }
        if let Err(e) = core.spi_mut().execute(OsdIoWriteLine(0, &line_buf)) {
            debug!("OSD write failed: {e}");
        }

        self.visible_until = Some(Instant::now() + MESSAGE_DURATION);
    }

    /// Call each iteration: hides the OSD once the message has expired.
    pub fn tick(&mut self, core: &mut MisterFpgaCore) {
        if let Some(until) = self.visible_until {
            if Instant::now() >= until {
                let _ = core.spi_mut().execute(OsdDisable);
                self.visible_until = None;
            }
        }
    }
}

/// Render a text string centered in a 256-byte OSD line buffer.
/// Each byte represents one column of 8 vertical pixels (bit 0 = top).
fn render_centered(text: &str) -> [u8; OSD_WIDTH] {
    let mut buf = [0u8; OSD_WIDTH];
    let text = text.as_bytes();
    let text_width = text.len() * CHAR_WIDTH;
    let start_x = if text_width < OSD_WIDTH {
        (OSD_WIDTH - text_width) / 2
    } else {
        0
    };

    for (i, &ch) in text.iter().enumerate() {
        let glyph = glyph_data(ch);
        let x = start_x + i * CHAR_WIDTH;
        for col in 0..5 {
            let px = x + col;
            if px < OSD_WIDTH {
                buf[px] = glyph[col];
            }
        }
        // 6th column stays 0 (inter-character spacing)
    }

    buf
}

/// Get the 5-column glyph data for an ASCII character.
/// Each byte is one column, bit 0 = top pixel, bit 6 = bottom pixel.
fn glyph_data(ch: u8) -> [u8; 5] {
    match ch {
        b' ' => [0x00, 0x00, 0x00, 0x00, 0x00],
        b'!' => [0x00, 0x00, 0x5F, 0x00, 0x00],
        b'.' => [0x00, 0x60, 0x60, 0x00, 0x00],
        b'-' => [0x08, 0x08, 0x08, 0x08, 0x08],
        b'/' => [0x20, 0x10, 0x08, 0x04, 0x02],
        b':' => [0x00, 0x36, 0x36, 0x00, 0x00],
        b'(' => [0x00, 0x1C, 0x22, 0x41, 0x00],
        b')' => [0x00, 0x41, 0x22, 0x1C, 0x00],
        b'#' => [0x14, 0x7F, 0x14, 0x7F, 0x14],
        b'0' => [0x3E, 0x51, 0x49, 0x45, 0x3E],
        b'1' => [0x00, 0x42, 0x7F, 0x40, 0x00],
        b'2' => [0x42, 0x61, 0x51, 0x49, 0x46],
        b'3' => [0x21, 0x41, 0x45, 0x4B, 0x31],
        b'4' => [0x18, 0x14, 0x12, 0x7F, 0x10],
        b'5' => [0x27, 0x45, 0x45, 0x45, 0x39],
        b'6' => [0x3C, 0x4A, 0x49, 0x49, 0x30],
        b'7' => [0x01, 0x71, 0x09, 0x05, 0x03],
        b'8' => [0x36, 0x49, 0x49, 0x49, 0x36],
        b'9' => [0x06, 0x49, 0x49, 0x29, 0x1E],
        b'A' => [0x7E, 0x11, 0x11, 0x11, 0x7E],
        b'B' => [0x7F, 0x49, 0x49, 0x49, 0x36],
        b'C' => [0x3E, 0x41, 0x41, 0x41, 0x22],
        b'D' => [0x7F, 0x41, 0x41, 0x22, 0x1C],
        b'E' => [0x7F, 0x49, 0x49, 0x49, 0x41],
        b'F' => [0x7F, 0x09, 0x09, 0x09, 0x01],
        b'G' => [0x3E, 0x41, 0x49, 0x49, 0x7A],
        b'H' => [0x7F, 0x08, 0x08, 0x08, 0x7F],
        b'I' => [0x00, 0x41, 0x7F, 0x41, 0x00],
        b'J' => [0x20, 0x40, 0x41, 0x3F, 0x01],
        b'K' => [0x7F, 0x08, 0x14, 0x22, 0x41],
        b'L' => [0x7F, 0x40, 0x40, 0x40, 0x40],
        b'M' => [0x7F, 0x02, 0x0C, 0x02, 0x7F],
        b'N' => [0x7F, 0x04, 0x08, 0x10, 0x7F],
        b'O' => [0x3E, 0x41, 0x41, 0x41, 0x3E],
        b'P' => [0x7F, 0x09, 0x09, 0x09, 0x06],
        b'Q' => [0x3E, 0x41, 0x51, 0x21, 0x5E],
        b'R' => [0x7F, 0x09, 0x19, 0x29, 0x46],
        b'S' => [0x46, 0x49, 0x49, 0x49, 0x31],
        b'T' => [0x01, 0x01, 0x7F, 0x01, 0x01],
        b'U' => [0x3F, 0x40, 0x40, 0x40, 0x3F],
        b'V' => [0x1F, 0x20, 0x40, 0x20, 0x1F],
        b'W' => [0x3F, 0x40, 0x38, 0x40, 0x3F],
        b'X' => [0x63, 0x14, 0x08, 0x14, 0x63],
        b'Y' => [0x07, 0x08, 0x70, 0x08, 0x07],
        b'Z' => [0x61, 0x51, 0x49, 0x45, 0x43],
        // Lowercase → render as uppercase
        b'a'..=b'z' => glyph_data(ch - 32),
        // Unknown → small square
        _ => [0x7F, 0x41, 0x41, 0x41, 0x7F],
    }
}
