// SPDX-License-Identifier: GPL-2.0+
/*
 * Anbernic RG Vita Pro Joypad Driver
 *
 * Supports:
 *   - GPIO digital buttons (D-pad, ABXY, shoulders, start/select, thumbstick clicks)
 *   - SPI MCU analog sticks via Spreadtrum MCU ("mcu,spi_joystick")
 *   - RGB LED control (16 LEDs, 8 per stick ring) via SPI MCU
 *
 * Hardware overview:
 *   - Platform device: "anbernic,rg-vita-pro-gamepad"
 *   - 19 GPIO buttons on gpio3 (active-low), parsed from DT child nodes
 *   - D-pad uses linux,input-type=EV_ABS with ABS_HAT0X/Y in DT,
 *     remapped to BTN_DPAD_* here for better SDL/ES compatibility
 *   - SPI MCU on spi@2ad00000 (Rockchip rk3066-spi), 1.4MHz
 *   - MCU powered by adc-power-ctl0 GPIO (gpio0 PB3, pin 27)
 *   - MCU needs ~500ms after power-on before responding
 *   - 16 RGB LEDs (8 per analog stick ring) controlled via SPI TX buffer
 *
 * SPI MCU protocol (reverse-engineered from stock singleadcjoy.ko):
 *
 *   TX buffer (64 bytes):
 *     [0-6]   Header: 5A 3A 66 66 00 0D 0A
 *     [7]     LED mode (0=off,1=static,2=per-LED,3=breathing,4=rainbow,5=reactive,6=palette)
 *     [8]     LED switch (0=off, 1=on)
 *     [9]     LED brightness (0-255, default 100)
 *     [10]    LED speed (default 2)
 *     [11-58] 16 LEDs x 3 bytes RGB
 *     [59]    Sequence tag1 (previous tag0)
 *     [60]    Sequence tag0 (incrementing)
 *     [61]    CRC16 high byte (over bytes 7-60)
 *     [62]    CRC16 low byte
 *     [63]    0x00
 *
 *   RX buffer (64 bytes):
 *     [0x20]  magic 0x5A
 *     [0x21]  magic 0x3A
 *     [0x22-0x2D] 6x uint16 LE axis values
 *     [0x2E-0x2F] checksum (sum of axis bytes)
 *
 * Copyright (c) 2026 REG-Linux
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/input.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/gpio/consumer.h>
#include <linux/gpio/consumer.h>
#include <linux/property.h>
#include <linux/spi/spi.h>
#include <linux/delay.h>

#define DRV_NAME "rgvitapro-joypad"
#define MAX_BUTTONS 32

/* SPI MCU protocol constants */
#define SPI_BUF_SIZE		0x40	/* 64 bytes */
#define SPI_MAGIC_0		0x5A
#define SPI_MAGIC_1		0x3A
#define SPI_DATA_OFFSET		0x20	/* magic bytes at this offset */
#define SPI_AXIS_OFFSET		0x22	/* 6x uint16 LE axes start here */
#define SPI_CHECKSUM_OFFSET	0x2E	/* uint16 LE checksum */
#define SPI_AXIS_COUNT		6

/* LED constants */
#define LED_COUNT		16
#define LED_PALETTE_SIZE	30
#define LED_DEFAULT_MODE	4	/* rainbow */
#define LED_DEFAULT_SWITCH	1	/* on */
#define LED_DEFAULT_LEVEL	100	/* brightness */
#define LED_DEFAULT_SPEED	2

/*
 * Rainbow/palette color table — 30 RGB triplets from stock BSP singleadcjoy.
 * Extracted via radare2 from vmlinux symbol "emu_color" at 0xa343c44.
 * Each entry is {R, G, B}. The driver cycles through these for animation.
 */
