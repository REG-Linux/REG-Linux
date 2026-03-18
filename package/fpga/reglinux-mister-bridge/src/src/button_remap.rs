use evdev::KeyCode;

/// A per-system button mapping from Linux evdev buttons to MiSTer button indices.
///
/// MiSTer cores define their own button layouts via the config string J section.
/// Indices 0-3 are always D-pad (Right, Left, Down, Up). Indices 4+ are face
/// buttons, shoulders, and system buttons in core-specific order.
///
/// This module provides per-system remap tables so that a standard Xbox/PS-style
/// gamepad feels natural on each console.
#[derive(Clone, Copy)]
pub struct ButtonRemap {
    pub south: u8,  // BTN_SOUTH (Xbox A / PS Cross / bottom)
    pub east: u8,   // BTN_EAST  (Xbox B / PS Circle / right)
    pub north: u8,  // BTN_NORTH (Xbox Y / PS Triangle / top)
    pub west: u8,   // BTN_WEST  (Xbox X / PS Square / left)
    pub tl: u8,     // BTN_TL  (L1 / LB)
    pub tr: u8,     // BTN_TR  (R1 / RB)
    pub tl2: u8,    // BTN_TL2 (L2 / LT)
    pub tr2: u8,    // BTN_TR2 (R2 / RT)
    pub select: u8, // BTN_SELECT
    pub start: u8,  // BTN_START
}

/// Default: A=4, B=5, X=6, Y=7, L=8, R=9, Select=10, Start=11, L2=12, R2=13
const DEFAULT: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 8, tr: 9, select: 10, start: 11, tl2: 12, tr2: 13,
};

/// NES / Game Boy / Game Boy Color / Game & Watch: 2-button (A=right, B=bottom)
/// Core: J,A,B → [4]=A, [5]=B
/// Xbox B(right)→A, Xbox A(bottom)→B
const TWO_BUTTON: ButtonRemap = ButtonRemap {
    south: 5, east: 4, north: 6, west: 7,
    tl: 8, tr: 9, select: 10, start: 11, tl2: 12, tr2: 13,
};

/// SNES: J,B,Y,Select,Start,A,X,L,R
/// [4]=B [5]=Y [6]=Select [7]=Start [8]=A [9]=X [10]=L [11]=R
/// Bottom→B(4), Left→Y(5), Right→A(8), Top→X(9)
const SNES: ButtonRemap = ButtonRemap {
    south: 4, east: 8, north: 9, west: 5,
    tl: 10, tr: 11, select: 6, start: 7, tl2: 12, tr2: 13,
};

/// GBA: J,A,B,Select,Start,L,R
/// [4]=A [5]=B [6]=Select [7]=Start [8]=L [9]=R
/// Right→A(4), Bottom→B(5)
const GBA: ButtonRemap = ButtonRemap {
    south: 5, east: 4, north: 6, west: 7,
    tl: 8, tr: 9, select: 6, start: 7, tl2: 12, tr2: 13,
};

/// Genesis / Megadrive: J,B,C,A,Start,X,Y,Z,Mode
/// [4]=B [5]=C [6]=A [7]=Start [8]=X [9]=Y [10]=Z [11]=Mode
/// Same face as 3-button, plus Top→X(8), LB→Y(9), RB→Z(10)
const GENESIS: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 8, west: 6,
    tl: 9, tr: 10, select: 11, start: 7, tl2: 12, tr2: 13,
};

/// Master System / Game Gear: J,Fire1,Fire2
/// [4]=Fire1 [5]=Fire2
/// Bottom→Fire1(4), Right→Fire2(5)
const SMS: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 8, tr: 9, select: 10, start: 11, tl2: 12, tr2: 13,
};

/// PC Engine / TurboGrafx: J,I,II,Select,Run
/// [4]=I [5]=II [6]=Select [7]=Run
/// Right→I(4), Bottom→II(5)
const PCE: ButtonRemap = ButtonRemap {
    south: 5, east: 4, north: 6, west: 7,
    tl: 8, tr: 9, select: 6, start: 7, tl2: 12, tr2: 13,
};

/// PSX: J,Cross,Circle,Square,Triangle,L1,R1,L2,R2,Select,Start
/// [4]=Cross [5]=Circle [6]=Square [7]=Triangle [8]=L1 [9]=R1
/// [10]=L2 [11]=R2 [12]=Select [13]=Start
/// Bottom→Cross(4), Right→Circle(5), Left→Square(6), Top→Triangle(7)
const PSX: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 7, west: 6,
    tl: 8, tr: 9, select: 12, start: 13, tl2: 10, tr2: 11,
};

/// Neo Geo: J,A,B,C,D,Select,Start
/// [4]=A [5]=B [6]=C [7]=D [8]=Select [9]=Start
/// Bottom→A(4), Right→B(5), Top→C(6), Left→D(7)
const NEOGEO: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 8, tr: 9, select: 8, start: 9, tl2: 12, tr2: 13,
};

/// N64: J,A,B,C-Up,C-Down,C-Left,C-Right,Z,L,R,Start
/// [4]=A [5]=B [6]=C-Up [7]=C-Down [8]=C-Left [9]=C-Right [10]=Z [11]=L [12]=R [13]=Start
/// South→A(4), East→B(5), North→C-Up(6), West→C-Down(7)
/// LB→L(11), RB→R(12), LT→Z(10), Select→C-Left(8), Start→Start(13)
const N64: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 11, tr: 12, select: 8, start: 13, tl2: 10, tr2: 9,
};

