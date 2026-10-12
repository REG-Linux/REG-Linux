use anyhow::{Context, Result};
use std::fs;
use std::path::{Path, PathBuf};
use tracing::info;

/// Static mapping from REG-Linux system names to MiSTer core filename prefixes.
///
/// Prefixes must match the part before `_YYYYMMDD.rbf` in the core filename.
/// Verified against MiSTer-devel GitHub repo names and mrext systems.md.
const SYSTEM_TO_CORE_PREFIX: &[(&str, &str)] = &[
    // Nintendo
    ("nes", "NES"),
    ("fds", "NES"),
    ("snes", "SNES"),
    ("n64", "N64"),
    ("gb", "Gameboy"),
    ("gbc", "Gameboy"),
    ("gba", "GBA"),
    ("sgb", "SGB"),
    ("gameandwatch", "GnW"),
    ("pokemini", "PokemonMini"),
    // Sega
    ("mastersystem", "SMS"),
    ("gamegear", "SMS"),
    ("sg1000", "SG1000"),
    ("megadrive", "Genesis"),
    ("segacd", "MegaCD"),
    ("sega32x", "S32X"),
    ("saturn", "Saturn"),
    // Sony
    ("psx", "PSX"),
    // NEC
    ("pcengine", "TurboGrafx16"),
    ("pcenginecd", "TurboGrafx16"),
    ("supergrafx", "SuperGrafx"),
    ("pcfx", "PCFX"),
    // SNK
    ("neogeo", "NeoGeo"),
    // Atari
    ("atari2600", "Atari2600"),
    ("atari5200", "Atari800"),
    ("atari7800", "Atari7800"),
    ("atari800", "Atari800"),
    ("atarist", "AtariST"),
    ("lynx", "AtariLynx"),
    ("jaguar", "Jaguar"),
    // Bandai
    ("wswan", "WonderSwan"),
    ("wswanc", "WonderSwan"),
    ("rx78", "RX78"),
    ("sv8000", "Super_Vision_8000"),
    // Epoch
    ("scv", "SuperCassetteVision"),
    // Commodore / Amiga
    ("c64", "C64"),
    ("c128", "C128"),
    ("c16", "C16"),
    ("c20", "VIC20"),
    ("pet", "PET2001"),
    ("amiga", "Minimig"),
    ("amiga500", "Minimig"),
    ("amiga1200", "Minimig"),
    // Sinclair
    ("zxspectrum", "ZX-Spectrum"),
    ("zx81", "ZX81"),
    ("zxnext", "ZXNext"),
    ("samcoupe", "SAMCoupe"),
    ("ql", "QL"),
    // Amstrad
    ("amstradcpc", "Amstrad"),
    ("amstradpcw", "Amstrad-PCW"),
    // Microsoft
    ("msx", "MSX"),
    ("msx1", "MSX"),
    ("msx2", "MSX"),
    // Apple
    ("apple1", "Apple-I"),
    ("apple2", "Apple-II"),
    ("macintosh", "MacPlus"),
    // PC
    ("dos", "ao486"),
    ("pcxt", "PCXT"),
    // Philips
    ("cdi", "CDi"),
    // Sharp
    ("x68000", "X68000"),
    // NEC
    ("pc88", "PC8801"),
    // Acorn
    ("archimedes", "Archie"),
    ("acornatom", "AcornAtom"),
    ("electron", "AcornElectron"),
    // Texas Instruments
    ("ti99", "TI-99_4A"),
    // Tandy
    ("coco", "CoCo3"),
    ("coco2", "CoCo2"),
    ("trs80", "TRS-80"),
    ("mc10", "AliceMC10"),
    // BBC
    ("bbc", "BBCMicro"),
    // Oric
    ("oric", "Oric"),
    // Mattel
    ("aquarius", "Aquarius"),
    // Other consoles
    ("colecovision", "ColecoVision"),
    ("colecoadam", "ColecoAdam"),
    ("intellivision", "Intv"),
    ("vectrex", "Vectrex"),
    ("o2em", "Odyssey2"),
    ("channelf", "ChannelF"),
    ("astrocde", "Astrocade"),
    ("advision", "AdventureVision"),
    ("vc4000", "VC4000"),
    ("arcadia", "Arcadia"),
    ("creativision", "CreatiVision"),
    ("pv1000", "Casio_PV-1000"),
    // Other portables
    ("supervision", "SuperVision"),
    ("gamate", "Gamate"),
    ("megaduck", "MegaDuck"),
    // Other computers
    ("jupiterace", "Jupiter"),
    ("laser310", "Laser310"),
    ("sordm5", "SordM5"),
    ("einstein", "TatungEinstein"),
    ("tomytutor", "TomyTutor"),
    ("camplynx", "Lynx48"),
    ("svi328", "Svi328"),
    ("enterprise", "Enterprise"),
    ("bk0011m", "BK0011M"),
    ("arduboy", "Arduboy"),
];

/// Find the best matching .rbf core file for a given system name.
///
/// Scans `cores_dir` for files matching `{Prefix}_*.rbf` and picks the newest
/// (by filename sort, which works because MiSTer cores use date-stamped names
/// like `NES_20240101.rbf`).
pub fn find_core_rbf(system_name: &str, cores_dir: &Path) -> Result<PathBuf> {
    let prefix = core_prefix_for_system(system_name)
        .with_context(|| format!("Unknown system: {system_name}"))?;

    info!("Looking for {prefix}_*.rbf in {}", cores_dir.display());

    let mut candidates: Vec<PathBuf> = fs::read_dir(cores_dir)
        .with_context(|| format!("Cannot read cores directory: {}", cores_dir.display()))?
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|path| {
            path.extension()
                .map_or(false, |ext| ext.eq_ignore_ascii_case("rbf"))
        })
        .filter(|path| {
            path.file_stem()
                .and_then(|s| s.to_str())
                .map_or(false, |name| {
                    name.starts_with(prefix) && name.as_bytes().get(prefix.len()) == Some(&b'_')
                })
        })
        .collect();

    // Sort descending by filename so newest (highest date) comes first
    candidates.sort_by(|a, b| b.file_name().cmp(&a.file_name()));

    candidates
        .into_iter()
        .next()
        .with_context(|| format!("No {prefix}_*.rbf found in {}", cores_dir.display()))
}

/// Get the MiSTer core filename prefix for a REG-Linux system name.
fn core_prefix_for_system(system_name: &str) -> Option<&'static str> {
    SYSTEM_TO_CORE_PREFIX
        .iter()
        .find(|(sys, _)| *sys == system_name)
        .map(|(_, prefix)| *prefix)
}

/// List all recognized cores found in the cores directory.
/// Returns a sorted list of (system_name, rbf_path) pairs.
pub fn list_available_cores(cores_dir: &Path) -> Result<Vec<(String, PathBuf)>> {
    let mut results = Vec::new();

    if !cores_dir.exists() {
        return Ok(results);
    }

    for &(system_name, _) in SYSTEM_TO_CORE_PREFIX {
        if let Ok(rbf_path) = find_core_rbf(system_name, cores_dir) {
            results.push((system_name.to_string(), rbf_path));
        }
    }

    results.sort_by(|a, b| a.0.cmp(&b.0));
    // Deduplicate: gamegear and mastersystem share SMS prefix
    results.dedup_by(|a, b| a.1 == b.1);
    Ok(results)
}