static const u8 emu_color[LED_PALETTE_SIZE][3] = {
	{0x00, 0x00, 0x00}, {0x57, 0x8e, 0x7b}, {0x13, 0x7c, 0x9d}, {0xa7, 0x66, 0x12},
	{0x11, 0x61, 0x44}, {0x52, 0x22, 0x31}, {0x3d, 0x42, 0x46}, {0xa4, 0x8d, 0x83},
	{0x6c, 0x7c, 0x9d}, {0x52, 0x93, 0xc3}, {0x83, 0x3b, 0x38}, {0x3b, 0x5a, 0xb7},
	{0x10, 0x61, 0x43}, {0x86, 0x53, 0x2e}, {0x80, 0x31, 0x58}, {0x39, 0x2e, 0x28},
	{0xaf, 0x8c, 0x00}, {0x2b, 0x12, 0x4e}, {0x39, 0x2e, 0x98}, {0xa7, 0x66, 0x12},
	{0x97, 0x2e, 0x98}, {0x82, 0x2e, 0x08}, {0x06, 0x47, 0x87}, {0x65, 0x58, 0x74},
	{0x08, 0xa5, 0xa0}, {0xa8, 0x39, 0x00}, {0xac, 0x52, 0x2d}, {0x80, 0x30, 0x58},
	{0x4d, 0x85, 0x62}, {0x10, 0x9b, 0x3a},
};

/* Analog axis defaults (signed, centered at 0 like stock driver) */
#define AXIS_DEFAULT_FUZZ	32
#define AXIS_DEFAULT_FLAT	32
#define AXIS_DEFAULT_DEADZONE	1500	/* from DT button-adc-deadzone (stock=1500) */
#define AXIS_TUNING_STICK	100	/* from DT abs_x-p-tuning (stock=100) */
#define AXIS_TUNING_TRIGGER	150	/* from DT abs_z-p-tuning: multiply by 150/100 */

/* CRC-16/CCITT lookup table (polynomial 0x1021, init 0x0000) */
static const u16 crc16_tab[256] = {
	0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
	0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
	0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
	0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
	0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
	0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
	0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
	0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
	0x4864, 0x5845, 0x6826, 0x7807, 0x08e0, 0x18c1, 0x28a2, 0x38a3,
	0xc94c, 0xd96d, 0xe90e, 0xf92f, 0x89c8, 0x99e9, 0xa98a, 0xb9ab,
	0x5a75, 0x4a54, 0x7a37, 0x6a16, 0x1af1, 0x0ad0, 0x3ab3, 0x2a92,
	0xdb7d, 0xcb5c, 0xfb3f, 0xeb1e, 0x9bf9, 0x8bd8, 0xbbbb, 0xab9a,
	0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
	0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
	0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
	0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
	0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
	0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
	0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
	0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
	0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
	0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
	0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
	0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
	0xd9ec, 0xc9cd, 0xf9ae, 0xe98f, 0x9968, 0x8949, 0xb92a, 0xa90b,
	0x58e4, 0x48c5, 0x78a6, 0x6887, 0x1860, 0x0841, 0x3822, 0x2803,
	0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
	0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
	0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
	0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
	0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
	0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
};

static u16 rgvp_crc16(const u8 *data, int len)
{
	u16 crc = 0x0000;
	int i;

	for (i = 0; i < len; i++) {
		u8 idx = (data[i] ^ (crc >> 8)) & 0xFF;
		crc = ((crc & 0xFF) << 8) ^ crc16_tab[idx];
	}
	return crc;
}

struct rgvp_button {
	struct gpio_desc *gpiod;
	int linux_code;
	int input_type;
	int abs_value;
	bool active_level;
	bool old_value;
	const char *label;
};

struct rgvp_joypad {
	struct device *dev;
	struct input_dev *input;

	/* GPIO buttons */
	struct rgvp_button buttons[MAX_BUTTONS];
	int button_count;
	int poll_interval;

	/* SPI MCU for analog sticks + LEDs */
	struct spi_device *spi;
	u8 spi_tx[SPI_BUF_SIZE];
	u8 spi_rx[SPI_BUF_SIZE];
	bool spi_ok;
	bool calibrated;
	s32 axes[SPI_AXIS_COUNT];
	s32 cal[SPI_AXIS_COUNT];	/* center calibration per axis */

	/* Analog tuning (from DT or defaults) */
	int adc_fuzz;
	int adc_flat;
	int adc_deadzone;

	/* RGB LED state */
	u8 led_mode;
	u8 led_switch;
	u8 led_level;
	u8 led_speed;
	u8 led_r, led_g, led_b;
	u8 tag0, tag1;
	u8 led_palette_idx;	/* current position in emu_color[] for animation */
	u8 led_anim_tick;	/* counter for speed-based animation timing */

	/* Rumble motor (GPIO on/off) */
	struct gpio_desc *rumble_gpio;
	bool rumble_enabled;
};

/* Global pointer so the SPI driver can find the platform driver instance */
static struct rgvp_joypad *g_joypad;

/*
 * Prepare SPI TX buffer with LED state and CRC
 */
