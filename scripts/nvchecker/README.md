# General concept
nvchecker is a tool to check for new versions. It handles numerous protocols, source websites ... An absolute swiss knife which comes with some specifications.

The whole purpose is to be able to gather buildroot packages versions (not all of them are compatible sadly), prepare a local cache of packages versions and their source repo, then have nvchecker fetch versions from source repos and compare.

## Pre-requisites
* Use `pip`, `pip3` or `pipx` (depending on your python version) to install nvchecker, see https://github.com/lilydjwg/nvchecker?tab=readme-ov-file#install-and-run
* You'll also need `git`.
* It's a good idea to have a github API token as nvchecker can use it to query the github API. Store it in `scripts/nvechecker/keyfile.toml` like this:

```
[keys]
github = "your_github_api_token"

```

## Internals
Mostly 2 cases to handle for a package version: tag or commit.

Tags are easy to manage, and nvchecker's sorting methods do a good job at it. So spotting new versions when running the script makes it evident to notice new versions.

Commits are a different story and need some background. Unless you clone a repo, you can't know the commit history. And when comparing commits, nvchecker didn't clone the repo, so it alphabetically sorts commits to compare versions, which is abolutely wrong. So commits, at a point, must come with a commit datetime that is a better way to compare versions

### check_updates.sh
That scripts is the root of all. It parses dirs or single files for data that can fill a nvchecker toml file. It will scan for buildroot .mk files, check the source (github ? gitlab ? git ?), version (commit ? tag-like ?), and produce a toml section for each package found.

`check_updates.sh` can have some incorrect guesses because the very few information from a .mk is not enough to guess some specific parameters. See overrides.conf

### packages.exclude
When you know some packages just can't be managed by check_updates.sh, simply add the package name here, 1 per line, and they will be skipped. For example: `libretro-blastem` is not managed by check_updates.sh because it is a mercurial repo and REG uses a commit id, not a tag.

### overrides.conf
This file helps to force some specific keys/value for the resulting toml section of a package, enhancing the default guess by check_updates.sh. The syntax is `<package>.<nvchecker parameter>=<value>`. Refer to the nvchecker documentation to know about possible parameters.

# Usage

Just run `scripts/nvchecker/check_updates.sh` You may eventually specify a dir or a .mk files (ex: `scripts/nvchecker/check_updates.sh package/engines/solarus-engine/solarus-engine.mk` or `scripts/nvchecker/check_updates.sh package/emulators`). The script will prepare a `nvchecker.toml` file based on the current buildroot packages' version and produce an output like:
```
[I 08-14 17:38:16.515 core:416] reglinux-scummvm: updated from v2.9.1 to v2.9.0 url=https://github.com/REG-Linux/REG-ScummVM/releases/tag/v2.9.0
[I 08-14 17:38:16.580 core:416] libretro-gearcoleco: updated from 1.5.1 to 1.5.2 url=https://github.com/drhelius/Gearcoleco/releases/tag/1.5.2
[I 08-14 17:38:16.607 core:416] reglinux-mame: updated from 0.276 to 0.279 url=https://github.com/REG-Linux/REG-MAME/releases/tag/0.279
[I 08-14 17:38:16.612 core:416] libretro-puae2021: updated from 20250524.134614 to 20250719.215831 revision=3fc66ee4b562910a17e2e2f3bad74572a8bcc134 url=https://github.com/libretro/libretro-uae/commit/3fc66ee4b562910a17e2e2f3bad74572a8bcc134
```

The result output depends on the package source/version, mainly if tag or commit. The output is, I hope, quite self explanatory. You read `<package>: updated from <buildroot version> to <source version>`. If `from` is missing, then we couldn't define the current buildroot version. The output will vary depending on the version form:
* tag: the new tag is shown + an url to it
* commit: as comparing commit age on commit id is absurd, nvchecker needs the commit date and show them, adding the last commit id so you can easily copy/paste

Packages that have no update are not shown!

You may addtionnally run:
* `nvcmp -c scripts/nvchecker/nvchecker.toml`: way shorter output than the script, but doesn't list new commits, just their date. But useful for a glance of packages that can be updated
* `nvcmp -c scripts/nvchecker/nvchecker.toml -a`: lists ALL packages, even those with no update

# Common errors and fixes

## nvchecker complains my github repo has no release
Sample error code:
```
[E 08-08 23:58:42.820 core:369] libretro-mame: unexpected error happened error=HTTPError(404, 'Not Found', HTTPResponse(_body=None,_error_is_response_code=True,buffer=<_io.BytesIO object at 0x7c5dc86576a0>,code=404,effective_url='https://api.github.com/repos/libretro/mame/releases/latest',error=HTTP 404: Not Found,headers=<tornado.httputil.HTTPHeaders object at 0x7c5dc84544d0>,reason='Not Found',request=<tornado.httpclient.HTTPRequest object at 0x7c5dc88933b0>,request_time=0.2619342803955078,start_time=1754690322.558608,time_info={'queue': 3.337860107421875e-06, 'namelookup': 0.0, 'connect': 0.0, 'appconnect': 0.0, 'pretransfer': 4.8e-05, 'starttransfer': 0.261671, 'total': 0.261828, 'redirect': 0.0}))
```
effective_url ends with /releases/latest for an error 404.
Many repos just have tags but no release. In that case, add to overrides.conf:
`<package>.use_latest_tag="true"`

This can also happen for repos that have only pre-releases. In that case, add `<package>.include_prereleases="true"`

## Github API tokens
Github limits non non autorized API calls pretty hard to 60 calls per hour!!! See https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users 

Authorized API calls are limited to 5 000 requests per hour. This can be easily reached, take care ...

# Useful links
* https://nvchecker.readthedocs.io/en/latest/index.html