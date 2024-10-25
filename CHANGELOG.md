# Changes in IPython kernel

<!-- <START NEW CHANGELOG ENTRY> -->

## 7.0.0a0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.3...314cc49da6e7d69d74f4741d4ea6568e926d1819))

### Enhancements made

- Detect parent change in more cases on unix [#1271](https://github.com/ipython/ipykernel/pull/1271) ([@bluss](https://github.com/bluss))
- Kernel subshells (JEP91) implementation [#1249](https://github.com/ipython/ipykernel/pull/1249) ([@ianthomas23](https://github.com/ianthomas23))
- Remove control queue [#1210](https://github.com/ipython/ipykernel/pull/1210) ([@ianthomas23](https://github.com/ianthomas23))
- Replace Tornado with AnyIO [#1079](https://github.com/ipython/ipykernel/pull/1079) ([@davidbrochart](https://github.com/davidbrochart))

### Bugs fixed

- Fix eventloop integration with anyio [#1265](https://github.com/ipython/ipykernel/pull/1265) ([@ianthomas23](https://github.com/ianthomas23))
- Explicitly close memory object streams [#1253](https://github.com/ipython/ipykernel/pull/1253) ([@ianthomas23](https://github.com/ianthomas23))
- Fixed error accessing sys.stdout/sys.stderr when those are None [#1247](https://github.com/ipython/ipykernel/pull/1247) ([@gregory-shklover](https://github.com/gregory-shklover))
- Correctly handle with_cell_id in async do_execute [#1227](https://github.com/ipython/ipykernel/pull/1227) ([@ianthomas23](https://github.com/ianthomas23))
- Do not import debugger/debugpy unless needed [#1223](https://github.com/ipython/ipykernel/pull/1223) ([@krassowski](https://github.com/krassowski))
- Allow datetime or str in test_sequential_control_messages [#1219](https://github.com/ipython/ipykernel/pull/1219) ([@ianthomas23](https://github.com/ianthomas23))
- Fix side effect import for pickleutil [#1217](https://github.com/ipython/ipykernel/pull/1217) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Remove direct use of asyncio [#1266](https://github.com/ipython/ipykernel/pull/1266) ([@davidbrochart](https://github.com/davidbrochart))
- Specify argtypes when using macos msg [#1264](https://github.com/ipython/ipykernel/pull/1264) ([@ianthomas23](https://github.com/ianthomas23))
- Forward port changelog for 6.29.4 and 5 to main branch [#1263](https://github.com/ipython/ipykernel/pull/1263) ([@ianthomas23](https://github.com/ianthomas23))
- Ignore warning from trio [#1262](https://github.com/ipython/ipykernel/pull/1262) ([@ianthomas23](https://github.com/ianthomas23))
- Build docs on ubuntu [#1257](https://github.com/ipython/ipykernel/pull/1257) ([@blink1073](https://github.com/blink1073))
- Avoid a DeprecationWarning on Python 3.13+ [#1248](https://github.com/ipython/ipykernel/pull/1248) ([@hroncok](https://github.com/hroncok))
- Catch IPython 8.24 DeprecationWarnings [#1242](https://github.com/ipython/ipykernel/pull/1242) ([@s-t-e-v-e-n-k](https://github.com/s-t-e-v-e-n-k))
- Update version to 7.0.0 [#1241](https://github.com/ipython/ipykernel/pull/1241) ([@mlucool](https://github.com/mlucool))
- Add compat with pytest 8 [#1231](https://github.com/ipython/ipykernel/pull/1231) ([@blink1073](https://github.com/blink1073))
- Set all min deps [#1229](https://github.com/ipython/ipykernel/pull/1229) ([@blink1073](https://github.com/blink1073))
- Update Release Scripts [#1221](https://github.com/ipython/ipykernel/pull/1221) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Forward port changelog for 6.29.4 and 5 to main branch [#1263](https://github.com/ipython/ipykernel/pull/1263) ([@ianthomas23](https://github.com/ianthomas23))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-02-26&to=2024-10-22&type=c))

[@agronholm](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aagronholm+updated%3A2024-02-26..2024-10-22&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2024-02-26..2024-10-22&type=Issues) | [@bluss](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Abluss+updated%3A2024-02-26..2024-10-22&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2024-02-26..2024-10-22&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2024-02-26..2024-10-22&type=Issues) | [@gregory-shklover](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Agregory-shklover+updated%3A2024-02-26..2024-10-22&type=Issues) | [@hroncok](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ahroncok+updated%3A2024-02-26..2024-10-22&type=Issues) | [@ianthomas23](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aianthomas23+updated%3A2024-02-26..2024-10-22&type=Issues) | [@ivanov](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aivanov+updated%3A2024-02-26..2024-10-22&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akrassowski+updated%3A2024-02-26..2024-10-22&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2024-02-26..2024-10-22&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2024-02-26..2024-10-22&type=Issues) | [@mlucool](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amlucool+updated%3A2024-02-26..2024-10-22&type=Issues) | [@s-t-e-v-e-n-k](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3As-t-e-v-e-n-k+updated%3A2024-02-26..2024-10-22&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 6.29.5

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.4...1e62d48298e353a9879fae99bc752f9bb48797ef))

### Bugs fixed

- Fix use of "%matplotlib osx" [#1237](https://github.com/ipython/ipykernel/pull/1237) ([@ianthomas23](https://github.com/ianthomas23))

### Maintenance and upkeep improvements

- \[6.x\] Update Release Scripts  [#1251](https://github.com/ipython/ipykernel/pull/1251) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-03-27&to=2024-06-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2024-03-27..2024-06-29&type=Issues) | [@ianthomas23](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aianthomas23+updated%3A2024-03-27..2024-06-29&type=Issues)

## 6.29.4

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.3...1cea5332ffc37f32e8232fd2b8b8ddd91b2bbdcf))

### Bugs fixed

- Fix side effect import for pickleutil [#1216](https://github.com/ipython/ipykernel/pull/1216) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Do not import debugger/debugpy unless needed [#1223](https://github.com/ipython/ipykernel/pull/1223) ([@krassowski](https://github.com/krassowski))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-02-26&to=2024-03-27&type=c))

[@agronholm](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aagronholm+updated%3A2024-02-26..2024-03-27&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2024-02-26..2024-03-27&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2024-02-26..2024-03-27&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akrassowski+updated%3A2024-02-26..2024-03-27&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2024-02-26..2024-03-27&type=Issues)

## 6.29.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.2...de2221ce155668c343084fde37b77fb6b1671dc9))

### Enhancements made

- Eventloop scheduling improvements for stop_on_error_timeout and schedule_next [#1212](https://github.com/ipython/ipykernel/pull/1212) ([@jdranczewski](https://github.com/jdranczewski))

### Bugs fixed

- Disable frozen modules by default, add a toggle [#1213](https://github.com/ipython/ipykernel/pull/1213) ([@krassowski](https://github.com/krassowski))

### Maintenance and upkeep improvements

- Fix typings and update project urls [#1214](https://github.com/ipython/ipykernel/pull/1214) ([@blink1073](https://github.com/blink1073))
- Unpin pytest-asyncio and update ruff config [#1209](https://github.com/ipython/ipykernel/pull/1209) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Correct spelling mistake [#1208](https://github.com/ipython/ipykernel/pull/1208) ([@joouha](https://github.com/joouha))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-02-07&to=2024-02-26&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2024-02-07..2024-02-26&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2024-02-07..2024-02-26&type=Issues) | [@jdranczewski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajdranczewski+updated%3A2024-02-07..2024-02-26&type=Issues) | [@joouha](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajoouha+updated%3A2024-02-07..2024-02-26&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akrassowski+updated%3A2024-02-07..2024-02-26&type=Issues)

## 6.29.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.1...d45fe71990d26c0bd5b7b3b2a4ccd3d1f6609899))

### Bugs fixed

- Fix: ipykernel_launcher, delete absolute sys.path\[0\] [#1206](https://github.com/ipython/ipykernel/pull/1206) ([@stdll00](https://github.com/stdll00))

### Maintenance and upkeep improvements

- Re-enable skipped debugger test [#1207](https://github.com/ipython/ipykernel/pull/1207) ([@ianthomas23](https://github.com/ianthomas23))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-02-06&to=2024-02-07&type=c))

[@ianthomas23](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aianthomas23+updated%3A2024-02-06..2024-02-07&type=Issues) | [@stdll00](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Astdll00+updated%3A2024-02-06..2024-02-07&type=Issues)

## 6.29.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.29.0...09c9b2ad9c15202c5d1896ba24ec978b726c073b))

### Bugs fixed

- fix: on exception, return a 0, so that the "sum" still computes [#1204](https://github.com/ipython/ipykernel/pull/1204) ([@petervandenabeele](https://github.com/petervandenabeele))
- Fix handling of "silent" in execute request [#1200](https://github.com/ipython/ipykernel/pull/1200) ([@Haadem](https://github.com/Haadem))

### Maintenance and upkeep improvements

- chore: update pre-commit hooks [#1205](https://github.com/ipython/ipykernel/pull/1205) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Do git ignore of /node_modules/.cache [#1203](https://github.com/ipython/ipykernel/pull/1203) ([@petervandenabeele](https://github.com/petervandenabeele))
- Bump the actions group with 1 update [#1201](https://github.com/ipython/ipykernel/pull/1201) ([@dependabot](https://github.com/dependabot))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2024-01-16&to=2024-02-06&type=c))

[@dependabot](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adependabot+updated%3A2024-01-16..2024-02-06&type=Issues) | [@Haadem](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AHaadem+updated%3A2024-01-16..2024-02-06&type=Issues) | [@petervandenabeele](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apetervandenabeele+updated%3A2024-01-16..2024-02-06&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2024-01-16..2024-02-06&type=Issues)

## 6.29.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.28.0...84955484ec1636ee4c7611471d20df2016b5cb57))

### Enhancements made

- Always set debugger to true in kernelspec [#1191](https://github.com/ipython/ipykernel/pull/1191) ([@ianthomas23](https://github.com/ianthomas23))

### Bugs fixed

- Revert "Enable `ProactorEventLoop` on windows for `ipykernel`" [#1194](https://github.com/ipython/ipykernel/pull/1194) ([@blink1073](https://github.com/blink1073))
- Make outputs go to correct cell when generated in threads/asyncio [#1186](https://github.com/ipython/ipykernel/pull/1186) ([@krassowski](https://github.com/krassowski))

### Maintenance and upkeep improvements

- Pin pytest-asyncio to 0.23.2 [#1189](https://github.com/ipython/ipykernel/pull/1189) ([@ianthomas23](https://github.com/ianthomas23))
- chore: update pre-commit hooks [#1187](https://github.com/ipython/ipykernel/pull/1187) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-12-26&to=2024-01-16&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-12-26..2024-01-16&type=Issues) | [@ianthomas23](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aianthomas23+updated%3A2023-12-26..2024-01-16&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akrassowski+updated%3A2023-12-26..2024-01-16&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-12-26..2024-01-16&type=Issues)

## 6.28.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.27.1...de45c7a49e197f0889f867f33f24cce322768a0e))

### Enhancements made

- Enable `ProactorEventLoop` on windows for `ipykernel` [#1184](https://github.com/ipython/ipykernel/pull/1184) ([@NewUserHa](https://github.com/NewUserHa))
- Adds a flag in debug_info for the copyToGlobals support [#1099](https://github.com/ipython/ipykernel/pull/1099) ([@brichet](https://github.com/brichet))

### Maintenance and upkeep improvements

- Support python 3.12 [#1185](https://github.com/ipython/ipykernel/pull/1185) ([@blink1073](https://github.com/blink1073))
- Bump actions/setup-python from 4 to 5 [#1181](https://github.com/ipython/ipykernel/pull/1181) ([@dependabot](https://github.com/dependabot))
- chore: update pre-commit hooks [#1179](https://github.com/ipython/ipykernel/pull/1179) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Refactor execute_request to reduce redundancy and improve consistency [#1177](https://github.com/ipython/ipykernel/pull/1177) ([@jjvraw](https://github.com/jjvraw))

### Documentation improvements

- Update pytest commands in README [#1178](https://github.com/ipython/ipykernel/pull/1178) ([@ianthomas23](https://github.com/ianthomas23))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-11-27&to=2023-12-26&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-11-27..2023-12-26&type=Issues) | [@brichet](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Abrichet+updated%3A2023-11-27..2023-12-26&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adependabot+updated%3A2023-11-27..2023-12-26&type=Issues) | [@ianthomas23](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aianthomas23+updated%3A2023-11-27..2023-12-26&type=Issues) | [@jjvraw](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajjvraw+updated%3A2023-11-27..2023-12-26&type=Issues) | [@NewUserHa](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ANewUserHa+updated%3A2023-11-27..2023-12-26&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-11-27..2023-12-26&type=Issues)

## 6.27.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.27.0...f9c517e868462d05d6854204c2ad0a244db1cd19))

### Bugs fixed

- Fix edit magic payload type [#1171](https://github.com/ipython/ipykernel/pull/1171) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-11-21&to=2023-11-27&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-11-21..2023-11-27&type=Issues)

## 6.27.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.26.0...465d34483103d23f471a4795fe5fabb9cf7ac3f5))

### Enhancements made

- Extend argument handling of do_execute with cell metadata [#1169](https://github.com/ipython/ipykernel/pull/1169) ([@jjvraw](https://github.com/jjvraw))

### Maintenance and upkeep improvements

- Update ruff and typings [#1167](https://github.com/ipython/ipykernel/pull/1167) ([@blink1073](https://github.com/blink1073))
- Clean up ruff config [#1165](https://github.com/ipython/ipykernel/pull/1165) ([@blink1073](https://github.com/blink1073))
- chore: update pre-commit hooks [#1164](https://github.com/ipython/ipykernel/pull/1164) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Clean up typing config [#1163](https://github.com/ipython/ipykernel/pull/1163) ([@blink1073](https://github.com/blink1073))
- Update typing for traitlets 5.13 [#1162](https://github.com/ipython/ipykernel/pull/1162) ([@blink1073](https://github.com/blink1073))
- Adopt ruff format [#1161](https://github.com/ipython/ipykernel/pull/1161) ([@blink1073](https://github.com/blink1073))
- Update typing for jupyter_client 8.5 [#1160](https://github.com/ipython/ipykernel/pull/1160) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-10-24&to=2023-11-21&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-10-24..2023-11-21&type=Issues) | [@jjvraw](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajjvraw+updated%3A2023-10-24..2023-11-21&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-10-24..2023-11-21&type=Issues)

## 6.26.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.25.2...966e0a41fc61e7850378ae672e28202eb29b10b0))

### Maintenance and upkeep improvements

- Update lint deps and add more typing [#1156](https://github.com/ipython/ipykernel/pull/1156) ([@blink1073](https://github.com/blink1073))
- Update typing for traitlets 5.11 [#1154](https://github.com/ipython/ipykernel/pull/1154) ([@blink1073](https://github.com/blink1073))
- chore: update pre-commit hooks [#1153](https://github.com/ipython/ipykernel/pull/1153) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Update IPython Typing Usage [#1152](https://github.com/ipython/ipykernel/pull/1152) ([@blink1073](https://github.com/blink1073))
- Update typing [#1150](https://github.com/ipython/ipykernel/pull/1150) ([@blink1073](https://github.com/blink1073))
- Use sp-repo-review [#1146](https://github.com/ipython/ipykernel/pull/1146) ([@blink1073](https://github.com/blink1073))
- Bump actions/checkout from 3 to 4 [#1144](https://github.com/ipython/ipykernel/pull/1144) ([@dependabot](https://github.com/dependabot))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-09-04&to=2023-10-24&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-09-04..2023-10-24&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adependabot+updated%3A2023-09-04..2023-10-24&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-09-04..2023-10-24&type=Issues)

## 6.25.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.25.1...9d3f7aecc4fe68f14ebcc4dad4b65b19676e820e))

### Bugs fixed

- Make iostream shutdown more robust [#1143](https://github.com/ipython/ipykernel/pull/1143) ([@blink1073](https://github.com/blink1073))
- Don't call QApplication.setQuitOnLastWindowClosed(False). [#1142](https://github.com/ipython/ipykernel/pull/1142) ([@anntzer](https://github.com/anntzer))
- Avoid starting IOPub background thread after it's been stopped [#1137](https://github.com/ipython/ipykernel/pull/1137) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-08-07&to=2023-09-04&type=c))

[@anntzer](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aanntzer+updated%3A2023-08-07..2023-09-04&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-08-07..2023-09-04&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2023-08-07..2023-09-04&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2023-08-07..2023-09-04&type=Issues)

## 6.25.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.25.0...18e54f31725d6645dd71a8749c9e1eb28281f804))

### Bugs fixed

- Modifying debugger to return the same breakpoints in 'debugInfo' response as 'setBreakpoints' [#1140](https://github.com/ipython/ipykernel/pull/1140) ([@vaishnavi17](https://github.com/vaishnavi17))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-07-25&to=2023-08-07&type=c))

[@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-07-25..2023-08-07&type=Issues) | [@vaishnavi17](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Avaishnavi17+updated%3A2023-07-25..2023-08-07&type=Issues)

## 6.25.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.24.0...09c3c359addf60e26078207990ad2ca932cf2613))

### Enhancements made

- feat: let display hook handle clear_output [#1135](https://github.com/ipython/ipykernel/pull/1135) ([@maartenbreddels](https://github.com/maartenbreddels))

### Bugs fixed

- Merge connection info into existing connection file if it already exists [#1133](https://github.com/ipython/ipykernel/pull/1133) ([@jasongrout](https://github.com/jasongrout))

### Maintenance and upkeep improvements

- Clean up lint [#1134](https://github.com/ipython/ipykernel/pull/1134) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-07-03&to=2023-07-25&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-07-03..2023-07-25&type=Issues) | [@fecet](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afecet+updated%3A2023-07-03..2023-07-25&type=Issues) | [@jasongrout](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajasongrout+updated%3A2023-07-03..2023-07-25&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2023-07-03..2023-07-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-07-03..2023-07-25&type=Issues)

## 6.24.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.23.3...0c1db099a32c4cb28bfb4b3508bb808d8b4092e7))

### New features added

- Let get_parent decide the channel to get parent header [#1128](https://github.com/ipython/ipykernel/pull/1128) ([@dby-tmwctw](https://github.com/dby-tmwctw))

### Bugs fixed

- Bugfix: binary stdout/stderr handling [#1129](https://github.com/ipython/ipykernel/pull/1129) ([@arieleiz](https://github.com/arieleiz))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-06-23&to=2023-07-03&type=c))

[@arieleiz](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aarieleiz+updated%3A2023-06-23..2023-07-03&type=Issues) | [@dby-tmwctw](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adby-tmwctw+updated%3A2023-06-23..2023-07-03&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2023-06-23..2023-07-03&type=Issues)

## 6.23.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.23.2...ea3e6479aca70f87282ec0b60412f2cfba59eb35))

### Bugs fixed

- Check existence of connection_file before writing [#1127](https://github.com/ipython/ipykernel/pull/1127) ([@fecet](https://github.com/fecet))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-06-12&to=2023-06-23&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-06-12..2023-06-23&type=Issues) | [@fecet](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afecet+updated%3A2023-06-12..2023-06-23&type=Issues)

## 6.23.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.23.1...112ca66da0ee8156b983094b2c8e2926ed63cfcb))

### Bugs fixed

- Avoid ResourceWarning on implicitly closed event pipe sockets [#1125](https://github.com/ipython/ipykernel/pull/1125) ([@minrk](https://github.com/minrk))
- fix: protect stdout/stderr restoration in `InProcessKernel._redirected_io` [#1122](https://github.com/ipython/ipykernel/pull/1122) ([@charles-cooper](https://github.com/charles-cooper))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-05-15&to=2023-06-12&type=c))

[@charles-cooper](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Acharles-cooper+updated%3A2023-05-15..2023-06-12&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2023-05-15..2023-06-12&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-05-15..2023-06-12&type=Issues)

## 6.23.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.23.0...d63c33afb9872f2781997b2428d7e9e0c1d23d41))

### Bugs fixed

- Avoid echoing onto a captured FD [#1111](https://github.com/ipython/ipykernel/pull/1111) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- update readthedocs env to 3.11 [#1117](https://github.com/ipython/ipykernel/pull/1117) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-05-08&to=2023-05-15&type=c))

[@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2023-05-08..2023-05-15&type=Issues)

## 6.23.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.22.0...3dd6dc9712ff6eb0a53cf79969dcefa0ba1b086e))

### Enhancements made

- Support control\<>iopub messages to e.g. unblock comm_msg from command execution  [#1114](https://github.com/ipython/ipykernel/pull/1114) ([@tkrabel-db](https://github.com/tkrabel-db))
- Add outstream hook similar to display publisher [#1110](https://github.com/ipython/ipykernel/pull/1110) ([@maartenbreddels](https://github.com/maartenbreddels))

### Maintenance and upkeep improvements

- Use local coverage [#1109](https://github.com/ipython/ipykernel/pull/1109) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-03-20&to=2023-05-08&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-03-20..2023-05-08&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2023-03-20..2023-05-08&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-03-20..2023-05-08&type=Issues) | [@tkrabel-db](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Atkrabel-db+updated%3A2023-03-20..2023-05-08&type=Issues)

## 6.22.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.21.3...e2972d763b5357d4e1cb9b5355593583ca6d5657))

### Bugs fixed

- Deprecate Comm class + Fix incompatibility with ipywidgets [#1097](https://github.com/ipython/ipykernel/pull/1097) ([@martinRenou](https://github.com/martinRenou))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-03-06&to=2023-03-20&type=c))

[@martinRenou](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AmartinRenou+updated%3A2023-03-06..2023-03-20&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-03-06..2023-03-20&type=Issues)

## 6.21.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.21.2...e46f75b93c388886f4b6ba32182e29c3cc486984))

### Bugs fixed

- Fix interrupt reply [#1101](https://github.com/ipython/ipykernel/pull/1101) ([@garlandz-db](https://github.com/garlandz-db))

### Maintenance and upkeep improvements

- Update docs link [#1103](https://github.com/ipython/ipykernel/pull/1103) ([@blink1073](https://github.com/blink1073))
- Add license [#1098](https://github.com/ipython/ipykernel/pull/1098) ([@dcsaba89](https://github.com/dcsaba89))

### Documentation improvements

- Update changelog for markdown typo [#1096](https://github.com/ipython/ipykernel/pull/1096) ([@mlucool](https://github.com/mlucool))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-02-13&to=2023-03-06&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-02-13..2023-03-06&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2023-02-13..2023-03-06&type=Issues) | [@dcsaba89](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adcsaba89+updated%3A2023-02-13..2023-03-06&type=Issues) | [@garlandz-db](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Agarlandz-db+updated%3A2023-02-13..2023-03-06&type=Issues) | [@mlucool](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amlucool+updated%3A2023-02-13..2023-03-06&type=Issues)

## 6.21.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.21.1...1a486e06155a4d8e58e716fd40468cb5738ed6bb))

### Bugs fixed

- Un-expose `__file__` and expose `__session__` instead. [#1095](https://github.com/ipython/ipykernel/pull/1095) ([@Carreau](https://github.com/Carreau))

### Maintenance and upkeep improvements

- Remove test_enter_eventloop [#1084](https://github.com/ipython/ipykernel/pull/1084) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-02-02&to=2023-02-13&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-02-02..2023-02-13&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2023-02-02..2023-02-13&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2023-02-02..2023-02-13&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2023-02-02..2023-02-13&type=Issues)

## 6.21.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.21.0...ac7776dfd68861ae005e1f142ec87cd6703847ea))

### Maintenance and upkeep improvements

- Restore nest-asyncio for tk loop [#1086](https://github.com/ipython/ipykernel/pull/1086) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-01-30&to=2023-02-02&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-01-30..2023-02-02&type=Issues)

## 6.21.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.20.2...dde698850d865dec89bba2305d1f3dc3134f8413))

### Enhancements made

- Expose session start file in `__file__`. [#1078](https://github.com/ipython/ipykernel/pull/1078) ([@Carreau](https://github.com/Carreau))
- Add copy_to_globals debug request handling [#1055](https://github.com/ipython/ipykernel/pull/1055) ([@brichet](https://github.com/brichet))

### Maintenance and upkeep improvements

- Adopt more lint rules [#1082](https://github.com/ipython/ipykernel/pull/1082) ([@blink1073](https://github.com/blink1073))
- Maintenance updates [#1081](https://github.com/ipython/ipykernel/pull/1081) ([@blink1073](https://github.com/blink1073))
- Test spyder kernels [#1080](https://github.com/ipython/ipykernel/pull/1080) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-01-16&to=2023-01-30&type=c))

[@agronholm](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aagronholm+updated%3A2023-01-16..2023-01-30&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2023-01-16..2023-01-30&type=Issues) | [@brichet](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Abrichet+updated%3A2023-01-16..2023-01-30&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2023-01-16..2023-01-30&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2023-01-16..2023-01-30&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2023-01-16..2023-01-30&type=Issues)

## 6.20.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.20.1...203ee2bce0b506257bd561d082e983330d1ebd14))

### Bugs fixed

- Fix Exception in OutStream.close() [#1076](https://github.com/ipython/ipykernel/pull/1076) ([@ilyasher](https://github.com/ilyasher))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2023-01-09&to=2023-01-16&type=c))

[@ilyasher](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ailyasher+updated%3A2023-01-09..2023-01-16&type=Issues)

## 6.20.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.20.0...5f07abc22a1c75672f7bee129505f19c954a7c36))

### Bugs fixed

- Don't raise error when trying to create another Qt app for Qt eventloop [#1071](https://github.com/ipython/ipykernel/pull/1071) ([@ccordoba12](https://github.com/ccordoba12))

### Maintenance and upkeep improvements

- Update CI [#1073](https://github.com/ipython/ipykernel/pull/1073) ([@blink1073](https://github.com/blink1073))
- Fix types and sync lint deps [#1070](https://github.com/ipython/ipykernel/pull/1070) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add api docs [#1067](https://github.com/ipython/ipykernel/pull/1067) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-26&to=2023-01-09&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-12-26..2023-01-09&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2022-12-26..2023-01-09&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-12-26..2023-01-09&type=Issues)

## 6.20.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.19.4...fbea757e117c1d3b0da29a40b4abcf3133a310f4))

### Enhancements made

- ENH: add `%gui` support for Qt6 [#1054](https://github.com/ipython/ipykernel/pull/1054) ([@shaperilio](https://github.com/shaperilio))

### Maintenance and upkeep improvements

- Add more ci checks [#1063](https://github.com/ipython/ipykernel/pull/1063) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-20&to=2022-12-26&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-12-20..2022-12-26&type=Issues) | [@shaperilio](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ashaperilio+updated%3A2022-12-20..2022-12-26&type=Issues)

## 6.19.4

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.19.3...07da48e686b5906525c2a6b8cfc11cd7c3d96a5f))

### Bugs fixed

- Don't pass `None` kernels to logging configurable in `Comm` [#1061](https://github.com/ipython/ipykernel/pull/1061) ([@bollwyvl](https://github.com/bollwyvl))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-19&to=2022-12-20&type=c))

[@bollwyvl](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Abollwyvl+updated%3A2022-12-19..2022-12-20&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-12-19..2022-12-20&type=Issues)

## 6.19.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.19.2...0925d09075280beb23c009ca0d361f73e5402e27))

### Bugs fixed

- format dates as ISO8601 [#1057](https://github.com/ipython/ipykernel/pull/1057) ([@GRcharles](https://github.com/GRcharles))
- Fix comms and add qtconsole downstream test [#1056](https://github.com/ipython/ipykernel/pull/1056) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Fix lint [#1058](https://github.com/ipython/ipykernel/pull/1058) ([@blink1073](https://github.com/blink1073))
- Fix comms and add qtconsole downstream test [#1056](https://github.com/ipython/ipykernel/pull/1056) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-08&to=2022-12-19&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-12-08..2022-12-19&type=Issues) | [@GRcharles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AGRcharles+updated%3A2022-12-08..2022-12-19&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-12-08..2022-12-19&type=Issues)

## 6.19.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.19.1...3c125ad5aa27de2ff412d7690de051115f175104))

### Bugs fixed

- Fix error in `%edit` magic [#1053](https://github.com/ipython/ipykernel/pull/1053) ([@ccordoba12](https://github.com/ccordoba12))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-08&to=2022-12-08&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-12-08..2022-12-08&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2022-12-08..2022-12-08&type=Issues)

## 6.19.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.19.0...5e1b155207c506f01df5808b1ba41f868a10f097))

### Bugs fixed

- fix: too many arguments dropped when passing to base comm constructor [#1051](https://github.com/ipython/ipykernel/pull/1051) ([@maartenbreddels](https://github.com/maartenbreddels))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-12-07&to=2022-12-08&type=c))

[@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-12-07..2022-12-08&type=Issues)

## 6.19.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.18.3...2c80e6c31e4912b2deaf5276b27568ba5088ad97))

### Bugs fixed

- Fix: there can be only one comm_manager [#1049](https://github.com/ipython/ipykernel/pull/1049) ([@maartenbreddels](https://github.com/maartenbreddels))

### Maintenance and upkeep improvements

- Adopt ruff and address lint [#1046](https://github.com/ipython/ipykernel/pull/1046) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-11-29&to=2022-12-07&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-11-29..2022-12-07&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-11-29..2022-12-07&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-11-29..2022-12-07&type=Issues)

## 6.18.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.18.2...c0f5b7e3a5287c288eff477ae70848decf25332d))

### Bugs fixed

- Fix Comm interface for downstream users [#1042](https://github.com/ipython/ipykernel/pull/1042) ([@maartenbreddels](https://github.com/maartenbreddels))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-11-29&to=2022-11-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-11-29..2022-11-29&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-11-29..2022-11-29&type=Issues)

## 6.18.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.18.1...a38167b1c689130df231fa77d712827bc75a8ba6))

### Bugs fixed

- Configurables needs to be configurable [#1037](https://github.com/ipython/ipykernel/pull/1037) ([@Carreau](https://github.com/Carreau))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-11-28&to=2022-11-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-11-28..2022-11-29&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2022-11-28..2022-11-29&type=Issues) | [@fperez](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afperez+updated%3A2022-11-28..2022-11-29&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-11-28..2022-11-29&type=Issues)

## 6.18.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.18.0...252c406a82fb9bab4071bfbc287b7a24a51752d8))

### Bugs fixed

- fix: use comm package in backwards compatible way [#1028](https://github.com/ipython/ipykernel/pull/1028) ([@maartenbreddels](https://github.com/maartenbreddels))

### Maintenance and upkeep improvements

- Add more testing and deprecate the Gtk event loops [#1036](https://github.com/ipython/ipykernel/pull/1036) ([@blink1073](https://github.com/blink1073))
- More coverage improvements [#1035](https://github.com/ipython/ipykernel/pull/1035) ([@blink1073](https://github.com/blink1073))
- Add more tests [#1034](https://github.com/ipython/ipykernel/pull/1034) ([@blink1073](https://github.com/blink1073))
- Add more kernel tests [#1032](https://github.com/ipython/ipykernel/pull/1032) ([@blink1073](https://github.com/blink1073))
- Add more coverage and add Readme badges [#1031](https://github.com/ipython/ipykernel/pull/1031) ([@blink1073](https://github.com/blink1073))
- Clean up testing and coverage [#1030](https://github.com/ipython/ipykernel/pull/1030) ([@blink1073](https://github.com/blink1073))
- Use base setup dependency type [#1029](https://github.com/ipython/ipykernel/pull/1029) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-11-21&to=2022-11-28&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-11-21..2022-11-28&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amaartenbreddels+updated%3A2022-11-21..2022-11-28&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AmartinRenou+updated%3A2022-11-21..2022-11-28&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-11-21..2022-11-28&type=Issues)

## 6.18.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.17.1...ce0b6c296bc19223d426892657878f28af0ec206))

### Enhancements made

- Add terminal color support [#1025](https://github.com/ipython/ipykernel/pull/1025) ([@blink1073](https://github.com/blink1073))
- Extract the Comm Python package [#973](https://github.com/ipython/ipykernel/pull/973) ([@martinRenou](https://github.com/martinRenou))

### Maintenance and upkeep improvements

- Add windows coverage and clean up workflows [#1023](https://github.com/ipython/ipykernel/pull/1023) ([@blink1073](https://github.com/blink1073))
- Increase coverage [#1021](https://github.com/ipython/ipykernel/pull/1021) ([@blink1073](https://github.com/blink1073))
- Allow releasing from repo [#1020](https://github.com/ipython/ipykernel/pull/1020) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-11-09&to=2022-11-21&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-11-09..2022-11-21&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AmartinRenou+updated%3A2022-11-09..2022-11-21&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-11-09..2022-11-21&type=Issues)

## 6.17.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.17.0...a06867786eaf0c5d9454d2df61f354c7012a625e))

### Maintenance and upkeep improvements

- Ignore the new Jupyter_core deprecation warning in CI [#1019](https://github.com/ipython/ipykernel/pull/1019) ([@jasongrout](https://github.com/jasongrout))
- Bump actions/checkout from 2 to 3 [#1018](https://github.com/ipython/ipykernel/pull/1018) ([@dependabot](https://github.com/dependabot))
- Add dependabot [#1017](https://github.com/ipython/ipykernel/pull/1017) ([@blink1073](https://github.com/blink1073))
- Add pyupgrade to pre-commit [#1014](https://github.com/ipython/ipykernel/pull/1014) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-10-31&to=2022-11-09&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-10-31..2022-11-09&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adependabot+updated%3A2022-10-31..2022-11-09&type=Issues) | [@jasongrout](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajasongrout+updated%3A2022-10-31..2022-11-09&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-10-31..2022-11-09&type=Issues)

## 6.17.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.16.2...db00586a25a4f047a90386f4947e60ff1dbee2b6))

### Enhancements made

- Enable webagg in %matplotlib [#1012](https://github.com/ipython/ipykernel/pull/1012) ([@zhizheng1](https://github.com/zhizheng1))

### Maintenance and upkeep improvements

- Update supported pythons to 3.8-3.11 [#1013](https://github.com/ipython/ipykernel/pull/1013) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-10-25&to=2022-10-31&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-10-25..2022-10-31&type=Issues) | [@zhizheng1](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Azhizheng1+updated%3A2022-10-25..2022-10-31&type=Issues)

## 6.16.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.16.1...99706182995e0fd5431965d4c9d96a8ce7afae12))

### Maintenance and upkeep improvements

- Fix failing test and update matrix [#1010](https://github.com/ipython/ipykernel/pull/1010) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-10-20&to=2022-10-25&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-10-20..2022-10-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-10-20..2022-10-25&type=Issues)

## 6.16.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.16.0...632a1ba3892bed707e1ee19fe1344e92475e19c9))

### Bugs fixed

- PR: Destroy tk app to avoid memory leak [#1008](https://github.com/ipython/ipykernel/pull/1008) ([@impact27](https://github.com/impact27))

### Maintenance and upkeep improvements

- Maintenance cleanup [#1006](https://github.com/ipython/ipykernel/pull/1006) ([@blink1073](https://github.com/blink1073))
- Ignore warnings in prereleases test [#1002](https://github.com/ipython/ipykernel/pull/1002) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-09-26&to=2022-10-20&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-09-26..2022-10-20&type=Issues) | [@impact27](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aimpact27+updated%3A2022-09-26..2022-10-20&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-09-26..2022-10-20&type=Issues)

## 6.16.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.15.3...92292ad9d844e594e9c97f7f391149023e58de9e))

### Maintenance and upkeep improvements

- Use hatch for version [#998](https://github.com/ipython/ipykernel/pull/998) ([@blink1073](https://github.com/blink1073))
- Add client 8 support [#996](https://github.com/ipython/ipykernel/pull/996) ([@blink1073](https://github.com/blink1073))
- Remove unused manifest file [#994](https://github.com/ipython/ipykernel/pull/994) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-09-13&to=2022-09-26&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-09-13..2022-09-26&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-09-13..2022-09-26&type=Issues)

## 6.15.3

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.15.2...861b1242a7601f1608707ed8bbfb6e801914cb4a))

### Bugs fixed

- PR: Close memory leak [#990](https://github.com/ipython/ipykernel/pull/990) ([@impact27](https://github.com/impact27))
- Handle all possible exceptions when trying to import the debugger [#987](https://github.com/ipython/ipykernel/pull/987) ([@JohanMabille](https://github.com/JohanMabille))

### Maintenance and upkeep improvements

- \[pre-commit.ci\] pre-commit autoupdate [#989](https://github.com/ipython/ipykernel/pull/989) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#985](https://github.com/ipython/ipykernel/pull/985) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Add python logo in svg format [#984](https://github.com/ipython/ipykernel/pull/984) ([@steff456](https://github.com/steff456))
- \[pre-commit.ci\] pre-commit autoupdate [#982](https://github.com/ipython/ipykernel/pull/982) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-08-29&to=2022-09-13&type=c))

[@impact27](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aimpact27+updated%3A2022-08-29..2022-09-13&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2022-08-29..2022-09-13&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-08-29..2022-09-13&type=Issues) | [@steff456](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Asteff456+updated%3A2022-08-29..2022-09-13&type=Issues)

## 6.15.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.15.1...724753a185b0954f0e662c226b86dc8146c62bcb))

### Bugs fixed

- `_abort_queues` is no longer async [#942](https://github.com/ipython/ipykernel/pull/942) ([@rhelmot](https://github.com/rhelmot))

### Maintenance and upkeep improvements

- \[pre-commit.ci\] pre-commit autoupdate [#978](https://github.com/ipython/ipykernel/pull/978) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#977](https://github.com/ipython/ipykernel/pull/977) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#976](https://github.com/ipython/ipykernel/pull/976) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#974](https://github.com/ipython/ipykernel/pull/974) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#971](https://github.com/ipython/ipykernel/pull/971) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#968](https://github.com/ipython/ipykernel/pull/968) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#966](https://github.com/ipython/ipykernel/pull/966) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-07-08&to=2022-08-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-07-08..2022-08-29&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-07-08..2022-08-29&type=Issues) | [@rayosborn](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Arayosborn+updated%3A2022-07-08..2022-08-29&type=Issues) | [@rhelmot](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Arhelmot+updated%3A2022-07-08..2022-08-29&type=Issues)

## 6.15.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.15.0...d9a8578ab2864b4ee636b12252e04a9b70047d0b))

### Bugs fixed

- Fix inclusion of launcher file and check in CI [#964](https://github.com/ipython/ipykernel/pull/964) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- \[pre-commit.ci\] pre-commit autoupdate [#962](https://github.com/ipython/ipykernel/pull/962) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#961](https://github.com/ipython/ipykernel/pull/961) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#960](https://github.com/ipython/ipykernel/pull/960) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-06-15&to=2022-07-08&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-06-15..2022-07-08&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-06-15..2022-07-08&type=Issues)

## 6.15.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.14.0...5c1adcae929d8b4d28bf2b7849fe0e220c729b26))

### Bugs fixed

- Fix compatibility with tornado 6.2 beta [#956](https://github.com/ipython/ipykernel/pull/956) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Back to top-level tornado IOLoop [#958](https://github.com/ipython/ipykernel/pull/958) ([@minrk](https://github.com/minrk))
- Explicitly require pyzmq >= 17 [#957](https://github.com/ipython/ipykernel/pull/957) ([@minrk](https://github.com/minrk))
- \[pre-commit.ci\] pre-commit autoupdate [#954](https://github.com/ipython/ipykernel/pull/954) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-06-13&to=2022-06-15&type=c))

[@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2022-06-13..2022-06-15&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-06-13..2022-06-15&type=Issues)

## 6.14.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.13.1...269569787419a47da562ed69fbe6363619f3b7e5))

### Enhancements made

- Add cpu_count to the usage_reply [#952](https://github.com/ipython/ipykernel/pull/952) ([@echarles](https://github.com/echarles))

### Bugs fixed

- use pss memory info type if available for the resource usage reply [#948](https://github.com/ipython/ipykernel/pull/948) ([@echarles](https://github.com/echarles))
- Ensure psutil for the process is accurate [#937](https://github.com/ipython/ipykernel/pull/937) ([@echarles](https://github.com/echarles))

### Maintenance and upkeep improvements

- Fix sphinx 5.0 support [#951](https://github.com/ipython/ipykernel/pull/951) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#950](https://github.com/ipython/ipykernel/pull/950) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-06-06&to=2022-06-13&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-06-06..2022-06-13&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-06-06..2022-06-13&type=Issues) | [@nishikantparmariam](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Anishikantparmariam+updated%3A2022-06-06..2022-06-13&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-06-06..2022-06-13&type=Issues)

## 6.13.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.13.0...82179ef8ae4e9bdcd99a4a4c3807e8f773f1e92c))

### Bugs fixed

- Fix richInspectVariables [#943](https://github.com/ipython/ipykernel/pull/943) ([@davidbrochart](https://github.com/davidbrochart))
- Force debugger metadata in built wheel [#941](https://github.com/ipython/ipykernel/pull/941) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- \[pre-commit.ci\] pre-commit autoupdate [#945](https://github.com/ipython/ipykernel/pull/945) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Clean up typings [#939](https://github.com/ipython/ipykernel/pull/939) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#938](https://github.com/ipython/ipykernel/pull/938) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Clean up types [#933](https://github.com/ipython/ipykernel/pull/933) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#932](https://github.com/ipython/ipykernel/pull/932) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Switch to hatch backend [#931](https://github.com/ipython/ipykernel/pull/931) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#928](https://github.com/ipython/ipykernel/pull/928) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#926](https://github.com/ipython/ipykernel/pull/926) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Allow enforce PR label workflow to add labels [#921](https://github.com/ipython/ipykernel/pull/921) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#920](https://github.com/ipython/ipykernel/pull/920) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#919](https://github.com/ipython/ipykernel/pull/919) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#917](https://github.com/ipython/ipykernel/pull/917) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-04-11&to=2022-06-06&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-04-11..2022-06-06&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2022-04-11..2022-06-06&type=Issues) | [@fabioz](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afabioz+updated%3A2022-04-11..2022-06-06&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afcollonval+updated%3A2022-04-11..2022-06-06&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-04-11..2022-06-06&type=Issues)

## 6.13.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.12.1...05c6e655e497a944fd738d9b744fad90bc78b70a))

### Enhancements made

- Add the PID to the resource usage reply [#908](https://github.com/ipython/ipykernel/pull/908) ([@echarles](https://github.com/echarles))

### Bugs fixed

- Fix qtconsole spawn [#915](https://github.com/ipython/ipykernel/pull/915) ([@andia89](https://github.com/andia89))

### Maintenance and upkeep improvements

- Add basic mypy support [#913](https://github.com/ipython/ipykernel/pull/913) ([@blink1073](https://github.com/blink1073))
- Clean up pre-commit [#911](https://github.com/ipython/ipykernel/pull/911) ([@blink1073](https://github.com/blink1073))
- Update setup.py [#909](https://github.com/ipython/ipykernel/pull/909) ([@tlinhart](https://github.com/tlinhart))
- \[pre-commit.ci\] pre-commit autoupdate [#906](https://github.com/ipython/ipykernel/pull/906) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-04-04&to=2022-04-11&type=c))

[@andia89](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aandia89+updated%3A2022-04-04..2022-04-11&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-04-04..2022-04-11&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-04-04..2022-04-11&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ameeseeksdev+updated%3A2022-04-04..2022-04-11&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apre-commit-ci+updated%3A2022-04-04..2022-04-11&type=Issues) | [@tlinhart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Atlinhart+updated%3A2022-04-04..2022-04-11&type=Issues)

## 6.12.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.12.0...3a04ea3fa50d01bcc09f10e3de8bb5570c2cd619))

### Maintenance and upkeep improvements

- Clean up test deps and test setup [#904](https://github.com/ipython/ipykernel/pull/904) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-04-04&to=2022-04-04&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-04-04..2022-04-04&type=Issues)

## 6.12.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.11.0...70073edbdae17be396093be96bf880da069e7e52))

### Enhancements made

- use packaging instead of pkg_resources to parse versions [#900](https://github.com/ipython/ipykernel/pull/900) ([@minrk](https://github.com/minrk))

### Bugs fixed

- Make cell_id optional [#902](https://github.com/ipython/ipykernel/pull/902) ([@blink1073](https://github.com/blink1073))
- Do not try to send on iostream if closed [#899](https://github.com/ipython/ipykernel/pull/899) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-03-31&to=2022-04-04&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-03-31..2022-04-04&type=Issues) | [@bollwyvl](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Abollwyvl+updated%3A2022-03-31..2022-04-04&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2022-03-31..2022-04-04&type=Issues)

## 6.11.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.10.0...d8520c1c68e0e1c401ecc36e962cf369366c3707))

### Enhancements made

- Include method signatures in experimental completion results [#895](https://github.com/ipython/ipykernel/pull/895) ([@MrBago](https://github.com/MrBago))
- Try to pass cell id to executing kernel. [#886](https://github.com/ipython/ipykernel/pull/886) ([@Carreau](https://github.com/Carreau))

### Maintenance and upkeep improvements

- Handle warnings in tests [#896](https://github.com/ipython/ipykernel/pull/896) ([@blink1073](https://github.com/blink1073))
- Run flake and remove deprecated import [#894](https://github.com/ipython/ipykernel/pull/894) ([@blink1073](https://github.com/blink1073))
- Add ignore-revs file [#893](https://github.com/ipython/ipykernel/pull/893) ([@blink1073](https://github.com/blink1073))
- Autoformat with black and isort [#892](https://github.com/ipython/ipykernel/pull/892) ([@blink1073](https://github.com/blink1073))
- Add pytest opts and pre-commit [#889](https://github.com/ipython/ipykernel/pull/889) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-03-28&to=2022-03-31&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-03-28..2022-03-31&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2022-03-28..2022-03-31&type=Issues) | [@MrBago](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AMrBago+updated%3A2022-03-28..2022-03-31&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ASylvainCorlay+updated%3A2022-03-28..2022-03-31&type=Issues)

## 6.10.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.9.2...3059fd97b7ccbd72e778f123bfb0ad92e7d9e9c8))

### Enhancements made

- Improve performance of stderr and stdout stream buffer [#888](https://github.com/ipython/ipykernel/pull/888) ([@MrBago](https://github.com/MrBago))

### Bugs fixed

- Check if the current thread is the io thread [#884](https://github.com/ipython/ipykernel/pull/884) ([@jamadeo](https://github.com/jamadeo))

### Maintenance and upkeep improvements

- More CI cleanup [#887](https://github.com/ipython/ipykernel/pull/887) ([@blink1073](https://github.com/blink1073))
- CI cleanup [#885](https://github.com/ipython/ipykernel/pull/885) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add precision about subprocess stdout/stderr capturing [#883](https://github.com/ipython/ipykernel/pull/883) ([@lesteve](https://github.com/lesteve))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-03-14&to=2022-03-28&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-03-14..2022-03-28&type=Issues) | [@jamadeo](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajamadeo+updated%3A2022-03-14..2022-03-28&type=Issues) | [@lesteve](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Alesteve+updated%3A2022-03-14..2022-03-28&type=Issues) | [@MrBago](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AMrBago+updated%3A2022-03-14..2022-03-28&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ASylvainCorlay+updated%3A2022-03-14..2022-03-28&type=Issues)

## 6.9.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.9.1...d6744f9e423dacc6b317b1d31805304e89cbec5d))

### Bugs fixed

- Catch error when shutting down kernel from the control channel [#877](https://github.com/ipython/ipykernel/pull/877) ([@ccordoba12](https://github.com/ccordoba12))
- Only kill children in process group at shutdown [#874](https://github.com/ipython/ipykernel/pull/874) ([@minrk](https://github.com/minrk))
- BUG: Kill subprocesses on shutdown. [#869](https://github.com/ipython/ipykernel/pull/869) ([@Carreau](https://github.com/Carreau))

### Maintenance and upkeep improvements

- Clean up CI [#871](https://github.com/ipython/ipykernel/pull/871) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-02-15&to=2022-03-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-02-15..2022-03-14&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2022-02-15..2022-03-14&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2022-02-15..2022-03-14&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-02-15..2022-03-14&type=Issues) | [@fabioz](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afabioz+updated%3A2022-02-15..2022-03-14&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2022-02-15..2022-03-14&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Avidartf+updated%3A2022-02-15..2022-03-14&type=Issues)

## 6.9.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.9.0...c27e5b95c3d104d9fb6cae3375aec0e98974dcff))

### Bugs fixed

- Add hostname to the usage reply [#865](https://github.com/ipython/ipykernel/pull/865) ([@echarles](https://github.com/echarles))
- Enable standard library debugging via config [#863](https://github.com/ipython/ipykernel/pull/863) ([@echarles](https://github.com/echarles))
- process_one only accepts coroutines for dispatch [#861](https://github.com/ipython/ipykernel/pull/861) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-02-07&to=2022-02-15&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-02-07..2022-02-15&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-02-07..2022-02-15&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2022-02-07..2022-02-15&type=Issues)

## 6.9.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.8.0...7a229c6c83d44d315f637ef63159a43c64ec73d6))

### Bugs fixed

- Fixed event forwarding [#855](https://github.com/ipython/ipykernel/pull/855) ([@JohanMabille](https://github.com/JohanMabille))
- use message queue for abort_queues [#853](https://github.com/ipython/ipykernel/pull/853) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-02-01&to=2022-02-07&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-02-01..2022-02-07&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2022-02-01..2022-02-07&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2022-02-01..2022-02-07&type=Issues)

## 6.8.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.7.0...4e775b70e7e1be7e96fe7c3c747f21f3d93f0181))

### Enhancements made

- Add support for the debug modules request [#816](https://github.com/ipython/ipykernel/pull/816) ([@echarles](https://github.com/echarles))

### Bugs fixed

- Handle all threads stopped correctly [#849](https://github.com/ipython/ipykernel/pull/849) ([@JohanMabille](https://github.com/JohanMabille))
- Fix the debug modules model [#848](https://github.com/ipython/ipykernel/pull/848) ([@echarles](https://github.com/echarles))
- Handled AllThreadsContinued and workaround for wrong threadId in cont… [#844](https://github.com/ipython/ipykernel/pull/844) ([@JohanMabille](https://github.com/JohanMabille))

### Maintenance and upkeep improvements

- Cancel duplicate runs [#850](https://github.com/ipython/ipykernel/pull/850) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-01-13&to=2022-02-01&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2022-01-13..2022-02-01&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-01-13..2022-02-01&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2022-01-13..2022-02-01&type=Issues)

## 6.7.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.6.1...0be80cbc81927f4fb20343840bf5834b48884717))

### Enhancements made

- Add usage_request and usage_reply based on psutil [#805](https://github.com/ipython/ipykernel/pull/805) ([@echarles](https://github.com/echarles))

### Bugs fixed

- Removed DebugStdLib from arguments of attach [#839](https://github.com/ipython/ipykernel/pull/839) ([@JohanMabille](https://github.com/JohanMabille))
- Normalize debugger temp file paths on Windows [#838](https://github.com/ipython/ipykernel/pull/838) ([@kycutler](https://github.com/kycutler))
- Breakpoint in cell with leading empty lines may be ignored [#829](https://github.com/ipython/ipykernel/pull/829) ([@fcollonval](https://github.com/fcollonval))

### Maintenance and upkeep improvements

- Skip on PyPy, seem to fail. [#837](https://github.com/ipython/ipykernel/pull/837) ([@Carreau](https://github.com/Carreau))
- Remove pipx to fix conflicts [#835](https://github.com/ipython/ipykernel/pull/835) ([@Carreau](https://github.com/Carreau))
- Remove impossible skipif. [#834](https://github.com/ipython/ipykernel/pull/834) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2022-01-03&to=2022-01-13&type=c))

[@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2022-01-03..2022-01-13&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2022-01-03..2022-01-13&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afcollonval+updated%3A2022-01-03..2022-01-13&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2022-01-03..2022-01-13&type=Issues) | [@kycutler](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akycutler+updated%3A2022-01-03..2022-01-13&type=Issues)

## 6.6.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.6.0...bdce14b32ca8cc8f4b1635ea47200f0828ec1e05))

### Bugs fixed

- PR: do_one_iteration is a coroutine [#830](https://github.com/ipython/ipykernel/pull/830) ([@impact27](https://github.com/impact27))

### Maintenance and upkeep improvements

- Clean python 2 artifacts. Fix #826 [#827](https://github.com/ipython/ipykernel/pull/827) ([@penguinolog](https://github.com/penguinolog))

### Documentation improvements

- Fix title position in changelog [#828](https://github.com/ipython/ipykernel/pull/828) ([@fcollonval](https://github.com/fcollonval))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-12-01&to=2022-01-03&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2021-12-01..2022-01-03&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2021-12-01..2022-01-03&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afcollonval+updated%3A2021-12-01..2022-01-03&type=Issues) | [@impact27](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aimpact27+updated%3A2021-12-01..2022-01-03&type=Issues) | [@ivanov](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aivanov+updated%3A2021-12-01..2022-01-03&type=Issues) | [@penguinolog](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apenguinolog+updated%3A2021-12-01..2022-01-03&type=Issues)

## 6.6.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.5.1...9566304175d844c23a1f2b1d70c10df475ed2868))

### Enhancements made

- Set `debugOptions` for breakpoints in python standard library source [#812](https://github.com/ipython/ipykernel/pull/812) ([@echarles](https://github.com/echarles))
- Send `omit_sections` to IPython to choose which sections of documentation you do not want [#809](https://github.com/ipython/ipykernel/pull/809) ([@fasiha](https://github.com/fasiha))

### Bugs fixed

- Added missing `exceptionPaths` field to `debugInfo` reply [#814](https://github.com/ipython/ipykernel/pull/814) ([@JohanMabille](https://github.com/JohanMabille))

### Maintenance and upkeep improvements

- Test `jupyter_kernel_test` as downstream [#813](https://github.com/ipython/ipykernel/pull/813) ([@blink1073](https://github.com/blink1073))
- Remove `nose` dependency [#808](https://github.com/ipython/ipykernel/pull/808) ([@Kojoley](https://github.com/Kojoley))
- Add explicit encoding to open calls in debugger [#807](https://github.com/ipython/ipykernel/pull/807) ([@dlukes](https://github.com/dlukes))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-11-18&to=2021-12-01&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2021-11-18..2021-12-01&type=Issues) | [@dlukes](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adlukes+updated%3A2021-11-18..2021-12-01&type=Issues) | [@echarles](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aecharles+updated%3A2021-11-18..2021-12-01&type=Issues) | [@fasiha](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afasiha+updated%3A2021-11-18..2021-12-01&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2021-11-18..2021-12-01&type=Issues) | [@Kojoley](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AKojoley+updated%3A2021-11-18..2021-12-01&type=Issues)

## 6.5.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.5.0...1ef2017781435d54348fbb170b8c5d096e3e1351))

### Bugs fixed

- Fix the temp file name created by the debugger [#801](https://github.com/ipython/ipykernel/pull/801) ([@eastonsuo](https://github.com/eastonsuo))

### Maintenance and upkeep improvements

- Enforce labels on PRs [#803](https://github.com/ipython/ipykernel/pull/803) ([@blink1073](https://github.com/blink1073))
- Unpin `IPython`, and remove some dependencies on it. [#796](https://github.com/ipython/ipykernel/pull/796) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-11-01&to=2021-11-18&type=c))

[@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2021-11-01..2021-11-18&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2021-11-01..2021-11-18&type=Issues) | [@eastonsuo](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aeastonsuo+updated%3A2021-11-01..2021-11-18&type=Issues)

## 6.5.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.4.2...e8d4f66e0f65e284aab444c53e9812dbbc814cb2))

### Bugs fixed

- Fix rich variables inspection [#793](https://github.com/ipython/ipykernel/pull/793) ([@fcollonval](https://github.com/fcollonval))
- Do not call `setQuitOnLastWindowClosed()` on a `QCoreApplication` [#791](https://github.com/ipython/ipykernel/pull/791) ([@stukowski](https://github.com/stukowski))

### Maintenance and upkeep improvements

- Drop `ipython_genutils` requirement [#792](https://github.com/ipython/ipykernel/pull/792) ([@penguinolog](https://github.com/penguinolog))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-10-20&to=2021-11-01&type=c))

[@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2021-10-20..2021-11-01&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afcollonval+updated%3A2021-10-20..2021-11-01&type=Issues) | [@penguinolog](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apenguinolog+updated%3A2021-10-20..2021-11-01&type=Issues) | [@stukowski](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Astukowski+updated%3A2021-10-20..2021-11-01&type=Issues)

## 6.4.2

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.4.1...231fd3c65f8a15e9e015546c0a6846e22df9ba2a))

### Enhancements made

- Enabled rich rendering of variables in the debugger [#787](https://github.com/ipython/ipykernel/pull/787) ([@JohanMabille](https://github.com/JohanMabille))

### Bugs fixed

- Remove setting of the eventloop function in the InProcessKernel [#781](https://github.com/ipython/ipykernel/pull/781) ([@rayosborn](https://github.com/rayosborn))

### Maintenance and upkeep improvements

- Add python version classifiers [#783](https://github.com/ipython/ipykernel/pull/783) ([@emuccino](https://github.com/emuccino))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-09-10&to=2021-10-19&type=c))

[@emuccino](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aemuccino+updated%3A2021-09-10..2021-10-19&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2021-09-10..2021-10-19&type=Issues) | [@rayosborn](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Arayosborn+updated%3A2021-09-10..2021-10-19&type=Issues)

## 6.4.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.4.0...4da7623c1ae733f32c0792d70e7af283a7b19d22))

### Merged PRs

- debugpy is now a build requirement [#773](https://github.com/ipython/ipykernel/pull/773) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-09-09&to=2021-09-10&type=c))

[@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2021-09-09..2021-09-10&type=Issues)

## 6.4.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.3.1...1ba6b48a97877ff7a564af32c531618efb7d2a57))

### Enhancements made

- Make `json_clean` a no-op for `jupyter-client` >= 7 [#708](https://github.com/ipython/ipykernel/pull/708) ([@martinRenou](https://github.com/martinRenou))

### Bugs fixed

- Do not assume kernels have loops [#766](https://github.com/ipython/ipykernel/pull/766) ([@Carreau](https://github.com/Carreau))
- Fix undefined variable [#765](https://github.com/ipython/ipykernel/pull/765) ([@martinRenou](https://github.com/martinRenou))

### Maintenance and upkeep improvements

- Make `ipykernel` work without `debugpy` [#767](https://github.com/ipython/ipykernel/pull/767) ([@frenzymadness](https://github.com/frenzymadness))
- Stop using deprecated `recv_multipart` when using in-process socket. [#762](https://github.com/ipython/ipykernel/pull/762) ([@Carreau](https://github.com/Carreau))
- Update some warnings with instructions and version number. [#761](https://github.com/ipython/ipykernel/pull/761) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-08-31&to=2021-09-09&type=c))

[@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2021-08-31..2021-09-09&type=Issues) | [@frenzymadness](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Afrenzymadness+updated%3A2021-08-31..2021-09-09&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AmartinRenou+updated%3A2021-08-31..2021-09-09&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2021-08-31..2021-09-09&type=Issues)

## 6.3

## 6.3.1

([Full Changelog](https://github.com/ipython/ipykernel/compare/v6.3.0...0b4a8eaa080fc11e240ada9c44c95841463da58c))

### Merged PRs

- Add dependency on IPython genutils. [#756](https://github.com/ipython/ipykernel/pull/756) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-08-30&to=2021-08-31&type=c))

[@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2021-08-30..2021-08-31&type=Issues)

## 6.3.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/6.2.0...07af2633ca88eda583e13649279a5b98473618a2))

### Enhancements made

- Add deep variable inspection [#753](https://github.com/ipython/ipykernel/pull/753) ([@JohanMabille](https://github.com/JohanMabille))
- Add `IPKernelApp.capture_fd_output` config to disable FD-level capture [#752](https://github.com/ipython/ipykernel/pull/752) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Remove more `nose` test references [#750](https://github.com/ipython/ipykernel/pull/750) ([@blink1073](https://github.com/blink1073))
- Remove `nose` `skipIf` in favor of `pytest` [#748](https://github.com/ipython/ipykernel/pull/748) ([@Carreau](https://github.com/Carreau))
- Remove more `nose` [#747](https://github.com/ipython/ipykernel/pull/747) ([@Carreau](https://github.com/Carreau))
- Set up release helper plumbing [#745](https://github.com/ipython/ipykernel/pull/745) ([@afshin](https://github.com/afshin))
- Test downstream projects [#635](https://github.com/ipython/ipykernel/pull/635) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-08-16&to=2021-08-30&type=c))

[@afshin](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aafshin+updated%3A2021-08-16..2021-08-30&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2021-08-16..2021-08-30&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2021-08-16..2021-08-30&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2021-08-16..2021-08-30&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2021-08-16..2021-08-30&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2021-08-16..2021-08-30&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akevin-bates+updated%3A2021-08-16..2021-08-30&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2021-08-16..2021-08-30&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ASylvainCorlay+updated%3A2021-08-16..2021-08-30&type=Issues)

## 6.2

## 6.2.0

### Enhancements made

- Add Support for Message Based Interrupt [#741](https://github.com/ipython/ipykernel/pull/741) ([@afshin](https://github.com/afshin))

### Maintenance and upkeep improvements

- Remove some more dependency on nose/iptest [#743](https://github.com/ipython/ipykernel/pull/743) ([@Carreau](https://github.com/Carreau))
- Remove block param from get_msg() [#736](https://github.com/ipython/ipykernel/pull/736) ([@davidbrochart](https://github.com/davidbrochart))

## 6.1

## 6.1.0

### Enhancements made

- Implemented `richInspectVariable` request handler [#734](https://github.com/ipython/ipykernel/pull/734) ([@JohanMabille](https://github.com/JohanMabille))

### Maintenance and upkeep improvements

- Bump `importlib-metadata` limit for `python<3.8` [#738](https://github.com/ipython/ipykernel/pull/738) ([@ltalirz](https://github.com/ltalirz))

### Bug Fixes

- Fix exception raised by `OutStream.write` [#726](https://github.com/ipython/ipykernel/pull/726) ([@SimonKrughoff](https://github.com/SimonKrughoff))

## 6.0

## 6.0.3

- `KernelApp`: rename ports variable to avoid override [#731](https://github.com/ipython/ipykernel/pull/731) ([@amorenoz](https://github.com/amorenoz))

## 6.0.2

### Bugs fixed

- Add watchfd keyword to InProcessKernel OutStream initialization [#727](https://github.com/ipython/ipykernel/pull/727) ([@rayosborn](https://github.com/rayosborn))
- Fix typo in eventloops.py [#711](https://github.com/ipython/ipykernel/pull/711) ([@selasley](https://github.com/selasley))
- \[bugfix\] fix in setup.py (comma before appnope) [#709](https://github.com/ipython/ipykernel/pull/709) ([@jstriebel](https://github.com/jstriebel))

### Maintenance and upkeep improvements

- Add upper bound to dependency versions. [#714](https://github.com/ipython/ipykernel/pull/714) ([@martinRenou](https://github.com/martinRenou))
- Replace non-existing function. [#723](https://github.com/ipython/ipykernel/pull/723) ([@Carreau](https://github.com/Carreau))
- Remove unused variables [#722](https://github.com/ipython/ipykernel/pull/722) ([@Carreau](https://github.com/Carreau))
- Do not use bare except [#721](https://github.com/ipython/ipykernel/pull/721) ([@Carreau](https://github.com/Carreau))
- misc whitespace and line too long [#720](https://github.com/ipython/ipykernel/pull/720) ([@Carreau](https://github.com/Carreau))
- Formatting: remove semicolon [#719](https://github.com/ipython/ipykernel/pull/719) ([@Carreau](https://github.com/Carreau))
- Clean most flake8 unused import warnings. [#718](https://github.com/ipython/ipykernel/pull/718) ([@Carreau](https://github.com/Carreau))
- Minimal flake8 config [#717](https://github.com/ipython/ipykernel/pull/717) ([@Carreau](https://github.com/Carreau))
- Remove CachingCompiler's filename_mapper [#710](https://github.com/ipython/ipykernel/pull/710) ([@martinRenou](https://github.com/martinRenou))

## 6.0.1

- Fix Tk and asyncio event loops [#704](https://github.com/ipython/ipykernel/pull/704) ([@ccordoba12](https://github.com/ccordoba12))
- Stringify variables that are not json serializable in inspectVariable [#702](https://github.com/ipython/ipykernel/pull/702) ([@JohanMabille](https://github.com/JohanMabille))

## 6.0.0

([Full Changelog](https://github.com/ipython/ipykernel/compare/aba2179420a3fa81ee6b8a13f928bf9e5ce50716...6d04ad2bdccd0dc0daf20f8d53555174b5fefc7b))

IPykernel 6.0 is the first major release in about two years, that brings a number of improvements, code cleanup, and new
features to IPython.

You should be able to view all closed issues and merged Pull Request for this
milestone [on
GitHub](https://github.com/ipython/ipykernel/issues?q=milestone%3A6.0+is%3Aclosed+),
as for any major releases, we advise greater care when updating that for minor
release and welcome any feedback (~50 Pull-requests).

IPykernel 6 should contain all changes of the 5.x series, in addition to the
following non-exhaustive changes.

- Support for the debugger protocol, when using `JupyterLab`, `RetroLab` or any
  frontend supporting the debugger protocol you should have access to the
  debugger functionalities.

- The control channel on IPykernel 6.0 is run in a separate thread, this may
  change the order in which messages are processed, though this change was necessary
  to accommodate the debugger.

- We now have a new dependency: `matplotlib-inline`, this helps to separate the
  circular dependency between IPython/IPykernel and matplotlib.

- On POSIX systems, all outputs to stdout/stderr should now be captured,
  including subprocesses and output of compiled libraries (blas, lapack....).
  In notebook server, some outputs that would previously go to the notebooks
  logs will now both head to notebook logs and in notebooks outputs. In
  terminal frontend like Jupyter Console, Emacs or other, this may ends up as
  duplicated outputs.

- coroutines are now native (async-def) , instead of using tornado's
  `@gen.coroutine`

- OutStreams can now be configured to report `istty() == True`, while this
  should make some output nicer (for example colored), it is likely to break
  others. Use with care.

### New features added

- Implementation of the debugger [#597](https://github.com/ipython/ipykernel/pull/597) ([@JohanMabille](https://github.com/JohanMabille))

### Enhancements made

- Make the `isatty` method of `OutStream` return `true` [#683](https://github.com/ipython/ipykernel/pull/683) ([@peendebak](https://github.com/peendebak))
- Allow setting cell name [#652](https://github.com/ipython/ipykernel/pull/652) ([@davidbrochart](https://github.com/davidbrochart))
- Try to capture all file descriptor output and err [#630](https://github.com/ipython/ipykernel/pull/630) ([@Carreau](https://github.com/Carreau))
- Implemented `inspectVariables` request [#624](https://github.com/ipython/ipykernel/pull/624) ([@JohanMabille](https://github.com/JohanMabille))
- Specify `ipykernel` in kernelspec [#616](https://github.com/ipython/ipykernel/pull/616) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Use `matplotlib-inline` [#591](https://github.com/ipython/ipykernel/pull/591) ([@martinRenou](https://github.com/martinRenou))
- Run control channel in separate thread [#585](https://github.com/ipython/ipykernel/pull/585) ([@SylvainCorlay](https://github.com/SylvainCorlay))

### Bugs fixed

- Remove references to deprecated `ipyparallel` [#695](https://github.com/ipython/ipykernel/pull/695) ([@minrk](https://github.com/minrk))
- Return len of item written to `OutStream` [#685](https://github.com/ipython/ipykernel/pull/685) ([@Carreau](https://github.com/Carreau))
- Call metadata methods on abort replies [#684](https://github.com/ipython/ipykernel/pull/684) ([@minrk](https://github.com/minrk))
- Fix keyboard interrupt issue in `dispatch_shell` [#673](https://github.com/ipython/ipykernel/pull/673) ([@marcoamonteiro](https://github.com/marcoamonteiro))
- Update `Trio` mode for compatibility with `Trio >= 0.18.0` [#627](https://github.com/ipython/ipykernel/pull/627) ([@mehaase](https://github.com/mehaase))
- Follow up `DeprecationWarning` Fix [#617](https://github.com/ipython/ipykernel/pull/617) ([@afshin](https://github.com/afshin))
- Flush control stream upon shutdown [#611](https://github.com/ipython/ipykernel/pull/611) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Fix Handling of `shell.should_run_async` [#605](https://github.com/ipython/ipykernel/pull/605) ([@afshin](https://github.com/afshin))
- Deacrease lag time for eventloop [#573](https://github.com/ipython/ipykernel/pull/573) ([@impact27](https://github.com/impact27))
- Fix "Socket operation on nonsocket" in downstream `nbclient` test. [#641](https://github.com/ipython/ipykernel/pull/641) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Stop control thread before closing sockets on it [#659](https://github.com/ipython/ipykernel/pull/659) ([@minrk](https://github.com/minrk))
- Fix debugging with native coroutines [#651](https://github.com/ipython/ipykernel/pull/651) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Fixup master build [#649](https://github.com/ipython/ipykernel/pull/649) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Fix parent header retrieval [#639](https://github.com/ipython/ipykernel/pull/639) ([@davidbrochart](https://github.com/davidbrochart))
- Add missing self [#636](https://github.com/ipython/ipykernel/pull/636) ([@Carreau](https://github.com/Carreau))
- Backwards compat with older versions of zmq [#665](https://github.com/ipython/ipykernel/pull/665) ([@mlucool](https://github.com/mlucool))

### Maintenance and upkeep improvements

- Remove pin on Jedi because that was already fixed in IPython [#692](https://github.com/ipython/ipykernel/pull/692) ([@ccordoba12](https://github.com/ccordoba12))
- Remove deprecated source parameter since 4.0.1 (2015) [#690](https://github.com/ipython/ipykernel/pull/690) ([@Carreau](https://github.com/Carreau))
- Remove deprecated `SocketABC` since 4.5.0 [#689](https://github.com/ipython/ipykernel/pull/689) ([@Carreau](https://github.com/Carreau))
- Remove deprecated profile options of `connect.py` [#688](https://github.com/ipython/ipykernel/pull/688) ([@Carreau](https://github.com/Carreau))
- Remove `ipykernel.codeutil` deprecated since IPykernel 4.3.1 (Feb 2016) [#687](https://github.com/ipython/ipykernel/pull/687) ([@Carreau](https://github.com/Carreau))
- Keep preferring `SelectorEventLoop` on Windows [#669](https://github.com/ipython/ipykernel/pull/669) ([@minrk](https://github.com/minrk))
- Add `Kernel.get_parent` to match `set_parent` [#661](https://github.com/ipython/ipykernel/pull/661) ([@minrk](https://github.com/minrk))
- Flush control queue prior to handling shell messages [#658](https://github.com/ipython/ipykernel/pull/658) ([@minrk](https://github.com/minrk))
- Add `Kernel.get_parent_header` [#657](https://github.com/ipython/ipykernel/pull/657) ([@minrk](https://github.com/minrk))
- Build docs only on Ubuntu: add jobs to check docstring formatting. [#644](https://github.com/ipython/ipykernel/pull/644) ([@Carreau](https://github.com/Carreau))
- Make deprecated `shell_streams` writable [#638](https://github.com/ipython/ipykernel/pull/638) ([@minrk](https://github.com/minrk))
- Use channel `get_msg` helper method [#634](https://github.com/ipython/ipykernel/pull/634) ([@davidbrochart](https://github.com/davidbrochart))
- Use native coroutines instead of tornado coroutines [#632](https://github.com/ipython/ipykernel/pull/632) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Make less use of `ipython_genutils` [#631](https://github.com/ipython/ipykernel/pull/631) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Run GitHub Actions on all branches [#625](https://github.com/ipython/ipykernel/pull/625) ([@afshin](https://github.com/afshin))
- Move Python-specific bits to ipkernel [#610](https://github.com/ipython/ipykernel/pull/610) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Update Python Requirement to 3.7 [#608](https://github.com/ipython/ipykernel/pull/608) ([@afshin](https://github.com/afshin))
- Replace import item from `ipython_genutils` to traitlets. [#601](https://github.com/ipython/ipykernel/pull/601) ([@Carreau](https://github.com/Carreau))
- Some removal of `ipython_genutils.py3compat`. [#600](https://github.com/ipython/ipykernel/pull/600) ([@Carreau](https://github.com/Carreau))
- Fixup `get_parent_header` call [#662](https://github.com/ipython/ipykernel/pull/662) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Update of `ZMQInteractiveshell`. [#643](https://github.com/ipython/ipykernel/pull/643) ([@Carreau](https://github.com/Carreau))
- Removed filtering of stack frames for testing [#633](https://github.com/ipython/ipykernel/pull/633) ([@JohanMabille](https://github.com/JohanMabille))
- Added 'type' field to variables returned by `inspectVariables` request [#628](https://github.com/ipython/ipykernel/pull/628) ([@JohanMabille](https://github.com/JohanMabille))
- Changed default timeout to 0.0 seconds for `stop_on_error_timeout` [#618](https://github.com/ipython/ipykernel/pull/618) ([@MSeal](https://github.com/MSeal))
- Attempt longer timeout [#615](https://github.com/ipython/ipykernel/pull/615) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Clean up release process and add tests [#596](https://github.com/ipython/ipykernel/pull/596) ([@afshin](https://github.com/afshin))
- Kernelspec: ensure path is writable before writing `kernel.json`. [#593](https://github.com/ipython/ipykernel/pull/593) ([@jellelicht](https://github.com/jellelicht))
- Add `configure_inline_support` and call it in the shell [#590](https://github.com/ipython/ipykernel/pull/590) ([@martinRenou](https://github.com/martinRenou))

### Documentation improvements

- Misc Updates to changelog for 6.0 [#686](https://github.com/ipython/ipykernel/pull/686) ([@Carreau](https://github.com/Carreau))
- Add 5.5.x Changelog entries [#672](https://github.com/ipython/ipykernel/pull/672) ([@blink1073](https://github.com/blink1073))
- Build docs only on ubuntu: add jobs to check docstring formatting. [#644](https://github.com/ipython/ipykernel/pull/644) ([@Carreau](https://github.com/Carreau))
- DOC: Autoreformat all docstrings. [#642](https://github.com/ipython/ipykernel/pull/642) ([@Carreau](https://github.com/Carreau))
- Bump Python to 3.8 in `readthedocs.yml` [#612](https://github.com/ipython/ipykernel/pull/612) ([@minrk](https://github.com/minrk))
- Fix typo [#663](https://github.com/ipython/ipykernel/pull/663) ([@SylvainCorlay](https://github.com/SylvainCorlay))
- Add release note to 5.5.0 about `stop_on_error_timeout` [#613](https://github.com/ipython/ipykernel/pull/613) ([@glentakahashi](https://github.com/glentakahashi))
- Move changelog to standard location [#604](https://github.com/ipython/ipykernel/pull/604) ([@afshin](https://github.com/afshin))
- Add changelog for 5.5 [#594](https://github.com/ipython/ipykernel/pull/594) ([@blink1073](https://github.com/blink1073))
- Change to markdown for changelog [#595](https://github.com/ipython/ipykernel/pull/595) ([@afshin](https://github.com/afshin))

### Deprecations in 6.0

- `Kernel`s now support only a single shell stream, multiple streams will now be ignored. The attribute
  `Kernel.shell_streams` (plural) is deprecated in ipykernel 6.0. Use `Kernel.shell_stream` (singular)
- `Kernel._parent_header` is deprecated, even though it was private. Use `.get_parent()` now.

### Removal in 6.0

- `ipykernel.codeutils` was deprecated since 4.x series (2016) and has been removed, please import similar
  functionalities from `ipyparallel`
- remove `find_connection_file` and `profile` argument of `connect_qtconsole` and `get_connection_info`, deprecated since IPykernel 4.2.2 (2016).

### Contributors to this release

([GitHub contributors page for this release](https://github.com/ipython/ipykernel/graphs/contributors?from=2021-01-11&to=2021-06-29&type=c))

[@afshin](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aafshin+updated%3A2021-01-11..2021-06-29&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ablink1073+updated%3A2021-01-11..2021-06-29&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ACarreau+updated%3A2021-01-11..2021-06-29&type=Issues) | [@ccordoba12](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Accordoba12+updated%3A2021-01-11..2021-06-29&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adavidbrochart+updated%3A2021-01-11..2021-06-29&type=Issues) | [@dsblank](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Adsblank+updated%3A2021-01-11..2021-06-29&type=Issues) | [@glentakahashi](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aglentakahashi+updated%3A2021-01-11..2021-06-29&type=Issues) | [@impact27](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aimpact27+updated%3A2021-01-11..2021-06-29&type=Issues) | [@ivanov](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aivanov+updated%3A2021-01-11..2021-06-29&type=Issues) | [@jellelicht](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajellelicht+updated%3A2021-01-11..2021-06-29&type=Issues) | [@jkablan](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Ajkablan+updated%3A2021-01-11..2021-06-29&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AJohanMabille+updated%3A2021-01-11..2021-06-29&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Akevin-bates+updated%3A2021-01-11..2021-06-29&type=Issues) | [@marcoamonteiro](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amarcoamonteiro+updated%3A2021-01-11..2021-06-29&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AmartinRenou+updated%3A2021-01-11..2021-06-29&type=Issues) | [@mehaase](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amehaase+updated%3A2021-01-11..2021-06-29&type=Issues) | [@minrk](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Aminrk+updated%3A2021-01-11..2021-06-29&type=Issues) | [@mlucool](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Amlucool+updated%3A2021-01-11..2021-06-29&type=Issues) | [@MSeal](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3AMSeal+updated%3A2021-01-11..2021-06-29&type=Issues) | [@peendebak](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Apeendebak+updated%3A2021-01-11..2021-06-29&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3ASylvainCorlay+updated%3A2021-01-11..2021-06-29&type=Issues) | [@tacaswell](https://github.com/search?q=repo%3Aipython%2Fipykernel+involves%3Atacaswell+updated%3A2021-01-11..2021-06-29&type=Issues)

## 5.5

### 5.5.5

- Keep preferring SelectorEventLoop on Windows. [#669](https://github.com/ipython/ipykernel/pull/669)

### 5.5.4

- Import `configure_inline_support` from `matplotlib_inline` if available [#654](https://github.com/ipython/ipykernel/pull/654)

### 5.5.3

- Revert Backport of #605: Fix Handling of `shell.should_run_async` [#622](https://github.com/ipython/ipykernel/pull/622)

### 5.5.2

**Note:** This release was deleted from PyPI since it had breaking changes.

- Changed default timeout to 0.0 seconds for stop_on_error_timeout. [#618](https://github.com/ipython/ipykernel/pull/618)

### 5.5.1

**Note:** This release was deleted from PyPI since it had breaking changes.

- Fix Handling of `shell.should_run_async`. [#605](https://github.com/ipython/ipykernel/pull/605)

### 5.5.0

- kernelspec: ensure path is writable before writing `kernel.json`. [#593](https://github.com/ipython/ipykernel/pull/593)
- Add `configure_inline_support` and call it in the shell. [#590](https://github.com/ipython/ipykernel/pull/590)
- Fix `stop_on_error_timeout` to now properly abort `execute_request`'s that fall within the timeout after an error. [#572](https://github.com/ipython/ipykernel/pull/572)

## 5.4

### 5.4.3

- Rework `wait_for_ready` logic. [#578](https://github.com/ipython/ipykernel/pull/578)

### 5.4.2

- Revert "Fix stop_on_error_timeout blocking other messages in
  queue". [#570](https://github.com/ipython/ipykernel/pull/570)

### 5.4.1

- Invalid syntax in `ipykernel/log.py`. [#567](https://github.com/ipython/ipykernel/pull/567)

### 5.4.0

5.4.0 is generally focused on code quality improvements and tornado
asyncio compatibility.

- Add github actions, bail on asyncio patch for tornado 6.1.
  [#564](https://github.com/ipython/ipykernel/pull/564)
- Start testing on Python 3.9. [#551](https://github.com/ipython/ipykernel/pull/551)
- Fix stack levels for ipykernel's deprecation warnings and stop
  using some deprecated APIs. [#547](https://github.com/ipython/ipykernel/pull/547)
- Add env parameter to kernel installation [#541](https://github.com/ipython/ipykernel/pull/541)
- Fix stop_on_error_timeout blocking other messages in queue.
  [#539](https://github.com/ipython/ipykernel/pull/539)
- Remove most of the python 2 compat code. [#537](https://github.com/ipython/ipykernel/pull/537)
- Remove u-prefix from strings. [#538](https://github.com/ipython/ipykernel/pull/538)

## 5.3

### 5.3.4

- Only run Qt eventloop in the shell stream. [#531](https://github.com/ipython/ipykernel/pull/531)

### 5.3.3

- Fix QSocketNotifier in the Qt event loop not being disabled for the
  control channel. [#525](https://github.com/ipython/ipykernel/pull/525)

### 5.3.2

- Restore timer based event loop as a Windows-compatible fallback.
  [#523](https://github.com/ipython/ipykernel/pull/523)

### 5.3.1

- Fix #520: run post_execute and post_run_cell on async cells
  [#521](https://github.com/ipython/ipykernel/pull/521)
- Fix exception causes in zmqshell.py [#516](https://github.com/ipython/ipykernel/pull/516)
- Make pdb on Windows interruptible [#490](https://github.com/ipython/ipykernel/pull/490)

### 5.3.0

5.3.0 Adds support for Trio event loops and has some bug fixes.

- Fix ipython display imports [#509](https://github.com/ipython/ipykernel/pull/509)
- Skip test_unc_paths if OS is not Windows [#507](https://github.com/ipython/ipykernel/pull/507)
- Allow interrupting input() on Windows, as part of effort to make pdb
  interruptible [#498](https://github.com/ipython/ipykernel/pull/498)
- Add Trio Loop [#479](https://github.com/ipython/ipykernel/pull/479)
- Flush from process even without newline [#478](https://github.com/ipython/ipykernel/pull/478)

## 5.2

### 5.2.1

- Handle system commands that use UNC paths on Windows
  [#500](https://github.com/ipython/ipykernel/pull/500)
- Add offset argument to seek in io test [#496](https://github.com/ipython/ipykernel/pull/496)

### 5.2.0

5.2.0 Includes several bugfixes and internal logic improvements.

- Produce better traceback when kernel is interrupted
  [#491](https://github.com/ipython/ipykernel/pull/491)
- Add `InProcessKernelClient.control_channel` for compatibility with
  jupyter-client v6.0.0 [#489](https://github.com/ipython/ipykernel/pull/489)
- Drop support for Python 3.4 [#483](https://github.com/ipython/ipykernel/pull/483)
- Work around issue related to Tornado with python3.8 on Windows
  ([#480](https://github.com/ipython/ipykernel/pull/480), [#481](https://github.com/ipython/ipykernel/pull/481))
- Prevent entering event loop if it is None [#464](https://github.com/ipython/ipykernel/pull/464)
- Use `shell.input_transformer_manager` when available
  [#411](https://github.com/ipython/ipykernel/pull/411)

## 5.1

### 5.1.4

5.1.4 Includes a few bugfixes, especially for compatibility with Python
3.8 on Windows.

- Fix pickle issues when using inline matplotlib backend
  [#476](https://github.com/ipython/ipykernel/pull/476)
- Fix an error during kernel shutdown [#463](https://github.com/ipython/ipykernel/pull/463)
- Fix compatibility issues with Python 3.8 ([#456](https://github.com/ipython/ipykernel/pull/456), [#461](https://github.com/ipython/ipykernel/pull/461))
- Remove some dead code ([#474](https://github.com/ipython/ipykernel/pull/474),
  [#467](https://github.com/ipython/ipykernel/pull/467))

### 5.1.3

5.1.3 Includes several bugfixes and internal logic improvements.

- Fix comm shutdown behavior by adding a `deleting` option to `close`
  which can be set to prevent registering new comm channels during
  shutdown ([#433](https://github.com/ipython/ipykernel/pull/433), [#435](https://github.com/ipython/ipykernel/pull/435))
- Fix `Heartbeat._bind_socket` to return on the first bind ([#431](https://github.com/ipython/ipykernel/pull/431))
- Moved `InProcessKernelClient.flush` to `DummySocket` ([#437](https://github.com/ipython/ipykernel/pull/437))
- Don't redirect stdout if nose machinery is not present ([#427](https://github.com/ipython/ipykernel/pull/427))
- Rename `_asyncio.py` to
  `_asyncio_utils.py` to avoid name conflicts on Python
  3.6+ ([#426](https://github.com/ipython/ipykernel/pull/426))
- Only generate kernelspec when installing or building wheel ([#425](https://github.com/ipython/ipykernel/pull/425))
- Fix priority ordering of control-channel messages in some cases
  [#443](https://github.com/ipython/ipykernel/pull/443)

### 5.1.2

5.1.2 fixes some socket-binding race conditions that caused testing
failures in nbconvert.

- Fix socket-binding race conditions ([#412](https://github.com/ipython/ipykernel/pull/412),
  [#419](https://github.com/ipython/ipykernel/pull/419))
- Add a no-op `flush` method to `DummySocket` and comply with stream
  API ([#405](https://github.com/ipython/ipykernel/pull/405))
- Update kernel version to indicate kernel v5.3 support ([#394](https://github.com/ipython/ipykernel/pull/394))
- Add testing for upcoming Python 3.8 and PEP 570 positional
  parameters ([#396](https://github.com/ipython/ipykernel/pull/396), [#408](https://github.com/ipython/ipykernel/pull/408))

### 5.1.1

5.1.1 fixes a bug that caused cells to get stuck in a busy state.

- Flush after sending replies [#390](https://github.com/ipython/ipykernel/pull/390)

### 5.1.0

5.1.0 fixes some important regressions in 5.0, especially on Windows.

[5.1.0 on GitHub](https://github.com/ipython/ipykernel/milestones/5.1)

- Fix message-ordering bug that could result in out-of-order
  executions, especially on Windows [#356](https://github.com/ipython/ipykernel/pull/356)
- Fix classifiers to indicate dropped Python 2 support
  [#354](https://github.com/ipython/ipykernel/pull/354)
- Remove some dead code [#355](https://github.com/ipython/ipykernel/pull/355)
- Support rich-media responses in `inspect_requests` (tooltips)
  [#361](https://github.com/ipython/ipykernel/pull/361)

## 5.0

### 5.0.0

[5.0.0 on GitHub](https://github.com/ipython/ipykernel/milestones/5.0)

- Drop support for Python 2. `ipykernel` 5.0 requires Python >= 3.4
- Add support for IPython's asynchronous code execution
  [#323](https://github.com/ipython/ipykernel/pull/323)
- Update release process in `CONTRIBUTING.md` [#339](https://github.com/ipython/ipykernel/pull/339)

## 4.10

[4.10 on GitHub](https://github.com/ipython/ipykernel/milestones/4.10)

- Fix compatibility with IPython 7.0 [#348](https://github.com/ipython/ipykernel/pull/348)
- Fix compatibility in cases where sys.stdout can be None
  [#344](https://github.com/ipython/ipykernel/pull/344)

## 4.9

### 4.9.0

[4.9.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.9)

- Python 3.3 is no longer supported [#336](https://github.com/ipython/ipykernel/pull/336)
- Flush stdout/stderr in KernelApp before replacing
  [#314](https://github.com/ipython/ipykernel/pull/314)
- Allow preserving stdout and stderr in KernelApp
  [#315](https://github.com/ipython/ipykernel/pull/315)
- Override writable method on OutStream [#316](https://github.com/ipython/ipykernel/pull/316)
- Add metadata to help display matplotlib figures legibly
  [#336](https://github.com/ipython/ipykernel/pull/336)

## 4.8

### 4.8.2

[4.8.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8.2)

- Fix compatibility issue with qt eventloop and pyzmq 17
  [#307](https://github.com/ipython/ipykernel/pull/307).

### 4.8.1

[4.8.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8.1)

- set zmq.ROUTER_HANDOVER socket option when available to workaround
  libzmq reconnect bug [#300](https://github.com/ipython/ipykernel/pull/300).
- Fix sdists including absolute paths for kernelspec files, which
  prevented installation from sdist on Windows
  [#306](https://github.com/ipython/ipykernel/pull/306).

### 4.8.0

[4.8.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.8)

- Cleanly shutdown integrated event loops when shutting down the
  kernel. [#290](https://github.com/ipython/ipykernel/pull/290)
- `%gui qt` now uses Qt 5 by default rather than Qt 4, following a
  similar change in terminal IPython. [#293](https://github.com/ipython/ipykernel/pull/293)
- Fix event loop integration for `asyncio` when run with Tornado 5, which uses asyncio where
  available. [#296](https://github.com/ipython/ipykernel/pull/296)

## 4.7

### 4.7.0

[4.7.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.7)

- Add event loop integration for `asyncio`.
- Use the new IPython completer API.
- Add support for displaying GIF images (mimetype `image/gif`).
- Allow the kernel to be interrupted without killing the Qt console.
- Fix `is_complete` response with cell magics.
- Clean up encoding of bytes objects.
- Clean up help links to use `https` and improve display titles.
- Clean up ioloop handling in preparation for tornado 5.

## 4.6

### 4.6.1

[4.6.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.6.1)

- Fix eventloop-integration bug preventing Qt windows/widgets from
  displaying with ipykernel 4.6.0 and IPython ≥ 5.2.
- Avoid deprecation warnings about naive datetimes when working with
  jupyter_client ≥ 5.0.

### 4.6.0

[4.6.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.6)

- Add to API `DisplayPublisher.publish` two new fully
  backward-compatible keyword-args:

  > - `update: bool`
  > - `transient: dict`

- Support new `transient` key in
  `display_data` messages spec for `publish`.
  For a display data message, `transient` contains data
  that shouldn't be persisted to files or documents. Add a
  `display_id` to this `transient` dict by
  `display(obj, display_id=\...)`

- Add `ipykernel_launcher` module which removes the
  current working directory from `sys.path` before
  launching the kernel. This helps to reduce the cases where the
  kernel won't start because there's a `random.py` (or
  similar) module in the current working directory.

- Add busy/idle messages on IOPub during processing of aborted
  requests

- Add active event loop setting to GUI, which enables the correct
  response to IPython's `is_event_loop_running_xxx`

- Include IPython kernelspec in wheels to reduce reliance on "native
  kernel spec" in jupyter_client

- Modify `OutStream` to inherit from
  `TextIOBase` instead of object to improve API support
  and error reporting

- Fix IPython kernel death messages at start, such as "Kernel
  Restarting..." and "Kernel appears to have died", when
  parent-poller handles PID 1

- Various bugfixes

## 4.5

### 4.5.2

[4.5.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5.2)

- Fix bug when instantiating Comms outside of the IPython kernel
  (introduced in 4.5.1).

### 4.5.1

[4.5.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5.1)

- Add missing `stream` parameter to overridden
  `getpass`
- Remove locks from iopub thread, which could cause deadlocks during
  debugging
- Fix regression where KeyboardInterrupt was treated as an aborted
  request, rather than an error
- Allow instantiating Comms outside of the IPython kernel

### 4.5.0

[4.5 on GitHub](https://github.com/ipython/ipykernel/milestones/4.5)

- Use figure.dpi instead of savefig.dpi to set DPI for inline figures
- Support ipympl matplotlib backend (requires IPython update as well
  to fully work)
- Various bugfixes, including fixes for output coming from threads,
  and `input` when called with
  non-string prompts, which stdlib allows.

## 4.4

### 4.4.1

[4.4.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.4.1)

- Fix circular import of matplotlib on Python 2 caused by the inline
  backend changes in 4.4.0.

### 4.4.0

[4.4.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.4)

- Use
  [MPLBACKEND](http://matplotlib.org/devel/coding_guide.html?highlight=mplbackend#developing-a-new-backend)
  environment variable to tell matplotlib >= 1.5 use use the inline
  backend by default. This is only done if MPLBACKEND is not already
  set and no backend has been explicitly loaded, so setting
  `MPLBACKEND=Qt4Agg` or calling `%matplotlib notebook` or
  `matplotlib.use('Agg')` will take precedence.
- Fixes for logging problems caused by 4.3, where logging could go to
  the terminal instead of the notebook.
- Add `--sys-prefix` and `--profile` arguments to
  `ipython kernel install`.
- Allow Comm (Widget) messages to be sent from background threads.
- Select inline matplotlib backend by default if `%matplotlib` magic
  or `matplotlib.use()` are not called explicitly (for matplotlib >=
  1.5).
- Fix some longstanding minor deviations from the message protocol
  (missing status: ok in a few replies, connect_reply format).
- Remove calls to NoOpContext from IPython, deprecated in 5.0.

## 4.3

### 4.3.2

- Use a nonempty dummy session key for inprocess kernels to avoid
  security warnings.

### 4.3.1

- Fix Windows Python 3.5 incompatibility caused by faulthandler patch
  in 4.3

### 4.3.0

[4.3.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.3)

- Publish all IO in a thread, via `IOPubThread`. This solves the problem of requiring
  `sys.stdout.flush` to be called in
  the notebook to produce output promptly during long-running cells.

- Remove references to outdated IPython guiref in kernel banner.

- Patch faulthandler to use `sys.__stderr__` instead of forwarded
  `sys.stderr`, which has no fileno when forwarded.

- Deprecate some vestiges of the Big Split:

  - `ipykernel.find_connection_file`
    is deprecated. Use
    `jupyter_client.find_connection_file` instead.

  \- Various pieces of code specific to IPython parallel are
  deprecated in ipykernel and moved to ipyparallel.

## 4.2

### 4.2.2

[4.2.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2.2)

- Don't show interactive debugging info when kernel crashes
- Fix handling of numerical types in json_clean
- Testing fixes for output capturing

### 4.2.1

[4.2.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2.1)

- Fix default display name back to "Python X" instead of "pythonX"

### 4.2.0

[4.2 on GitHub](https://github.com/ipython/ipykernel/milestones/4.2)

- Support sending a full message in initial opening of comms
  (metadata, buffers were not previously allowed)
- When using `ipython kernel install --name` to install the IPython
  kernelspec, default display-name to the same value as `--name`.

## 4.1

### 4.1.1

[4.1.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.1.1)

- Fix missing `ipykernel.__version__` on Python 2.
- Fix missing `target_name` when opening comms from the frontend.

### 4.1.0

[4.1 on GitHub](https://github.com/ipython/ipykernel/milestones/4.1)

- add `ipython kernel install` entrypoint for installing the IPython
  kernelspec
- provisional implementation of `comm_info` request/reply for msgspec
  v5.1

## 4.0

[4.0 on GitHub](https://github.com/ipython/ipykernel/milestones/4.0)

4.0 is the first release of ipykernel as a standalone package.