static void rgvp_spi_prepare_tx(struct rgvp_joypad *joypad)
{
	u8 *tx = joypad->spi_tx;
	u16 crc;
	u8 old_tag0 = joypad->tag0;
	int i;

	/* Header */
	tx[0] = 0x5A;
	tx[1] = 0x3A;
	tx[2] = 0x66;
	tx[3] = 0x66;
	tx[4] = 0x00;
	tx[5] = 0x0D;
	tx[6] = 0x0A;

	/* LED control */
	tx[7] = joypad->led_mode;
	tx[8] = joypad->led_switch;
	tx[9] = joypad->led_level;
	tx[10] = joypad->led_speed;

	/* LED color data — fill TX[11..58] based on mode */
	if (joypad->led_switch) {
		const u8 *c;
		u8 lvl = joypad->led_level;

		switch (joypad->led_mode) {
		case 1: /* Static: all LEDs same custom color */
			for (i = 0; i < LED_COUNT; i++) {
				tx[11 + i * 3] = joypad->led_r;
				tx[12 + i * 3] = joypad->led_g;
				tx[13 + i * 3] = joypad->led_b;
			}
			break;
		case 4: /* Rainbow: cycle through emu_color palette */
		case 6: /* Palette: same animation, different speed */
			/* Advance animation based on speed */
			joypad->led_anim_tick++;
			if (joypad->led_anim_tick >= joypad->led_speed) {
				joypad->led_anim_tick = 0;
				joypad->led_palette_idx++;
				if (joypad->led_palette_idx >= LED_PALETTE_SIZE)
					joypad->led_palette_idx = 0;
			}
			c = emu_color[joypad->led_palette_idx];
			/* Fill all 16 LEDs with palette color scaled by brightness */
			for (i = 0; i < LED_COUNT; i++) {
				tx[11 + i * 3] = (u8)((u16)c[0] * lvl / 255);
				tx[12 + i * 3] = (u8)((u16)c[1] * lvl / 255);
				tx[13 + i * 3] = (u8)((u16)c[2] * lvl / 255);
			}
			break;
		case 3: /* Breathing: pulse brightness on static color */
			/* Simple triangle wave on brightness */
			joypad->led_anim_tick++;
			{
				u8 breath = joypad->led_anim_tick;
				if (breath > 127)
					breath = 255 - breath;
				breath = (u8)((u16)breath * lvl / 127);
				for (i = 0; i < LED_COUNT; i++) {
					tx[11 + i * 3] = (u8)((u16)joypad->led_r * breath / 255);
					tx[12 + i * 3] = (u8)((u16)joypad->led_g * breath / 255);
					tx[13 + i * 3] = (u8)((u16)joypad->led_b * breath / 255);
				}
			}
			break;
		default: /* Mode 0 (off) or unknown: zero color data */
			memset(&tx[11], 0, LED_COUNT * 3);
			break;
		}
	} else {
		memset(&tx[11], 0, LED_COUNT * 3);
	}

	/* Sequence tags */
	joypad->tag0++;
	joypad->tag1 = old_tag0;
	tx[59] = joypad->tag1;
	tx[60] = joypad->tag0;

	/* CRC-16/CCITT over bytes 7-60 (54 bytes) */
	crc = rgvp_crc16(&tx[7], 54);
	tx[61] = (crc >> 8) & 0xFF;
	tx[62] = crc & 0xFF;

	tx[63] = 0x00;
}

/*
 * Read analog stick data from SPI MCU
 * Returns 0 on success with axes[] populated, -1 on failure
 */
