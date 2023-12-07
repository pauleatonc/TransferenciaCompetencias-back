import os


def organigrama_regional_path(instance, filename):
    # Obtiene la extensión del archivo
    ext = filename.split('.')[-1]

    # Construye el nuevo nombre del archivo
    region = instance.region.nombre if instance.region else 'SinRegion'
    competencia_nombre = instance.paso1.competencia.nombre if instance.paso1 and instance.paso1.competencia else 'SinCompetencia'

    # Formato: Organigrama-Region-Competencia.ext
    new_filename = f"Organigrama-{region}-{competencia_nombre}.{ext}"

    # Retorna la ruta completa del nuevo archivo
    return os.path.join('formulario_sectorial', new_filename)
