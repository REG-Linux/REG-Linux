from pathlib import Path
from typing import Any

from configgen.settings import UnixSettings

from .libretroConfig import retroarchCustom

# ==========================
# Default RetroArch settings
# ==========================
CONFIG_DEFAULTS = {
    # User Interface
    "menu_driver": "ozone",
    "content_show_favorites": "false",
    "content_show_images": "false",
    "content_show_music": "false",
    "content_show_video": "false",
    "content_show_history": "false",
    "content_show_playlists": "false",
    "content_show_add": "false",
    "menu_show_load_core": "false",
    "menu_show_load_content": "false",
    "menu_show_online_updater": "false",
    "menu_show_core_updater": "false",
    # Input (SDL2 based)
    "input_autodetect_enable": "true",
    "input_remap_binds_enable": "true",
    "input_joypad_driver": "sdl2",
    "input_enable_hotkey_btn": "5",
    "input_reset_btn": "0",
    "input_menu_toggle_btn": "3",
    "input_exit_emulator_btn": "6",
    "input_load_state_btn": "10",
    "input_save_state_btn": "9",
    "input_state_slot_increase_btn": "13",
    "input_state_slot_decrease_btn": "14",
    "input_player1_analog_dpad_mode": "1",
    "input_player2_analog_dpad_mode": "1",
    "input_player3_analog_dpad_mode": "1",
    "input_player4_analog_dpad_mode": "1",
    "input_player5_analog_dpad_mode": "1",
    "input_player6_analog_dpad_mode": "1",
    "input_player7_analog_dpad_mode": "1",
    "input_player8_analog_dpad_mode": "1",
    "input_enable_hotkey": "shift",
    "input_menu_toggle": "f1",
    "input_exit_emulator": "escape",
    # Video
    "video_aspect_ratio_auto": "false",
    "video_gpu_screenshot": "true",
    "video_shader_enable": "false",
    "aspect_ratio_index": "22",
    # Audio
    "audio_volume": "2.0",
    # General settings
    "global_core_options": "true",
    "config_save_on_exit": "false",
    "savestate_auto_save": "false",
    "savestate_auto_load": "false",
    "menu_swap_ok_cancel_buttons": "true",
    # Accentuation and UX
    "rgui_extended_ascii": "true",
    "rgui_show_start_screen": "false",
    "video_font_enable": "true",
    "savestate_thumbnail_enable": "true",
    "all_users_control_menu": "false",
    "cheevos_badges_enable": "true",
    "builtin_imageviewer_enable": "false",
    "fps_update_interval": "30",
}

# ==========================
# RetroArch paths
# ==========================
CONFIG_PATHS = {
    "core_options_path": '"/userdata/system/configs/retroarch/cores/retroarch-core-options.cfg"',
    "assets_directory": '"/usr/share/libretro/assets"',
    "screenshot_directory": '"/userdata/screenshots/"',
    "recording_output_directory": '"/userdata/screenshots/"',
    "savestate_directory": '"/userdata/saves/"',
    "savefile_directory": '"/userdata/saves/"',
    "extraction_directory": '"/userdata/extractions/"',
    "cheat_database_path": '"/userdata/cheats/cht/"',
    "cheat_settings_path": '"/userdata/cheats/saves/"',
    "system_directory": '"/userdata/bios/"',
    "joypad_autoconfig_dir": '"/userdata/system/configs/retroarch/autoconfig/"',
    "video_shader_dir": '"/usr/share/reglinux/shaders/"',
    "video_filter_dir": '"/usr/share/video_filters"',
    "audio_filter_dir": '"/usr/share/audio_filters"',
}


def generateRetroarchCustom():
    """
    Generate the RetroArch custom configuration file.
    If the file is corrupted (UnicodeError), it will be recreated.
    """
    # Ensure the target directory exists
    custom_dir = Path(retroarchCustom).parent
    if not custom_dir.exists():
        custom_dir.mkdir(parents=True, exist_ok=True)

    # Load or recreate the settings handler
    try:
        retroarchSettings = UnixSettings(retroarchCustom, separator=" ")
    except UnicodeError:
        Path(retroarchCustom).unlink()
        retroarchSettings = UnixSettings(retroarchCustom, separator=" ")

    # Apply all default settings
    for key, value in CONFIG_DEFAULTS.items():
        retroarchSettings.save(key, f'"{value}"')

    # Write to file
    retroarchSettings.write()


def generateRetroarchCustomPathes(retroarchSettings: Any) -> None:
    """
    Save RetroArch custom paths into the configuration.
    This is called separately because paths may vary depending on the system.
    """
    for key, value in CONFIG_PATHS.items():
        retroarchSettings.save(key, value)