static int rgvp_spi_read(struct rgvp_joypad *joypad)
{
	struct spi_transfer xfer = {
		.tx_buf = joypad->spi_tx,
		.rx_buf = joypad->spi_rx,
		.len = SPI_BUF_SIZE,
	};
	struct spi_message msg;
	u8 *rx;
	u16 sum;
	int i, ret;

	if (!joypad->spi)
		return -1;

	/* Prepare TX with LED state + CRC before each transfer */
	rgvp_spi_prepare_tx(joypad);

	spi_message_init(&msg);
	spi_message_add_tail(&xfer, &msg);

	ret = spi_sync(joypad->spi, &msg);
	if (ret)
		return -1;

	rx = joypad->spi_rx;

	/* Validate magic bytes */
	if (rx[SPI_DATA_OFFSET] != SPI_MAGIC_0 ||
	    rx[SPI_DATA_OFFSET + 1] != SPI_MAGIC_1)
		return -1;

	/* Validate checksum: sum of bytes 0x22..0x2D */
	sum = 0;
	for (i = SPI_AXIS_OFFSET; i < SPI_CHECKSUM_OFFSET; i++)
		sum += rx[i];

	if (rx[SPI_CHECKSUM_OFFSET] != (sum & 0xFF) ||
	    rx[SPI_CHECKSUM_OFFSET + 1] != ((sum >> 8) & 0xFF))
		return -1;

	/* Extract 6 axis values: uint16 LE, then scale 13-bit to 16-bit */
	for (i = 0; i < SPI_AXIS_COUNT; i++) {
		u16 raw = rx[SPI_AXIS_OFFSET + i * 2] |
			  (rx[SPI_AXIS_OFFSET + i * 2 + 1] << 8);
		s32 scaled = (s32)((raw & 0x1FFF) << 3);

		/* Auto-calibrate center on first valid read */
		if (!joypad->calibrated)
			joypad->cal[i] = scaled;

		/* Zero-center: subtract calibration value */
		scaled -= joypad->cal[i];

		/* Apply deadzone */
		if (abs(scaled) <= joypad->adc_deadzone) {
			scaled = 0;
		} else {
			int tuning = (i < 4) ? AXIS_TUNING_STICK : AXIS_TUNING_TRIGGER;
			scaled = scaled * tuning / 100;
		}

		/* Clamp to [-cal, +cal] (symmetric range around 0) */
		if (scaled > joypad->cal[i])
			scaled = joypad->cal[i];
		else if (scaled < -joypad->cal[i])
			scaled = -joypad->cal[i];

		joypad->axes[i] = scaled;
	}

	if (!joypad->calibrated)
		joypad->calibrated = true;

	return 0;
}

static void rgvp_poll(struct input_dev *input)
{
	struct rgvp_joypad *joypad = input_get_drvdata(input);
	int i;

	/* GPIO buttons */
	for (i = 0; i < joypad->button_count; i++) {
		struct rgvp_button *btn = &joypad->buttons[i];
		int raw, pressed;

		raw = gpiod_get_raw_value_cansleep(btn->gpiod);
		if (raw < 0)
			continue;

		pressed = (raw == btn->active_level) ? 1 : 0;
		if (pressed == btn->old_value)
			continue;

		btn->old_value = pressed;
		input_event(input, EV_KEY, btn->linux_code, pressed);
	}

	/* SPI analog sticks (also sends LED commands via TX) */
	if (joypad->spi_ok && rgvp_spi_read(joypad) == 0) {
		input_report_abs(input, ABS_RY, joypad->axes[0]);
		input_report_abs(input, ABS_RX, joypad->axes[1]);
		input_report_abs(input, ABS_Y,  joypad->axes[2]);
		input_report_abs(input, ABS_X,  joypad->axes[3]);
		input_report_abs(input, ABS_Z,  joypad->axes[4]);
		input_report_abs(input, ABS_RZ, joypad->axes[5]);
	}

	input_sync(input);
}

/* --- sysfs attributes for LED control --- */

#define LED_ATTR_RW(_name, _field) \
static ssize_t _name##_show(struct device *dev, \
		struct device_attribute *attr, char *buf) \
{ \
	struct rgvp_joypad *j = platform_get_drvdata(to_platform_device(dev)); \
	return sysfs_emit(buf, "%u\n", j->_field); \
} \
static ssize_t _name##_store(struct device *dev, \
		struct device_attribute *attr, const char *buf, size_t count) \
{ \
	struct rgvp_joypad *j = platform_get_drvdata(to_platform_device(dev)); \
	u8 val; \
	if (kstrtou8(buf, 0, &val)) return -EINVAL; \
	j->_field = val; \
	return count; \
} \
static DEVICE_ATTR_RW(_name)

LED_ATTR_RW(led_mode, led_mode);
LED_ATTR_RW(led_switch, led_switch);
LED_ATTR_RW(led_level, led_level);
LED_ATTR_RW(led_speed, led_speed);
LED_ATTR_RW(led_r, led_r);
LED_ATTR_RW(led_g, led_g);
LED_ATTR_RW(led_b, led_b);

