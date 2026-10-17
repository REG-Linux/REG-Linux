# sm6115 kernel patches

Linux 7.2.x on the ROCKNIX stack for this SoC. Patches that come from another
project carry an `Origin:` line naming the file they were taken from; where the
original has an author and sign-offs they are kept in the patch header.

- ROCKNIX: https://github.com/ROCKNIX/distribution (`projects/ROCKNIX/devices/*/patches`,
  `projects/ROCKNIX/packages/audio/alsa-ucm-conf/patches`), compared against
  `075a7c303b92` (2026-10-17). Many ROCKNIX patches have no author header upstream, so
  none can be shown here either.
- Patches without an `Origin:` line are REG-Linux's own, or carry their upstream
  author in `From:`.