/// Saturn: J,A,B,C,X,Y,Z,L,R,Start
/// [4]=A [5]=B [6]=C [7]=X [8]=Y [9]=Z [10]=L [11]=R [12]=Start
/// South→A(4), East→B(5), West→X(7), North→Y(8)
/// RB→C(6), RT→Z(9), LB→L(10), LT→R(11), Start→Start(12)
const SATURN: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 8, west: 7,
    tl: 10, tr: 6, select: 13, start: 12, tl2: 11, tr2: 9,
};

/// Atari 2600 / 7800: J,Fire (single button)
const ATARI: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 8, tr: 9, select: 10, start: 11, tl2: 12, tr2: 13,
};

/// ColecoVision: J,Fire1,Fire2,1,2,3,4,5,6,7,8,9,*,0,#
/// First two buttons at 4,5
const COLECO: ButtonRemap = ButtonRemap {
    south: 4, east: 5, north: 6, west: 7,
    tl: 8, tr: 9, select: 10, start: 11, tl2: 12, tr2: 13,
};

/// Get the button remap table for a given system name.
pub fn get_remap(system: &str) -> ButtonRemap {
    match system {
        // 2-button systems (NES-style: A=right, B=left/bottom)
        "nes" | "fds" | "gb" | "gbc" | "sgb" | "gameandwatch"
        | "pokemini" | "supervision" | "gamate" | "megaduck"
        | "advision" | "creativision" => TWO_BUTTON,

        // N64 (A, B, C-buttons, Z, L, R, Start)
        "n64" => N64,

        // SNES-style (4 face + L/R, with Select/Start in middle)
        "snes" | "satellaview" | "sufami" => SNES,

        // GBA (A/B + L/R)
        "gba" => GBA,

        // Sega Genesis / Megadrive (6-button layout)
        "megadrive" | "sega32x" | "segacd" => GENESIS,

        // Sega Master System / Game Gear / SG-1000
        "mastersystem" | "gamegear" | "sg1000" => SMS,

        // PC Engine / TurboGrafx / PC-FX
        "pcengine" | "pcenginecd" | "supergrafx" | "pcfx" => PCE,

        // PlayStation
        "psx" => PSX,

        // Saturn (6-button: A,B,C,X,Y,Z + L,R)
        "saturn" => SATURN,

        // Neo Geo
        "neogeo" => NEOGEO,

        // Atari consoles
        "atari2600" | "atari5200" | "atari7800" | "lynx" | "jaguar" => ATARI,

        // ColecoVision / Intellivision / Coleco Adam / Epoch SCV
        "colecovision" | "intellivision" | "colecoadam" | "scv" | "pv1000" => COLECO,

        // WonderSwan (same 2-button feel)
        "wswan" | "wswanc" => TWO_BUTTON,

        // Vectrex / Odyssey / Channel F / Arcadia / VC4000
        "vectrex" | "o2em" | "channelf" | "astrocde"
        | "vc4000" | "arcadia" | "rx78" | "sv8000" => ATARI,

        // Computer systems (keyboard-driven, default button map is fine)
        "c64" | "c128" | "c16" | "c20" | "pet"
        | "amiga" | "amiga500" | "amiga1200"
        | "msx" | "msx1" | "msx2" | "dos" | "pcxt"
        | "zxspectrum" | "zx81" | "zxnext" | "samcoupe" | "ql"
        | "amstradcpc" | "amstradpcw"
        | "apple1" | "apple2" | "macintosh" | "bbc" | "oric" | "aquarius"
        | "atari800" | "atarist" | "ti99" | "coco" | "coco2" | "trs80" | "mc10"
        | "x68000" | "pc88" | "archimedes" | "acornatom" | "electron"
        | "jupiterace" | "laser310" | "sordm5" | "einstein" | "tomytutor"
        | "camplynx" | "svi328" | "enterprise" | "bk0011m" | "arduboy" => DEFAULT,

        // CD-based consoles (default mapping works)
        "cdi" => DEFAULT,

        _ => DEFAULT,
    }
}

/// Map an evdev KeyCode to a MiSTer button index using the given remap table.
/// D-pad buttons always map to indices 0-3 regardless of system.
pub fn map_button(remap: &ButtonRemap, code: KeyCode) -> Option<u8> {
    match code {
        // D-pad is universal
        KeyCode::BTN_DPAD_UP => Some(3),
        KeyCode::BTN_DPAD_DOWN => Some(2),
        KeyCode::BTN_DPAD_LEFT => Some(1),
        KeyCode::BTN_DPAD_RIGHT => Some(0),
        // Face buttons
        KeyCode::BTN_SOUTH => Some(remap.south),
        KeyCode::BTN_EAST => Some(remap.east),
        KeyCode::BTN_NORTH => Some(remap.north),
        KeyCode::BTN_WEST => Some(remap.west),
        // Shoulders / triggers
        KeyCode::BTN_TL => Some(remap.tl),
        KeyCode::BTN_TR => Some(remap.tr),
        KeyCode::BTN_TL2 => Some(remap.tl2),
        KeyCode::BTN_TR2 => Some(remap.tr2),
        // System buttons
        KeyCode::BTN_SELECT => Some(remap.select),
        KeyCode::BTN_START => Some(remap.start),
        _ => None,
    }
}