static struct attribute *rgvp_led_attrs[] = {
	&dev_attr_led_mode.attr,
	&dev_attr_led_switch.attr,
	&dev_attr_led_level.attr,
	&dev_attr_led_speed.attr,
	&dev_attr_led_r.attr,
	&dev_attr_led_g.attr,
	&dev_attr_led_b.attr,
	NULL,
};

static const struct attribute_group rgvp_led_group = {
	.attrs = rgvp_led_attrs,
};

/* --- Rumble motor via PWM --- */

static int rgvp_rumble_play(struct input_dev *dev, void *data,
			    struct ff_effect *effect)
{
	struct rgvp_joypad *joypad = data;
	u16 magnitude;

	if (!joypad->rumble_gpio || !joypad->rumble_enabled)
		return 0;

	/* Use the stronger of strong/weak (single motor, on/off) */
	magnitude = max(effect->u.rumble.strong_magnitude,
			effect->u.rumble.weak_magnitude);

	gpiod_set_value_cansleep(joypad->rumble_gpio, magnitude ? 1 : 0);
	return 0;
}

static ssize_t rumble_enable_show(struct device *dev,
				  struct device_attribute *attr, char *buf)
{
	struct rgvp_joypad *j = platform_get_drvdata(to_platform_device(dev));
	return sysfs_emit(buf, "%u\n", j->rumble_enabled ? 1 : 0);
}

static ssize_t rumble_enable_store(struct device *dev,
				   struct device_attribute *attr,
				   const char *buf, size_t count)
{
	struct rgvp_joypad *j = platform_get_drvdata(to_platform_device(dev));
	bool val;

	if (kstrtobool(buf, &val))
		return -EINVAL;

	j->rumble_enabled = val;
	if (!val && j->rumble_gpio)
		gpiod_set_value_cansleep(j->rumble_gpio, 0);
	return count;
}
static DEVICE_ATTR_RW(rumble_enable);

/* --- Button parsing --- */

static int rgvp_parse_buttons(struct rgvp_joypad *joypad)
{
	struct device *dev = joypad->dev;
	struct device_node *np = dev->of_node;
	struct device_node *child;
	int count = 0;

	for_each_child_of_node(np, child) {
		struct rgvp_button *btn;
		struct gpio_desc *gpiod;
		u32 code = 0, type = EV_KEY, abs_val = 0;

		if (count >= MAX_BUTTONS)
			break;

		gpiod = devm_fwnode_gpiod_get(dev, of_fwnode_handle(child),
					      NULL, GPIOD_IN, child->name);
		if (IS_ERR(gpiod))
			continue;

		of_property_read_u32(child, "linux,code", &code);
		of_property_read_u32(child, "linux,input-type", &type);
		of_property_read_u32(child, "linux,abs-value", &abs_val);

		if (code == 0)
			continue;

		/* Remap D-pad from ABS_HAT0X/Y to BTN_DPAD_* */
		if (type == EV_ABS) {
			if (code == ABS_HAT0X && abs_val == 2)
				code = BTN_DPAD_LEFT;
			else if (code == ABS_HAT0X && abs_val == 1)
				code = BTN_DPAD_RIGHT;
			else if (code == ABS_HAT0Y && abs_val == 2)
				code = BTN_DPAD_UP;
			else if (code == ABS_HAT0Y && abs_val == 1)
				code = BTN_DPAD_DOWN;
			type = EV_KEY;
		}

		/* Fix A/B swap: stock DTB GPIOs are wired opposite */
		if (code == BTN_SOUTH)
			code = BTN_EAST;
		else if (code == BTN_EAST)
			code = BTN_SOUTH;

		/* Remap KEY_F10 to BTN_MODE (guide/hotkey) for SDL visibility */
		if (code == KEY_F10)
			code = BTN_MODE;

		btn = &joypad->buttons[count];
		btn->gpiod = gpiod;
		btn->linux_code = code;
		btn->input_type = type;
		btn->abs_value = abs_val;
		btn->active_level = gpiod_is_active_low(gpiod) ? 0 : 1;
		btn->old_value = 0;
		btn->label = child->name;

		count++;
	}

	joypad->button_count = count;
	dev_info(dev, "parsed %d GPIO buttons\n", count);
	return count > 0 ? 0 : -ENODEV;
}

