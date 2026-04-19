# Dynamically import all files in folder
from util import log
from pathlib import Path
import os
import importlib

_imported = False

# Automatically import all files within this folder
def import_domains():
    
    # Prevents importing again if we already have imported the domains
	global _imported
	if _imported:
		return
	
	_imported = True
	importlist = list_domains()
 
	# Import all of the files
	[importlib.import_module("db.domains."+i) for i in importlist]
  
	# Return the list of files
	return importlist

# List all of the domains within this folder
def list_domains():
    # Get path to this folder
	domainpath = Path.cwd() / "db" / "domains"

	# Filter: return true only for strings that contain ".py" and do not contain "_"
	def __importfilter__(s):
		imported = ".py" in s and "_" not in s
		if imported:
			log.info(f"Importing domain {s}")
		return imported

	# List files in this folder, run them through the above filter to get only the domain python files, then strip the ".py"
	return [i[:-3] for i in list(filter(__importfilter__, os.listdir(domainpath)))]

__all__ = import_domains() or []