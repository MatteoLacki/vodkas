import argparse
from docstr2argparse import parse_arguments
import logging
from pathlib import Path
from pprint import pprint

from vodkas import apex3d, peptide3d, iadbs, plgs
from vodkas.fastas import get_fastas
from vodkas.fs import find_free_path, move_folder
from vodkas.header_txt import parse_header_txt
from vodkas.logging import get_logger
from vodkas.misc import get_defaults

DEBUG = True

P = lambda x: dict(parse_arguments(x))
A = {**P(get_fastas), **P(apex3d), **P(peptide3d), **P(iadbs)}
A.update(P(plgs))

del A['input_file'], A['output_dir'], A['out_folder']
del A['fasta_file'], A['--PLGS'], A['raw_folder']

default_out = Path(r'C:/SYMPHONY_VODKAS/temp')
default_log = Path(r'C:/SYMPHONY_VODKAS/temp_logs/plgs.log')
default_server = Path(r'X:/SYMPHONY_VODKAS/temp_logs')
default_net_db = Path(r'Y:/TESTRES') if DEBUG else Path(r'Y:/RES')

A['raw_folders'] = {
    'type': Path,
    'help': 'Path(s) to the raw_folder(s) to be analysed.',
    'nargs': "+"}
A["--out_folder"] = {
    'type': Path,
    'default': default_out,
    'help': f"Local folder to save data to (there we will place the results) [default = {default_out}]."}
A["--log_file"] = {
    'type': Path,
    'default': default_log,
    'help': f"Local log file [default = {default_log}]."}
A["--log_server_folder"] = {
    'type': Path,
    'default': default_server,
    'help': f"Network folder for logs [default = {default_server}]."}
A["--network_db_folder"] = {
    'type': Path,
    'default': default_net_db,
    'help': f"Network folder for results. Set to '' (empty word) if you want to skip copying [default = {default_net_db}]."}

parser = argparse.ArgumentParser(description='Analyze Waters Raw Data with PLGS.')
for name, kwds in sorted(A.items()):
    parser.add_argument(name, **kwds)
args = parser.parse_args().__dict__

log_file = args['log_file']
log_format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s:'
logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)
log = get_logger('PLGS', log_format)
del args['log_file']

out = args['out_folder']
del args['out_folder']

network_db_folder = args['network_db_folder']
if not network_db_folder.parents[0].exists():
    raise FileNotFoundError(f"Network drive missing: mount '{network_db_folder.parents[0]}'.")

log.info("Running analysis on folders:")
log.info(args['raw_folders'])
print(args)

for raw_folder in args['raw_folders']:
    log.info(f"analyzing: {raw_folder}")
    try:
        if not raw_folder.is_dir():
            log.error(f"missing: {raw_folder}")
            raise FileNotFoundError(f"Did not find {raw_folder}")
        acquired_name = raw_folder.stem
        header_txt = parse_header_txt(raw_folder/'_HEADER.TXT')
        sample_set = header_txt['Sample Description'][:8]
        out_folder = out/sample_set/acquired_name
        plgs_ok = plgs(raw_folder, out_folder, **args)
        if plgs_ok and network_db_folder:
            ##                              Y:\RES\         2019-008\   O191017-04
            # net_folder = find_free_path(network_db_folder/sample_set/acquired_name)
            ##                              Y:\RES\         O191017-04
            net_set_folder = network_db_folder/sample_set
            net_set_folder.mkdir(parents=True, exist_ok=True)
            net_folder = find_free_path(network_db_folder/sample_set/acquired_name)
            try:
                move_folder(out_folder, net_folder)
                if not out_folder.parent.glob('*'):
                    out_folder.parent.rmdir()
                log.info("Moved results to the server.")
            except RuntimeError as e:
                log.warning(f"Could not copy '{raw_folder}'.")
                log.warning(repr(e))
            else:
                print("PLGS unsuccessful.")
        log.info(f"Finished with '{raw_folder}'.")
    except Exception as e:
        log.warning(repr(e))
log.info("PLGS finished.")