static int rgvp_setup_input(struct rgvp_joypad *joypad)
{
	struct input_dev *input;
	int i, error;
	const char *name = DRV_NAME;

	device_property_read_string(joypad->dev, "joypad-name", &name);

	input = devm_input_allocate_device(joypad->dev);
	if (!input)
		return -ENOMEM;

	input->name = name;
	input->phys = DRV_NAME "/input0";
	input->id.bustype = BUS_HOST;
	input->id.vendor = 0x484b;
	input->id.product = 0x1101;
	input->id.version = 0x0100;

	device_property_read_u32(joypad->dev, "joypad-product",
				 (u32 *)&input->id.product);
	device_property_read_u32(joypad->dev, "joypad-revision",
				 (u32 *)&input->id.version);

	/* GPIO buttons */
	for (i = 0; i < joypad->button_count; i++)
		input_set_capability(input, EV_KEY, joypad->buttons[i].linux_code);

	/* Analog stick axes */
	input_set_abs_params(input, ABS_X,  -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);
	input_set_abs_params(input, ABS_Y,  -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);
	input_set_abs_params(input, ABS_RX, -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);
	input_set_abs_params(input, ABS_RY, -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);
	input_set_abs_params(input, ABS_Z,  -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);
	input_set_abs_params(input, ABS_RZ, -16384, 16384,
			     joypad->adc_fuzz, joypad->adc_flat);

	/* Rumble (force feedback) via GPIO — optional */
	if (joypad->rumble_gpio) {
		input_set_capability(input, EV_FF, FF_RUMBLE);
		error = input_ff_create_memless(input, joypad, rgvp_rumble_play);
		if (error)
			dev_warn(joypad->dev, "FF rumble init failed: %d\n", error);
	}

	input_set_drvdata(input, joypad);

	error = input_setup_polling(input, rgvp_poll);
	if (error) {
		dev_err(joypad->dev, "input_setup_polling failed: %d\n", error);
		return error;
	}

	input_set_poll_interval(input, joypad->poll_interval);

	error = input_register_device(input);
	if (error) {
		dev_err(joypad->dev, "input_register_device failed: %d\n", error);
		return error;
	}

	joypad->input = input;
	return 0;
}

static int rgvp_probe(struct platform_device *pdev)
{
	struct rgvp_joypad *joypad;
	struct device *dev = &pdev->dev;
	int error;

	joypad = devm_kzalloc(dev, sizeof(*joypad), GFP_KERNEL);
	if (!joypad)
		return -ENOMEM;

	joypad->dev = dev;
	joypad->poll_interval = 10;
	joypad->adc_fuzz = AXIS_DEFAULT_FUZZ;
	joypad->adc_flat = AXIS_DEFAULT_FLAT;
	joypad->adc_deadzone = AXIS_DEFAULT_DEADZONE;

	/* LED defaults: rainbow mode, on, brightness 100, speed 2 */
	joypad->led_mode = LED_DEFAULT_MODE;
	joypad->led_switch = LED_DEFAULT_SWITCH;
	joypad->led_level = LED_DEFAULT_LEVEL;
	joypad->led_speed = LED_DEFAULT_SPEED;

	device_property_read_u32(dev, "poll-interval", &joypad->poll_interval);
	device_property_read_u32(dev, "button-adc-fuzz", &joypad->adc_fuzz);
	device_property_read_u32(dev, "button-adc-flat", &joypad->adc_flat);
	device_property_read_u32(dev, "button-adc-deadzone", &joypad->adc_deadzone);

	platform_set_drvdata(pdev, joypad);
	g_joypad = joypad;

	/* Power up the SPI MCU via adc-power-ctl0 GPIO */
	{
		struct gpio_desc *pwr_gpiod;

		pwr_gpiod = devm_gpiod_get_optional(dev, "adc-power-ctl0",
						    GPIOD_OUT_HIGH);
		if (!IS_ERR_OR_NULL(pwr_gpiod)) {
			dev_info(dev, "MCU power GPIO high, waiting 500ms\n");
			msleep(500);
		}
	}

	/* Rumble motor GPIO — optional, don't fail if absent */
	joypad->rumble_gpio = devm_gpiod_get_optional(dev, "rumble",
						      GPIOD_OUT_LOW);
	if (IS_ERR(joypad->rumble_gpio)) {
		dev_warn(dev, "rumble GPIO not available: %ld\n",
			 PTR_ERR(joypad->rumble_gpio));
		joypad->rumble_gpio = NULL;
	} else if (joypad->rumble_gpio) {
		joypad->rumble_enabled = true;
		dev_info(dev, "rumble motor GPIO acquired\n");
	}

	error = rgvp_parse_buttons(joypad);
	if (error) {
		dev_err(dev, "no buttons found: %d\n", error);
		return error;
	}

	error = rgvp_setup_input(joypad);
	if (error) {
		dev_err(dev, "input setup failed: %d\n", error);
		return error;
	}

	/* Create LED sysfs attributes */
	error = sysfs_create_group(&dev->kobj, &rgvp_led_group);
	if (error)
		dev_warn(dev, "failed to create LED sysfs: %d\n", error);

	/* Create rumble sysfs attribute */
	if (joypad->rumble_gpio) {
		error = device_create_file(dev, &dev_attr_rumble_enable);
		if (error)
			dev_warn(dev, "failed to create rumble sysfs: %d\n", error);
	}

	dev_info(dev, "RG Vita Pro joypad: %d buttons, poll %dms, LEDs mode=%d, SPI %s\n",
		 joypad->button_count, joypad->poll_interval,
		 joypad->led_mode,
		 joypad->spi_ok ? "OK" : "pending");

	return 0;
}

