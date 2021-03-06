from pathlib import Path
from furious_fastas import fastas as _fastas, Fastas as _Fastas
from platform import system


db_path = r'X:/SYMPHONY_VODKAS/fastas/latest' if system() == 'Windows' else r'/home/matteo/SYMPHONY_VODKAS/fastas/latest' 


def fastas_gui(db=db_path):
    """A terminal proto-gui for the fastas."""
    standard_fastas = {p.stem.split('_')[0]:p for p in Path(db).glob(f"*/PLGS/*.fasta")}
    path = input('fastas to use (human|wheat|..|custom path): ')
    reverse = False
    add_contaminants = False
    if str(path) in standard_fastas:
        print(f"Selected: {path}: {standard_fastas[path]}")
        print()
    else:
        path = Path(path)
        if path.exists():
            print(f"Selected: {path}")
            if '_pipelineFriendly.fasta' in path.name:
                print('We once dealt with these fastas.')
                if '_contaminated' in path.stem:
                    print("Contaminants were attached.")
                if '_reversed' in path.stem:
                    print("Fastas contain reversed sequences.")
                input('Press ENTER.')
                print()
            else:
                add_contaminants = input('Adding contaminants: to stop me write "no": ')
                add_contaminants = add_contaminants.lower() != 'no'
                print(f'Contaminants: {add_contaminants}')
                reverse = input('Reversing fastas: to stop me write "no": ')
                reverse = reverse.lower() != 'no'
                print(f'Reversing fastas: {reverse}')
                input('Press ENTER.')
                print()
        else:
            raise FileNotFoundError('Fastas are not found')    
    return path, add_contaminants, reverse, db



def fastas(path,
           add_contaminants=True,
           reverse=True,
           db=db_path):
    """Get proper fastas.

    Can prompt for usage.
    If not, simply finds out if the fastas are among the standard ones.
    If they ain't, you can choose to add in contaminants, reverse them, and make them altogether useable for iaDBs.

    Args:
        path (str): path to fasta file or one of the standard proteomes used, e.g. 'human'.
        db (str): Path to fastas DB: used when supplying reduced fasta names, e.g. 'human'.
        add_contaminants (boolean): Should we add in contaminants.
        reverse (boolean):Should we reverse the fastas.

    Returns:
        Path: path to the fastas.
    """
    standard_fastas = {p.stem.split('_')[0]:p for p in Path(db).glob(f"*/PLGS/*.fasta")}
    if str(path) in standard_fastas:
        return standard_fastas[str(path)]
    else:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError('Path does not exist.')
        if '_pipelineFriendly.fasta' in path.name:
            return path
        else:
            final_name = path.stem
            if add_contaminants:
                final_name += "_contaminated"
            if reverse:
                final_name += "_reversed"
            final_name += "_pipelineFriendly.fasta"
            outpath = path.parent/final_name
            if not outpath.exists():
                fs = _fastas(path)
                if add_contaminants:
                    from furious_fastas.contaminants import contaminants
                    fs.extend(contaminants)
                fs_gnl = _Fastas(f.to_ncbi_general() for f in fs)
                assert fs_gnl.same_fasta_types(), "Fastas are not in the same format."
                if reverse:
                    fs_gnl.reverse()
                outpath = path.parent/(path.stem + '_contaminated_reversed_pipelineFriendly.fasta')
                fs_gnl.write(outpath)
            return outpath
