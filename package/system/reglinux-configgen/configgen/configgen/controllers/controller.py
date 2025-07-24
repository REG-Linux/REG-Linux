class Controller:
    def __init__(self, guid,  name="", inputs=None, type="", index="-1", dev=None):
        self.guid = guid
        self.name = name
        self.type = type
        self.index = index
        self.dev = dev
        if inputs == None:
            self.inputs = dict()
        else:
            self.inputs = inputs

    def generateSDLGameDBLine(self):
        return _generateSdlGameControllerConfig(self)


def _generateSdlGameControllerConfig(controller):
    """Returns an SDL_GAMECONTROLLERCONFIG-formatted string for the given configuration."""
    config = []
    config.append(controller.guid)
    config.append(controller.name)
    
    for key, value in controller.inputs.items():
        config.append(f"{key}:{value}")
    
    config.append('')
    return ','.join(config)


def generateSdlGameControllerConfig(controllers):
    configs = []
    for idx, controller in controllers.items():
        configs.append(controller.generateSDLGameDBLine())
    return "\n".join(configs)


def writeSDLGameDBAllControllers(controllers, outputFile = "/tmp/gamecontrollerdb.txt"):
    with open(outputFile, "w") as text_file:
        text_file.write(generateSdlGameControllerConfig(controllers))
    return outputFile
