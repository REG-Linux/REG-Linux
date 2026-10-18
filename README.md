## 🕹️🐧 REG Linux 🕹️🐧
**REG Linux** (Retro Emulation Gaming Linux) is an **immutable operating system** built for **retro-gaming consoles, handhelds, and mini-PCs**.

It is designed to be **lightweight, fast, and reliable**, with a modern toolchain, systemd-free init system, and optimized Buildroot base.  
REG Linux runs on **ARM, AArch64, RISC-V 64-bit, and x86-64** architectures.

[![Activity](https://img.shields.io/github/commit-activity/m/REG-Linux/REG-Linux)](https://github.com/REG-Linux/REG-Linux)
[![PR](https://img.shields.io/github/issues-pr-closed/REG-Linux/REG-Linux)](https://github.com/REG-Linux/REG-Linux/pulls)
[![Stars](https://img.shields.io/github/stars/REG-Linux?style=social)](https://github.com/REG-Linux)
[![Forks](https://img.shields.io/github/forks/REG-Linux?style=social)](https://github.com/REG-Linux)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Freglinux.org&up_color=green&up_message=online)](https://reglinux.org)
[![Discord](https://img.shields.io/discord/357518249883205632?label=Discord)](https://discord.gg/reglinux)
[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/reglinux?style=social)](https://www.reddit.com/r/reglinux/)
[![Twitter](https://img.shields.io/twitter/follow/REG_linux?style=social)](https://twitter.com/REG_linux)
[![YouTube](https://img.shields.io/youtube/channel/views/UClFpqHKoXsOIV-GjyZqoZcw?style=social)](https://www.youtube.com/channel/UClFpqHKoXsOIV-GjyZqoZcw/featured)

---

### 🎮 What is REG Linux?

REG Linux is a **portable retro-gaming OS** that can be written to a USB stick or SD card to instantly turn any compatible board or computer into a console.

- 🔒 Immutable system image  
- ⚙️ Based on Buildroot. systemd-free init system  
- 🚀 Optimized for performance and fast boot  
- 🧩 Modular packaging system (no overlayfs required)  
- 💾 Read-only root filesystem with `/userdata` persistence  
- 🕹️ Out-of-the-box support for dozens of emulators and cores  
- 🧠 Designed for embedded and handheld SoCs (Allwinner, Rockchip, Amlogic, Snapdragon, SpacemiT K1, etc.)

---

### 🌍 Project Resources

- 🌐 **Website:** [https://reglinux.org](https://reglinux.org) — latest releases and supported devices  
- 📚 **Wiki:** [https://wiki.reglinux.org](https://wiki.reglinux.org) — documentation and developer guides  
- 💬 **Discord:** [https://discord.gg/reglinux](https://discord.gg/reglinux) — community, support, and discussion  
- 🧠 **GitHub Organization:** [https://github.com/REG-Linux](https://github.com/REG-Linux)

---

### 🆘 Need Help?

Join our active community:

- 💬 [Discord Server](https://discord.gg/reglinux) → `#help-and-support` channel  
- 📰 [Reddit Community](https://www.reddit.com/r/reglinux/)  

---

### 🤝 Contributing

REG Linux is open to contributions from developers, designers, and testers:

- 🧩 **Development:** submit pull requests — [makeapullrequest.com](https://makeapullrequest.com/)  
- 🌍 **Translations:** help localize menus, docs, and UI components  
- 🎨 **Themes:** create and share themes for EmulationStation-style front-ends  
- 📢 **Spread the word:** talk about REG Linux on YouTube, X (Twitter), or in retro-gaming communities  

Donations and hardware contributions will soon be accepted to support ongoing development.

---

### ⚖️ License

REG Linux is built from open-source software, but it is **not entirely open source**:

| Component | License |
| --------- | ------- |
| This repository (board support, package recipes, configurations, overlays, scripts) | GPL-2.0-or-later, see [COPYING](COPYING). Patches follow the license of the software they patch |
| The software the recipes build (kernel, emulators, libraries…) | Each package's own license, listed by `make legal-info` |
| **REG-Station** (frontend) and **regmsg** (system daemon) | **Proprietary.** Only binaries are published, at [REG-Station-binaries](https://github.com/REG-Linux/REG-Station-binaries) and [regmsg-binaries](https://github.com/REG-Linux/regmsg-binaries) |
| Some firmware and GPU drivers | Vendor binaries under their own licenses |

The open-source parts of REG-Station and regmsg are listed with their notices in `/usr/share/regstation/THIRD_PARTY_LICENSES` and `/usr/share/regmsg/THIRD_PARTY_LICENSES` on every image.

---

### 🗂️ Repository Overview

| Directory | Description |
|------------|-------------|
| **`board/`** | Platform-specific configuration: patches and board support for SBCs and handhelds. |
| **`buildroot/`** | The Buildroot framework used to assemble REG Linux images. |
| **`configs/`** | Build configurations defining what packages and options are enabled per device. |
| **`package/`** | The main system and emulator packages (Makefiles, patches, configuration). |
| **`scripts/`** | Utilities and helper scripts for building, flashing, or managing devices. |

A more detailed explanation of the build process and directory layout is available in the [Wiki → Developer Guide](https://wiki.reglinux.org/dev-guide/).

---

### 🧑‍💻 Build Instructions

```bash
git clone --recurse-submodules https://github.com/REG-Linux/REG-Linux.git
Install docker using your package manager, then :
cd REG-Linux
make reglinux-docker-image
make xxx-build     
Example: building for Allwinner H700 target
make h700-build
Example: building for x86_64_v3
make x86_64_v3-build
