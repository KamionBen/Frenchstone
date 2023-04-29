"""

Example:
    >>> import log
    >>> log.CORE.info("My message")
    2023-04-29 11:01:48,428|core  |INFO|My message
    
    les logs sont set par default sur info,
    log.set_level(log.DEBUG) par exemple pour changer le level des logs en debug
    
    les logs sont enregistrer dans un fichier temporaire.
    from log import _log
    _log.get_file_path() pour recuperer le path de ce fichier
"""

from ._log import (CORE,
                   CLASSE,
                   CARTE,
                   ENTITY,
                   ACTION)
