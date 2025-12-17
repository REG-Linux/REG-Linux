"""Módulo responsável por gerenciar as configurações de bezel para o emulador Libretro."""

from json import load
from os import path, makedirs, remove, listdir, unlink, symlink
from configgen.systemFiles import OVERLAY_CONFIG_FILE
from configgen.utils.bezels import (
    gunsBorderSize,
    createTransparentBezel,
    getBezelInfos,
    fast_image_size,
    padImage,
    gun_borders_size,
    gunBorderImage,
    gunsBordersColorFomConfig,
    tatooImage,
)
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L188
RATIO_INDEXES = [
    "4/3",
    "16/9",
    "16/10",
    "16/15",
    "21/9",
    "1/1",
    "2/1",
    "3/2",
    "3/4",
    "4/1",
    "9/16",
    "5/4",
    "6/5",
    "7/9",
    "8/3",
    "8/7",
    "19/12",
    "19/14",
    "30/17",
    "32/9",
    "config",
    "squarepixel",
    "core",
    "custom",
    "full",
]


def is_ratio_defined(key, dict):
    """Verifica se uma chave está definida no dicionário."""
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0


def writeBezelConfig(
    generator,
    bezel,
    shaderBezel,
    retroarchConfig,
    rom,
    gameResolution,
    system,
    guns_borders_size,
):
    """Escreve a configuração de bezel no arquivo de configuração do RetroArch."""
    # desabilita o overlay
    # se todos os passos forem realizados com sucesso, habilita-os
    retroarchConfig["input_overlay_hide_in_menu"] = "false"
    overlay_cfg_file = OVERLAY_CONFIG_FILE

    # os bezels estão desabilitados
    # valores padrão caso algo dê errado
    retroarchConfig["input_overlay_enable"] = "false"
    retroarchConfig["video_message_pos_x"] = 0.05
    retroarchConfig["video_message_pos_y"] = 0.05

    # texto especial...
    if bezel == "none" or bezel == "":
        bezel = None

    eslog.debug("libretro bezel: {}".format(bezel))

    # criar um bezel falso se as armas precisarem
    if bezel is None and guns_borders_size is not None:
        eslog.debug("guns need border")
        gunBezelFile = "/tmp/bezel_gun_black.png"
        gunBezelInfoFile = "/tmp/bezel_gun_black.info"

        w = gameResolution["width"]
        h = gameResolution["height"]
        h5 = gunsBorderSize(w, h)

        # poderia ser melhor calcular a proporção enquanto no RA é forçado a 4/3...
        ratio = generator.getInGameRatio(system.config, gameResolution, rom)
        top = h5
        left = h5
        bottom = h5
        right = h5
        if ratio == 4 / 3:
            left = (w - (h - 2 * h5) * 4 / 3) // 2
            right = left

        with open(gunBezelInfoFile, "w") as fd:
            fd.write(
                "{"
                + f' "width":{w}, "height":{h}, "top":{top}, "left":{left}, "bottom":{bottom}, "right":{right}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000'
                + "}"
            )
        createTransparentBezel(
            gunBezelFile, gameResolution["width"], gameResolution["height"]
        )
        # se o jogo precisar de um bezel específico, para desenhar borda, considere como um bezel específico por jogo, como para thebezelproject para evitar caches
        bz_infos = {
            "png": gunBezelFile,
            "info": gunBezelInfoFile,
            "layout": None,
            "mamezip": None,
            "specific_to_game": True,
        }
    else:
        if bezel is None:
            return
        bz_infos = getBezelInfos(rom, bezel, system.name, True)
        if bz_infos is None:
            return

    overlay_info_file = bz_infos["info"]
    overlay_png_file = bz_infos["png"]
    bezel_game = bz_infos["specific_to_game"]

    # apenas o arquivo png é obrigatório
    if path.exists(overlay_info_file):
        try:
            with open(overlay_info_file) as f:
                infos = load(f)
        except:
            infos = {}
    else:
        infos = {}

    # se a imagem não estiver no tamanho correto, encontre o tamanho correto
    bezelNeedAdaptation = False

    if (
        "width" not in infos
        or "height" not in infos
        or "top" not in infos
        or "left" not in infos
        or "bottom" not in infos
        or "right" not in infos
        or shaderBezel
    ):
        viewPortUsed = False
    else:
        viewPortUsed = True

    gameRatio = float(gameResolution["width"]) / float(gameResolution["height"])

    if viewPortUsed:
        if (
            gameResolution["width"] != infos["width"]
            or gameResolution["height"] != infos["height"]
        ):
            if (
                gameResolution["width"] == 1080 and gameResolution["height"] == 1920
            ):  # tela girada (RP5)
                bezelNeedAdaptation = False
            else:
                if (
                    gameRatio < 1.6 and guns_borders_size is None
                ):  # vamos usar bezels apenas para razões de aspecto 16:10, 5:3, 16:9 e maiores ; não pular se as bordas de arma forem necessárias
                    return
                else:
                    bezelNeedAdaptation = True
        retroarchConfig["aspect_ratio_index"] = str(
            RATIO_INDEXES.index("custom")
        )  # sobrescrito do início deste arquivo
        if is_ratio_defined("ratio", system.config):
            if system.config["ratio"] in RATIO_INDEXES:
                retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index(
                    system.config["ratio"]
                )
                retroarchConfig["video_aspect_ratio_auto"] = "false"

    else:
        # quando não há informações sobre largura e altura no .info, assuma que a TV é HD 16/9 e as informações são fornecidas pelo core
        if (
            gameRatio < 1.6 and guns_borders_size is None
        ):  # vamos usar bezels apenas para razões de aspecto 16:10, 5:3, 16:9 e maiores ; não pular se as bordas de arma forem necessárias
            return
        else:
            # Sem info sobre o bezel, vamos obter a largura e altura da imagem do bezel e aplicar as
            # razões dos bezels 16:9 1920x1080 usuais (exemplo: theBezelProject)
            try:
                infos["width"], infos["height"] = fast_image_size(overlay_png_file)
                infos["top"] = int(infos["height"] * 2 / 1080)
                infos["left"] = int(
                    infos["width"] * 241 / 1920
                )  # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = onde começa a viewport
                infos["bottom"] = int(infos["height"] * 2 / 1080)
                infos["right"] = int(infos["width"] * 241 / 1920)
                bezelNeedAdaptation = True
            except:
                pass  # ai, nenhuma razão será aplicada.
        if (
            gameResolution["width"] == infos["width"]
            and gameResolution["height"] == infos["height"]
        ):
            bezelNeedAdaptation = False
        if not shaderBezel:
            retroarchConfig["aspect_ratio_index"] = str(RATIO_INDEXES.index("custom"))
            if (
                is_ratio_defined("ratio", system.config)
                and system.config["ratio"] in RATIO_INDEXES
            ):
                retroarchConfig["aspect_ratio_index"] = RATIO_INDEXES.index(
                    system.config["ratio"]
                )
                retroarchConfig["video_aspect_ratio_auto"] = "false"

    if not shaderBezel:
        retroarchConfig["input_overlay_enable"] = "true"
    retroarchConfig["input_overlay_scale"] = "1.0"
    retroarchConfig["input_overlay"] = overlay_cfg_file
    retroarchConfig["input_overlay_hide_in_menu"] = "true"

    if "opacity" not in infos:
        infos["opacity"] = 1.0
    if "messagex" not in infos:
        infos["messagex"] = 0.0
    if "messagey" not in infos:
        infos["messagey"] = 0.0

    retroarchConfig["input_overlay_opacity"] = infos["opacity"]
    if retroarchConfig["aspect_ratio_index"] == str(RATIO_INDEXES.index("custom")):
        retroarchConfig["video_viewport_bias_x"] = "0.000000"
        retroarchConfig["video_viewport_bias_y"] = "0.000000"

    # opção stretch
    if (
        system.isOptSet("bezel_stretch")
        and system.getOptBoolean("bezel_stretch") == True
    ):
        bezel_stretch = True
    else:
        bezel_stretch = False

    tattoo_output_png = "/tmp/bezel_tattooed.png"
    if bezelNeedAdaptation:
        wratio = gameResolution["width"] / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])

        # Stretch também cuida de cortar o bezel e adaptar a viewport, se a proporção for < 16:9
        if (
            gameResolution["width"] < infos["width"]
            or gameResolution["height"] < infos["height"]
        ):
            eslog.debug("Screen resolution smaller than bezel: forcing stretch")
            bezel_stretch = True
        if bezel_game is True:
            output_png_file = "/tmp/bezel_per_game.png"
            create_new_bezel_file = True
        else:
            # A lógica para cache de bezels do sistema não é mais sempre verdadeira agora que temos tatuagens
            output_png_file = (
                "/tmp/"
                + path.splitext(path.basename(overlay_png_file))[0]
                + "_adapted.png"
            )
            if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
                create_new_bezel_file = True
            else:
                if (not path.exists(tattoo_output_png)) and path.exists(
                    output_png_file
                ):
                    create_new_bezel_file = False
                    eslog.debug(f"Using cached bezel file {output_png_file}")
                else:
                    try:
                        remove(tattoo_output_png)
                    except:
                        pass
                    create_new_bezel_file = True
            if create_new_bezel_file:
                fadapted = [
                    "/tmp/" + f for f in listdir("/tmp/") if (f[-12:] == "_adapted.png")
                ]
                fadapted.sort(key=lambda x: path.getmtime(x))
                # Manter apenas os últimos 10 bezels gerados para economizar espaço em tmpfs /tmp
                if len(fadapted) >= 10:
                    for i in range(10):
                        fadapted.pop()
                    eslog.debug(f"Removing unused bezel file: {fadapted}")
                    for fr in fadapted:
                        try:
                            remove(fr)
                        except:
                            pass

        if bezel_stretch:
            borderx = 0
            viewportRatio = float(infos["width"]) / float(infos["height"])
            if viewportRatio - gameRatio > 0.01:
                new_x = int(infos["width"] * gameRatio / viewportRatio)
                delta = int(infos["width"] - new_x)
                borderx = delta // 2
            eslog.debug(f"Bezel_stretch: need to cut off {borderx} pixels")
            retroarchConfig["custom_viewport_x"] = (
                infos["left"] - borderx / 2
            ) * wratio
            retroarchConfig["custom_viewport_y"] = infos["top"] * hratio
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"] + borderx
            ) * wratio
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            ) * hratio
            retroarchConfig["video_message_pos_x"] = infos["messagex"] * wratio
            retroarchConfig["video_message_pos_y"] = infos["messagey"] * hratio
        else:
            xoffset = gameResolution["width"] - infos["width"]
            yoffset = gameResolution["height"] - infos["height"]
            retroarchConfig["custom_viewport_x"] = infos["left"] + xoffset / 2
            retroarchConfig["custom_viewport_y"] = infos["top"] + yoffset / 2
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"]
            )
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            )
            retroarchConfig["video_message_pos_x"] = infos["messagex"] + xoffset / 2
            retroarchConfig["video_message_pos_y"] = infos["messagey"] + yoffset / 2

        if create_new_bezel_file is True:
            # Padding left and right borders for ultrawide screens (larger than 16:9 aspect ratio)
            # or up/down for 4K
            eslog.debug(f"Generating a new adapted bezel file {output_png_file}")
            try:
                padImage(
                    overlay_png_file,
                    output_png_file,
                    gameResolution["width"],
                    gameResolution["height"],
                    infos["width"],
                    infos["height"],
                    bezel_stretch,
                )
            except Exception as e:
                eslog.debug(f"Failed to create the adapated image: {e}")
                return
        overlay_png_file = output_png_file  # substituir pelo novo arquivo (recriado ou em cache em /tmp)
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png
    else:
        if viewPortUsed:
            retroarchConfig["custom_viewport_x"] = infos["left"]
            retroarchConfig["custom_viewport_y"] = infos["top"]
            retroarchConfig["custom_viewport_width"] = (
                infos["width"] - infos["left"] - infos["right"]
            )
            retroarchConfig["custom_viewport_height"] = (
                infos["height"] - infos["top"] - infos["bottom"]
            )
        retroarchConfig["video_message_pos_x"] = infos["messagex"]
        retroarchConfig["video_message_pos_y"] = infos["messagey"]
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            tatooImage(overlay_png_file, tattoo_output_png, system)
            overlay_png_file = tattoo_output_png

    if guns_borders_size is not None:
        eslog.debug("Draw gun borders")
        output_png_file = "/tmp/bezel_gunborders.png"
        inner_size, outer_size = gun_borders_size(guns_borders_size)
        gunBorderImage(
            overlay_png_file,
            output_png_file,
            inner_size,
            outer_size,
            gunsBordersColorFomConfig(system.config),
        )
        overlay_png_file = output_png_file

    eslog.debug(f"Bezel file set to {overlay_png_file}")
    writeBezelCfgConfig(overlay_cfg_file, overlay_png_file)

    # Para shaders que irão querer usar a decoração do Batocera como parte do shader em vez de um overlay
    if shaderBezel:
        # Criar caminho se necessário, limpar bezels antigos
        shaderBezelPath = "/var/run/shader_bezels"
        shaderBezelFile = shaderBezelPath + "/bezel.png"
        if not path.exists(shaderBezelPath):
            makedirs(shaderBezelPath)
            eslog.debug("Creating shader bezel path {}".format(overlay_png_file))
        if path.exists(shaderBezelFile):
            eslog.debug("Removing old shader bezel {}".format(shaderBezelFile))
            if path.islink(shaderBezelFile):
                unlink(shaderBezelFile)
            else:
                remove(shaderBezelFile)

        # Link bezel png file to the fixed path.
        # Shaders should use this path to find the art.
        symlink(overlay_png_file, shaderBezelFile)
        eslog.debug(
            "Symlinked bezel file {} to {} for selected shader".format(
                overlay_png_file, shaderBezelFile
            )
        )


def writeBezelCfgConfig(cfgFile, overlay_png_file):
    """Escreve o arquivo de configuração do bezel."""
    fd = open(cfgFile, "w")
    fd.write("overlays = 1\n")
    fd.write('overlay0_overlay = "' + overlay_png_file + '"\n')
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()


def isLowResolution(gameResolution):
    """Verifica se a resolução é baixa."""
    return gameResolution["width"] < 480 or gameResolution["height"] < 480
