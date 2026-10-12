use mister_fpga::core::MisterFpgaCore;
use mister_fpga::fpga::feature::SpiFeatureSet;
use mister_fpga::fpga::IntoLowLevelSpiCommand;

/// MiSTer UIO_ANALOG command (0x1A).
///
/// Sends analog joystick values to the FPGA core. Each axis is a signed 8-bit
/// value (-128..127). The command sends the player index followed by two 16-bit
/// words: {left_y, left_x} and {right_y, right_x}.
///
/// This command is not implemented in the mister-fpga crate, so we implement it
/// directly using the public SPI traits.
struct UioAnalogCmd;

impl IntoLowLevelSpiCommand for UioAnalogCmd {
    fn into_ll_spi_command(self) -> (SpiFeatureSet, u16) {
        (SpiFeatureSet::IO, 0x1A)
    }
}

/// Per-gamepad analog state.
#[derive(Clone, Copy, Default)]
pub struct AnalogState {
    pub left_x: i8,
    pub left_y: i8,
    pub right_x: i8,
    pub right_y: i8,
}

impl AnalogState {
    /// Returns true if any axis has a non-zero value.
    #[allow(dead_code)]
    pub fn is_active(&self) -> bool {
        self.left_x != 0 || self.left_y != 0 || self.right_x != 0 || self.right_y != 0
    }
}

/// Send analog joystick values to the FPGA core for a given player.
pub fn send_analog(core: &mut MisterFpgaCore, player: u8, state: &AnalogState) {
    let word1 = ((state.left_y as u8 as u16) << 8) | (state.left_x as u8 as u16);
    let word2 = ((state.right_y as u8 as u16) << 8) | (state.right_x as u8 as u16);

    let _ = core
        .spi_mut()
        .command(UioAnalogCmd)
        .write(player as u16)
        .write(word1)
        .write(word2);
}

/// Analog stick deadzone for analog output (10%).
/// Smaller than the digital deadzone (25%) for finer control.
const ANALOG_DEADZONE: f32 = 0.10;

/// Convert an evdev axis value to a signed 8-bit value for MiSTer analog input.
///
/// Applies a 10% deadzone and scales the remaining range to -128..127.
pub fn axis_to_i8(value: i32, minimum: i32, maximum: i32) -> i8 {
    let center = (minimum + maximum) / 2;
    let half_range = ((maximum - minimum) as f32) / 2.0;
    if half_range < 1.0 {
        return 0;
    }

    let normalized = (value - center) as f32 / half_range;

    // Apply deadzone
    if normalized.abs() < ANALOG_DEADZONE {
        return 0;
    }

    // Scale remaining range to full i8 range
    let sign = normalized.signum();
    let scaled = (normalized.abs() - ANALOG_DEADZONE) / (1.0 - ANALOG_DEADZONE);
    (sign * scaled * 127.0).clamp(-128.0, 127.0) as i8
}