static void rgvp_remove(struct platform_device *pdev)
{
	struct rgvp_joypad *joypad = platform_get_drvdata(pdev);

	if (joypad->rumble_gpio) {
		gpiod_set_value_cansleep(joypad->rumble_gpio, 0);
		device_remove_file(&pdev->dev, &dev_attr_rumble_enable);
	}

	sysfs_remove_group(&pdev->dev.kobj, &rgvp_led_group);
}

/* --- Platform driver (GPIO buttons, main device) --- */

static const struct of_device_id rgvp_of_match[] = {
	{ .compatible = "anbernic,rg-vita-pro-gamepad", },
	{ },
};
MODULE_DEVICE_TABLE(of, rgvp_of_match);

static struct platform_driver rgvp_driver = {
	.probe = rgvp_probe,
	.remove = rgvp_remove,
	.driver = {
		.name = DRV_NAME,
		.of_match_table = rgvp_of_match,
	},
};

/* --- SPI driver (analog sticks MCU) --- */

static int rgvp_spi_probe(struct spi_device *spi)
{
	int ret;

	spi->bits_per_word = 8;
	spi->mode = SPI_MODE_0;
	ret = spi_setup(spi);
	if (ret) {
		dev_err(&spi->dev, "spi_setup failed: %d\n", ret);
		return ret;
	}

	if (g_joypad) {
		g_joypad->spi = spi;
		/* TX buffer will be prepared fresh each frame by rgvp_spi_prepare_tx */
		memset(g_joypad->spi_tx, 0, SPI_BUF_SIZE);
		g_joypad->spi_ok = true;
		dev_info(&spi->dev, "SPI MCU connected to joypad (LEDs enabled)\n");
	} else {
		dev_warn(&spi->dev, "SPI MCU probed before joypad\n");
	}

	return 0;
}

static const struct of_device_id rgvp_spi_of_match[] = {
	{ .compatible = "mcu,spi_joystick", },
	{ },
};
MODULE_DEVICE_TABLE(of, rgvp_spi_of_match);

static const struct spi_device_id rgvp_spi_id[] = {
	{ "mcu_spi_joystick", 0 },
	{ },
};
MODULE_DEVICE_TABLE(spi, rgvp_spi_id);

static struct spi_driver rgvp_spi_driver = {
	.probe = rgvp_spi_probe,
	.driver = {
		.name = "rgvitapro-spi-mcu",
		.of_match_table = rgvp_spi_of_match,
	},
	.id_table = rgvp_spi_id,
};

/* --- Module init/exit --- */

static int __init rgvp_init(void)
{
	int ret;

	ret = platform_driver_register(&rgvp_driver);
	if (ret)
		return ret;

	ret = spi_register_driver(&rgvp_spi_driver);
	if (ret) {
		platform_driver_unregister(&rgvp_driver);
		return ret;
	}

	return 0;
}

static void __exit rgvp_exit(void)
{
	spi_unregister_driver(&rgvp_spi_driver);
	platform_driver_unregister(&rgvp_driver);
}

module_init(rgvp_init);
module_exit(rgvp_exit);

MODULE_AUTHOR("REG-Linux");
MODULE_DESCRIPTION("Anbernic RG Vita Pro Joypad — GPIO buttons + SPI MCU sticks + RGB LEDs + PWM rumble");
MODULE_LICENSE("GPL v2");
