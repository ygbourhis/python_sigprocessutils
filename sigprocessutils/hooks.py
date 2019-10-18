from distutils.command import install  # pylint: disable=E0401


def setup_hook(config):
    """Filter config parsed from a setup.cfg to inject our defaults."""
    # Tell distutils not to put the data_files in platform-specific
    # installation locations. See here for an explanation:
    # https://groups.google.com/forum/#!topic/comp.lang.python/Nex7L-026uw
    for scheme in install.INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']
