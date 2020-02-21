from vodkas.cli import make_cli
from vodkas.peptide3d import peptide3d

if __name__ == '__main__':
    make_cli(peptide3d, custom_delete=['--subprocess_run_kwds'])