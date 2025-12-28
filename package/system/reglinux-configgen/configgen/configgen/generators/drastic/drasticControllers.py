from typing import Any


def setDrasticController(drasticConfig: Any) -> None:
    keyboardpart = "".join(
        (
            "controls_a[CONTROL_INDEX_UP]                           = 338          # Arrow Up        \n",
            "controls_a[CONTROL_INDEX_DOWN]                         = 337          # Arrow Down      \n",
            "controls_a[CONTROL_INDEX_LEFT]                         = 336          # Arrow Left      \n",
            "controls_a[CONTROL_INDEX_RIGHT]                        = 335          # Arrow Right     \n",
            "controls_a[CONTROL_INDEX_A]                            = 101          # E               \n",
            "controls_a[CONTROL_INDEX_B]                            = 114          # R               \n",
            "controls_a[CONTROL_INDEX_X]                            = 100          # D               \n",
            "controls_a[CONTROL_INDEX_Y]                            = 102          # F               \n",
            "controls_a[CONTROL_INDEX_L]                            = 99           # C               \n",
            "controls_a[CONTROL_INDEX_R]                            = 118          # V               \n",
            "controls_a[CONTROL_INDEX_START]                        = 13           # Return          \n",
            "controls_a[CONTROL_INDEX_SELECT]                       = 32           # Space           \n",
            "controls_a[CONTROL_INDEX_HINGE]                        = 104          # H               \n",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_UP]              = 65535        # PAD2KEY MOUSE   \n",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_DOWN]            = 65535        # PAD2KEY MOUSE   \n",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_LEFT]            = 65535        # PAD2KEY MOUSE   \n",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]           = 65535        # PAD2KEY MOUSE   \n",
            "controls_a[CONTROL_INDEX_TOUCH_CURSOR_PRESS]           = 360          # Left Click      \n",
            "controls_a[CONTROL_INDEX_MENU]                         = 314          # F1              \n",
            "controls_a[CONTROL_INDEX_SAVE_STATE]                   = 318          # F5              \n",
            "controls_a[CONTROL_INDEX_LOAD_STATE]                   = 320          # F7              \n",
            "controls_a[CONTROL_INDEX_FAST_FORWARD]                 = 9            # Tab             \n",
            "controls_a[CONTROL_INDEX_SWAP_SCREENS]                 = 315          # F2              \n",
            "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_A]           = 316          # F3              \n",
            "controls_a[CONTROL_INDEX_SWAP_ORIENTATION_B]           = 317          # F4              \n",
            "controls_a[CONTROL_INDEX_LOAD_GAME]                    = 65535        # DISABLED        \n",
            "controls_a[CONTROL_INDEX_QUIT]                         = 325          # F12             \n",
            "controls_a[CONTROL_INDEX_FAKE_MICROPHONE]              = 121          # Y               \n",
            # "controls_a[CONTROL_INDEX_UI_UP]                       = 105          # I               \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_DOWN]                     = 107          # K               \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_LEFT]                     = 106          # J               \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_RIGHT]                    = 108          # L               \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_SELECT]                   = 13           # Return          \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_BACK]                     = 8            # BackSpace       \n",  Let Drastic Choose Default
            # "controls_a[CONTROL_INDEX_UI_EXIT]                     = 27           # Escape          \n",  Let Drastic Choose Default
            "controls_a[CONTROL_INDEX_UI_PAGE_UP]                   = 331          # PageUp          \n",
            "controls_a[CONTROL_INDEX_UI_PAGE_DOWN]                 = 334          # PageDown        \n",
            "controls_a[CONTROL_INDEX_UI_SWITCH]                    = 117          # U                 ",
        )
    )

    padpart = "".join(
        (
            "controls_b[CONTROL_INDEX_UP]                           = 65535   \n",
            "controls_b[CONTROL_INDEX_DOWN]                         = 65535   \n",
            "controls_b[CONTROL_INDEX_LEFT]                         = 65535   \n",
            "controls_b[CONTROL_INDEX_RIGHT]                        = 65535   \n",
            "controls_b[CONTROL_INDEX_A]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_B]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_X]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_Y]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_L]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_R]                            = 65535   \n",
            "controls_b[CONTROL_INDEX_START]                        = 65535   \n",
            "controls_b[CONTROL_INDEX_SELECT]                       = 65535   \n",
            "controls_b[CONTROL_INDEX_HINGE]                        = 65535   \n",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_UP]              = 65535   \n",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_DOWN]            = 65535   \n",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_LEFT]            = 65535   \n",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_RIGHT]           = 65535   \n",
            "controls_b[CONTROL_INDEX_TOUCH_CURSOR_PRESS]           = 65535   \n",
            "controls_b[CONTROL_INDEX_MENU]                         = 65535   \n",
            "controls_b[CONTROL_INDEX_SAVE_STATE]                   = 65535   \n",
            "controls_b[CONTROL_INDEX_LOAD_STATE]                   = 65535   \n",
            "controls_b[CONTROL_INDEX_FAST_FORWARD]                 = 65535   \n",
            "controls_b[CONTROL_INDEX_SWAP_SCREENS]                 = 65535   \n",
            "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_A]           = 65535   \n",
            "controls_b[CONTROL_INDEX_SWAP_ORIENTATION_B]           = 65535   \n",
            "controls_b[CONTROL_INDEX_LOAD_GAME]                    = 65535   \n",
            "controls_b[CONTROL_INDEX_QUIT]                         = 65535   \n",
            "controls_b[CONTROL_INDEX_FAKE_MICROPHONE]              = 65535   \n",
            # "controls_b[CONTROL_INDEX_UI_UP]                       = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_DOWN]                     = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_LEFT]                     = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_RIGHT]                    = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_SELECT]                   = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_BACK]                     = 65535   \n", Let Drastic Generate for Pad
            # "controls_b[CONTROL_INDEX_UI_EXIT]                     = 65535   \n", Let Drastic Generate for Pad
            "controls_b[CONTROL_INDEX_UI_PAGE_UP]                   = 65535   \n",
            "controls_b[CONTROL_INDEX_UI_PAGE_DOWN]                 = 65535   \n",
            "controls_b[CONTROL_INDEX_UI_SWITCH]                    = 65535     ",
        )
    )

    drasticConfig.write(keyboardpart)
    drasticConfig.write("\n")
    drasticConfig.write("\n")
    drasticConfig.write(padpart)
