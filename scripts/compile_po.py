import sys
from pathlib import Path
try:
    import polib
except Exception as e:
    print('polib no está instalado:', e)
    sys.exit(2)

root = Path(__file__).resolve().parent.parent
po_files = list(root.glob('locale/**/LC_MESSAGES/*.po'))
if not po_files:
    print('No se encontraron archivos .po')
    sys.exit(0)

for po in po_files:
    try:
        p = polib.pofile(str(po))
        mo_path = po.with_suffix('.mo')
        p.save_as_mofile(str(mo_path))
        print(f'Compilado: {po} -> {mo_path}')
    except Exception as e:
        print(f'Error compilando {po}:', e)