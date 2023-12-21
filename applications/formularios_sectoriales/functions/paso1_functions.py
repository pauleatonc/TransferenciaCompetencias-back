import os


def organigrama_regional_path(instance, filename):
    # Obtiene la extensión del archivo
    ext = filename.split('.')[-1]

    # Construye el nuevo nombre del archivo
    region = instance.region.region if instance.region else 'SinRegion'

    # Accede a competencia a través de FormularioSectorial
    competencia_nombre = 'SinCompetencia'
    if instance.paso1 and instance.paso1.formulario_sectorial and instance.paso1.formulario_sectorial.competencia:
        competencia_nombre = instance.paso1.formulario_sectorial.competencia.nombre

    # Formato: Organigrama-Region-Competencia.ext
    new_filename = f"Organigrama-{region}-{competencia_nombre}.{ext}"

    # Retorna la ruta completa del nuevo archivo
    return os.path.join('formulario_sectorial', new_filename)
